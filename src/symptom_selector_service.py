"""
Serviço para seleção objetiva de sintomas com opções pré-definidas.
"""

class SymptomSelectorService:
    def __init__(self):
        self.symptom_categories = self._load_symptom_categories()
    
    def _load_symptom_categories(self):
        """Carrega categorias de sintomas organizadas por sistema"""
        return {
            "Sintomas Gerais": [
                "Febre", "Fadiga", "Perda de peso", "Ganho de peso", 
                "Sudorese", "Calafrios", "Mal-estar geral", "Fraqueza"
            ],
            "Sistema Cardiovascular": [
                "Dor no peito", "Palpitações", "Falta de ar", "Inchaço nas pernas",
                "Tontura", "Desmaio", "Pressão alta", "Pressão baixa"
            ],
            "Sistema Respiratório": [
                "Tosse seca", "Tosse com catarro", "Falta de ar", "Chiado no peito",
                "Dor ao respirar", "Respiração rápida", "Congestão nasal", "Espirros"
            ],
            "Sistema Digestivo": [
                "Dor abdominal", "Náuseas", "Vômitos", "Diarreia", "Constipação",
                "Azia", "Queimação no estômago", "Perda de apetite", "Inchaço abdominal"
            ],
            "Sistema Urinário": [
                "Dor ao urinar", "Urgência urinária", "Micção frequente", "Sangue na urina",
                "Urina turva", "Dor lombar", "Incontinência urinária", "Retenção urinária"
            ],
            "Sistema Neurológico": [
                "Dor de cabeça", "Tontura", "Confusão mental", "Perda de memória",
                "Convulsões", "Tremores", "Formigamento", "Perda de coordenação"
            ],
            "Sistema Musculoesquelético": [
                "Dor nas articulações", "Dor muscular", "Rigidez matinal", "Inchaço articular",
                "Limitação de movimento", "Dor nas costas", "Dor no pescoço", "Cãibras"
            ],
            "Pele e Anexos": [
                "Erupção cutânea", "Coceira", "Vermelhidão", "Descamação",
                "Feridas que não cicatrizam", "Mudança na cor da pele", "Queda de cabelo", "Unhas frágeis"
            ],
            "Sistema Endócrino": [
                "Sede excessiva", "Fome excessiva", "Micção excessiva", "Intolerância ao calor",
                "Intolerância ao frio", "Alterações menstruais", "Crescimento anormal", "Mudanças de humor"
            ],
            "Saúde Mental": [
                "Tristeza persistente", "Ansiedade", "Irritabilidade", "Perda de interesse",
                "Alterações do sono", "Pensamentos negativos", "Dificuldade de concentração", "Isolamento social"
            ]
        }
    
    def get_all_symptom_categories(self):
        """Retorna todas as categorias de sintomas"""
        return self.symptom_categories
    
    def get_symptoms_by_category(self, category):
        """Retorna sintomas de uma categoria específica"""
        return self.symptom_categories.get(category, [])
    
    def search_symptoms(self, query):
        """Busca sintomas que contenham o termo pesquisado"""
        results = []
        query_lower = query.lower()
        
        for category, symptoms in self.symptom_categories.items():
            matching_symptoms = [s for s in symptoms if query_lower in s.lower()]
            if matching_symptoms:
                results.append({
                    'category': category,
                    'symptoms': matching_symptoms
                })
        
        return results
    
    def get_related_symptoms(self, selected_symptoms):
        """Sugere sintomas relacionados baseados nos já selecionados"""
        # Mapeamento de sintomas relacionados
        related_map = {
            "Febre": ["Calafrios", "Sudorese", "Mal-estar geral"],
            "Dor ao urinar": ["Urgência urinária", "Micção frequente", "Urina turva"],
            "Tosse": ["Falta de ar", "Dor no peito", "Catarro"],
            "Dor de cabeça": ["Tontura", "Náuseas", "Sensibilidade à luz"],
            "Dor abdominal": ["Náuseas", "Vômitos", "Perda de apetite"],
            "Fadiga": ["Fraqueza", "Sonolência", "Dificuldade de concentração"]
        }
        
        suggestions = set()
        for symptom in selected_symptoms:
            if symptom in related_map:
                suggestions.update(related_map[symptom])
        
        # Remove sintomas já selecionados
        suggestions = suggestions - set(selected_symptoms)
        
        return list(suggestions)
    
    def validate_symptom_combination(self, symptoms):
        """Valida se a combinação de sintomas faz sentido clinicamente"""
        # Combinações que podem indicar condições específicas
        combinations = {
            "Infecção Urinária": ["Dor ao urinar", "Urgência urinária", "Micção frequente"],
            "Gripe/Resfriado": ["Febre", "Tosse", "Congestão nasal", "Mal-estar geral"],
            "Diabetes": ["Sede excessiva", "Micção excessiva", "Fome excessiva", "Perda de peso"],
            "Hipertensão": ["Dor de cabeça", "Tontura", "Palpitações"],
            "Depressão": ["Tristeza persistente", "Perda de interesse", "Fadiga", "Alterações do sono"]
        }
        
        matches = []
        for condition, required_symptoms in combinations.items():
            matching_count = sum(1 for s in required_symptoms if s in symptoms)
            if matching_count >= 2:  # Pelo menos 2 sintomas da condição
                matches.append({
                    'condition': condition,
                    'matching_symptoms': matching_count,
                    'total_symptoms': len(required_symptoms),
                    'confidence': (matching_count / len(required_symptoms)) * 100
                })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)

