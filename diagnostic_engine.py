"""
Motor de diagnóstico baseado em sintomas e laudos médicos.
Analisa relatórios de sintomas e sugere diagnósticos prováveis.
"""
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os

@dataclass
class Symptom:
    name: str
    severity: str  # 'leve', 'moderado', 'grave'
    duration: str  # 'agudo', 'crônico', 'intermitente'
    location: str = ""  # localização anatômica
    
@dataclass
class DiagnosticResult:
    cid_code: str
    disease_name: str
    probability: float  # 0.0 a 1.0
    matching_symptoms: List[str]
    additional_info: Dict
    confidence_level: str  # 'baixa', 'média', 'alta'

class DiagnosticEngine:
    def __init__(self):
        self.symptom_database = self._load_symptom_database()
        self.disease_patterns = self._load_disease_patterns()
        self.cid10_data = self._load_cid_data()
    
    def _load_cid_data(self):
        """Carrega dados do CID-10."""
        cid10_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cid10_datasus.json')
        if os.path.exists(cid10_path):
            with open(cid10_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_symptom_database(self) -> Dict:
        """Carrega base de dados de sintomas por doença."""
        return {
            # Doenças Cardiovasculares
            'I10': {  # Hipertensão essencial
                'name': 'Hipertensão essencial',
                'primary_symptoms': [
                    'dor de cabeça', 'cefaleia', 'dor na nuca',
                    'tontura', 'vertigem', 'tonteira',
                    'visão turva', 'visão embaçada',
                    'palpitações', 'batimento cardíaco acelerado',
                    'fadiga', 'cansaço', 'fraqueza'
                ],
                'secondary_symptoms': [
                    'zumbido no ouvido', 'sangramento nasal',
                    'falta de ar', 'dispneia',
                    'dor no peito', 'pressão no peito'
                ],
                'risk_factors': ['obesidade', 'sedentarismo', 'estresse', 'idade avançada'],
                'severity_indicators': ['pressão sistólica > 180', 'pressão diastólica > 110']
            },
            
            'I21': {  # Infarto agudo do miocárdio
                'name': 'Infarto agudo do miocárdio',
                'primary_symptoms': [
                    'dor no peito', 'dor torácica', 'aperto no peito',
                    'dor irradiando para braço esquerdo',
                    'dor irradiando para mandíbula',
                    'falta de ar', 'dispneia',
                    'sudorese', 'suor frio',
                    'náusea', 'vômito'
                ],
                'secondary_symptoms': [
                    'palidez', 'ansiedade', 'sensação de morte iminente',
                    'palpitações', 'fadiga extrema'
                ],
                'emergency_indicators': ['dor torácica intensa', 'sudorese profusa', 'dispneia grave']
            },
            
            # Doenças Endócrinas
            'E11': {  # Diabetes mellitus tipo 2
                'name': 'Diabetes mellitus não-insulino-dependente',
                'primary_symptoms': [
                    'sede excessiva', 'polidipsia',
                    'micção frequente', 'poliúria',
                    'fome excessiva', 'polifagia',
                    'perda de peso', 'emagrecimento',
                    'fadiga', 'cansaço',
                    'visão turva', 'visão embaçada'
                ],
                'secondary_symptoms': [
                    'cicatrização lenta', 'infecções recorrentes',
                    'formigamento nas mãos', 'formigamento nos pés',
                    'pele seca', 'coceira na pele'
                ],
                'risk_factors': ['obesidade', 'sedentarismo', 'histórico familiar'],
                'complications': ['neuropatia', 'retinopatia', 'nefropatia']
            },
            
            # Doenças Respiratórias
            'J18': {  # Pneumonia
                'name': 'Pneumonia por organismo não especificado',
                'primary_symptoms': [
                    'febre', 'febre alta', 'hipertermia',
                    'tosse', 'tosse com catarro', 'tosse produtiva',
                    'dificuldade para respirar', 'dispneia', 'falta de ar',
                    'dor no peito', 'dor torácica',
                    'calafrios', 'tremores'
                ],
                'secondary_symptoms': [
                    'fadiga', 'mal-estar geral',
                    'dor de cabeça', 'cefaleia',
                    'perda de apetite', 'náusea',
                    'sudorese', 'suor noturno'
                ],
                'severity_indicators': ['febre > 39°C', 'dispneia grave', 'cianose']
            },
            
            'J45': {  # Asma
                'name': 'Asma',
                'primary_symptoms': [
                    'falta de ar', 'dispneia', 'dificuldade para respirar',
                    'chiado no peito', 'sibilos', 'ruído respiratório',
                    'tosse', 'tosse seca', 'tosse noturna',
                    'aperto no peito', 'opressão torácica'
                ],
                'secondary_symptoms': [
                    'ansiedade', 'fadiga',
                    'dificuldade para dormir',
                    'irritabilidade'
                ],
                'triggers': ['alérgenos', 'exercício', 'estresse', 'infecções respiratórias']
            },
            
            # Doenças Digestivas
            'K29': {  # Gastrite
                'name': 'Gastrite e duodenite',
                'primary_symptoms': [
                    'dor no estômago', 'dor epigástrica', 'dor abdominal superior',
                    'queimação no estômago', 'azia', 'pirose',
                    'náusea', 'enjoo',
                    'vômito', 'vômitos',
                    'sensação de estômago cheio', 'plenitude gástrica'
                ],
                'secondary_symptoms': [
                    'perda de apetite', 'inapetência',
                    'eructações', 'arrotos',
                    'flatulência', 'gases',
                    'mal-estar geral'
                ],
                'aggravating_factors': ['alimentos condimentados', 'álcool', 'estresse', 'medicamentos']
            },
            
            # Doenças Mentais
            'F32': {  # Episódios depressivos
                'name': 'Episódios depressivos',
                'primary_symptoms': [
                    'tristeza persistente', 'humor deprimido',
                    'perda de interesse', 'anedonia',
                    'fadiga', 'falta de energia',
                    'alterações do sono', 'insônia', 'hipersonia',
                    'alterações do apetite', 'perda de apetite', 'aumento do apetite'
                ],
                'secondary_symptoms': [
                    'dificuldade de concentração', 'problemas de memória',
                    'sentimentos de culpa', 'baixa autoestima',
                    'pensamentos de morte', 'ideação suicida',
                    'irritabilidade', 'ansiedade'
                ],
                'severity_indicators': ['ideação suicida', 'sintomas psicóticos', 'incapacidade funcional']
            },
            
            'F41': {  # Transtornos de ansiedade
                'name': 'Outros transtornos ansiosos',
                'primary_symptoms': [
                    'preocupação excessiva', 'ansiedade',
                    'inquietação', 'agitação',
                    'tensão muscular', 'rigidez muscular',
                    'fadiga', 'cansaço',
                    'dificuldade de concentração'
                ],
                'secondary_symptoms': [
                    'palpitações', 'taquicardia',
                    'sudorese', 'tremores',
                    'falta de ar', 'sensação de sufocamento',
                    'tontura', 'náusea',
                    'alterações do sono'
                ],
                'panic_symptoms': ['medo de morrer', 'medo de enlouquecer', 'despersonalização']
            },
            
            # Doenças Neurológicas
            'G40': {  # Epilepsia
                'name': 'Epilepsia',
                'primary_symptoms': [
                    'convulsões', 'crises convulsivas',
                    'perda de consciência', 'desmaio',
                    'movimentos involuntários', 'espasmos',
                    'rigidez muscular', 'contrações musculares'
                ],
                'secondary_symptoms': [
                    'confusão mental pós-ictal',
                    'dor de cabeça', 'cefaleia',
                    'fadiga', 'sonolência',
                    'perda de memória temporária'
                ],
                'aura_symptoms': ['sensações estranhas', 'alterações visuais', 'odores estranhos']
            },
            
            # Doenças Urinárias
            'N30': {  # Cistite
                'name': 'Cistite',
                'primary_symptoms': [
                    'dor ao urinar', 'disúria', 'ardor ao urinar',
                    'urgência urinária', 'vontade frequente de urinar',
                    'dor na bexiga', 'dor suprapúbica',
                    'urina turva', 'urina com odor forte'
                ],
                'secondary_symptoms': [
                    'sangue na urina', 'hematúria',
                    'febre baixa', 'mal-estar',
                    'dor nas costas', 'dor lombar'
                ],
                'complications': ['pielonefrite', 'sepse urinária']
            },
            
            # Doenças Infecciosas
            'A90': {  # Dengue
                'name': 'Dengue clássico',
                'primary_symptoms': [
                    'febre alta', 'febre súbita',
                    'dor de cabeça intensa', 'cefaleia frontal',
                    'dor atrás dos olhos', 'dor retroorbital',
                    'dores musculares', 'mialgia',
                    'dores nas articulações', 'artralgia'
                ],
                'secondary_symptoms': [
                    'náusea', 'vômito',
                    'manchas vermelhas na pele', 'exantema',
                    'fadiga', 'mal-estar geral',
                    'perda de apetite'
                ],
                'warning_signs': ['dor abdominal intensa', 'vômitos persistentes', 'sangramento']
            }
        }
    
    def _load_disease_patterns(self) -> Dict:
        """Carrega padrões de reconhecimento de doenças em texto."""
        return {
            'cardiovascular': {
                'keywords': ['coração', 'cardíaco', 'pressão', 'hipertensão', 'infarto', 'angina'],
                'symptoms': ['dor no peito', 'palpitações', 'falta de ar', 'tontura']
            },
            'respiratory': {
                'keywords': ['pulmão', 'respiratório', 'tosse', 'pneumonia', 'asma', 'bronquite'],
                'symptoms': ['tosse', 'falta de ar', 'chiado', 'febre', 'catarro']
            },
            'digestive': {
                'keywords': ['estômago', 'intestino', 'digestivo', 'gastrite', 'úlcera'],
                'symptoms': ['dor abdominal', 'náusea', 'vômito', 'azia', 'diarreia']
            },
            'neurological': {
                'keywords': ['neurológico', 'cérebro', 'epilepsia', 'convulsão', 'enxaqueca'],
                'symptoms': ['dor de cabeça', 'convulsões', 'tontura', 'confusão']
            },
            'mental': {
                'keywords': ['depressão', 'ansiedade', 'psiquiátrico', 'mental', 'humor'],
                'symptoms': ['tristeza', 'ansiedade', 'insônia', 'fadiga', 'irritabilidade']
            },
            'endocrine': {
                'keywords': ['diabetes', 'tireóide', 'hormonal', 'endócrino'],
                'symptoms': ['sede', 'micção frequente', 'perda de peso', 'fadiga']
            },
            'urinary': {
                'keywords': ['urinário', 'bexiga', 'rim', 'cistite', 'infecção urinária'],
                'symptoms': ['dor ao urinar', 'urgência urinária', 'sangue na urina']
            },
            'infectious': {
                'keywords': ['infecção', 'vírus', 'bactéria', 'febre', 'gripe', 'dengue'],
                'symptoms': ['febre', 'mal-estar', 'dor de cabeça', 'fadiga']
            }
        }
    
    def analyze_symptoms_report(self, report: str) -> List[DiagnosticResult]:
        """Analisa relatório de sintomas e retorna diagnósticos prováveis."""
        if not report or len(report.strip()) < 10:
            return []
        
        # Normalizar texto
        report_lower = report.lower().strip()
        
        # Extrair sintomas do texto
        extracted_symptoms = self._extract_symptoms(report_lower)
        
        # Calcular probabilidades para cada doença
        diagnostic_results = []
        
        for cid_code, disease_info in self.symptom_database.items():
            probability, matching_symptoms = self._calculate_disease_probability(
                extracted_symptoms, disease_info
            )
            
            if probability > 0.1:  # Threshold mínimo de 10%
                confidence = self._determine_confidence_level(probability, len(matching_symptoms))
                
                result = DiagnosticResult(
                    cid_code=cid_code,
                    disease_name=disease_info['name'],
                    probability=probability,
                    matching_symptoms=matching_symptoms,
                    confidence_level=confidence,
                    additional_info={
                        'total_symptoms_found': len(extracted_symptoms),
                        'matching_symptoms_count': len(matching_symptoms),
                        'primary_symptoms_matched': len([s for s in matching_symptoms 
                                                       if s in disease_info.get('primary_symptoms', [])]),
                        'recommendations': self._generate_recommendations(cid_code, probability)
                    }
                )
                
                diagnostic_results.append(result)
        
        # Ordenar por probabilidade
        diagnostic_results.sort(key=lambda x: x.probability, reverse=True)
        
        return diagnostic_results[:5]  # Retornar top 5 diagnósticos
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extrai sintomas do texto usando padrões e palavras-chave."""
        symptoms_found = []
        
        # Lista expandida de sintomas comuns
        symptom_patterns = {
            # Dor
            'dor de cabeça': ['dor de cabeça', 'cefaleia', 'dor na cabeça', 'dor craniana'],
            'dor no peito': ['dor no peito', 'dor torácica', 'aperto no peito', 'pressão no peito'],
            'dor abdominal': ['dor abdominal', 'dor na barriga', 'dor no estômago', 'dor epigástrica'],
            'dor ao urinar': ['dor ao urinar', 'ardor ao urinar', 'disúria', 'queimação ao urinar'],
            'dor muscular': ['dor muscular', 'mialgia', 'dores no corpo', 'dor nos músculos'],
            'dor nas articulações': ['dor nas articulações', 'artralgia', 'dor nas juntas'],
            
            # Respiratório
            'falta de ar': ['falta de ar', 'dispneia', 'dificuldade para respirar', 'falta de fôlego'],
            'tosse': ['tosse', 'tossindo', 'pigarro'],
            'chiado no peito': ['chiado no peito', 'sibilos', 'ruído respiratório'],
            
            # Digestivo
            'náusea': ['náusea', 'enjoo', 'ânsia'],
            'vômito': ['vômito', 'vomitando', 'vômitos'],
            'azia': ['azia', 'queimação', 'pirose'],
            'diarreia': ['diarreia', 'fezes líquidas', 'evacuações frequentes'],
            
            # Neurológico
            'tontura': ['tontura', 'tonteira', 'vertigem', 'desequilíbrio'],
            'convulsões': ['convulsões', 'convulsão', 'crises convulsivas', 'espasmos'],
            'confusão': ['confusão mental', 'desorientação', 'confuso'],
            
            # Cardiovascular
            'palpitações': ['palpitações', 'batimento acelerado', 'coração disparado', 'taquicardia'],
            
            # Geral
            'febre': ['febre', 'temperatura alta', 'hipertermia', 'febril'],
            'fadiga': ['fadiga', 'cansaço', 'fraqueza', 'exaustão'],
            'sudorese': ['sudorese', 'suor', 'transpiração excessiva'],
            'perda de peso': ['perda de peso', 'emagrecimento', 'peso diminuindo'],
            'perda de apetite': ['perda de apetite', 'inapetência', 'sem fome'],
            
            # Urinário
            'urgência urinária': ['urgência urinária', 'vontade frequente de urinar', 'micção frequente'],
            'sangue na urina': ['sangue na urina', 'hematúria', 'urina com sangue'],
            
            # Mental
            'tristeza': ['tristeza', 'deprimido', 'melancolia', 'humor baixo'],
            'ansiedade': ['ansiedade', 'ansioso', 'preocupação excessiva', 'nervosismo'],
            'insônia': ['insônia', 'dificuldade para dormir', 'sono ruim'],
            
            # Específicos
            'sede excessiva': ['sede excessiva', 'polidipsia', 'muita sede'],
            'visão turva': ['visão turva', 'visão embaçada', 'vista embaçada'],
            'formigamento': ['formigamento', 'dormência', 'parestesia']
        }
        
        # Buscar padrões no texto
        for symptom_name, patterns in symptom_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    symptoms_found.append(symptom_name)
                    break  # Evitar duplicatas
        
        return list(set(symptoms_found))  # Remover duplicatas
    
    def _calculate_disease_probability(self, symptoms: List[str], disease_info: Dict) -> Tuple[float, List[str]]:
        """Calcula probabilidade de uma doença baseada nos sintomas."""
        primary_symptoms = disease_info.get('primary_symptoms', [])
        secondary_symptoms = disease_info.get('secondary_symptoms', [])
        
        matching_symptoms = []
        primary_matches = 0
        secondary_matches = 0
        
        # Verificar correspondências
        for symptom in symptoms:
            # Verificar sintomas primários
            for primary in primary_symptoms:
                if self._symptoms_match(symptom, primary):
                    matching_symptoms.append(symptom)
                    primary_matches += 1
                    break
            else:
                # Verificar sintomas secundários se não encontrou primário
                for secondary in secondary_symptoms:
                    if self._symptoms_match(symptom, secondary):
                        matching_symptoms.append(symptom)
                        secondary_matches += 1
                        break
        
        # Calcular probabilidade
        if not matching_symptoms:
            return 0.0, []
        
        # Peso maior para sintomas primários
        primary_weight = 0.8
        secondary_weight = 0.3
        
        total_primary = len(primary_symptoms)
        total_secondary = len(secondary_symptoms)
        
        if total_primary > 0:
            primary_score = (primary_matches / total_primary) * primary_weight
        else:
            primary_score = 0
        
        if total_secondary > 0:
            secondary_score = (secondary_matches / total_secondary) * secondary_weight
        else:
            secondary_score = 0
        
        # Bonus por ter múltiplos sintomas
        symptom_bonus = min(len(matching_symptoms) * 0.1, 0.3)
        
        probability = min(primary_score + secondary_score + symptom_bonus, 1.0)
        
        return probability, list(set(matching_symptoms))
    
    def _symptoms_match(self, symptom1: str, symptom2: str) -> bool:
        """Verifica se dois sintomas são equivalentes."""
        symptom1 = symptom1.lower().strip()
        symptom2 = symptom2.lower().strip()
        
        # Correspondência exata
        if symptom1 == symptom2:
            return True
        
        # Correspondência parcial (uma contém a outra)
        if symptom1 in symptom2 or symptom2 in symptom1:
            return True
        
        # Verificar palavras-chave comuns
        words1 = set(symptom1.split())
        words2 = set(symptom2.split())
        
        # Se têm pelo menos 2 palavras em comum (excluindo palavras muito comuns)
        common_words = ['de', 'da', 'do', 'na', 'no', 'em', 'para', 'com', 'por']
        meaningful_words1 = words1 - set(common_words)
        meaningful_words2 = words2 - set(common_words)
        
        intersection = meaningful_words1 & meaningful_words2
        
        if len(intersection) >= 2:
            return True
        
        # Verificar se uma palavra importante está presente
        important_words = ['dor', 'febre', 'tosse', 'náusea', 'fadiga', 'sangue']
        for word in important_words:
            if word in meaningful_words1 and word in meaningful_words2:
                return True
        
        return False
    
    def _determine_confidence_level(self, probability: float, matching_count: int) -> str:
        """Determina nível de confiança do diagnóstico."""
        if probability >= 0.7 and matching_count >= 3:
            return 'alta'
        elif probability >= 0.4 and matching_count >= 2:
            return 'média'
        else:
            return 'baixa'
    
    def _generate_recommendations(self, cid_code: str, probability: float) -> List[str]:
        """Gera recomendações baseadas no diagnóstico."""
        recommendations = []
        
        if probability >= 0.7:
            recommendations.append("Procure atendimento médico para confirmação do diagnóstico")
            recommendations.append("Realize exames complementares conforme orientação médica")
        elif probability >= 0.4:
            recommendations.append("Considere consulta médica para avaliação")
            recommendations.append("Monitore a evolução dos sintomas")
        else:
            recommendations.append("Observe a evolução dos sintomas")
            recommendations.append("Procure atendimento médico se os sintomas piorarem")
        
        # Recomendações específicas por tipo de doença
        if cid_code.startswith('I'):  # Cardiovascular
            recommendations.append("Evite esforços físicos intensos")
            recommendations.append("Monitore a pressão arterial")
        elif cid_code.startswith('J'):  # Respiratório
            recommendations.append("Mantenha-se hidratado")
            recommendations.append("Evite ambientes com fumaça ou poluição")
        elif cid_code.startswith('F'):  # Mental
            recommendations.append("Busque apoio psicológico se necessário")
            recommendations.append("Pratique técnicas de relaxamento")
        elif cid_code.startswith('E'):  # Endócrino
            recommendations.append("Monitore a alimentação")
            recommendations.append("Realize exames laboratoriais")
        
        return recommendations
    
    def generate_medical_report(self, diagnostic_results: List[DiagnosticResult], 
                              original_symptoms: str) -> str:
        """Gera relatório médico baseado nos resultados do diagnóstico."""
        if not diagnostic_results:
            return "Não foi possível identificar um diagnóstico provável baseado nos sintomas relatados."
        
        report = "RELATÓRIO DE ANÁLISE DE SINTOMAS\n"
        report += "=" * 50 + "\n\n"
        
        report += f"SINTOMAS RELATADOS:\n{original_symptoms}\n\n"
        
        report += "DIAGNÓSTICOS PROVÁVEIS:\n\n"
        
        for i, result in enumerate(diagnostic_results[:3], 1):
            report += f"{i}. {result.disease_name} (CID: {result.cid_code})\n"
            report += f"   Probabilidade: {result.probability:.1%}\n"
            report += f"   Confiança: {result.confidence_level.title()}\n"
            report += f"   Sintomas correspondentes: {', '.join(result.matching_symptoms)}\n"
            
            if result.additional_info.get('recommendations'):
                report += f"   Recomendações:\n"
                for rec in result.additional_info['recommendations']:
                    report += f"   - {rec}\n"
            
            report += "\n"
        
        report += "OBSERVAÇÕES IMPORTANTES:\n"
        report += "- Este relatório é baseado em análise automatizada de sintomas\n"
        report += "- Não substitui consulta médica presencial\n"
        report += "- Procure atendimento médico para diagnóstico definitivo\n"
        report += "- Em caso de emergência, procure atendimento imediato\n"
        
        return report
    
    def analyze_medical_report_advanced(self, report: str) -> Dict:
        """Análise avançada de laudo médico com extração de informações estruturadas."""
        analysis = {
            'symptoms_extracted': [],
            'possible_diagnoses': [],
            'severity_assessment': 'não determinada',
            'urgency_level': 'rotina',
            'recommendations': [],
            'follow_up_needed': True
        }
        
        # Extrair sintomas
        symptoms = self._extract_symptoms(report.lower())
        analysis['symptoms_extracted'] = symptoms
        
        # Obter diagnósticos prováveis
        diagnostic_results = self.analyze_symptoms_report(report)
        analysis['possible_diagnoses'] = [
            {
                'cid_code': result.cid_code,
                'disease_name': result.disease_name,
                'probability': result.probability,
                'confidence': result.confidence_level
            }
            for result in diagnostic_results
        ]
        
        # Avaliar gravidade e urgência
        analysis['severity_assessment'] = self._assess_severity(symptoms, diagnostic_results)
        analysis['urgency_level'] = self._assess_urgency(symptoms, diagnostic_results)
        
        # Gerar recomendações
        if diagnostic_results:
            analysis['recommendations'] = diagnostic_results[0].additional_info.get('recommendations', [])
        
        return analysis
    
    def _assess_severity(self, symptoms: List[str], diagnostic_results: List[DiagnosticResult]) -> str:
        """Avalia gravidade baseada nos sintomas e diagnósticos."""
        severe_symptoms = [
            'dor no peito', 'falta de ar', 'convulsões', 'sangue na urina',
            'febre alta', 'perda de consciência'
        ]
        
        severe_count = sum(1 for symptom in symptoms if any(severe in symptom for severe in severe_symptoms))
        
        if severe_count >= 2:
            return 'grave'
        elif severe_count == 1:
            return 'moderada'
        elif diagnostic_results and diagnostic_results[0].probability > 0.7:
            return 'moderada'
        else:
            return 'leve'
    
    def _assess_urgency(self, symptoms: List[str], diagnostic_results: List[DiagnosticResult]) -> str:
        """Avalia urgência do atendimento."""
        emergency_symptoms = [
            'dor no peito', 'falta de ar', 'convulsões', 'perda de consciência',
            'sangramento', 'febre alta'
        ]
        
        emergency_count = sum(1 for symptom in symptoms if any(emergency in symptom for emergency in emergency_symptoms))
        
        if emergency_count >= 2:
            return 'emergência'
        elif emergency_count == 1:
            return 'urgente'
        elif diagnostic_results and diagnostic_results[0].probability > 0.8:
            return 'prioritário'
        else:
            return 'rotina'

