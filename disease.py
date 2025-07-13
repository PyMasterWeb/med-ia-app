from flask import Blueprint, request, jsonify
import json
import os
from src.services.drug_interaction_checker import DrugInteractionChecker
from src.services.render_api import RenderAPI

disease_bp = Blueprint('disease', __name__)

# Inicializar serviços
render_api = RenderAPI()
drug_checker = DrugInteractionChecker()

# Carregar dados CID-10
cid10_data = []
cid10_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cid10_datasus.json')
if os.path.exists(cid10_path):
    with open(cid10_path, 'r', encoding='utf-8') as f:
        cid10_data = json.load(f)
else:
    # Dados de exemplo se não existir o arquivo
    cid10_data = [
        {"code": "A01.0", "description": "Febre tifóide"},
        {"code": "A01.1", "description": "Febre paratifóide A"},
        {"code": "I10", "description": "Hipertensão essencial"},
        {"code": "I10.0", "description": "Hipertensão arterial sistêmica"},
        {"code": "E11", "description": "Diabetes mellitus não-insulino-dependente"},
        {"code": "E10", "description": "Diabetes mellitus insulino-dependente"},
        {"code": "E14", "description": "Diabetes mellitus não especificado"},
        {"code": "J44", "description": "Outras doenças pulmonares obstrutivas crônicas"},
        {"code": "K29", "description": "Gastrite e duodenite"},
        {"code": "F32", "description": "Episódios depressivos"},
        {"code": "F41", "description": "Outros transtornos ansiosos"},
        {"code": "F20", "description": "Esquizofrenia"},
        {"code": "F20.0", "description": "Esquizofrenia paranoide"},
        {"code": "F20.1", "description": "Esquizofrenia hebefrênica"},
        {"code": "F20.2", "description": "Esquizofrenia catatônica"},
        {"code": "F25", "description": "Transtornos esquizoafetivos"},
        {"code": "G40", "description": "Epilepsia"},
        {"code": "M79", "description": "Outros transtornos dos tecidos moles"},
        {"code": "N18", "description": "Doença renal crônica"},
        {"code": "R50", "description": "Febre não especificada"},
        {"code": "J18", "description": "Pneumonia por organismo não especificado"},
        {"code": "J45", "description": "Asma"},
        {"code": "J11", "description": "Influenza devida a vírus não identificado"}
    ]

@disease_bp.route('/search', methods=['POST'])
def search_diseases():
    """Busca doenças por código CID ou nome."""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query é obrigatória'}), 400
    
    results = []
    
    # Buscar no CID-10 local primeiro
    for disease in cid10_data:
        codigo = disease.get('code', '').upper()  # Mudança: 'codigo' para 'code'
        nome = disease.get('description', '').lower()  # Mudança: 'nome' para 'description'
        query_lower = query.lower()
        query_upper = query.upper()
        
        # Busca mais flexível
        if (query_upper in codigo or 
            query_lower in nome or
            any(word in nome for word in query_lower.split()) or
            any(word in query_lower for word in nome.split())):
            
            # Enriquecer com informações adicionais
            enriched_disease = {
                'codigo': disease.get('code'),
                'nome': disease.get('description')
            }
            enriched_disease = enrich_disease_info(enriched_disease)
            results.append(enriched_disease)
            
            # Parar se já encontrou resultados suficientes
            if len(results) >= 5:
                break
    
    # Buscar no CID-11 se ainda não encontrou resultados suficientes
    # try:
    #     icd11_results = icd11_api.search_diseases(query)
    #     for icd11_disease in icd11_results[:3]:  # Limitar a 3 resultados do CID-11
    #         if medication_enricher:
    #             enriched_disease = medication_enricher.enrich_disease_with_medications(icd11_disease)
    #         else:
    #             enriched_disease = icd11_disease
    #         enriched_disease = enrich_disease_info(enriched_disease)
    #         results.append(enriched_disease)
    # except Exception as e:
    #     print(f"Erro ao buscar no CID-11: {e}")
    
    return jsonify({
        'results': results[:10],  # Limitar a 10 resultados
        'total': len(results)
    })

@disease_bp.route('/categories', methods=['GET'])
def get_categories():
    """Retorna categorias CID-10."""
    categories = {}
    
    for disease in cid10_data:
        codigo = disease.get('codigo', '')
        if codigo:
            categoria = codigo[0]  # Primeira letra do código
            if categoria not in categories:
                categories[categoria] = {
                    'letra': categoria,
                    'descricao': get_category_description(categoria),
                    'count': 0
                }
            categories[categoria]['count'] += 1
    
    return jsonify(list(categories.values()))

@disease_bp.route('/interactions', methods=['POST'])
def check_drug_interactions():
    """Verifica interações medicamentosas."""
    data = request.get_json()
    medications = data.get('medications', [])
    
    if not medications or len(medications) < 2:
        return jsonify({'error': 'Pelo menos 2 medicamentos são necessários'}), 400
    
    interaction_summary = drug_checker.get_interaction_summary(medications)
    
    return jsonify(interaction_summary)

@disease_bp.route('/medications/<disease_name>', methods=['GET'])
def get_medications_for_disease_route(disease_name):
    """Retorna medicamentos para uma doença específica."""
    if medication_enricher:
        medications = medication_enricher.get_medications_for_disease(disease_name)
    else:
        medications = []
    
    return jsonify({
        'disease': disease_name,
        'medications': medications
    })

@disease_bp.route('/symptoms/<cid_code>', methods=['GET'])
def get_symptoms(cid_code):
    """Retorna sintomas para um código CID específico."""
    # Primeiro, tentar buscar na API Render
    try:
        render_symptoms = render_api.get_symptoms_data(cid_code)
        if render_symptoms:
            return jsonify({
                'cid_code': cid_code,
                'disease_name': render_symptoms.get('disease_name', ''),
                'symptoms': render_symptoms.get('symptoms', [])
            })
    except Exception as e:
        print(f"Erro ao buscar sintomas na API Render: {e}")
    
    # Buscar doença pelo código CID localmente
    disease = None
    for d in cid10_data:
        if d.get('code', '').upper() == cid_code.upper():
            disease = d
            break
    
    if not disease:
        return jsonify({'error': 'Doença não encontrada'}), 404
    
    # Gerar sintomas baseados no nome da doença
    symptoms = generate_symptoms_for_disease(disease.get('description', ''))
    
    return jsonify({
        'cid_code': cid_code,
        'disease_name': disease.get('description', ''),
        'symptoms': symptoms
    })

@disease_bp.route('/medication_therapy/<cid_code>', methods=['GET'])
def get_medication_therapy(cid_code):
    """Retorna terapia medicamentosa para um código CID específico."""
    # Buscar doença pelo código CID
    disease = None
    for d in cid10_data:
        if d.get('code', '').upper() == cid_code.upper():
            disease = d
            break
    
    if not disease:
        return jsonify({'error': 'Doença não encontrada'}), 404
    
    # Gerar medicamentos baseados no nome da doença
    medications = generate_default_medications(disease.get('description', ''))
    
    return jsonify({
        'cid_code': cid_code,
        'disease_name': disease.get('description', ''),
        'medications': medications
    })

@disease_bp.route('/non_medication_therapy/<cid_code>', methods=['GET'])
def get_non_medication_therapy(cid_code):
    """Retorna terapia não medicamentosa para um código CID específico."""
    # Buscar doença pelo código CID
    disease = None
    for d in cid10_data:
        if d.get('code', '').upper() == cid_code.upper():
            disease = d
            break
    
    if not disease:
        return jsonify({'error': 'Doença não encontrada'}), 404
    
    # Gerar terapias não medicamentosas baseadas no nome da doença
    therapies = generate_non_medication_therapies(disease.get('description', ''))
    
    return jsonify({
        'cid_code': cid_code,
        'disease_name': disease.get('description', ''),
        'therapies': therapies
    })

@disease_bp.route('/diagnosis_info/<cid_code>', methods=['GET'])
def get_diagnosis_info(cid_code):
    """Retorna informações de diagnóstico para um código CID específico."""
    disease = None
    for d in cid10_data:
        if d.get('code', '').upper() == cid_code.upper():
            disease = d
            break
    
    if not disease:
        return jsonify({'error': 'Doença não encontrada'}), 404
    
    enriched_disease = enrich_disease_info(disease)
    
    return jsonify({
        'cid_code': cid_code,
        'disease_name': enriched_disease.get('description', ''),
        'severity': enriched_disease.get('gravidade', 'Não especificada'),
        'prognosis': enriched_disease.get('prognostico', 'Não especificado'),
        'treatment_type': enriched_disease.get('tipo_tratamento', 'Não especificado'),
        'has_treatment': enriched_disease.get('tem_tratamento', False),
        'is_disabling': enriched_disease.get('incapacitante', False)
    })

@disease_bp.route('/diagnose', methods=['POST'])
def diagnose_from_report():
    """Diagnostica doença baseada em laudo médico."""
    data = request.get_json()
    report = data.get('report', '').strip()
    
    if not report:
        return jsonify({'error': 'Laudo médico é obrigatório'}), 400
    
    # Analisar o laudo e encontrar possível diagnóstico
    diagnosis = analyze_medical_report(report)
    
    if not diagnosis:
        return jsonify({'error': 'Não foi possível identificar um diagnóstico no laudo'}), 404
    
    return jsonify({
        'diagnosis': diagnosis
    })

def enrich_disease_info(disease):
    """Enriquece informações da doença com dados médicos."""
    codigo = disease.get('code', '')
    nome = disease.get('description', '')
    
    # Lógica simplificada de enriquecimento
    disease['tem_tratamento'] = determine_treatment_availability(codigo, nome)
    disease['incapacitante'] = determine_disability_status(codigo, nome)
    disease['tipo_tratamento'] = determine_treatment_type(codigo, nome)
    disease['gravidade'] = determine_severity(codigo, nome)
    disease['prognostico'] = determine_prognosis(codigo, nome)
    
    return disease

def determine_treatment_availability(codigo, nome):
    """Determina se a doença tem tratamento."""
    untreatable_patterns = ['malformação', 'congênita', 'hereditária', 'genética']
    if any(pattern in nome.lower() for pattern in untreatable_patterns):
        return False
    return True

def determine_disability_status(codigo, nome):
    """Determina se a doença é incapacitante."""
    disabling_patterns = ['paralisia', 'cegueira', 'surdez', 'amputação', 'tetraplegia', 'paraplegia']
    if any(pattern in nome.lower() for pattern in disabling_patterns):
        return True
    return False

def determine_treatment_type(codigo, nome):
    """Determina o tipo de tratamento."""
    if 'infecção' in nome.lower() or 'bacteriana' in nome.lower():
        return 'Medicamentoso'
    elif 'fratura' in nome.lower() or 'lesão' in nome.lower():
        return 'Cirúrgico'
    elif 'mental' in nome.lower() or 'psicológico' in nome.lower():
        return 'Psicológico'
    else:
        return 'Medicamentoso'

def determine_severity(codigo, nome):
    """Determina a gravidade da doença."""
    severe_patterns = ['maligno', 'grave', 'aguda', 'severa']
    mild_patterns = ['leve', 'benigno', 'crônica']
    
    if any(pattern in nome.lower() for pattern in severe_patterns):
        return 'Grave'
    elif any(pattern in nome.lower() for pattern in mild_patterns):
        return 'Leve'
    else:
        return 'Moderada'

def determine_prognosis(codigo, nome):
    """Determina o prognóstico da doença."""
    good_patterns = ['benigno', 'curável', 'tratável']
    poor_patterns = ['maligno', 'terminal', 'progressiva']
    
    if any(pattern in nome.lower() for pattern in good_patterns):
        return 'Bom com tratamento adequado'
    elif any(pattern in nome.lower() for pattern in poor_patterns):
        return 'Reservado'
    else:
        return 'Variável conforme tratamento'

def get_category_description(letra):
    """Retorna descrição da categoria CID-10."""
    descriptions = {
        'A': 'Doenças infecciosas e parasitárias',
        'B': 'Doenças infecciosas e parasitárias',
        'C': 'Neoplasias',
        'D': 'Doenças do sangue e dos órgãos hematopoéticos',
        'E': 'Doenças endócrinas, nutricionais e metabólicas',
        'F': 'Transtornos mentais e comportamentais',
        'G': 'Doenças do sistema nervoso',
        'H': 'Doenças do olho e anexos / Doenças do ouvido',
        'I': 'Doenças do aparelho circulatório',
        'J': 'Doenças do aparelho respiratório',
        'K': 'Doenças do aparelho digestivo',
        'L': 'Doenças da pele e do tecido subcutâneo',
        'M': 'Doenças do sistema osteomuscular',
        'N': 'Doenças do aparelho geniturinário',
        'O': 'Gravidez, parto e puerpério',
        'P': 'Afecções originadas no período perinatal',
        'Q': 'Malformações congênitas',
        'R': 'Sintomas, sinais e achados anormais',
        'S': 'Lesões, envenenamento e outras consequências',
        'T': 'Lesões, envenenamento e outras consequências',
        'U': 'Códigos para propósitos especiais',
        'V': 'Causas externas de morbidade e mortalidade',
        'W': 'Causas externas de morbidade e mortalidade',
        'X': 'Causas externas de morbidade e mortalidade',
        'Y': 'Causas externas de morbidade e mortalidade',
        'Z': 'Fatores que influenciam o estado de saúde'
    }
    return descriptions.get(letra, f'Categoria {letra}')

def generate_symptoms_for_disease(disease_name):
    """Gera sintomas baseados no nome da doença."""
    symptoms_map = {
        'hipertensão': ['Dor de cabeça', 'Tontura', 'Visão turva', 'Fadiga', 'Palpitações'],
        'diabetes': ['Sede excessiva', 'Micção frequente', 'Fadiga', 'Visão turva', 'Perda de peso'],
        'pneumonia': ['Febre', 'Tosse com catarro', 'Dificuldade para respirar', 'Dor no peito', 'Fadiga'],
        'gripe': ['Febre', 'Dor de cabeça', 'Dores musculares', 'Tosse', 'Congestão nasal'],
        'asma': ['Falta de ar', 'Chiado no peito', 'Tosse', 'Aperto no peito', 'Dificuldade para dormir'],
        'gastrite': ['Dor no estômago', 'Náusea', 'Vômito', 'Sensação de queimação', 'Perda de apetite'],
        'depressão': ['Tristeza persistente', 'Perda de interesse', 'Fadiga', 'Alterações do sono', 'Dificuldade de concentração'],
        'ansiedade': ['Preocupação excessiva', 'Inquietação', 'Fadiga', 'Dificuldade de concentração', 'Tensão muscular'],
        'febre': ['Temperatura corporal elevada', 'Calafrios', 'Sudorese', 'Dor de cabeça', 'Mal-estar geral']
    }
    
    # Buscar sintomas por palavras-chave no nome da doença
    disease_lower = disease_name.lower()
    for key, symptoms in symptoms_map.items():
        if key in disease_lower:
            return symptoms
    
    # Sintomas genéricos se não encontrar específicos
    return ['Consulte um médico para avaliação detalhada dos sintomas']

def generate_non_medication_therapies(disease_name):
    """Gera terapias não medicamentosas baseadas no nome da doença."""
    therapies_map = {
        'hipertensão': ['Dieta com baixo teor de sódio', 'Exercícios físicos regulares', 'Controle do peso', 'Redução do estresse', 'Parar de fumar'],
        'diabetes': ['Dieta balanceada', 'Exercícios físicos', 'Monitoramento da glicose', 'Controle do peso', 'Educação em diabetes'],
        'pneumonia': ['Repouso', 'Hidratação adequada', 'Fisioterapia respiratória', 'Evitar fumo', 'Vacinação preventiva'],
        'gripe': ['Repouso', 'Hidratação', 'Isolamento', 'Higiene das mãos', 'Vacinação anual'],
        'asma': ['Evitar alérgenos', 'Exercícios respiratórios', 'Controle ambiental', 'Fisioterapia respiratória', 'Educação sobre a doença'],
        'gastrite': ['Dieta adequada', 'Evitar álcool e fumo', 'Controle do estresse', 'Refeições regulares', 'Evitar alimentos irritantes'],
        'depressão': ['Psicoterapia', 'Exercícios físicos', 'Atividades sociais', 'Técnicas de relaxamento', 'Suporte familiar'],
        'ansiedade': ['Terapia cognitivo-comportamental', 'Técnicas de relaxamento', 'Exercícios físicos', 'Meditação', 'Suporte psicológico'],
        'febre': ['Repouso', 'Hidratação abundante', 'Compressas frias', 'Roupas leves', 'Ambiente ventilado']
    }
    
    # Buscar terapias por palavras-chave no nome da doença
    disease_lower = disease_name.lower()
    for key, therapies in therapies_map.items():
        if key in disease_lower:
            return therapies
    
    # Terapias genéricas se não encontrar específicas
    return ['Consulte um médico para orientações específicas de tratamento']

def generate_default_medications(disease_name):
    """Gera medicamentos padrão quando não há dados específicos."""
    medications_map = {
        'hipertensão': [
            {'principio_ativo': 'Losartana', 'nomes_comerciais': ['Cozaar', 'Losartec'], 'dosagem_usual': '50mg 1x/dia', 'via_administracao': 'Oral'},
            {'principio_ativo': 'Enalapril', 'nomes_comerciais': ['Renitec', 'Vasopril'], 'dosagem_usual': '10mg 2x/dia', 'via_administracao': 'Oral'}
        ],
        'diabetes': [
            {'principio_ativo': 'Metformina', 'nomes_comerciais': ['Glifage', 'Glucophage'], 'dosagem_usual': '850mg 2x/dia', 'via_administracao': 'Oral'},
            {'principio_ativo': 'Glibenclamida', 'nomes_comerciais': ['Daonil', 'Euglucon'], 'dosagem_usual': '5mg 1x/dia', 'via_administracao': 'Oral'}
        ],
        'febre': [
            {'principio_ativo': 'Paracetamol', 'nomes_comerciais': ['Tylenol', 'Parador'], 'dosagem_usual': '750mg 6/6h', 'via_administracao': 'Oral'},
            {'principio_ativo': 'Dipirona', 'nomes_comerciais': ['Novalgina', 'Anador'], 'dosagem_usual': '500mg 6/6h', 'via_administracao': 'Oral'}
        ]
    }
    
    disease_lower = disease_name.lower()
    for key, medications in medications_map.items():
        if key in disease_lower:
            return medications
    
    return [{'principio_ativo': 'Consultar médico', 'nomes_comerciais': ['Prescrição médica necessária'], 'dosagem_usual': 'Conforme orientação médica', 'via_administracao': 'Conforme prescrição'}]

def analyze_medical_report(report):
    """Analisa laudo médico e retorna diagnóstico provável."""
    report_lower = report.lower()
    
    # Dicionário de palavras-chave para diagnósticos
    diagnosis_keywords = {
        'hipertensão': ['pressão alta', 'hipertensão', 'pressão arterial elevada', 'pa elevada'],
        'diabetes': ['diabetes', 'glicemia elevada', 'hiperglicemia', 'açúcar alto'],
        'pneumonia': ['pneumonia', 'infecção pulmonar', 'consolidação pulmonar', 'infiltrado pulmonar'],
        'gripe': ['gripe', 'influenza', 'síndrome gripal', 'resfriado'],
        'asma': ['asma', 'broncoespasmo', 'chiado', 'sibilos'],
        'gastrite': ['gastrite', 'inflamação gástrica', 'dor epigástrica', 'úlcera'],
        'depressão': ['depressão', 'transtorno depressivo', 'humor deprimido', 'tristeza'],
        'ansiedade': ['ansiedade', 'transtorno de ansiedade', 'pânico', 'fobia'],
        'febre': ['febre', 'temperatura elevada', 'hipertermia', 'estado febril']
    }
    
    # Buscar por palavras-chave no laudo
    for disease, keywords in diagnosis_keywords.items():
        for keyword in keywords:
            if keyword in report_lower:
                # Encontrar a doença correspondente no CID-10
                for d in cid10_data:
                    if disease in d.get('nome', '').lower():
                        # Enriquecer com informações completas
                        if medication_enricher:
                            enriched_disease = medication_enricher.enrich_disease_with_medications(d)
                        else:
                            enriched_disease = d
                            enriched_disease['medications'] = generate_default_medications(d.get('nome', ''))
                        
                        return {
                            'cid_code': d.get('codigo', ''),
                            'name': d.get('nome', ''),
                            'symptoms': generate_symptoms_for_disease(d.get('nome', '')),
                            'medications': enriched_disease.get('medications', []),
                            'non_medication_therapies': generate_non_medication_therapies(d.get('nome', ''))
                        }
    
    return None


    
    # Adicionando terapias específicas para esquizofrenia e outras doenças mentais
    therapies_map.update({
        'esquizofrenia': ['Psicoterapia individual', 'Terapia familiar', 'Reabilitação psicossocial', 'Terapia ocupacional', 'Suporte comunitário', 'Grupos de apoio'],
        'epilepsia': ['Evitar fatores desencadeantes', 'Sono adequado', 'Controle do estresse', 'Atividade física moderada', 'Dieta cetogênica (em casos específicos)'],
        'doença renal': ['Dieta com restrição de proteína', 'Controle da pressão arterial', 'Controle do diabetes', 'Hidratação adequada', 'Exercícios físicos leves']
    })
    
    # Buscar terapias por palavras-chave no nome da doença
    disease_lower = disease_name.lower()
    for key, therapies in therapies_map.items():
        if key in disease_lower:
            return therapies
    
    # Terapias genéricas se não encontrar específicas
    return ['Consulte um médico para orientações específicas de tratamento não medicamentoso']

def generate_default_medications(disease_name):
    """Gera medicamentos padrão baseados no nome da doença."""
    medications_map = {
        'hipertensão': [
            {'principio_ativo': 'Losartana', 'nomes_comerciais': ['Cozaar', 'Losartec', 'Aradois']},
            {'principio_ativo': 'Enalapril', 'nomes_comerciais': ['Renitec', 'Vasopril', 'Enalapril']},
            {'principio_ativo': 'Amlodipina', 'nomes_comerciais': ['Norvasc', 'Amlocor', 'Amlodipina']}
        ],
        'diabetes': [
            {'principio_ativo': 'Metformina', 'nomes_comerciais': ['Glifage', 'Glucoformin', 'Metformina']},
            {'principio_ativo': 'Glibenclamida', 'nomes_comerciais': ['Daonil', 'Euglucon', 'Glibenclamida']},
            {'principio_ativo': 'Insulina', 'nomes_comerciais': ['Humulin', 'Novolin', 'Lantus']}
        ],
        'esquizofrenia': [
            {'principio_ativo': 'Risperidona', 'nomes_comerciais': ['Risperdal', 'Risperidona', 'Zargus']},
            {'principio_ativo': 'Olanzapina', 'nomes_comerciais': ['Zyprexa', 'Olanzapina', 'Zyprexa Zydis']},
            {'principio_ativo': 'Haloperidol', 'nomes_comerciais': ['Haldol', 'Haloperidol', 'Haldol Decanoato']}
        ],
        'depressão': [
            {'principio_ativo': 'Sertralina', 'nomes_comerciais': ['Zoloft', 'Sertralina', 'Assert']},
            {'principio_ativo': 'Fluoxetina', 'nomes_comerciais': ['Prozac', 'Fluoxetina', 'Daforin']},
            {'principio_ativo': 'Escitalopram', 'nomes_comerciais': ['Lexapro', 'Escitalopram', 'Reconter']}
        ],
        'epilepsia': [
            {'principio_ativo': 'Carbamazepina', 'nomes_comerciais': ['Tegretol', 'Carbamazepina', 'Carbazina']},
            {'principio_ativo': 'Fenitoína', 'nomes_comerciais': ['Hidantal', 'Fenitoína', 'Epelin']},
            {'principio_ativo': 'Ácido Valproico', 'nomes_comerciais': ['Depakene', 'Valproato', 'Epilim']}
        ]
    }
    
    # Buscar medicamentos por palavras-chave no nome da doença
    disease_lower = disease_name.lower()
    for key, medications in medications_map.items():
        if key in disease_lower:
            return medications
    
    # Medicamentos genéricos se não encontrar específicos
    return [{'principio_ativo': 'Consulte um médico', 'nomes_comerciais': ['Prescrição médica necessária']}]

def analyze_medical_report(report):
    """Analisa laudo médico e retorna possível diagnóstico."""
    # Implementação simplificada - em produção seria mais complexa
    report_lower = report.lower()
    
    # Mapear palavras-chave para diagnósticos
    diagnosis_keywords = {
        'hipertensão': {'codigo': 'I10', 'nome': 'Hipertensão essencial'},
        'diabetes': {'codigo': 'E11', 'nome': 'Diabetes mellitus não-insulino-dependente'},
        'esquizofrenia': {'codigo': 'F20', 'nome': 'Esquizofrenia'},
        'depressão': {'codigo': 'F32', 'nome': 'Episódios depressivos'},
        'epilepsia': {'codigo': 'G40', 'nome': 'Epilepsia'}
    }
    
    for keyword, diagnosis in diagnosis_keywords.items():
        if keyword in report_lower:
            # Enriquecer diagnóstico com sintomas e tratamentos
            diagnosis['symptoms'] = generate_symptoms_for_disease(diagnosis['nome'])
            diagnosis['medications'] = generate_default_medications(diagnosis['nome'])
            diagnosis['non_medication_therapies'] = generate_non_medication_therapies(diagnosis['nome'])
            return diagnosis
    
    return None

