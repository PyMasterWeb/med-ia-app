import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.disease import db
from src.routes.disease import disease_bp
from src.routes.enhanced_disease import enhanced_disease_bp

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'med-ia-secret-key-2024')

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints - mantendo compatibilidade com rotas antigas
app.register_blueprint(disease_bp, url_prefix='/api')
app.register_blueprint(enhanced_disease_bp, url_prefix='/api/v2')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas e popular dados
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

@app.route('/api/health')
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'ok', 
        'message': 'Med-IA API está funcionando!',
        'version': '2.0',
        'features': {
            'cid_categorization': True,
            'name_search': True,
            'custom_cid_insertion': True,
            'symptom_diagnosis': True,
            'enhanced_drug_interactions': True,
            'medical_reports': True
        }
    })

@app.route('/api/v2/health')
def health_check_v2():
    """Endpoint para verificar se a API v2 está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Med-IA API v2.0 está funcionando!',
        'services': {
            'cid_categorizer': 'ativo',
            'diagnostic_engine': 'ativo',
            'enhanced_drug_checker': 'ativo'
        },
        'endpoints': {
            'categories': '/api/v2/categories',
            'search_by_name': '/api/v2/search/name',
            'search_by_code': '/api/v2/search/code',
            'add_custom_cid': '/api/v2/add_custom_cid',
            'diagnose_symptoms': '/api/v2/diagnose/symptoms',
            'advanced_analysis': '/api/v2/diagnose/advanced_analysis',
            'check_interactions': '/api/v2/interactions/check',
            'drug_alternatives': '/api/v2/interactions/alternatives',
            'comprehensive_analysis': '/api/v2/comprehensive_analysis'
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve arquivos estáticos e SPA"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

