import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Importar blueprints
from src.routes.disease import disease_bp
from src.routes.enhanced_disease import enhanced_disease_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Registrar blueprints ANTES das rotas catch-all
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
        "static_files": os.listdir(app.static_folder) if app.static_folder and os.path.exists(app.static_folder) else [],
        "blueprints": list(app.blueprints.keys()),
        "total_routes": len(list(app.url_map.iter_rules()))
    })

# Rota para arquivos estáticos específicos (CSS, JS, imagens)
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos específicos"""
    # Só serve arquivos que realmente existem
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, filename)):
        return send_from_directory(app.static_folder, filename)
    else:
        # Para rotas que não existem, retorna a página principal (SPA behavior)
        # MAS apenas se não for uma rota de API
        if not filename.startswith('api/'):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            # Se for uma rota de API que não existe, retorna 404 JSON
            return jsonify({"error": "API endpoint not found"}), 404

@app.errorhandler(404)
def not_found(error):
    """Handler para 404"""
    # Se a requisição é para API, retorna JSON
    if hasattr(error, 'description') and 'api/' in str(error.description):
        return jsonify({"error": "API endpoint not found"}), 404
    else:
        # Caso contrário, retorna a página principal
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception:
            return "Aplicativo Med-IA - Página não encontrada", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

