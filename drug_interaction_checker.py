class DrugInteractionChecker:
    def __init__(self):
        # Dados de exemplo para interações medicamentosas
        self.interactions_data = {
            ("dipirona", "paracetamol"): {
                "severity": "Leve",
                "description": "Aumento do risco de toxicidade hepática com uso prolongado e doses elevadas.",
                "recommendation": "Evitar o uso concomitante. Se necessário, monitorar a função hepática."
            },
            ("amoxicilina", "metotrexato"): {
                "severity": "Moderada",
                "description": "Amoxicilina pode diminuir a excreção renal de metotrexato, aumentando sua toxicidade.",
                "recommendation": "Monitorar níveis de metotrexato e toxicidade. Ajustar dose se necessário."
            },
            ("varfarina", "aspirina"): {
                "severity": "Grave",
                "description": "Aumento significativo do risco de sangramento.",
                "recommendation": "Contraindicado. Se o uso for inevitável, monitorar rigorosamente o INR e sinais de sangramento."
            },
            ("insulina", "betabloqueador"): {
                "severity": "Moderada",
                "description": "Betabloqueadores podem mascarar sintomas de hipoglicemia (tremores, taquicardia).",
                "recommendation": "Monitorar glicemia mais frequentemente. Educar o paciente sobre sintomas atípicos de hipoglicemia."
            }
        }

    def get_interaction_summary(self, medications):
        medications_lower = sorted([m.lower() for m in medications])
        
        # Verifica se há uma interação direta para o par exato
        if tuple(medications_lower) in self.interactions_data:
            interaction = self.interactions_data[tuple(medications_lower)]
            return [{
                "medication1": medications[0],
                "medication2": medications[1],
                "severity": interaction["severity"],
                "description": interaction["description"],
                "recommendation": interaction["recommendation"]
            }]
        
        # Se não houver interação direta, retorna uma mensagem genérica
        return [{
            "medication1": medications[0],
            "medication2": medications[1],
            "severity": "Nenhuma",
            "description": "Não foram encontradas interações medicamentosas conhecidas para este par. Sempre consulte um profissional de saúde.",
            "recommendation": "Continue monitorando e informe seu médico sobre todos os medicamentos que você usa."
        }]


