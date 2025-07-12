"""
Serviço para fornecer detalhes completos das doenças incluindo gravidade, tratamento e medicamentos.
"""
import json
import os

class DiseaseDetailsService:
    def __init__(self):
        self.disease_details = self._load_disease_details()
    
    def _load_disease_details(self):
        """Carrega base de dados com detalhes das doenças"""
        return {
            # Diabetes
            "E10": {
                "name": "Diabetes mellitus insulino-dependente",
                "severity": "Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso",
                "medications": ["Insulina", "Metformina"],
                "non_medication_treatment": ["Dieta controlada", "Exercícios físicos", "Monitoramento glicêmico"],
                "symptoms": ["polidipsia", "poliúria", "perda de peso", "fadiga"],
                "complications": ["Cetoacidose diabética", "Neuropatia", "Retinopatia", "Nefropatia"],
                "prognosis": "Controlável com tratamento adequado"
            },
            "E11": {
                "name": "Diabetes mellitus não-insulino-dependente",
                "severity": "Moderada a Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso e não medicamentoso",
                "medications": ["Metformina", "Glibenclamida", "Insulina (casos avançados)"],
                "non_medication_treatment": ["Dieta", "Exercícios", "Controle de peso"],
                "symptoms": ["sede excessiva", "micção frequente", "fadiga", "visão turva"],
                "complications": ["Complicações cardiovasculares", "Neuropatia", "Problemas renais"],
                "prognosis": "Bom com controle adequado"
            },
            
            # Hipertensão
            "I10": {
                "name": "Hipertensão essencial",
                "severity": "Moderada a Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso e não medicamentoso",
                "medications": ["Enalapril", "Losartana", "Hidroclorotiazida", "Amlodipina"],
                "non_medication_treatment": ["Dieta hipossódica", "Exercícios", "Redução do estresse"],
                "symptoms": ["dor de cabeça", "tontura", "palpitações"],
                "complications": ["AVC", "Infarto", "Insuficiência renal", "Problemas cardíacos"],
                "prognosis": "Controlável com tratamento contínuo"
            },
            
            # Infecções urinárias
            "N30": {
                "name": "Cistite",
                "severity": "Leve a Moderada",
                "has_treatment": True,
                "treatment_type": "Medicamentoso",
                "medications": ["Nitrofurantoína", "Sulfametoxazol + Trimetoprima", "Ciprofloxacino"],
                "non_medication_treatment": ["Hidratação abundante", "Higiene adequada"],
                "symptoms": ["disúria", "urgência urinária", "polaciúria", "dor suprapúbica"],
                "complications": ["Pielonefrite", "Infecção recorrente"],
                "prognosis": "Excelente com tratamento adequado"
            },
            
            # Pneumonia
            "J18": {
                "name": "Pneumonia não especificada",
                "severity": "Moderada a Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso",
                "medications": ["Amoxicilina", "Azitromicina", "Ceftriaxona"],
                "non_medication_treatment": ["Repouso", "Hidratação", "Fisioterapia respiratória"],
                "symptoms": ["tosse", "febre", "dispneia", "dor torácica"],
                "complications": ["Insuficiência respiratória", "Sepse", "Derrame pleural"],
                "prognosis": "Bom com tratamento precoce"
            },
            
            # Depressão
            "F32": {
                "name": "Episódios depressivos",
                "severity": "Leve a Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso e não medicamentoso",
                "medications": ["Fluoxetina", "Sertralina", "Escitalopram", "Amitriptilina"],
                "non_medication_treatment": ["Psicoterapia", "Terapia cognitivo-comportamental", "Exercícios"],
                "symptoms": ["tristeza", "anedonia", "fadiga", "alterações do sono"],
                "complications": ["Ideação suicida", "Isolamento social", "Prejuízo funcional"],
                "prognosis": "Bom com tratamento adequado"
            },
            
            # Gastrite
            "K29": {
                "name": "Gastrite e duodenite",
                "severity": "Leve a Moderada",
                "has_treatment": True,
                "treatment_type": "Medicamentoso e não medicamentoso",
                "medications": ["Omeprazol", "Ranitidina", "Sucralfato"],
                "non_medication_treatment": ["Dieta adequada", "Evitar irritantes", "Controle do estresse"],
                "symptoms": ["dor epigástrica", "náuseas", "vômitos", "queimação"],
                "complications": ["Úlcera péptica", "Sangramento", "Perfuração"],
                "prognosis": "Excelente com mudanças no estilo de vida"
            },
            
            # Asma
            "J45": {
                "name": "Asma",
                "severity": "Leve a Grave",
                "has_treatment": True,
                "treatment_type": "Medicamentoso",
                "medications": ["Salbutamol", "Budesonida", "Formoterol", "Prednisolona"],
                "non_medication_treatment": ["Evitar alérgenos", "Exercícios respiratórios"],
                "symptoms": ["dispneia", "sibilos", "tosse", "opressão torácica"],
                "complications": ["Status asmático", "Insuficiência respiratória"],
                "prognosis": "Controlável com tratamento adequado"
            }
        }
    
    def get_disease_details(self, cid_code):
        """Retorna detalhes completos de uma doença pelo código CID"""
        return self.disease_details.get(cid_code.upper(), None)
    
    def get_all_diseases_with_details(self):
        """Retorna todas as doenças com detalhes"""
        return self.disease_details
    
    def search_diseases_by_symptom(self, symptom):
        """Busca doenças que apresentam um sintoma específico"""
        results = []
        symptom_lower = symptom.lower()
        
        for cid, details in self.disease_details.items():
            if any(symptom_lower in s.lower() for s in details.get('symptoms', [])):
                results.append({
                    'cid': cid,
                    'name': details['name'],
                    'severity': details['severity'],
                    'matching_symptoms': [s for s in details['symptoms'] if symptom_lower in s.lower()]
                })
        
        return results
    
    def get_diseases_by_severity(self, severity):
        """Retorna doenças filtradas por gravidade"""
        results = []
        
        for cid, details in self.disease_details.items():
            if severity.lower() in details['severity'].lower():
                results.append({
                    'cid': cid,
                    'name': details['name'],
                    'severity': details['severity'],
                    'has_treatment': details['has_treatment']
                })
        
        return results
    
    def get_treatment_info(self, cid_code):
        """Retorna informações específicas de tratamento"""
        details = self.get_disease_details(cid_code)
        if not details:
            return None
        
        return {
            'has_treatment': details['has_treatment'],
            'treatment_type': details['treatment_type'],
            'medications': details.get('medications', []),
            'non_medication_treatment': details.get('non_medication_treatment', []),
            'prognosis': details.get('prognosis', 'Não especificado')
        }

