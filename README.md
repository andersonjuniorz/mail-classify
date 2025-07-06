# Classificador Inteligente de E-mails com IA

![Banner do Projeto (Opcional)](./favicon.png)

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

