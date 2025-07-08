![image](https://github.com/user-attachments/assets/bf271820-508a-4aad-9ed0-de5a2997fd9e)

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
* **Docker Engine:** Para executar o backend containerizado.
* **Git:** Para clonar o repositório.
* **NVIDIA Container Toolkit (para uso de GPU com Docker)**
    Se você deseja que o Docker acesse sua GPU NVIDIA para o backend (usando `USE_GPU=True` no `.env`), você precisará instalar o NVIDIA Container Toolkit em seu sistema Ubuntu real. As instruções detalhadas podem ser encontradas em: [NVIDIA Container Toolkit Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### 1. Clonar o Repositório

```bash
git clone git@github.com:andersonjuniorz/mail-classify.git
```
## ▶️ Como Usar o Aplicativo Localmente

Após configurar seu ambiente conforme a seção anterior, siga estes passos para iniciar e usar a aplicação.

### Iniciar a Aplicação Completa (Frontend e Backend)

1.  Abra seu terminal e navegue para a **raiz do seu repositório** (onde está o `docker-compose.yml`, `Backend/` e `Frontend/`):

2.  Na primeira vez que você rodar (ou após grandes alterações em dependências/código), construa as imagens Docker sem usar o cache para garantir que tudo esteja atualizado:

```bash
docker compose build --no-cache backend frontend
```

**Observação:** A construção da imagem pode demorar alguns minutos (devido à instalação de bibliotecas de IA no backend e Node.js no frontend). Em execuções futuras, você pode omitir `--no-cache` para usar o cache e acelerar o processo.

3.  Após a construção (ou em execuções subsequentes), inicie os serviços Docker Compose (backend e frontend):

```bash
docker compose up -d
```
**`-d`:** Inicia os contêineres em segundo plano (detached mode), liberando seu terminal.

### Testar a Aplicação

Teste as funcionalidades de upload de arquivos (`.txt` ou `.pdf`) e a inserção de texto manual. A IA deve classificar e gerar respostas automáticas na interface.

### Verificar LOGs do Frontend e Backend (Caso queira)

Aguarde alguns segundos para que os serviços iniciem completamente (especialmente o backend, que carrega o modelo de IA). Você pode verificar o status dos contêineres com:

```bash
docker-compose ps
```
E ver os logs do frontend e backend com:

```bash
docker-compose logs backend
docker-compose logs frontend
```  

### Ferramentas de Gerenciamento de Contêineres (Opcional)

Para gerenciar contêineres e orquestração em larga escala, podem ser utilizadas ferramentas adicionais, caso prefira:

* **Portainer:** Uma interface gráfica de usuário (UI) para gerenciamento simplificado de ambientes Docker e Kubernetes.
* **Podman:** Uma alternativa ao Docker para construir, executar e gerenciar contêineres e imagens, compatível com a CLI do Docker, mas sem daemon.
* **Docker Swarm:** A ferramenta de orquestração nativa do Docker, mais simples que o Kubernetes para clusters menores.
* **Kubernetes:** Uma plataforma de orquestração de contêineres de código aberto para automatizar o deploy, escalonamento e gerenciamento de aplicações containerizadas.


### Acessar o Aplicativo

Com o backend e frontend Dockerizados rodando, abra seu navegador e acesse a URL:

```bash
http://localhost
```

A aplicação React (frontend) será exibida. A comunicação com o backend será feita internamente na rede Docker Compose, resolvendo quaisquer problemas de Mixed Content ou CORS em ambiente local.

### Parar a Aplicação

Para parar e remover os contêineres e redes criadas pelo Docker Compose, navegue para a raiz do seu repositório (onde está o `docker-compose.yml`) e execute:

```bash
docker-compose down
```
