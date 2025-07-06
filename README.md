![image](https://github.com/user-attachments/assets/ba4047a8-8a73-4c4a-b5e6-8b7816afe804)

![image](https://github.com/user-attachments/assets/e996a51c-19b4-4930-9787-898ce0972fe5)

![image](https://github.com/user-attachments/assets/42fcc4b9-3b5f-43d8-b865-940b6a26de68)





# Classificador Inteligente de E-mails com IA


Este projeto é uma aplicação web simples, porém robusta, desenvolvida para classificar e-mails em categorias predefinidas (`Produtivo` ou `Improdutivo`) e sugerir respostas automáticas com base na classificação. A solução utiliza Inteligência Artificial (IA) no backend, com um frontend intuitivo para interação do usuário.

## 🚀 Funcionalidades

* **Entrada Flexível de E-mails:**
    * Upload de arquivos de e-mail nos formatos `.txt` ou `.pdf`.
    * Inclusão direta de texto de e-mails através de formulário manual (`Enviar Para`, `Assunto`, `Mensagem`).

* **Classificação de E-mails com IA:**
    * Utiliza um modelo de Processamento de Linguagem Natural (PLN) baseado em Transformers (Hugging Face) para categorizar o conteúdo.
    * Capacidade de classificar e-mails em **português** e **inglês** (devido ao uso de um modelo multilíngue e treinamento em dataset misto).
* **Sugestão de Respostas Automáticas:**
    * Gera uma resposta padrão adequada à categoria identificada.
* **Interface Intuitiva:**
    * Frontend moderno e responsivo desenvolvido em React e TypeScript.
    * Exibição clara dos resultados da classificação e da resposta sugerida.
* **Containerização com Docker:**
    * Backend empacotado em um contêiner Docker para garantir consistência e portabilidade do ambiente em diferentes sistemas.

## 🛠️ Tecnologias Utilizadas

**Backend:**
* **Python 3.12:** Linguagem de programação principal.
* **Flask:** Microframework web para construção da API REST.
* **Flask-Cors:** Gerenciamento de políticas CORS.
* **Hugging Face Transformers:** Biblioteca para modelos de PLN (DistilBERT Multilíngue).
* **PyTorch:** Framework de deep learning que suporta os modelos Transformers.
* **Pandas:** Manipulação e pré-processamento de dados.
* **PyPDF2:** Extração de texto de arquivos PDF.
* **Gunicorn:** Servidor WSGI para produção do Flask.
* **python-dotenv:** Carregamento de variáveis de ambiente.
* **Docker:** Containerização do backend.

**Frontend:**
* **React:** Biblioteca JavaScript para construção da interface de usuário.
* **TypeScript:** Superset do JavaScript que adiciona tipagem estática.
* **Vite:** Ferramenta de build frontend.

---

## ⚙️ Como Configurar o Ambiente Local

Siga os passos abaixo para configurar seu ambiente de desenvolvimento.

### Pré-requisitos

* **Node.js e npm/yarn:** Para o frontend React.
* **Python 3.12:** Para o backend Flask.
* **pip:** Gerenciador de pacotes Python.
* **Docker Desktop (ou Docker Engine):** Para executar o backend containerizado.
* **Git:** Para clonar o repositório.
* **Opcional: NVIDIA Container Toolkit (para uso de GPU com Docker)**
    Se você deseja que o Docker acesse sua GPU NVIDIA para o backend (usando `USE_GPU=True` no `.env`), você precisará instalar o NVIDIA Container Toolkit em seu sistema Ubuntu real. As instruções detalhadas podem ser encontradas em: [NVIDIA Container Toolkit Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### 1. Clonar o Repositório

```bash
git clone git@github.com:andersonjuniorz/mail-classify.git
```

## ▶️ Como Usar o Aplicativo Localmente

Após configurar seu ambiente conforme a seção anterior, siga estes passos para iniciar e usar a aplicação:

### 1. Iniciar o Backend (Flask com IA no Docker)

1.  Abra seu terminal e navegue para a pasta raíz (onde está o Backend e Frontend):

2.  Inicie o serviço Docker Compose. Na primeira vez, ou após alterações em dependências/código Python, ele construirá a imagem Docker.
    ```bash
    docker-compose up --build 
    ```
    * **Observação:** A primeira construção da imagem pode demorar vários minutos (devido à instalação de bibliotecas de IA).
    * Para rodar o backend em segundo plano (detached mode), use: `docker-compose up -d --build`
    * Para parar o backend quando terminar, use: `docker-compose down`
    * Se encontrar problemas de cache (`gunicorn not found`), force uma reconstrução sem cache com: `docker-compose build --no-cache backend` e depois `docker-compose up backend`.

3.  Aguarde até ver nos logs do terminal que o Gunicorn está escutando na porta `5000` (ex: `Listening at: http://0.0.0.0:5000`).

### 2. Iniciar o Frontend (React)

1.  Abra **outro terminal** (mantenha o terminal do backend rodando).
2.  Entre na pasta do **Frontend** do projeto:
    ```bash
    cd ../Frontend/                
    ```
3.  Instale as dependências JavaScript (apenas na primeira vez):
    ```bash
    npm install # ou yarn install
    ```
4.  Inicie o servidor de desenvolvimento do React:
    ```bash
    npm run dev # (Para Vite)
    ```
    * A aplicação React estará acessível em `http://localhost:5173` (ou a porta padrão do Vite, que será exibida no terminal).

### 3. Testar a Aplicação

* Com o backend Dockerizado e o frontend React rodando, acesse a URL do frontend no seu navegador (ex: `http://localhost:5173`).
* Teste as funcionalidades de upload de arquivos (`.txt` ou `.pdf`) e a inserção de texto manual. A IA deve classificar e gerar respostas automáticas na interface.

---
