import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importações dos módulos
try:
    from src.cid_categorizer import CIDCategorizer
    from src.diagnostic_engine import DiagnosticEngine
    from src.drug_interaction_checker import DrugInteractionChecker
    from src.enhanced_drug_interaction_checker import EnhancedDrugInteractionChecker
    from src.symptom_selector_service import SymptomSelectorService
    from src.routes.disease import DiseaseDetailsService
    from src.routes.enhanced_disease import enhanced_disease_bp
    from src.models.disease import Disease
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)

# Registrar blueprints
try:
    app.register_blueprint(enhanced_disease_bp, url_prefix='/api')
except Exception as e:
    logger.error(f"Erro ao registrar blueprint: {e}")

# Inicializar serviços
try:
    cid_categorizer = CIDCategorizer()
    diagnostic_engine = DiagnosticEngine()
    drug_checker = DrugInteractionChecker()
    enhanced_drug_checker = EnhancedDrugInteractionChecker()
    symptom_service = SymptomSelectorService()
    disease_service = DiseaseDetailsService()
except Exception as e:
    logger.error(f"Erro ao inicializar serviços: {e}")

@app.route('/')
def index():
    """Página principal da aplicação"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"Erro ao servir index.html: {e}")
        return jsonify({"error": "Página não encontrada"}), 404

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "message": "Med-IA API está funcionando",
        "version": "2.0"
    })

@app.route('/api/search/diseases')
def search_diseases():
    """Buscar doenças por termo"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"error": "Parâmetro 'q' é obrigatório"}), 400
        
        results = disease_service.search_diseases(query)
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Erro na busca de doenças: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/diseases/<disease_id>')
def get_disease_details(disease_id):
    """Obter detalhes de uma doença específica"""
    try:
        details = disease_service.get_disease_details(disease_id)
        if not details:
            return jsonify({"error": "Doença não encontrada"}), 404
        return jsonify(details)
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da doença: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Realizar diagnóstico baseado em sintomas"""
    try:
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({"error": "Lista de sintomas é obrigatória"}), 400
        
        symptoms = data['symptoms']
        if not isinstance(symptoms, list) or not symptoms:
            return jsonify({"error": "Lista de sintomas deve ser não vazia"}), 400
        
        diagnosis = diagnostic_engine.diagnose(symptoms)
        return jsonify(diagnosis)
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/drug-interactions', methods=['POST'])
def check_drug_interactions():
    """Verificar interações medicamentosas"""
    try:
        data = request.get_json()
        if not data or 'drugs' not in data:
            return jsonify({"error": "Lista de medicamentos é obrigatória"}), 400
        
        drugs = data['drugs']
        if not isinstance(drugs, list) or len(drugs) < 2:
            return jsonify({"error": "Pelo menos 2 medicamentos são necessários"}), 400
        
        interactions = enhanced_drug_checker.check_interactions(drugs)
        return jsonify(interactions)
    except Exception as e:
        logger.error(f"Erro na verificação de interações: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/symptoms/suggest')
def suggest_symptoms():
    """Sugerir sintomas baseado em entrada parcial"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"suggestions": []})
        
        suggestions = symptom_service.suggest_symptoms(query)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        logger.error(f"Erro na sugestão de sintomas: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/categories')
def get_categories():
    """Obter categorias CID-10"""
    try:
        categories = cid_categorizer.get_categories()
        return jsonify({"categories": categories})
    except Exception as e:
        logger.error(f"Erro ao obter categorias: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Banco de dados inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

