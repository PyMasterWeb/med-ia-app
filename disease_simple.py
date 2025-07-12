import json
import os

# Dados de exemplo caso o arquivo JSON tenha problemas
default_data = [
    {"codigo": "A01.0", "nome": "Febre tifóide"},
    {"codigo": "A01.1", "nome": "Febre paratifóide A"},
    {"codigo": "I10", "nome": "Hipertensão essencial"},
    {"codigo": "I10.0", "nome": "Hipertensão arterial sistêmica"},
    {"codigo": "E11", "nome": "Diabetes mellitus não-insulino-dependente"},
    {"codigo": "E10", "nome": "Diabetes mellitus insulino-dependente"},
    {"codigo": "E14", "nome": "Diabetes mellitus não especificado"},
    {"codigo": "J44", "nome": "Outras doenças pulmonares obstrutivas crônicas"},
    {"codigo": "K29", "nome": "Gastrite e duodenite"},
    {"codigo": "F32", "nome": "Episódios depressivos"},
    {"codigo": "F41", "nome": "Outros transtornos ansiosos"},
    {"codigo": "F20", "nome": "Esquizofrenia"},
    {"codigo": "F20.0", "nome": "Esquizofrenia paranoide"},
    {"codigo": "F20.1", "nome": "Esquizofrenia hebefrênica"},
    {"codigo": "F20.2", "nome": "Esquizofrenia catatônica"},
    {"codigo": "F25", "nome": "Transtornos esquizoafetivos"},
    {"codigo": "G40", "nome": "Epilepsia"},
    {"codigo": "M79", "nome": "Outros transtornos dos tecidos moles"},
    {"codigo": "N18", "nome": "Doença renal crônica"},
    {"codigo": "R50", "nome": "Febre não especificada"},
    {"codigo": "J18", "nome": "Pneumonia por organismo não especificado"},
    {"codigo": "J45", "nome": "Asma"},
    {"codigo": "J11", "nome": "Influenza devida a vírus não identificado"}
]

# Carregar dados CID-10
cid10_data = []
cid10_path = os.path.join(os.path.dirname(__file__), 'cid10_datasus.json')

try:
    if os.path.exists(cid10_path):
        with open(cid10_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Tentar corrigir JSON malformado
            if content.strip():
                # Remover vírgulas extras no final
                content = content.strip().rstrip(',')
                if not content.endswith(']'):
                    content += ']'
                if not content.startswith('['):
                    content = '[' + content
                cid10_data = json.loads(content)
            else:
                cid10_data = default_data
    else:
        cid10_data = default_data
except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
    print(f"Erro ao carregar CID-10: {e}. Usando dados padrão.")
    cid10_data = default_data

def search_disease_by_name(query):
    """Busca doenças por nome ou código CID."""
    results = []
    query_lower = query.lower()
    
    for disease in cid10_data:
        # Suportar ambos os formatos de chave
        code = disease.get('codigo') or disease.get('code', '')
        name = disease.get('nome') or disease.get('description', '')
        
        code = code.upper()
        name_lower = name.lower()
        
        if (query.upper() in code or 
            query_lower in name_lower or
            any(word in name_lower for word in query_lower.split())):
            
            results.append({
                'code': code,
                'description': name,
                'relevance': 90 if query.upper() in code else 70,
                'subcategory': {
                    'category': code[0] if code else 'N/A'
                }
            })
            
            if len(results) >= 10:
                break
    
    return results

