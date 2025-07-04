# Este arquivo será responsável por criar e configurar a instância do seu aplicativo Flask.

from flask import Flask
from flask_cors import CORS
import PyPDF2

def create_app():
    app = Flask(__name__)
    CORS(app) # Habilita CORS para o aplicativo

    # Importe e registre as rotas aqui para evitar importações circulares
    from .routes import upload_files
    app.add_url_rule('/upload', view_func=upload_files, methods=['POST'])

    return app