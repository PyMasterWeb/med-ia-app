import os
import json
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configurações da API Render
CLIENT_ID = os.environ.get('CLIENT_ID', '84b64ed5-c3b1-47d1-a230-5a8234ed6a09_3cc45ea9-bba3-4857-8098-df9277fed4e0')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'cSAbaw4dlFaGxBceLnnAvo6nHZLtTC3unArNaz8GCA4=')
API_KEY = os.environ.get('API_KEY', 'rnd_MXAQGe8GLrsBKdKvqzxkYFOxWShO')

# Carregar dados do CID-10
def load_cid10_data():
    try:
        with open('cid10_datasus.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Converter lista para dicionário para facilitar busca
            if isinstance(data, list):
                cid_dict = {}
                for item in data:
                    if isinstance(item, dict) and 'code' in item:
                        cid_dict[item['code']] = {
                            'name': item.get('description', ''),
                            'category': item.get('category', 'Não categorizado'),
                            'description': item.get('description', ''),
                            'symptoms': item.get('symptoms', []),
                            'treatments': item.get('treatments', [])
                        }
                return cid_dict
            return data
    except FileNotFoundError:
        print("Arquivo cid10_datasus.json não encontrado")
        return {}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return {}

cid10_data = load_cid10_data()

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
        "version": "1.0",
        "api_configured": bool(CLIENT_ID and CLIENT_SECRET and API_KEY),
        "cid10_loaded": len(cid10_data) > 0,
        "total_diseases": len(cid10_data)
    })

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Endpoint para buscar doenças"""
    search_term = request.args.get('search', '').lower()
    
    if not search_term:
        return jsonify({"error": "Termo de busca é obrigatório"}), 400
    
    results = []
    for code, disease_info in cid10_data.items():
        if isinstance(disease_info, dict):
            name = disease_info.get('name', '').lower()
            if search_term in name or search_term in code.lower():
                results.append({
                    "code": code,
                    "name": disease_info.get('name', ''),
                    "category": disease_info.get('category', ''),
                    "description": disease_info.get('description', '')
                })
    
    return jsonify({
        "results": results[:20],  # Limitar a 20 resultados
        "total": len(results)
    })

@app.route('/api/disease/<code>', methods=['GET'])
def get_disease_details(code):
    """Endpoint para obter detalhes de uma doença específica"""
    code = code.upper()
    
    if code not in cid10_data:
        return jsonify({"error": "Código CID-10 não encontrado"}), 404
    
    disease_info = cid10_data[code]
    return jsonify({
        "code": code,
        "name": disease_info.get('name', ''),
        "category": disease_info.get('category', ''),
        "description": disease_info.get('description', ''),
        "symptoms": disease_info.get('symptoms', []),
        "treatments": disease_info.get('treatments', [])
    })

@app.route('/api/symptoms', methods=['POST'])
def analyze_symptoms():
    """Endpoint para análise de sintomas"""
    data = request.get_json()
    
    if not data or 'symptoms' not in data:
        return jsonify({"error": "Lista de sintomas é obrigatória"}), 400
    
    symptoms = data['symptoms']
    
    # Análise simples baseada em correspondência de sintomas
    possible_diseases = []
    
    for code, disease_info in cid10_data.items():
        if isinstance(disease_info, dict) and 'symptoms' in disease_info:
            disease_symptoms = disease_info.get('symptoms', [])
            matches = 0
            
            for symptom in symptoms:
                for disease_symptom in disease_symptoms:
                    if symptom.lower() in disease_symptom.lower():
                        matches += 1
                        break
            
            if matches > 0:
                confidence = (matches / len(symptoms)) * 100
                possible_diseases.append({
                    "code": code,
                    "name": disease_info.get('name', ''),
                    "confidence": round(confidence, 2),
                    "matching_symptoms": matches,
                    "total_symptoms": len(symptoms)
                })
    
    # Ordenar por confiança
    possible_diseases.sort(key=lambda x: x['confidence'], reverse=True)
    
    return jsonify({
        "analyzed_symptoms": symptoms,
        "possible_diseases": possible_diseases[:10],  # Top 10
        "disclaimer": "Esta análise é apenas informativa e não substitui consulta médica."
    })

@app.route('/api/test')
def api_test():
    """Endpoint de teste da API"""
    return jsonify({
        'status': 'ok', 
        'message': 'API test endpoint working!',
        'timestamp': str(os.environ.get('TZ', 'UTC'))
    })

# Rota para arquivos estáticos específicos
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos específicos"""
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, filename)):
        return send_from_directory(app.static_folder, filename)
    else:
        # Para rotas que não existem, retorna a página principal (SPA behavior)
        if not filename.startswith('api/'):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({"error": "API endpoint not found"}), 404

@app.errorhandler(404)
def not_found(error):
    """Handler para 404"""
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para 500"""
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Iniciando Med-IA API na porta {port}")
    print(f"CID-10 carregado: {len(cid10_data)} doenças")
    app.run(host='0.0.0.0', port=port, debug=debug)

