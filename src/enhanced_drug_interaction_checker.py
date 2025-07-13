"""
Sistema aprimorado de verificação de interações medicamentosas.
Inclui informações detalhadas sobre reações adversas e mecanismos de interação.
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

@dataclass
class DrugInteraction:
    drug1: str
    drug2: str
    severity: str  # 'Leve', 'Moderada', 'Grave', 'Contraindicada'
    mechanism: str  # Mecanismo da interação
    clinical_effects: List[str]  # Efeitos clínicos observados
    adverse_reactions: List[str]  # Reações adversas específicas
    management: str  # Como gerenciar a interação
    monitoring: List[str]  # O que monitorar
    alternatives: List[str]  # Medicamentos alternativos
    onset_time: str  # Tempo para início dos efeitos
    evidence_level: str  # Nível de evidência científica

class EnhancedDrugInteractionChecker:
    def __init__(self):
        self.interactions_database = self._load_interactions_database()
        self.drug_aliases = self._load_drug_aliases()
        
    def _load_drug_aliases(self) -> Dict[str, List[str]]:
        """Carrega aliases e nomes comerciais dos medicamentos."""
        return {
            'paracetamol': ['acetaminofeno', 'tylenol', 'parador', 'dôrico', 'febralgin'],
            'dipirona': ['metamizol', 'novalgina', 'anador', 'dorflex', 'buscopan composto'],
            'ibuprofeno': ['advil', 'alivium', 'buscofem', 'ibupril', 'motrin'],
            'aspirina': ['ácido acetilsalicílico', 'aas', 'aspirina', 'somalgin'],
            'amoxicilina': ['amoxil', 'flemoxon', 'hiconcil', 'amoxicilina'],
            'azitromicina': ['zitromax', 'azimix', 'azitromicina'],
            'omeprazol': ['losec', 'peprazol', 'omeprazol'],
            'sinvastatina': ['zocor', 'sinvastatina', 'vaslip'],
            'metformina': ['glifage', 'glucoformin', 'metformina'],
            'losartana': ['cozaar', 'losartec', 'aradois'],
            'enalapril': ['renitec', 'vasopril', 'enalapril'],
            'propranolol': ['inderal', 'propranolol'],
            'varfarina': ['marevan', 'varfarina', 'coumadin'],
            'digoxina': ['digoxina', 'lanoxin'],
            'fenitoína': ['hidantal', 'fenitoína', 'epelin'],
            'carbamazepina': ['tegretol', 'carbamazepina'],
            'lítio': ['carbolitium', 'lítio'],
            'fluoxetina': ['prozac', 'daforin', 'fluoxetina'],
            'sertralina': ['zoloft', 'assert', 'sertralina'],
            'diazepam': ['valium', 'diazepam', 'compaz'],
            'clonazepam': ['rivotril', 'clonazepam'],
            'insulina': ['humulin', 'novolin', 'lantus', 'insulina'],
            'prednisona': ['meticorten', 'prednisona'],
            'levotiroxina': ['puran', 'synthroid', 'levotiroxina']
        }
    
    def _load_interactions_database(self) -> Dict[Tuple[str, str], DrugInteraction]:
        """Carrega base de dados completa de interações medicamentosas."""
        interactions = {}
        
        # Interações Cardiovasculares
        interactions[('varfarina', 'aspirina')] = DrugInteraction(
            drug1='varfarina',
            drug2='aspirina',
            severity='Contraindicada',
            mechanism='Sinergismo anticoagulante - inibição da agregação plaquetária e da coagulação',
            clinical_effects=[
                'Aumento significativo do risco de sangramento',
                'Prolongamento excessivo do tempo de coagulação',
                'Risco de hemorragias graves'
            ],
            adverse_reactions=[
                'Sangramento gastrointestinal',
                'Hematomas espontâneos',
                'Sangramento intracraniano',
                'Epistaxe',
                'Hematúria',
                'Melena'
            ],
            management='Contraindicação absoluta. Se anticoagulação necessária, usar apenas varfarina com monitoramento rigoroso do INR',
            monitoring=['INR diário', 'Hemograma completo', 'Sinais de sangramento'],
            alternatives=['Clopidogrel (com cautela)', 'Anticoagulantes diretos'],
            onset_time='2-7 dias',
            evidence_level='Alto - estudos clínicos controlados'
        )
        
        interactions[('enalapril', 'losartana')] = DrugInteraction(
            drug1='enalapril',
            drug2='losartana',
            severity='Moderada',
            mechanism='Duplo bloqueio do sistema renina-angiotensina-aldosterona',
            clinical_effects=[
                'Hipotensão excessiva',
                'Hipercalemia',
                'Deterioração da função renal'
            ],
            adverse_reactions=[
                'Tontura severa',
                'Síncope',
                'Arritmias por hipercalemia',
                'Insuficiência renal aguda'
            ],
            management='Evitar combinação. Se necessário, iniciar com doses baixas e monitorar rigorosamente',
            monitoring=['Pressão arterial', 'Função renal', 'Potássio sérico'],
            alternatives=['Usar apenas um dos medicamentos', 'Adicionar diurético'],
            onset_time='1-3 dias',
            evidence_level='Moderado - estudos observacionais'
        )
        
        # Interações com Antibióticos
        interactions[('amoxicilina', 'varfarina')] = DrugInteraction(
            drug1='amoxicilina',
            drug2='varfarina',
            severity='Moderada',
            mechanism='Alteração da flora intestinal reduz síntese de vitamina K',
            clinical_effects=[
                'Potencialização do efeito anticoagulante',
                'Aumento do INR'
            ],
            adverse_reactions=[
                'Sangramento aumentado',
                'Equimoses',
                'Sangramento gengival'
            ],
            management='Monitorar INR mais frequentemente durante e após o tratamento antibiótico',
            monitoring=['INR a cada 2-3 dias', 'Sinais de sangramento'],
            alternatives=['Cefalexina', 'Clindamicina'],
            onset_time='3-5 dias',
            evidence_level='Moderado'
        )
        
        interactions[('azitromicina', 'digoxina')] = DrugInteraction(
            drug1='azitromicina',
            drug2='digoxina',
            severity='Grave',
            mechanism='Inibição do metabolismo da digoxina por bactérias intestinais',
            clinical_effects=[
                'Aumento dos níveis séricos de digoxina',
                'Toxicidade digitálica'
            ],
            adverse_reactions=[
                'Náuseas e vômitos',
                'Arritmias cardíacas',
                'Distúrbios visuais (visão amarelada)',
                'Confusão mental',
                'Bradicardia'
            ],
            management='Reduzir dose de digoxina em 50% ou suspender temporariamente',
            monitoring=['Níveis séricos de digoxina', 'ECG', 'Sinais de toxicidade'],
            alternatives=['Claritromicina', 'Doxiciclina'],
            onset_time='2-4 dias',
            evidence_level='Alto'
        )
        
        # Interações com Anti-inflamatórios
        interactions[('ibuprofeno', 'enalapril')] = DrugInteraction(
            drug1='ibuprofeno',
            drug2='enalapril',
            severity='Moderada',
            mechanism='AINEs reduzem síntese de prostaglandinas vasodilatadoras',
            clinical_effects=[
                'Redução do efeito anti-hipertensivo',
                'Deterioração da função renal',
                'Retenção de sódio e água'
            ],
            adverse_reactions=[
                'Aumento da pressão arterial',
                'Edema',
                'Insuficiência renal',
                'Hipercalemia'
            ],
            management='Evitar uso prolongado. Se necessário, monitorar função renal e pressão arterial',
            monitoring=['Pressão arterial', 'Creatinina', 'Potássio', 'Peso corporal'],
            alternatives=['Paracetamol', 'Corticoides tópicos'],
            onset_time='1-2 semanas',
            evidence_level='Alto'
        )
        
        interactions[('aspirina', 'ibuprofeno')] = DrugInteraction(
            drug1='aspirina',
            drug2='ibuprofeno',
            severity='Moderada',
            mechanism='Competição pelo sítio de ligação da COX-1 plaquetária',
            clinical_effects=[
                'Redução do efeito antiagregante da aspirina',
                'Aumento do risco cardiovascular'
            ],
            adverse_reactions=[
                'Perda da proteção cardiovascular',
                'Aumento do risco de infarto',
                'Irritação gastrointestinal'
            ],
            management='Tomar aspirina pelo menos 2 horas antes do ibuprofeno',
            monitoring=['Sinais de eventos cardiovasculares', 'Sintomas gastrointestinais'],
            alternatives=['Paracetamol', 'Celecoxibe'],
            onset_time='Imediato',
            evidence_level='Alto'
        )
        
        # Interações com Antidepressivos
        interactions[('fluoxetina', 'varfarina')] = DrugInteraction(
            drug1='fluoxetina',
            drug2='varfarina',
            severity='Moderada',
            mechanism='Inibição do CYP2C9 e deslocamento da ligação proteica',
            clinical_effects=[
                'Aumento dos níveis de varfarina',
                'Potencialização do efeito anticoagulante'
            ],
            adverse_reactions=[
                'Sangramento aumentado',
                'Hematomas',
                'Sangramento gastrointestinal'
            ],
            management='Monitorar INR mais frequentemente e ajustar dose de varfarina',
            monitoring=['INR semanal', 'Sinais de sangramento'],
            alternatives=['Sertralina', 'Citalopram'],
            onset_time='1-2 semanas',
            evidence_level='Moderado'
        )
        
        interactions[('sertralina', 'tramadol')] = DrugInteraction(
            drug1='sertralina',
            drug2='tramadol',
            severity='Grave',
            mechanism='Aumento do risco de síndrome serotoninérgica',
            clinical_effects=[
                'Excesso de serotonina no SNC',
                'Síndrome serotoninérgica'
            ],
            adverse_reactions=[
                'Agitação e confusão',
                'Tremores e rigidez muscular',
                'Hipertermia',
                'Taquicardia',
                'Diaforese',
                'Convulsões'
            ],
            management='Evitar combinação. Se necessário, usar doses baixas e monitorar rigorosamente',
            monitoring=['Sinais neurológicos', 'Temperatura corporal', 'Frequência cardíaca'],
            alternatives=['Paracetamol', 'Codeína'],
            onset_time='Horas a dias',
            evidence_level='Alto'
        )
        
        # Interações com Diabetes
        interactions[('metformina', 'propranolol')] = DrugInteraction(
            drug1='metformina',
            drug2='propranolol',
            severity='Leve',
            mechanism='Mascaramento dos sintomas de hipoglicemia',
            clinical_effects=[
                'Redução dos sinais autonômicos de hipoglicemia',
                'Dificuldade de reconhecer hipoglicemia'
            ],
            adverse_reactions=[
                'Hipoglicemia não reconhecida',
                'Sudorese como único sintoma',
                'Risco de hipoglicemia grave'
            ],
            management='Educar paciente sobre sintomas atípicos de hipoglicemia',
            monitoring=['Glicemia capilar mais frequente', 'Sintomas neuroglicopênicos'],
            alternatives=['Metoprolol', 'Carvedilol'],
            onset_time='Imediato',
            evidence_level='Moderado'
        )
        
        # Interações com Anticonvulsivantes
        interactions[('fenitoína', 'varfarina')] = DrugInteraction(
            drug1='fenitoína',
            drug2='varfarina',
            severity='Moderada',
            mechanism='Indução enzimática do CYP2C9 e deslocamento proteico',
            clinical_effects=[
                'Efeito bifásico: inicial aumento, depois redução do efeito anticoagulante',
                'Instabilidade do INR'
            ],
            adverse_reactions=[
                'Sangramento inicial',
                'Posterior risco trombótico',
                'Dificuldade de controle do INR'
            ],
            management='Monitorar INR muito frequentemente e ajustar doses conforme necessário',
            monitoring=['INR 2-3x por semana', 'Sinais de sangramento e trombose'],
            alternatives=['Levetiracetam', 'Lamotrigina'],
            onset_time='1-2 semanas',
            evidence_level='Alto'
        )
        
        # Interações com Gastroprotetores
        interactions[('omeprazol', 'clopidogrel')] = DrugInteraction(
            drug1='omeprazol',
            drug2='clopidogrel',
            severity='Moderada',
            mechanism='Inibição do CYP2C19 reduz ativação do clopidogrel',
            clinical_effects=[
                'Redução do efeito antiagregante',
                'Aumento do risco cardiovascular'
            ],
            adverse_reactions=[
                'Perda da proteção antitrombótica',
                'Aumento do risco de infarto',
                'Trombose de stent'
            ],
            management='Preferir pantoprazol ou usar com intervalo de 12 horas',
            monitoring=['Eventos cardiovasculares', 'Função plaquetária se disponível'],
            alternatives=['Pantoprazol', 'Ranitidina'],
            onset_time='3-7 dias',
            evidence_level='Alto'
        )
        
        # Adicionar interações reversas (drug2, drug1)
        reverse_interactions = {}
        for (drug1, drug2), interaction in interactions.items():
            reverse_interactions[(drug2, drug1)] = DrugInteraction(
                drug1=drug2,
                drug2=drug1,
                severity=interaction.severity,
                mechanism=interaction.mechanism,
                clinical_effects=interaction.clinical_effects,
                adverse_reactions=interaction.adverse_reactions,
                management=interaction.management,
                monitoring=interaction.monitoring,
                alternatives=interaction.alternatives,
                onset_time=interaction.onset_time,
                evidence_level=interaction.evidence_level
            )
        
        interactions.update(reverse_interactions)
        return interactions
    
    def normalize_drug_name(self, drug_name: str) -> str:
        """Normaliza nome do medicamento para busca."""
        drug_name = drug_name.lower().strip()
        
        # Remover dosagens e formas farmacêuticas
        drug_name = re.sub(r'\d+\s*mg|\d+\s*g|\d+\s*ml', '', drug_name)
        drug_name = re.sub(r'comprimido|cápsula|solução|xarope|gotas', '', drug_name)
        drug_name = drug_name.strip()
        
        # Buscar nome genérico através dos aliases
        for generic_name, aliases in self.drug_aliases.items():
            if drug_name in aliases or drug_name == generic_name:
                return generic_name
        
        return drug_name
    
    def check_interactions(self, medications: List[str]) -> List[Dict]:
        """Verifica interações entre uma lista de medicamentos."""
        if len(medications) < 2:
            return []
        
        # Normalizar nomes dos medicamentos
        normalized_meds = [self.normalize_drug_name(med) for med in medications]
        
        interactions_found = []
        
        # Verificar todas as combinações possíveis
        for i in range(len(normalized_meds)):
            for j in range(i + 1, len(normalized_meds)):
                drug1 = normalized_meds[i]
                drug2 = normalized_meds[j]
                
                interaction = self.interactions_database.get((drug1, drug2))
                
                if interaction:
                    interactions_found.append({
                        'drug1': medications[i],
                        'drug2': medications[j],
                        'drug1_generic': drug1,
                        'drug2_generic': drug2,
                        'severity': interaction.severity,
                        'mechanism': interaction.mechanism,
                        'clinical_effects': interaction.clinical_effects,
                        'adverse_reactions': interaction.adverse_reactions,
                        'management': interaction.management,
                        'monitoring': interaction.monitoring,
                        'alternatives': interaction.alternatives,
                        'onset_time': interaction.onset_time,
                        'evidence_level': interaction.evidence_level,
                        'risk_level': self._calculate_risk_level(interaction)
                    })
        
        # Ordenar por gravidade
        severity_order = {'Contraindicada': 4, 'Grave': 3, 'Moderada': 2, 'Leve': 1}
        interactions_found.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
        
        return interactions_found
    
    def _calculate_risk_level(self, interaction: DrugInteraction) -> str:
        """Calcula nível de risco baseado na gravidade e evidência."""
        severity_score = {
            'Contraindicada': 4,
            'Grave': 3,
            'Moderada': 2,
            'Leve': 1
        }.get(interaction.severity, 0)
        
        evidence_score = {
            'Alto': 3,
            'Moderado': 2,
            'Baixo': 1
        }.get(interaction.evidence_level.split(' - ')[0], 1)
        
        total_score = severity_score * evidence_score
        
        if total_score >= 9:
            return 'Muito Alto'
        elif total_score >= 6:
            return 'Alto'
        elif total_score >= 3:
            return 'Moderado'
        else:
            return 'Baixo'
    
    def get_interaction_summary(self, medications: List[str]) -> Dict:
        """Retorna resumo completo das interações encontradas."""
        interactions = self.check_interactions(medications)
        
        summary = {
            'total_medications': len(medications),
            'total_interactions': len(interactions),
            'severity_breakdown': {
                'Contraindicada': 0,
                'Grave': 0,
                'Moderada': 0,
                'Leve': 0
            },
            'highest_severity': 'Nenhuma',
            'requires_immediate_attention': False,
            'interactions': interactions,
            'general_recommendations': []
        }
        
        if interactions:
            # Contar por gravidade
            for interaction in interactions:
                severity = interaction['severity']
                summary['severity_breakdown'][severity] += 1
            
            # Determinar maior gravidade
            for severity in ['Contraindicada', 'Grave', 'Moderada', 'Leve']:
                if summary['severity_breakdown'][severity] > 0:
                    summary['highest_severity'] = severity
                    break
            
            # Verificar se requer atenção imediata
            summary['requires_immediate_attention'] = any(
                interaction['severity'] in ['Contraindicada', 'Grave'] 
                for interaction in interactions
            )
            
            # Gerar recomendações gerais
            summary['general_recommendations'] = self._generate_general_recommendations(interactions)
        
        return summary
    
    def _generate_general_recommendations(self, interactions: List[Dict]) -> List[str]:
        """Gera recomendações gerais baseadas nas interações encontradas."""
        recommendations = []
        
        has_contraindicated = any(i['severity'] == 'Contraindicada' for i in interactions)
        has_severe = any(i['severity'] == 'Grave' for i in interactions)
        has_moderate = any(i['severity'] == 'Moderada' for i in interactions)
        
        if has_contraindicated:
            recommendations.append("⚠️ ATENÇÃO: Foram encontradas interações CONTRAINDICADAS. Contate imediatamente seu médico.")
            recommendations.append("Não tome estes medicamentos juntos sem orientação médica urgente.")
        
        if has_severe:
            recommendations.append("🔴 Interações GRAVES detectadas. Consulte seu médico antes de continuar o tratamento.")
            recommendations.append("Pode ser necessário ajustar doses ou substituir medicamentos.")
        
        if has_moderate:
            recommendations.append("🟡 Interações MODERADAS encontradas. Monitoramento médico é recomendado.")
            recommendations.append("Informe seu médico sobre todos os medicamentos que você está tomando.")
        
        # Recomendações gerais
        recommendations.extend([
            "📋 Mantenha uma lista atualizada de todos os seus medicamentos.",
            "💊 Sempre informe médicos e farmacêuticos sobre todos os medicamentos em uso.",
            "⏰ Respeite horários e doses prescritas.",
            "🚫 Nunca pare ou altere medicamentos sem orientação médica."
        ])
        
        return recommendations
    
    def search_drug_alternatives(self, drug_name: str, indication: str = "") -> List[str]:
        """Busca alternativas medicamentosas para evitar interações."""
        normalized_drug = self.normalize_drug_name(drug_name)
        
        # Base de dados simplificada de alternativas
        alternatives_db = {
            'aspirina': ['clopidogrel', 'ticagrelor', 'prasugrel'],
            'varfarina': ['rivaroxabana', 'apixabana', 'dabigatrana'],
            'omeprazol': ['pantoprazol', 'lansoprazol', 'ranitidina'],
            'ibuprofeno': ['paracetamol', 'celecoxibe', 'naproxeno'],
            'fluoxetina': ['sertralina', 'citalopram', 'escitalopram'],
            'propranolol': ['metoprolol', 'atenolol', 'carvedilol'],
            'fenitoína': ['levetiracetam', 'lamotrigina', 'carbamazepina']
        }
        
        return alternatives_db.get(normalized_drug, [])
    
    def generate_interaction_report(self, medications: List[str]) -> str:
        """Gera relatório detalhado de interações medicamentosas."""
        summary = self.get_interaction_summary(medications)
        
        report = "RELATÓRIO DE INTERAÇÕES MEDICAMENTOSAS\n"
        report += "=" * 50 + "\n\n"
        
        report += f"MEDICAMENTOS ANALISADOS ({summary['total_medications']}):\n"
        for i, med in enumerate(medications, 1):
            report += f"{i}. {med}\n"
        report += "\n"
        
        report += f"TOTAL DE INTERAÇÕES ENCONTRADAS: {summary['total_interactions']}\n\n"
        
        if summary['total_interactions'] > 0:
            report += "RESUMO POR GRAVIDADE:\n"
            for severity, count in summary['severity_breakdown'].items():
                if count > 0:
                    report += f"- {severity}: {count} interação(ões)\n"
            report += "\n"
            
            report += "DETALHES DAS INTERAÇÕES:\n\n"
            for i, interaction in enumerate(summary['interactions'], 1):
                report += f"{i}. {interaction['drug1']} + {interaction['drug2']}\n"
                report += f"   Gravidade: {interaction['severity']}\n"
                report += f"   Mecanismo: {interaction['mechanism']}\n"
                report += f"   Efeitos Clínicos:\n"
                for effect in interaction['clinical_effects']:
                    report += f"   - {effect}\n"
                report += f"   Reações Adversas Possíveis:\n"
                for reaction in interaction['adverse_reactions']:
                    report += f"   - {reaction}\n"
                report += f"   Conduta: {interaction['management']}\n"
                report += f"   Monitoramento: {', '.join(interaction['monitoring'])}\n"
                report += f"   Tempo de Início: {interaction['onset_time']}\n"
                report += f"   Nível de Evidência: {interaction['evidence_level']}\n\n"
            
            report += "RECOMENDAÇÕES GERAIS:\n"
            for rec in summary['general_recommendations']:
                report += f"- {rec}\n"
        else:
            report += "✅ Nenhuma interação medicamentosa conhecida foi encontrada.\n"
            report += "Continue seguindo as orientações médicas e farmacêuticas.\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += "IMPORTANTE: Este relatório é baseado em dados científicos disponíveis.\n"
        report += "Sempre consulte seu médico ou farmacêutico para orientações personalizadas.\n"
        
        return report

