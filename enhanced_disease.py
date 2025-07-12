"""
Rotas aprimoradas da API com novos serviços integrados.
"""
from flask import Blueprint, request, jsonify
import json
import os
from src.services.cid_categorizer import CIDCategorizer
from src.services.diagnostic_engine import DiagnosticEngine
from src.services.enhanced_drug_interaction_checker import EnhancedDrugInteractionChecker
from src.services.disease_details_service import DiseaseDetailsService
from src.services.symptom_selector_service import SymptomSelectorService

enhanced_disease_bp = Blueprint('enhanced_disease', __name__)

# Inicializar serviços
cid_categorizer = CIDCategorizer()
diagnostic_engine = DiagnosticEngine()
drug_checker = EnhancedDrugInteractionChecker()
disease_details = DiseaseDetailsService()
symptom_selector = SymptomSelectorService()

@enhanced_disease_bp.route('/categories', methods=['GET'])
def get_cid_categories():
    """Retorna categorias CID-10 organizadas com subcategorias."""
    try:
        categories = cid_categorizer.get_categories()
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar categorias: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/categories/<category_letter>/diseases', methods=['GET'])
def get_diseases_by_category(category_letter):
    """Retorna doenças de uma categoria específica."""
    try:
        diseases = cid_categorizer.get_diseases_by_category(category_letter)
        return jsonify({
            'success': True,
            'category': category_letter.upper(),
            'diseases': diseases,
            'total_diseases': len(diseases)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar doenças da categoria: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/search/name', methods=['POST'])
def search_diseases_by_name():
    """Busca doenças por nome com algoritmo aprimorado."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 20)
        
        if not query or len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query deve ter pelo menos 2 caracteres'
            }), 400
        
        results = cid_categorizer.search_by_name(query, limit)
        
        # Enriquecer resultados com informações da categoria
        enriched_results = []
        for result in results:
            subcategory_info = cid_categorizer.get_subcategory_info(result['code'])
            result['subcategory'] = subcategory_info
            enriched_results.append(result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': enriched_results,
            'total_found': len(enriched_results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na busca por nome: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/search/code', methods=['POST'])
def search_disease_by_code():
    """Busca doença por código CID específico."""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Código CID é obrigatório'
            }), 400
        
        # Busca exata
        disease = cid_categorizer.search_by_code(code)
        
        if disease:
            # Enriquecer com informações da subcategoria
            subcategory_info = cid_categorizer.get_subcategory_info(code)
            disease['subcategory'] = subcategory_info
            
            return jsonify({
                'success': True,
                'disease': disease
            })
        else:
            # Busca por padrão se não encontrou exato
            pattern_results = cid_categorizer.search_by_code_pattern(code, 10)
            return jsonify({
                'success': True,
                'exact_match': False,
                'pattern_results': pattern_results,
                'message': f'Código exato não encontrado. Mostrando códigos similares a "{code}"'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na busca por código: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/add_custom_cid', methods=['POST'])
def add_custom_cid():
    """Permite que médicos adicionem códigos CID personalizados."""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        description = data.get('description', '').strip()
        user_type = data.get('user_type', 'patient')  # Em produção, viria do token de autenticação
        
        if not code or not description:
            return jsonify({
                'success': False,
                'error': 'Código e descrição são obrigatórios'
            }), 400
        
        new_disease = cid_categorizer.add_custom_cid(code, description, user_type)
        
        return jsonify({
            'success': True,
            'message': 'Código CID personalizado adicionado com sucesso',
            'disease': new_disease
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao adicionar CID personalizado: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/diagnose/symptoms', methods=['POST'])
def diagnose_from_symptoms():
    """Diagnostica baseado em relatório de sintomas."""
    try:
        data = request.get_json()
        symptoms_report = data.get('symptoms_report', '').strip()
        include_report = data.get('include_report', False)
        
        if not symptoms_report or len(symptoms_report) < 10:
            return jsonify({
                'success': False,
                'error': 'Relatório de sintomas deve ter pelo menos 10 caracteres'
            }), 400
        
        # Analisar sintomas
        diagnostic_results = diagnostic_engine.analyze_symptoms_report(symptoms_report)
        
        response = {
            'success': True,
            'original_symptoms': symptoms_report,
            'diagnostic_results': [
                {
                    'cid_code': result.cid_code,
                    'disease_name': result.disease_name,
                    'probability': round(result.probability * 100, 1),  # Converter para porcentagem
                    'confidence_level': result.confidence_level,
                    'matching_symptoms': result.matching_symptoms,
                    'additional_info': result.additional_info
                }
                for result in diagnostic_results
            ],
            'total_diagnoses': len(diagnostic_results)
        }
        
        # Incluir relatório médico se solicitado
        if include_report and diagnostic_results:
            medical_report = diagnostic_engine.generate_medical_report(diagnostic_results, symptoms_report)
            response['medical_report'] = medical_report
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro no diagnóstico por sintomas: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/diagnose/advanced_analysis', methods=['POST'])
def advanced_medical_analysis():
    """Análise médica avançada de laudo com informações estruturadas."""
    try:
        data = request.get_json()
        medical_report = data.get('medical_report', '').strip()
        
        if not medical_report or len(medical_report) < 20:
            return jsonify({
                'success': False,
                'error': 'Laudo médico deve ter pelo menos 20 caracteres'
            }), 400
        
        # Análise avançada
        analysis = diagnostic_engine.analyze_medical_report_advanced(medical_report)
        
        return jsonify({
            'success': True,
            'original_report': medical_report,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na análise avançada: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/interactions/check', methods=['POST'])
def check_drug_interactions():
    """Verifica interações medicamentosas com informações detalhadas."""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        include_report = data.get('include_report', False)
        
        if not medications or len(medications) < 2:
            return jsonify({
                'success': False,
                'error': 'Pelo menos 2 medicamentos são necessários'
            }), 400
        
        # Verificar interações
        interaction_summary = drug_checker.get_interaction_summary(medications)
        
        response = {
            'success': True,
            'medications': medications,
            'summary': interaction_summary
        }
        
        # Incluir relatório detalhado se solicitado
        if include_report:
            detailed_report = drug_checker.generate_interaction_report(medications)
            response['detailed_report'] = detailed_report
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na verificação de interações: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/interactions/alternatives', methods=['POST'])
def get_drug_alternatives():
    """Busca alternativas medicamentosas para evitar interações."""
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '').strip()
        indication = data.get('indication', '').strip()
        
        if not drug_name:
            return jsonify({
                'success': False,
                'error': 'Nome do medicamento é obrigatório'
            }), 400
        
        alternatives = drug_checker.search_drug_alternatives(drug_name, indication)
        
        return jsonify({
            'success': True,
            'original_drug': drug_name,
            'indication': indication,
            'alternatives': alternatives,
            'total_alternatives': len(alternatives)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar alternativas: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/comprehensive_analysis', methods=['POST'])
def comprehensive_medical_analysis():
    """Análise médica abrangente combinando diagnóstico e interações."""
    try:
        data = request.get_json()
        symptoms_report = data.get('symptoms_report', '').strip()
        current_medications = data.get('current_medications', [])
        include_reports = data.get('include_reports', False)
        
        if not symptoms_report and not current_medications:
            return jsonify({
                'success': False,
                'error': 'Relatório de sintomas ou lista de medicamentos é obrigatória'
            }), 400
        
        analysis_result = {
            'success': True,
            'timestamp': str(datetime.now()),
            'analysis_type': 'comprehensive'
        }
        
        # Análise de sintomas se fornecida
        if symptoms_report and len(symptoms_report) >= 10:
            diagnostic_results = diagnostic_engine.analyze_symptoms_report(symptoms_report)
            analysis_result['diagnostic_analysis'] = {
                'symptoms_report': symptoms_report,
                'diagnostic_results': [
                    {
                        'cid_code': result.cid_code,
                        'disease_name': result.disease_name,
                        'probability': round(result.probability * 100, 1),
                        'confidence_level': result.confidence_level,
                        'matching_symptoms': result.matching_symptoms
                    }
                    for result in diagnostic_results
                ]
            }
            
            if include_reports and diagnostic_results:
                medical_report = diagnostic_engine.generate_medical_report(diagnostic_results, symptoms_report)
                analysis_result['diagnostic_analysis']['medical_report'] = medical_report
        
        # Análise de interações se medicamentos fornecidos
        if current_medications and len(current_medications) >= 2:
            interaction_summary = drug_checker.get_interaction_summary(current_medications)
            analysis_result['interaction_analysis'] = {
                'medications': current_medications,
                'summary': interaction_summary
            }
            
            if include_reports:
                interaction_report = drug_checker.generate_interaction_report(current_medications)
                analysis_result['interaction_analysis']['detailed_report'] = interaction_report
        
        # Recomendações integradas
        integrated_recommendations = []
        
        if 'diagnostic_analysis' in analysis_result:
            if analysis_result['diagnostic_analysis']['diagnostic_results']:
                top_diagnosis = analysis_result['diagnostic_analysis']['diagnostic_results'][0]
                if top_diagnosis['probability'] > 50:
                    integrated_recommendations.append(f"Diagnóstico provável: {top_diagnosis['disease_name']} (CID: {top_diagnosis['cid_code']})")
        
        if 'interaction_analysis' in analysis_result:
            if analysis_result['interaction_analysis']['summary']['requires_immediate_attention']:
                integrated_recommendations.append("⚠️ ATENÇÃO: Interações medicamentosas graves detectadas")
        
        integrated_recommendations.extend([
            "Consulte um médico para avaliação completa",
            "Mantenha lista atualizada de medicamentos",
            "Monitore sintomas e efeitos adversos"
        ])
        
        analysis_result['integrated_recommendations'] = integrated_recommendations
        
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na análise abrangente: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API aprimorada está funcionando."""
    return jsonify({
        'status': 'ok',
        'message': 'Med-IA API Aprimorada está funcionando!',
        'services': {
            'cid_categorizer': 'ativo',
            'diagnostic_engine': 'ativo',
            'drug_interaction_checker': 'ativo'
        },
        'version': '2.0'
    })

# Importar datetime para timestamp
from datetime import datetime



@enhanced_disease_bp.route('/categories/<category_letter>/diseases', methods=['GET'])
def get_diseases_by_category(category_letter):
    """Retorna todas as doenças de uma categoria específica."""
    try:
        diseases = cid_categorizer.get_diseases_by_category(category_letter.upper())
        
        if not diseases:
            return jsonify({
                'success': False,
                'message': f'Nenhuma doença encontrada para a categoria {category_letter.upper()}',
                'diseases': []
            }), 404
        
        # Enriquecer com detalhes das doenças
        enriched_diseases = []
        for disease in diseases:
            details = disease_details.get_disease_details(disease['code'])
            if details:
                disease.update({
                    'severity': details['severity'],
                    'has_treatment': details['has_treatment'],
                    'treatment_type': details['treatment_type']
                })
            enriched_diseases.append(disease)
        
        return jsonify({
            'success': True,
            'category': category_letter.upper(),
            'total_diseases': len(enriched_diseases),
            'diseases': enriched_diseases
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar doenças da categoria: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/disease/<cid_code>/details', methods=['GET'])
def get_disease_full_details(cid_code):
    """Retorna detalhes completos de uma doença específica."""
    try:
        details = disease_details.get_disease_details(cid_code.upper())
        
        if not details:
            return jsonify({
                'success': False,
                'message': f'Detalhes não encontrados para o CID {cid_code.upper()}'
            }), 404
        
        return jsonify({
            'success': True,
            'cid_code': cid_code.upper(),
            'disease_details': details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar detalhes da doença: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/symptoms/categories', methods=['GET'])
def get_symptom_categories():
    """Retorna todas as categorias de sintomas disponíveis."""
    try:
        categories = symptom_selector.get_all_symptom_categories()
        
        return jsonify({
            'success': True,
            'total_categories': len(categories),
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar categorias de sintomas: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/symptoms/search', methods=['POST'])
def search_symptoms():
    """Busca sintomas por termo."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query de busca é obrigatória'
            }), 400
        
        results = symptom_selector.search_symptoms(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sintomas: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/symptoms/validate', methods=['POST'])
def validate_symptoms():
    """Valida combinação de sintomas e sugere condições possíveis."""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        if not symptoms:
            return jsonify({
                'success': False,
                'message': 'Lista de sintomas é obrigatória'
            }), 400
        
        # Validar combinação
        matches = symptom_selector.validate_symptom_combination(symptoms)
        
        # Sugerir sintomas relacionados
        suggestions = symptom_selector.get_related_symptoms(symptoms)
        
        return jsonify({
            'success': True,
            'selected_symptoms': symptoms,
            'possible_conditions': matches,
            'suggested_symptoms': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao validar sintomas: {str(e)}'
        }), 500

@enhanced_disease_bp.route('/diagnose/objective_symptoms', methods=['POST'])
def diagnose_by_objective_symptoms():
    """Diagnóstico baseado em sintomas selecionados objetivamente."""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        include_report = data.get('include_report', False)
        
        if not symptoms:
            return jsonify({
                'success': False,
                'message': 'Lista de sintomas é obrigatória'
            }), 400
        
        # Converter lista de sintomas em texto para o motor de diagnóstico
        symptoms_text = f"Paciente apresenta os seguintes sintomas: {', '.join(symptoms)}"
        
        # Usar o motor de diagnóstico existente
        results = diagnostic_engine.analyze_symptoms(symptoms_text, include_report)
        
        # Enriquecer com validação de sintomas
        validation = symptom_selector.validate_symptom_combination(symptoms)
        
        # Adicionar informações de validação aos resultados
        if results.get('success'):
            results['symptom_validation'] = validation
            results['selected_symptoms'] = symptoms
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar diagnóstico: {str(e)}'
        }), 500

