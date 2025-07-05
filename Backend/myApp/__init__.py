# ========================================================================
# ---- Responsavel por criar e configurar a instancia do Flask -----------
# ========================================================================

from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app) # Habilita CORS para o aplicativo

    # Importa e registra as rotas
    from .routes import upload_files
    app.add_url_rule('/upload', view_func=upload_files, methods=['POST'])

    return app