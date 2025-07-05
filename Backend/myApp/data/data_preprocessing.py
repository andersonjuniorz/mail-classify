# =============================================================================
# ---- Responsavel pela limpeza e pre-processamento de dados de emails --------
# =============================================================================

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

    # Aplica a sequencia de pre-processamento a uma unica string de email.        
    def clean_text(self, text: str) -> str:
        
        if not isinstance(text, str):
            return ""
        
        text = self._remove_headers(text)
        text = self._remove_signatures(text)
        text = self._remove_urls_emails(text)
        text = self._to_lowercase(text)
        text = self._remove_punctuation_and_numbers(text)
        text = self._remove_extra_whitespace(text)
        
        return text


    # Remove cabecalhos de email ate a primeira linha vazia
    def _remove_headers(self, email_text: str) -> str:

        if not isinstance(email_text, str):
            return ""       
        match = re.search(r'\n\s*\n', email_text)
        if match:
            return email_text[match.end():].strip()        
        return email_text

    # Remove assinaturas comuns e avisos legais
    def _remove_signatures(self, email_text: str) -> str:

        if not isinstance(email_text, str):
            return ""
        
        patterns = [
            r'-----Original Message-----',
            r'From:.*',
            r'Sent:.*',
            r'To:.*',
            r'Subject:.*',
            r'[\s]*_{3,}[\s]*',
            r'[\s]*-{3,}[\s]*',
            r'Regards,',
            r'Sincerely,',
            r'Thank you,',
            r'V/R,',
            r'Best regards,',
            r'Sent from my BlackBerry',
            r'Confidentiality Notice:',
            r'This email and any files transmitted with it are confidential'
        ]

        for pattern in patterns:
            match = re.search(pattern, email_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                email_text = email_text[:match.start()].strip()

        return email_text

    # Remove URLs e enderecos de email
    def _remove_urls_emails(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S*@\S*\s?', '', text)
        return text
    
    # Converte texto para minusculas
    def _to_lowercase(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        return text.lower()
    
    # Remove pontuacao e numeros
    def _remove_punctuation_and_numbers(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text

    # Remove espacos extras e quebras de linha
    def _remove_extra_whitespace(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # Aplica a sequencia de pre-processamento a uma coluna de DataFrame.
    def preprocess_dataframe(self, dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
        if column_name not in dataframe.columns:
            raise ValueError(f"A coluna '{column_name}' não existe no DataFrame.")
        
        processed_df = dataframe.copy()
        
        # Garante que a coluna e do tipo string
        series_to_process = processed_df[column_name].astype(str).fillna('') 

        print(f"Iniciando pré-processamento da coluna '{column_name}'...")
        series_to_process = series_to_process.apply(self._remove_headers)
        series_to_process = series_to_process.apply(self._remove_signatures)
        series_to_process = series_to_process.apply(self._remove_urls_emails)
        series_to_process = series_to_process.apply(self._to_lowercase)
        series_to_process = series_to_process.apply(self._remove_punctuation_and_numbers)
        series_to_process = series_to_process.apply(self._remove_extra_whitespace)
        print("Pré-processamento concluído.")

        processed_df[f'{column_name}_processed'] = series_to_process
        return processed_df

# Email Dataset (para PyTorch Trainer)
class EmailDataset(Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.encodings['input_ids'])

# Carrega, pre-processa e tokeniza datasets de emails para treinamento da IA
def prepare_data_for_ia(file_paths: list[str], text_column: str = 'message', category_column: str = 'label'):
    try:
        all_dfs = []

        for f_path in file_paths:
            if os.path.exists(f_path):
                df_lang = pd.read_csv(f_path)

                # Debug: limite de amostras por arquivo
                # df_lang = df_lang.head(500) 

                print(f"--- CSV '{f_path}' Carregado com Sucesso ({len(df_lang)} amostras) ---")
                all_dfs.append(df_lang)
            else:
                print(f"AVISO: CSV '{f_path}' não encontrado. Será ignorado.")

        if not all_dfs:
            raise FileNotFoundError("Nenhum arquivo CSV de dados encontrado para processamento. Pelo menos um arquivo deve ser fornecido e existir.")

        df_combined = pd.concat(all_dfs, ignore_index=True)
        print(f"Dataset combinado para treinamento: {len(df_combined)} amostras totais.")

        # Debug: Limite total de amostras no dataset combinado
        # df_combined = df_combined.head(1000)

        if text_column not in df_combined.columns:
            raise ValueError(f"Coluna de texto '{text_column}' não encontrada no dataset combinado.")
        
        preprocessor = EmailPreprocessor()
        df_cleaned = preprocessor.preprocess_dataframe(df_combined.copy(), text_column)
        
        cleaned_text_column = f'{text_column}_processed'
        if cleaned_text_column not in df_cleaned.columns:
             raise ValueError(f"A coluna '{cleaned_text_column}' não foi criada pela classe EmailPreprocessor.")

        print("\nPrimeiras 5 linhas do DataFrame com texto limpo:")
        print(df_cleaned[[text_column, cleaned_text_column]].head())

        # Variaveis do .env com valores default para configuracao do tokenizador
        MODEL_NAME_FROM_ENV = os.getenv("MODEL_NAME", "distilbert-base-multilingual-cased")
        MAX_LENGTH_FROM_ENV = int(os.getenv("MAX_LENGTH", 128))

        print(f"\n--- Carregando Tokenizador: {MODEL_NAME_FROM_ENV} ---")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_FROM_ENV)
        
        print(f"--- Aplicando Tokenização na coluna '{cleaned_text_column}' ---")
        tokenized_data = tokenizer(
            df_cleaned[cleaned_text_column].tolist(),
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
        
        labels = None
        if category_column in df_cleaned.columns:
            print(f"\n--- Preparando Labels da coluna '{category_column}' ---")
            unique_categories = df_cleaned[category_column].unique()
            print(f"Categorias únicas encontradas: {unique_categories}")

            # Mapeamento de categorias - string para numericas (0, 1)
            category_mapping = {
                'Produtivo': 0,
                'Improdutivo': 1,
            }

            df_cleaned['numeric_labels'] = df_cleaned[category_column].map(category_mapping)
            
            initial_rows = len(df_cleaned)
            df_cleaned.dropna(subset=['numeric_labels'], inplace=True)
            if len(df_cleaned) < initial_rows:
                print(f"AVISO: {initial_rows - len(df_cleaned)} linhas removidas devido a categorias não mapeadas ou nulas.")
            
            df_cleaned['numeric_labels'] = df_cleaned['numeric_labels'].astype(int)
            labels = df_cleaned['numeric_labels'].tolist()
            print(f"Primeiras 5 labels numéricas: {labels[:5]}")
            print(f"Número total de amostras com labels: {len(labels)}")
        else:
            print(f"\nAVISO: Coluna de categoria '{category_column}' não encontrada. Não serão geradas labels para treinamento.")
        
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
# -------------- Bloco de teste local para data_preprocessing.py --------------
# =============================================================================

if __name__ == "__main__":

    # Este bloco so sera executado se voce rodar 'python myapp/data/data_preprocessing.py' diretamente
    # Caminhos de exemplo para o teste local (ajuste conforme seu setup)
    test_file_path_en = './datasets/email_dataset_en.csv'
    test_file_path_pt = './datasets/email_dataset_pt.csv'

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)         # Evita truncar de dados
    pd.set_option("display.max_colwidth", None)

    processed_df_test = prepare_data_for_ia(
        file_paths=[test_file_path_en, test_file_path_pt],
        text_column='message',
        category_column='label'
    )

    if processed_df_test is not None:
        print("\n--- DataFrame Combinado, Pré-processado e Tokenizado (Teste) ---")
        print(processed_df_test[['message', 'message_processed', 'numeric_labels', 'input_ids', 'attention_mask']].head())