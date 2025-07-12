import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import json

# Importar módulos locais
from disease import search_disease_by_name
from enhanced_disease import enhanced_search_disease_by_name, get_disease_details
from cid_categorizer import get_all_categories, get_diseases_by_category
from diagnostic_engine import diagnose_symptoms, diagnose_objective_symptoms
from symptom_selector_service import get_symptom_categories
from enhanced_drug_interaction_checker import check_drug_interactions

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    """Serve a página principal"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        return f"Erro ao carregar página: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Med-IA API está funcionando!",
        "version": "2.0"
    })

# API v1 - Compatibilidade
@app.route('/api/search', methods=['POST'])
def api_search_disease():
    """Buscar doença por nome - API v1"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"success": False, "message": "Query é obrigatória"}), 400
        
        results = search_disease_by_name(query)
        return jsonify({
            "success": True,
            "results": results,
            "total_found": len(results)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# API v2 - Versão aprimorada
@app.route('/api/v2/health')
def api_v2_health():
    """Health check endpoint v2"""
    return jsonify({
        "status": "healthy",
        "message": "Med-IA API v2 está funcionando!",
        "version": "2.0",
        "features": [
            "Busca aprimorada de doenças",
            "Diagnóstico por sintomas",
            "Verificação de interações medicamentosas",
            "Categorização CID-10"
        ]
    })

@app.route('/api/v2/search/name', methods=['POST'])
def api_v2_search_disease():
    """Buscar doença por nome - API v2"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"success": False, "message": "Query é obrigatória"}), 400
        
        results = enhanced_search_disease_by_name(query)
        return jsonify({
            "success": True,
            "results": results,
            "total_found": len(results)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/disease/<code>/details')
def api_v2_disease_details(code):
    """Obter detalhes de uma doença específica"""
    try:
        details = get_disease_details(code)
        if details:
            return jsonify({
                "success": True,
                "disease_details": details
            })
        else:
            return jsonify({"success": False, "message": "Doença não encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/categories')
def api_v2_categories():
    """Listar todas as categorias CID-10"""
    try:
        categories = get_all_categories()
        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(categories)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/categories/<category_letter>/diseases')
def api_v2_category_diseases(category_letter):
    """Listar doenças de uma categoria específica"""
    try:
        diseases = get_diseases_by_category(category_letter.upper())
        return jsonify({
            "success": True,
            "category": category_letter.upper(),
            "diseases": diseases,
            "total_diseases": len(diseases)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/diagnose/symptoms', methods=['POST'])
def api_v2_diagnose_symptoms():
    """Diagnóstico baseado em descrição de sintomas"""
    try:
        data = request.get_json()
        symptoms_report = data.get('symptoms_report', '').strip()
        include_report = data.get('include_report', False)
        
        if not symptoms_report:
            return jsonify({"success": False, "message": "Descrição de sintomas é obrigatória"}), 400
        
        results = diagnose_symptoms(symptoms_report, include_report=include_report)
        return jsonify({
            "success": True,
            **results
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/diagnose/objective_symptoms', methods=['POST'])
def api_v2_diagnose_objective_symptoms():
    """Diagnóstico baseado em sintomas selecionados objetivamente"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        include_report = data.get('include_report', False)
        
        if not symptoms or len(symptoms) == 0:
            return jsonify({"success": False, "message": "Lista de sintomas é obrigatória"}), 400
        
        results = diagnose_objective_symptoms(symptoms, include_report=include_report)
        return jsonify({
            "success": True,
            **results
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/symptoms/categories')
def api_v2_symptom_categories():
    """Obter categorias de sintomas disponíveis"""
    try:
        categories = get_symptom_categories()
        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(categories)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/interactions/check', methods=['POST'])
def api_v2_check_interactions():
    """Verificar interações medicamentosas"""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        include_report = data.get('include_report', False)
        
        if not medications or len(medications) < 2:
            return jsonify({"success": False, "message": "Pelo menos 2 medicamentos são necessários"}), 400
        
        results = check_drug_interactions(medications, include_report=include_report)
        return jsonify({
            "success": True,
            **results
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    try:
        return send_from_directory('.', filename)
    except Exception:
        # Se o arquivo não existir, retorna a página principal (SPA behavior)
        return send_from_directory('.', 'index.html')

@app.errorhandler(404)
def not_found(error):
    """Handler para 404 - retorna a página principal"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception:
        return "Aplicativo Med-IA - Página não encontrada", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

