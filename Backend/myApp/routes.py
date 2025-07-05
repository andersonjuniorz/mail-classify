from flask import request, jsonify
import PyPDF2
import os
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

from myApp.data.data_preprocessing import EmailPreprocessor 

load_dotenv()

# ==============================================================
# ------------------- Configuracoes da IA ----------------------
# ==============================================================

# Configurando dados da IA + Fallback (caso os dados nao sejam encontrados)
MODEL_PATH = os.getenv("MODEL_PATH", "./fine_tuned_classifier")
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-multilingual-cased")
MAX_LENGTH = int(os.getenv("MAX_LENGTH", 64))

# Mapeamento reverso para exibir 
# labels em texto (ID numerico -> string categoria)
LABEL_MAP = {
    0: 'Produtivo',
    1: 'Improdutivo'
}

# ==============================================================
# ------------- Carregar Modelo e Tokenizador ------------------
# ==============================================================

# Define o dispositivo: CPU ou GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n--- Carregando Modelo de Classificação da IA para o Flask (dispositivo: {device}) ---")

try:
    # Carrega o tokenizador (com base no caminho do modelo salvo)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

    # Carrega o modelo treinado (tbm com base no caminho do modelo salvo)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    model.to(device) # Move o modelo para o dispositivo correto (CPU ou GPU)
    model.eval()    # Coloca o modelo em modo de avaliacao (sem treinamento)
    
    print("Modelo de IA e Tokenizador carregados com sucesso no Flask!")

except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo ou tokenizador do Flask: {e}")
    tokenizer = None
    model = None

# Instancia do pre-processador de email (sua classe)
email_preprocessor = EmailPreprocessor()


# ==============================================================
# ------------------ Classificação da IA -----------------------
# ==============================================================

# Chamada para classificar o texto extraido/digitado
def classify_email(email_text: str):

    if not model or not tokenizer:
        print("ERRO: Modelo ou tokenizador não carregados. Não é possível classificar.")
        return "Erro de IA", 0.0 # Retorna um erro e probabilidade nula

    # 1. Pre-processar o texto (limpeza)
    cleaned_text = email_preprocessor.clean_text(email_text) 

    # Se texto nao foi limpo retorna erro
    if not cleaned_text.strip():
        return "Texto Vazio", 0.0

    # 2. Tokenizar o texto
    inputs = tokenizer(
        cleaned_text,
        return_tensors="pt", 
        truncation=True,
        padding='max_length',
        max_length=MAX_LENGTH # Usa o MAX_LENGTH configurado
    )
    # Move os inputs tokenizados para o mesmo dispositivo do modelo (CPU ou GPU)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # 3. Fazer a inferencia (previsao)
    # Desativa o calculo de gradientes 
    # (economiza memoria e e mais rapido para inferencia)
    with torch.no_grad():
        outputs = model(**inputs)
    

    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class_id = int(torch.argmax(probabilities, dim=-1).item())

    predicted_category = LABEL_MAP.get(predicted_class_id, "Desconhecido")
    
    return predicted_category, probabilities.tolist()[0]


# ==============================================================
# ------------ Geração de Resposta Automática da IA ------------
# ==============================================================

def generate_response(category: str):
    
    if category == 'Produtivo':
        return "Prezado(a) [Nome do Cliente/Colega],\n\nRecebemos sua mensagem e já estamos analisando sua solicitação/dúvida. Em breve entraremos em contato com mais detalhes ou a solução.\n\nAtenciosamente,\n[Nome da Empresa/Equipe]"
    
    elif category == 'Improdutivo':
        return "Prezado(a) [Nome do Cliente/Colega],\n\nAgradecemos sua mensagem. Não é necessária nenhuma ação imediata de nossa parte. Manteremos você informado(a) sobre novidades futuras.\n\nAtenciosamente,\n[Nome da Empresa/Equipe]"
    
    elif category == 'Texto Vazio': # Resposta para texto que ficou vazio após limpeza
        return "Desculpe, não conseguimos processar o conteúdo fornecido. Por favor, certifique-se de que o texto do e-mail é relevante."
    
    else: # Categoria desconhecida ou erro de IA
        return "Prezado(a) cliente,\n\nRecebemos sua mensagem. Infelizmente, não conseguimos categorizá-la no momento. Por favor, reformule sua dúvida ou entre em contato diretamente com nossa equipe de suporte se for urgente.\n\nAtenciosamente,\n[Nome da Empresa/Equipe]"


# ==============================================================
# ------ Rota de Upload do Flask (onde a IA será usada) --------
# ==============================================================

# Chamado quando a rota /upload e acessada
def upload_files():
    processed_contents = [] # Lista para armazenar o resultado de cada e-mail processado
    
    # Logica para lidar com UPLOAD DE ARQUIVOS (txt, pdf)
    if 'files' in request.files and request.files.getlist('files'):
        uploaded_files = request.files.getlist('files')
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            
            file_content = file.read()
            file.seek(0)
            
            extracted_text = ""

            # .TXT - Extracao de texto baseada no tipo de arquivo
            if file.content_type == 'text/plain':

                try:
                    extracted_text = file_content.decode('utf-8').strip()

                except UnicodeDecodeError:
                    extracted_text = 'Não foi possível decodificar o arquivo TXT (codificação inválida).'
            
            # .PDF - Extracao de texto baseada no tipo de arquivo
            elif file.content_type == 'application/pdf':

                try:
                    pdf_reader = PyPDF2.PdfReader(file.stream)
                    pdf_text = ""

                    for page_num in range(len(pdf_reader.pages)):

                        page = pdf_reader.pages[page_num]
                        pdf_text += page.extract_text() or ""

                    extracted_text = pdf_text.strip()

                except Exception as e:
                    extracted_text = f'Não foi possível extrair texto do PDF: {str(e)}'
            
            else:
                extracted_text = 'Tipo de arquivo não suportado para extração de texto.'
            

            # ==============================================================
            # ------ INTEGRAÇÃO DA IA: Classificar e Gerar Resposta --------
            # ==============================================================

            # Classificar e Gerar Resposta
            category, probabilities = classify_email(extracted_text)
            suggested_response = generate_response(category)

            file_info = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(file_content),
                'extracted_text': extracted_text,
                'category': category, # Categoria prevista pela IA
                'probabilities': probabilities, # Probabilidades da previsão
                'suggested_response': suggested_response # Resposta automática gerada
            }
            
            processed_contents.append(file_info)

    # Logica para lidar com TEXTO DIRETO INSERIDO
    elif 'email_text' in request.form:
        email_text_data = request.form['email_text']
        cleaned_email_text = email_text_data.strip()

        # Se o texto digitado esta vazio ou so tem espacos
        if not cleaned_email_text:
            return jsonify({
                'message': 'Conteúdo vazio.',
                'files': [{
                    'filename': 'email_digitado.txt',
                    'extracted_text': '',
                    'category': 'Texto Vazio',
                    'suggested_response': generate_response('Texto Vazio')
                }]
            }), 200 # Retorna 200 OK, mas com categoria 'Texto Vazio'
        
        # Se o texto digitado esta vazio ou so tem espacos
        category, probabilities = classify_email(cleaned_email_text)
        suggested_response = generate_response(category)

        text_info = {
            'filename': 'email_digitado.txt',
            'content_type': 'text/plain',
            'size': len(cleaned_email_text.encode('utf-8')),
            'extracted_text': cleaned_email_text,
            'category': category, 
            'probabilities': probabilities,
            'suggested_response': suggested_response
        }
        
        processed_contents.append(text_info)

    # Se nenhum conteudo (nem arquivo, nem texto digitado) foi fornecido
    if not processed_contents:
        return jsonify({'error': 'Nenhum conteúdo de e-mail válido fornecido para processamento.'}), 400

    # Retorna uma resposta unificada para o frontend
    return jsonify({
        'message': 'Conteúdo(s) processado(s) com sucesso!',
        'files': processed_contents
    }), 200