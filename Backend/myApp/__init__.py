# ========================================================================
# ---- Responsavel por criar e configurar a instancia do Flask -----------
# ========================================================================

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

import os

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost") 
                       
def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": [FRONTEND_ORIGIN]}})

    # Importa e registra as rotas
    from .routes import upload_files
    app.add_url_rule('/upload', view_func=upload_files, methods=['POST'])

    return app