import pandas as pd
import os


# ============================================================================
# ------------------------------- Configurações ------------------------------
# ============================================================================

# Caminho para o CSV original (Big Data)
INPUT_CSV_PATH = '/home/user/Documents/kaggle/emails.csv'

# Caminho novo CSV gerado a partir do big data (Novo)
OUTPUT_CSV_PATH = '/home/user/Documents/kaggle/emails_amostra.csv'

# Numero de linhas a manter
NUM_LINES_TO_KEEP = 100 # primeiras Linhas

# ============================================================================
# -------------------------- Script de Processamento -------------------------
# ============================================================================


def create_subset_csv(input_path: str, output_path: str, num_lines: int):
    
    # Carrega as primeiras 'num_lines' do CSV e salva em um novo CSV
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de entrada '{input_path}' não encontrado.")
        return

    print(f"Carregando as primeiras {num_lines} linhas de '{input_path}'...")
    try:
        # Carrega apenas as primeiras 'num_lines' do CSV
        # Isso e muito eficiente em memoria, pois nao carrega o arquivo inteiro
        df_subset = pd.read_csv(input_path, nrows=num_lines)
        
        print(f"\nColunas carregadas: {df_subset.columns.tolist()}")
        print(f"Primeiras 5 linhas da amostra:\n{df_subset.head()}")

        print(f"\nSalvando {len(df_subset)} linhas em '{output_path}'...")

        # Salva o subconjunto em um novo arquivo CSV
        # index=False evitando que o Pandas salve o indice do DataFrame como uma coluna
        df_subset.to_csv(output_path, index=False)

        print("Operação concluída com sucesso!")
        print(f"O novo arquivo '{output_path}' contém as primeiras {len(df_subset)} linhas do dataset original.")

    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    create_subset_csv(INPUT_CSV_PATH, OUTPUT_CSV_PATH, NUM_LINES_TO_KEEP)
