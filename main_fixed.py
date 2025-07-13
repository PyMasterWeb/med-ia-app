import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Importar blueprints
from src.routes.disease import disease_bp
from src.routes.enhanced_disease import enhanced_disease_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Registrar blueprints
app.register_blueprint(disease_bp, url_prefix='/api')
app.register_blueprint(enhanced_disease_bp, url_prefix='/api/v2')

@app.route('/')
def index():
    """Serve a página principal"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return f"Erro ao carregar página: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Med-IA API está funcionando!",
        "static_folder": app.static_folder,
        "static_files": os.listdir(app.static_folder) if app.static_folder and os.path.exists(app.static_folder) else []
    })

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception:
        # Se o arquivo não existir, retorna a página principal (SPA behavior)
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(error):
    """Handler para 404 - retorna a página principal"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception:
        return "Aplicativo Med-IA - Página não encontrada", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

