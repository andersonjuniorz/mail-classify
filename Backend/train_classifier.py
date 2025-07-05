import os
import torch # AGORA é seguro importar torch
import pandas as pd
import sys # Para sys.exit()

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers.trainer import Trainer
from transformers.training_args import TrainingArguments

from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from myApp.data.data_preprocessing import EmailDataset, prepare_data_for_ia

from dotenv import load_dotenv # load_dotenv precisa ser importado e executado primeiro

if os.name == 'posix': # Módulo resource só está disponível em sistemas Unix-like
    import resource 

# =========================================================================
# === INÍCIO DO BLOCO DE CONFIGURAÇÃO DE DISPOSITIVO (CPU/GPU) VIA .env ===
# ESTE BLOCO DEVE SER EXECUTADO ANTES DE QUALQUER 'import torch'
# =========================================================================

load_dotenv() # Carrega as variáveis de ambiente AGORA MESMO

# 1. Lê as preferências do usuário do .env
USE_GPU_PREFERENCE = os.getenv("USE_GPU", "False").lower() == "true"
MIN_GPU_VRAM_GB = float(os.getenv("MIN_GPU_VRAM_GB", 4.0)) 
MAX_RAM_MB = int(os.getenv("MAX_RAM_MB", 0)) # Lê o limite de RAM em MB (0 = sem limite)

# Variável para armazenar a decisão final do dispositivo
final_device = "cpu" # Assume CPU por padrão

# 2. Define a variável de ambiente CUDA_VISIBLE_DEVICES baseado na preferência INICIAL
# Esta variável PRECISA ser setada antes do PyTorch ser importado.
if not USE_GPU_PREFERENCE:
    # Se o usuário escolheu explicitamente NÃO usar GPU, forçamos CPU aqui.
    os.environ["CUDA_VISIBLE_DEVICES"] = "" 
    print("\nINFO: Preferência definida para CPU (USE_GPU=False). GPU(s) ocultas do PyTorch.")
    # Como a preferência é CPU, já sabemos o dispositivo final
    final_device = "cpu"
else:
    # Se o usuário escolheu usar GPU, NÃO setamos a variável de ambiente AGORA.
    # Isso permite que o PyTorch tente detectar GPUs quando for importado.
    # A verificação de VRAM e mensagens mais detalhadas virão após o import torch.
    print("\nINFO: Preferência definida para GPU (USE_GPU=True). Tentando usar GPU se disponível e suficiente VRAM.")
    # O final_device será determinado no bloco principal após o import torch

# =========================================================================
# === FIM DO BLOCO DE CONFIGURAÇÃO DE DISPOSITIVO ===
# =========================================================================


# =========================================================================
# === INÍCIO DOS IMPORTS DAS BIBLIOTECAS (AGORA É SEGURO IMPORTAR TORCH) ===
# =========================================================================


# =========================================================================
# === FIM DOS IMPORTS ===
# =========================================================================


# --- Configurações do Modelo com fallback (lidos do .env e convertidos para o tipo correto) ---
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-multilingual-cased")
NUM_LABELS = int(os.getenv("NUM_LABELS", 2))
MAX_LENGTH = int(os.getenv("MAX_LENGTH", 64)) # Usei 128, mas reduzi pra 64 pra economizar RAM
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1)) # Reduzi de 8 para 1 para economizar RAM
LEARNING_RATE = float(os.getenv("LEARNING_RATE", 2e-5))
NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", 3))


# --- Função para calcular métricas de avaliação do modelo ---
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    # average='weighted' é bom para classes desbalanceadas
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# --- Bloco de execução principal do script ---
if __name__ == "__main__":
    print("--- Iniciando Treinamento do Classificador de E-mails ---")

    # =========================================================================
    # === BLOCO DE DECISÃO FINAL DE DISPOSITIVO E APLICAÇÃO DE LIMITE DE RAM ===
    # =========================================================================
    # Re-avalia o dispositivo final se a preferência era GPU
    if USE_GPU_PREFERENCE: 
        if torch.cuda.is_available():
            try:
                gpu_total_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if gpu_total_memory_gb >= MIN_GPU_VRAM_GB: 
                    final_device = "cuda" # Decisão final: usar GPU
                    print(f"\nINFO: Usando GPU {torch.cuda.get_device_name(0)} com {gpu_total_memory_gb:.2f} GB VRAM.")
                else:
                    print(f"\nAVISO: VRAM da GPU ({gpu_total_memory_gb:.2f} GB) abaixo do limite ({MIN_GPU_VRAM_GB} GB). Treinamento na CPU.")
                    final_device = "cpu" # Força CPU se VRAM insuficiente
            except RuntimeError as e:
                print(f"\nAVISO: Erro ao acessar propriedades da GPU (Device 0): {e}. Treinamento na CPU.")
                final_device = "cpu" # Força CPU em caso de erro
        else:
            print("\nAVISO: GPU não detectada ou acessível. O treinamento continuará na CPU.")
            final_device = "cpu" # Força CPU se GPU não disponível
    # Se USE_GPU_PREFERENCE era False, final_device já é "cpu" do bloco inicial.

    # APLICAR LIMITE DE RAM APENAS SE O FINAL_DEVICE FOR CPU
    if final_device == "cpu" and MAX_RAM_MB > 0 and os.name == 'posix':
        try:
            soft_limit_bytes = MAX_RAM_MB * 1024 * 1024 # Converte MB para bytes
            # Define o limite de memória virtual para o processo.
            # RLIMIT_AS (Address Space) é a memória virtual total que o processo pode alocar.
            resource.setrlimit(resource.RLIMIT_AS, (soft_limit_bytes, soft_limit_bytes))
            print(f"\nINFO: Limite de RAM definido para {MAX_RAM_MB} MB para o processo na CPU. O processo falhará com MemoryError se exceder este limite.")
        except Exception as e:
            print(f"\nAVISO: Não foi possível definir o limite de RAM: {e}. O treinamento continuará sem limite explícito de processo.")
    elif final_device == "cuda" and MAX_RAM_MB > 0 and os.name == 'posix':
        print("\nINFO: Limite de RAM em CPU (MAX_RAM_MB) será ignorado, pois o treinamento está usando GPU.")
    # =========================================================================
    # === FIM DO BLOCO DE DECISÃO FINAL DE DISPOSITIVO ===
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: PREPARAÇÃO DOS DADOS (fica logo após a config de GPU/CPU) ---
    # -------------------------------------------------------------------------
    
    # Obtenha o caminho base e a lista de idiomas dos datasets do .env
    dataset_base_path = os.getenv('DATASET_BASE_PATH')
    dataset_languages_str = os.getenv('DATASET_LANGUAGES')

    if not dataset_base_path or not dataset_languages_str:
        print("ERRO: Variáveis de ambiente 'DATASET_BASE_PATH' ou 'DATASET_LANGUAGES' não definidas no .env.")
        print("Por favor, verifique seu arquivo .env.")
        sys.exit(1) # Use sys.exit(1) para indicar erro

    # Constrói a lista de caminhos de CSV dinamicamente
    languages = [lang.strip() for lang in dataset_languages_str.split(',') if lang.strip()]
    all_csv_paths = []
    for lang in languages:
        csv_path = os.path.join(dataset_base_path, f"email_dataset_{lang}.csv")
        all_csv_paths.append(csv_path)

    # --- DIAGNÓSTICO DE CAMINHOS (mantido para sua depuração visual) ---
    print("\n--- DIAGNÓSTICO DE CAMINHOS ---")
    print(f"Diretório de Trabalho Atual (CWD): {os.getcwd()}")
    print(f"DATASET_BASE_PATH lido do .env: '{dataset_base_path}'")
    print(f"Caminhos CSV construídos e verificação de existência:")
    
    found_any_file = False
    for p in all_csv_paths:
        exists = os.path.exists(p)
        print(f"  - '{p}' (Existe: {exists})")
        if exists:
            found_any_file = True
    print("-----------------------------\n")
    # FIM DO DIAGNÓSTICO

    # Se a lista de caminhos estiver vazia (ex: DATASET_LANGUAGES vazio no .env)
    if not all_csv_paths: 
        print(f"ERRO: Nenhuma linguagem de dataset especificada em DATASET_LANGUAGES no .env.")
        sys.exit(1) # Use sys.exit(1) para indicar erro
    
    # Se, após o diagnóstico, nenhum arquivo existir (mesmo que a lista não esteja vazia)
    if not found_any_file:
         print(f"ERRO CRÍTICO: Nenhum arquivo CSV do dataset foi realmente encontrado. Verifique os caminhos absolutos/relativos e a capitalização no seu .env e no seu sistema de arquivos.")
         sys.exit(1) # Força a saída para não continuar com erro de dados

    text_col = 'message' 
    category_col = 'label' 

    df_final = prepare_data_for_ia(
        file_paths=all_csv_paths,
        text_column=text_col, 
        category_column=category_col
    )
    
    if df_final is None:
        print("Erro na preparação dos dados. O treinamento não pode continuar.")
        sys.exit(1) # Use sys.exit(1) para indicar erro

    if 'numeric_labels' not in df_final.columns:
        print("ERRO: Coluna 'numeric_labels' não encontrada no DataFrame. Verifique o mapeamento de categorias em data_preprocessing.py.")
        sys.exit(1) # Use sys.exit(1) para indicar erro
    
    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: DIVISÃO E CRIAÇÃO DE DATASETS (fica logo após a prep de dados) ---
    # -------------------------------------------------------------------------
    
    train_df, val_df = train_test_split(
        df_final, 
        test_size=0.2, 
        random_state=42, 
        stratify=df_final['numeric_labels'] 
    )

    print(f"\nConjunto de Treinamento: {len(train_df)} amostras")
    print(f"Conjunto de Validação: {len(val_df)} amostras")

    train_encodings = {
        'input_ids': train_df['input_ids'].tolist(),
        'attention_mask': train_df['attention_mask'].tolist(),
        'token_type_ids': train_df['token_type_ids'].tolist() if 'token_type_ids' in df_final.columns else None
    }
    val_encodings = {
        'input_ids': val_df['input_ids'].tolist(),
        'attention_mask': val_df['attention_mask'].tolist(),
        'token_type_ids': val_df['token_type_ids'].tolist() if 'token_type_ids' in df_final.columns else None
    }

    train_encodings = {k: v for k, v in train_encodings.items() if v is not None}
    val_encodings = {k: v for k, v in val_encodings.items() if v is not None}

    train_dataset = EmailDataset(train_encodings, train_df['numeric_labels'].tolist())
    val_dataset = EmailDataset(val_encodings, val_df['numeric_labels'].tolist())

    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: CARREGAMENTO DO MODELO E TOKENIZADOR ---
    # -------------------------------------------------------------------------

    print(f"\n--- Carregando Modelo para Classificação: {MODEL_NAME} ---")
    # O modelo será carregado na CPU ou GPU dependendo das variáveis de ambiente e disponibilidade real
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME) 

    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: CONFIGURAÇÃO DOS ARGUMENTOS DE TREINAMENTO ---
    # -------------------------------------------------------------------------

    print("\n--- Configurando Argumentos de Treinamento ---")
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE, # Será batch_size real na CPU
        per_device_eval_batch_size=BATCH_SIZE,  # Será batch_size real na CPU
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=500,
        eval_strategy="epoch", 
        save_strategy="epoch",   
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        report_to="none"
    )

    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: INICIALIZAÇÃO DO TRAINER E TREINAMENTO ---
    # -------------------------------------------------------------------------

    print("\n--- Inicializando e Treinando o Modelo ---")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    # -------------------------------------------------------------------------
    # --- PRÓXIMO BLOCO: AVALIAÇÃO E SALVAMENTO DO MODELO ---
    # -------------------------------------------------------------------------

    print("\n--- Avaliando o Modelo no Conjunto de Validação ---")
    eval_results = trainer.evaluate()
    print(f"Resultados da Avaliação: {eval_results}")

    output_model_path = "./fine_tuned_classifier"
    print(f"\n--- Salvando Modelo e Tokenizador em: {output_model_path} ---")
    trainer.save_model(output_model_path)
    tokenizer.save_pretrained(output_model_path)
    print("Modelo e Tokenizador salvos com sucesso!")

    print("\n--- Treinamento Concluído! O modelo está pronto para ser integrado ao Flask. ---")