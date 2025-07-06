# ======================================================================================
# ----------Responsavel pela limpeza e pre-processamento de dados de emails-------------
# ======================================================================================

import os
import re
import pandas as pd
import torch

from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from dotenv import load_dotenv

load_dotenv()


class EmailPreprocessor:

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """
        Aplica a sequencia de pre-processamento a uma unica string de email.
        """
        if not isinstance(text, str):
            return ""
        
        # Ordem de processamento:
        # 1. Remover URLs e enderecos de email (sao ruidos universais)
        text = self._remove_urls_emails(text)
        # 2. Remover cabecalhos de email (parte mais complexa)
        text = self._remove_headers_refined(text) 
        # 3. Remover assinaturas (tambem ruidos)
        text = self._remove_signatures_refined(text) 
        # 4. Converter para minusculas
        text = self._to_lowercase(text) 
        # 5. Normalizar pontuacao e caracteres especiais (mantem numeros, remove excesso)
        text = self._normalize_text_characters(text)
        # 6. Remover espacos extras
        text = self._remove_extra_whitespace(text) 
        
        return text

    # --- FUNCOES DE LIMPEZA REFINADAS ---

    def _remove_headers_refined(self, email_text: str) -> str:
        """
        Remove linhas de cabecalho comuns (From, To, Subject, etc.) no inicio do email.
        Tenta encontrar o corpo do email de forma mais precisa.
        """
        if not isinstance(email_text, str):
            return ""
        
        lines = email_text.split('\n')
        body_start_index = 0
        
        # Padroes comuns de inicio de linha de cabecalho (case-insensitive e com espacos no inicio)
        # Mais robusto que apenas novas linhas duplas
        header_patterns = re.compile(
            r'^(Message-ID|Date|From|To|Subject|Cc|Bcc|Mime-Version|Content-Type|Content-Transfer-Encoding|X-From|X-To|X-cc|X-bcc|X-Folder|X-Origin|X-FileName):',
            re.IGNORECASE
        )
        
        # Itera sobre as linhas para encontrar o fim do cabecalho
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Se a linha esta vazia apos cabecalhos, ou nao corresponde a um padrao de cabecalho
            if not line_stripped or not header_patterns.match(line_stripped):
                body_start_index = i
                # Se encontrou uma linha nao-cabecalho ou vazia, verifica se o proximo eh conteudo real
                # Isso evita cortar o corpo se houver um cabecalho que nao esta na lista
                if i + 1 < len(lines) and lines[i+1].strip(): # Proxima linha nao vazia, assume que e o corpo
                    break
            
        # Junta as linhas a partir do inicio do corpo
        return '\n'.join(lines[body_start_index:]).strip()

    def _remove_signatures_refined(self, email_text: str) -> str:
        """
        Remove assinaturas comuns e avisos legais do final do email.
        """
        if not isinstance(email_text, str):
            return ""
        
        patterns = [
            r'-----Original Message-----', r'From:.*', r'Sent:.*', r'To:.*',
            r'Subject:.*', r'[\s]*_{3,}[\s]*', r'[\s]*-{3,}[\s]*',
            r'Regards,', r'Sincerely,', r'Thank you,', r'V/R,',
            r'Best regards,', r'Sent from my BlackBerry', r'Confidentiality Notice:',
            r'This email and any files transmitted with it are confidential',
            r'This message is intended only for the use of the individual or entity to which it is addressed and may contain information that is confidential and privileged.' 
        ]
        
        # Percorre os padroes de assinatura, removendo do final do texto
        for pattern in patterns:
            # re.DOTALL faz com que '.' inclua novas linhas para pegar assinaturas multi-linha
            match = re.search(pattern, email_text, re.IGNORECASE | re.DOTALL)
            if match:
                email_text = email_text[:match.start()].strip()
                break # Para apos encontrar a primeira assinatura e remover
        return email_text

    def _remove_urls_emails(self, text: str) -> str:
        # Remove URLs e enderecos de email
        if not isinstance(text, str):
            return ""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S*@\S*\s?', '', text)
        return text
    
    def _to_lowercase(self, text: str) -> str:
        # Converte texto para minusculas
        if not isinstance(text, str):
            return ""
        return text.lower()
    
    # Nova funcao para normalizar pontuacao e manter numeros
    def _normalize_text_characters(self, text: str) -> str:
        """
        Normaliza caracteres especiais (substitui por espaco) e mantem letras, numeros e espacos.
        """
        if not isinstance(text, str):
            return ""
        
        # Substitui qualquer coisa que NAO seja letra (a-z), numero (0-9) ou espaco (\s) por um espaco
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove multiplos espacos e espacos no inicio/fim
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _remove_extra_whitespace(self, text: str) -> str:
        # Remove espacos extras
        if not isinstance(text, str):
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def preprocess_dataframe(self, dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:

        """
        Aplica a sequencia de pre-processamento a uma coluna de DataFrame.
        """
        if column_name not in dataframe.columns:
            raise ValueError(f"A coluna '{column_name}' nao existe no DataFrame.")
        
        processed_df = dataframe.copy()
        
        # Garante que a coluna e do tipo string
        series_to_process = processed_df[column_name].astype(str).fillna('') 

        print(f"Iniciando pre-processamento da coluna '{column_name}'...")
        
        series_to_process = series_to_process.apply(self.clean_text) 
        print("Pre-processamento concluido.")

        processed_df[f'{column_name}_processed'] = series_to_process
        return processed_df

# Email Dataset (para PyTorch Trainer)
class EmailDataset(Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        # Converte itens para tensores PyTorch
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        # Retorna o numero de amostras
        return len(self.encodings['input_ids'])

# Carrega, pre-processa e tokeniza datasets de emails para treinamento da IA
def prepare_data_for_ia(file_paths: list[str], text_column: str = 'message', category_column: str = 'label'):
    """
    Carrega, pre-processa e tokeniza datasets de emails para treinamento da IA.
    """
    try:
        all_dfs = []

        for f_path in file_paths:
            if os.path.exists(f_path):
                df_lang = pd.read_csv(f_path)
                print(f"--- CSV '{f_path}' Carregado com Sucesso ({len(df_lang)} amostras) ---")
                all_dfs.append(df_lang)
            else:
                print(f"AVISO: CSV '{f_path}' nao encontrado. Sera ignorado.")

        if not all_dfs:
            raise FileNotFoundError("Nenhum arquivo CSV de dados encontrado para processamento. Pelo menos um arquivo deve ser fornecido e existir.")

        df_combined = pd.concat(all_dfs, ignore_index=True)
        print(f"Dataset combinado para treinamento: {len(df_combined)} amostras totais.")

        if text_column not in df_combined.columns:
            raise ValueError(f"Coluna de texto '{text_column}' nao encontrada no dataset combinado.")
        
        preprocessor = EmailPreprocessor()
        df_cleaned = preprocessor.preprocess_dataframe(df_combined.copy(), text_column)
        
        cleaned_text_column = f'{text_column}_processed'
        if cleaned_text_column not in df_cleaned.columns:
             raise ValueError(f"A coluna '{cleaned_text_column}' nao foi criada pela classe EmailPreprocessor.")

        print("\nPrimeiras 5 linhas do DataFrame com texto limpo:")
        print(df_cleaned[[text_column, cleaned_text_column]].head())
        
        # Inicializa labels como None
        labels = None

        if category_column in df_cleaned.columns:
            print(f"\n--- Preparando Labels da coluna '{category_column}' ---")
            unique_categories = df_cleaned[category_column].unique()
            print(f"Categorias unicas encontradas: {unique_categories}")

            # Mapeamento de categorias - string para numericas (0, 1)
            category_mapping = {
                'Produtivo': 0,
                'Improdutivo': 1,
            }

            df_cleaned['numeric_labels'] = df_cleaned[category_column].map(category_mapping)
            
            initial_rows = len(df_cleaned)

            df_cleaned.dropna(subset=['numeric_labels'], inplace=True)
            if len(df_cleaned) < initial_rows:
                print(f"AVISO: {initial_rows - len(df_cleaned)} linhas removidas devido a categorias nao mapeadas ou nulas.")
            
            df_cleaned['numeric_labels'] = df_cleaned['numeric_labels'].astype(int)
            labels = df_cleaned['numeric_labels'].tolist()
            print(f"Primeiras 5 labels numericas: {labels[:5]}")
            print(f"Numero total de amostras com labels: {len(labels)}")
        else:
            print(f"\nAVISO: Coluna de categoria '{category_column}' nao encontrada. Nao serao geradas labels para treinamento.")
        
        # Variaveis do .env com valores default para configuracao do tokenizador
        MODEL_NAME_FROM_ENV = os.getenv("MODEL_NAME", "distilbert-base-multilingual-cased")
        MAX_LENGTH_FROM_ENV = int(os.getenv("MAX_LENGTH", 128))

        print(f"\n--- Carregando Tokenizador: {MODEL_NAME_FROM_ENV} ---")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_FROM_ENV)
        
        print(f"--- Aplicando Tokenizacao na coluna '{cleaned_text_column}' ({len(df_cleaned)} amostras) ---")
        tokenized_data = tokenizer(
            df_cleaned[cleaned_text_column].tolist(), # list de 420
            truncation=True,
            padding='max_length',
            max_length=MAX_LENGTH_FROM_ENV,
            return_tensors='pt'
        )

        print("\nPrimeiras 5 entradas tokenizadas (input_ids):")
        for i in range(min(5, len(df_cleaned))):
            print(f"Original: {df_cleaned[cleaned_text_column].iloc[i][:70]}...")
            print(f"Input IDs: {tokenized_data['input_ids'][i][:10]}...")
            print("-" * 20)
        
        # Adiciona as colunas de tokenizacao ao DataFrame
        # Agora tokenized_data tem 420 entradas, e df_cleaned tem 420 linhas. Match!
        df_cleaned['input_ids'] = tokenized_data['input_ids'].tolist()
        df_cleaned['attention_mask'] = tokenized_data['attention_mask'].tolist()
        if 'token_type_ids' in tokenized_data:
            df_cleaned['token_type_ids'] = tokenized_data['token_type_ids'].tolist()

        return df_cleaned 

    except FileNotFoundError as e:
        print(f"ERRO: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao processar os dados: {e}")
        import traceback
        traceback.print_exc()
        return None

# =============================================================================
# ------------------------- Bloco de teste local ------------------------------
# =============================================================================

if __name__ == "__main__":

    test_file_path_en = './datasets/email_dataset_en.csv'
    test_file_path_pt = './datasets/email_dataset_pt.csv'

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)         # Evita truncar dados
    pd.set_option("display.max_colwidth", None)

    processed_df_test = prepare_data_for_ia(
        file_paths=[test_file_path_en, test_file_path_pt],
        text_column='message',
        category_column='label'
    )

    if processed_df_test is not None:
        print("\n--- DataFrame Combinado, Pre-processado e Tokenizado (Teste) ---")
        print(processed_df_test[['message', 'message_processed', 'numeric_labels', 'input_ids', 'attention_mask']].head())