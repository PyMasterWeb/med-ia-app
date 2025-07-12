import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import json

# Importar módulos locais
from disease_simple import search_disease_by_name

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
        
        results = search_disease_by_name(query)
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
        # Dados básicos de exemplo para detalhes da doença
        details = {
            "severity": "Moderada",
            "has_treatment": True,
            "treatment_type": "Medicamentoso",
            "medications": ["Consulte um médico"],
            "non_medication_treatment": ["Mudanças no estilo de vida"],
            "symptoms": ["Consulte um médico para avaliação"],
            "prognosis": "Bom com tratamento adequado"
        }
        
        return jsonify({
            "success": True,
            "disease_details": details
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/categories')
def api_v2_categories():
    """Listar todas as categorias CID-10"""
    try:
        categories = [
            {"letter": "A", "title": "Doenças infecciosas e parasitárias", "description": "Infecções causadas por vírus, bactérias, parasitas"},
            {"letter": "B", "title": "Doenças infecciosas e parasitárias", "description": "Continuação das doenças infecciosas"},
            {"letter": "C", "title": "Neoplasias", "description": "Tumores malignos e benignos"},
            {"letter": "D", "title": "Doenças do sangue", "description": "Doenças do sangue e órgãos hematopoéticos"},
            {"letter": "E", "title": "Doenças endócrinas", "description": "Doenças endócrinas, nutricionais e metabólicas"},
            {"letter": "F", "title": "Transtornos mentais", "description": "Transtornos mentais e comportamentais"},
            {"letter": "G", "title": "Doenças do sistema nervoso", "description": "Doenças do sistema nervoso"},
            {"letter": "I", "title": "Doenças do aparelho circulatório", "description": "Doenças do coração e vasos sanguíneos"},
            {"letter": "J", "title": "Doenças do aparelho respiratório", "description": "Doenças dos pulmões e vias respiratórias"},
            {"letter": "K", "title": "Doenças do aparelho digestivo", "description": "Doenças do sistema digestivo"}
        ]
        
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
        # Buscar doenças que começam com a letra da categoria
        from disease_simple import cid10_data
        
        diseases = []
        for disease in cid10_data:
            code = disease.get('codigo') or disease.get('code', '')
            if code.upper().startswith(category_letter.upper()):
                diseases.append({
                    'code': code,
                    'description': disease.get('nome') or disease.get('description', ''),
                    'severity': 'Moderada',
                    'has_treatment': True,
                    'treatment_type': 'Medicamentoso'
                })
        
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
        
        # Diagnóstico simplificado baseado em palavras-chave
        results = []
        if 'febre' in symptoms_report.lower():
            results.append({
                'disease_name': 'Febre não especificada',
                'cid_code': 'R50',
                'probability': 85,
                'confidence_level': 'Alta',
                'matching_symptoms': ['febre']
            })
        
        if 'dor de cabeça' in symptoms_report.lower():
            results.append({
                'disease_name': 'Cefaleia',
                'cid_code': 'R51',
                'probability': 80,
                'confidence_level': 'Alta',
                'matching_symptoms': ['dor de cabeça']
            })
        
        medical_report = "Baseado nos sintomas relatados, recomenda-se consulta médica para avaliação adequada."
        
        return jsonify({
            "success": True,
            "diagnostic_results": results,
            "total_diagnoses": len(results),
            "medical_report": medical_report if include_report else None
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
        
        # Validação de sintomas simplificada
        symptom_validation = []
        for symptom in symptoms:
            symptom_validation.append({
                'condition': f'Condição relacionada a {symptom}',
                'confidence': 75.0,
                'matching_symptoms': 1,
                'total_symptoms': 1
            })
        
        # Resultados de diagnóstico
        diagnostic_results = []
        if 'febre' in [s.lower() for s in symptoms]:
            diagnostic_results.append({
                'disease_name': 'Febre não especificada',
                'cid_code': 'R50',
                'probability': 85,
                'confidence_level': 'Alta',
                'matching_symptoms': ['febre']
            })
        
        medical_report = f"Análise baseada em {len(symptoms)} sintomas selecionados. Recomenda-se avaliação médica."
        
        return jsonify({
            "success": True,
            "symptom_validation": symptom_validation,
            "diagnostic_results": diagnostic_results,
            "total_diagnoses": len(diagnostic_results),
            "medical_report": medical_report if include_report else None
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/v2/symptoms/categories')
def api_v2_symptom_categories():
    """Obter categorias de sintomas disponíveis"""
    try:
        categories = {
            "Sintomas Gerais": ["Febre", "Fadiga", "Perda de peso", "Mal-estar"],
            "Sintomas Respiratórios": ["Tosse", "Falta de ar", "Dor no peito", "Chiado"],
            "Sintomas Digestivos": ["Náusea", "Vômito", "Dor abdominal", "Diarreia"],
            "Sintomas Neurológicos": ["Dor de cabeça", "Tontura", "Confusão", "Convulsões"],
            "Sintomas Cardiovasculares": ["Palpitações", "Dor no peito", "Inchaço", "Pressão alta"]
        }
        
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
        
        # Simulação de verificação de interações
        interactions = []
        if len(medications) >= 2:
            interactions.append({
                'drug1': medications[0],
                'drug2': medications[1],
                'severity': 'Leve',
                'mechanism': 'Possível interação farmacocinética',
                'clinical_effects': ['Monitoramento recomendado']
            })
        
        summary = {
            'total_interactions': len(interactions),
            'highest_severity': 'Leve' if interactions else 'Nenhuma',
            'interactions': interactions
        }
        
        detailed_report = f"Análise de {len(medications)} medicamentos. {len(interactions)} interações encontradas."
        
        return jsonify({
            "success": True,
            "summary": summary,
            "detailed_report": detailed_report if include_report else None
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

