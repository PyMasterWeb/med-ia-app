"""
Serviço para categorização e busca aprimorada de códigos CID-10.
"""
import json
import os
from typing import List, Dict, Optional
import re

class CIDCategorizer:
    def __init__(self):
        self.cid10_data = []
        self.categories = {}
        self.load_cid_data()
        self.setup_categories()
    
    def load_cid_data(self):
        """Carrega dados do CID-10 do arquivo JSON."""
        cid10_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cid10_datasus.json')
        if os.path.exists(cid10_path):
            with open(cid10_path, 'r', encoding='utf-8') as f:
                self.cid10_data = json.load(f)
        else:
            # Dados de exemplo se não existir o arquivo
            self.cid10_data = [
                {"code": "A01.0", "description": "Febre tifóide"},
                {"code": "A01.1", "description": "Febre paratifóide A"},
                {"code": "I10", "description": "Hipertensão essencial"},
                {"code": "E11", "description": "Diabetes mellitus não-insulino-dependente"},
                {"code": "F32", "description": "Episódios depressivos"},
                {"code": "G40", "description": "Epilepsia"},
                {"code": "J44", "description": "Outras doenças pulmonares obstrutivas crônicas"},
                {"code": "K29", "description": "Gastrite e duodenite"},
                {"code": "N18", "description": "Doença renal crônica"},
                {"code": "R50", "description": "Febre não especificada"}
            ]
    
    def setup_categories(self):
        """Configura as categorias do CID-10."""
        self.categories = {
            'A': {
                'letter': 'A',
                'title': 'Doenças infecciosas e parasitárias (A00-A99)',
                'description': 'Inclui doenças causadas por vírus, bactérias, fungos e parasitas',
                'subcategories': {
                    'A00-A09': 'Doenças infecciosas intestinais',
                    'A15-A19': 'Tuberculose',
                    'A20-A28': 'Certas zoonoses bacterianas',
                    'A30-A49': 'Outras doenças bacterianas',
                    'A50-A64': 'Infecções com modo de transmissão predominantemente sexual',
                    'A65-A69': 'Outras doenças por espiroquetas',
                    'A70-A74': 'Outras doenças causadas por clamídias',
                    'A75-A79': 'Rickettsioses',
                    'A80-A89': 'Infecções virais do sistema nervoso central',
                    'A90-A99': 'Febres por arbovírus e febres hemorrágicas virais'
                }
            },
            'B': {
                'letter': 'B',
                'title': 'Doenças infecciosas e parasitárias (B00-B99)',
                'description': 'Continuação das doenças infecciosas e parasitárias',
                'subcategories': {
                    'B00-B09': 'Infecções virais caracterizadas por lesões de pele e mucosas',
                    'B15-B19': 'Hepatite viral',
                    'B20-B24': 'Doença pelo vírus da imunodeficiência humana [HIV]',
                    'B25-B34': 'Outras doenças por vírus',
                    'B35-B49': 'Micoses',
                    'B50-B64': 'Doenças devidas a protozoários',
                    'B65-B83': 'Helmintíases',
                    'B85-B89': 'Pediculose, acaríase e outras infestações',
                    'B90-B94': 'Sequelas de doenças infecciosas e parasitárias',
                    'B95-B97': 'Agentes de doenças bacterianas, virais e outros agentes infecciosos',
                    'B99': 'Outras doenças infecciosas'
                }
            },
            'C': {
                'letter': 'C',
                'title': 'Neoplasias (C00-C97)',
                'description': 'Tumores malignos, benignos e de comportamento incerto',
                'subcategories': {
                    'C00-C14': 'Neoplasias malignas do lábio, cavidade oral e faringe',
                    'C15-C26': 'Neoplasias malignas dos órgãos digestivos',
                    'C30-C39': 'Neoplasias malignas dos órgãos respiratórios e intratorácicos',
                    'C40-C41': 'Neoplasias malignas dos ossos e cartilagens articulares',
                    'C43-C44': 'Melanoma e outras neoplasias malignas da pele',
                    'C45-C49': 'Neoplasias malignas do tecido mesotelial e tecidos moles',
                    'C50': 'Neoplasia maligna da mama',
                    'C51-C58': 'Neoplasias malignas dos órgãos genitais femininos',
                    'C60-C63': 'Neoplasias malignas dos órgãos genitais masculinos',
                    'C64-C68': 'Neoplasias malignas do trato urinário',
                    'C69-C72': 'Neoplasias malignas do olho, encéfalo e outras partes do SNC',
                    'C73-C75': 'Neoplasias malignas da tireóide e outras glândulas endócrinas',
                    'C76-C80': 'Neoplasias malignas de localização mal definida',
                    'C81-C96': 'Neoplasias malignas do tecido linfático, hematopoético e tecidos correlatos',
                    'C97': 'Neoplasias malignas de localizações múltiplas independentes'
                }
            },
            'D': {
                'letter': 'D',
                'title': 'Doenças do sangue e dos órgãos hematopoéticos (D50-D89)',
                'description': 'Anemias, distúrbios da coagulação e outros distúrbios do sangue',
                'subcategories': {
                    'D50-D53': 'Anemias nutricionais',
                    'D55-D59': 'Anemias hemolíticas',
                    'D60-D64': 'Anemia aplástica e outras anemias',
                    'D65-D69': 'Defeitos da coagulação, púrpura e outras afecções hemorrágicas',
                    'D70-D77': 'Outras doenças do sangue e dos órgãos hematopoéticos',
                    'D80-D89': 'Alguns transtornos que comprometem o mecanismo imunitário'
                }
            },
            'E': {
                'letter': 'E',
                'title': 'Doenças endócrinas, nutricionais e metabólicas (E00-E90)',
                'description': 'Diabetes, distúrbios da tireóide, obesidade e outras doenças metabólicas',
                'subcategories': {
                    'E00-E07': 'Transtornos da glândula tireóide',
                    'E10-E14': 'Diabetes mellitus',
                    'E15-E16': 'Outros transtornos da regulação da glicose',
                    'E20-E35': 'Transtornos de outras glândulas endócrinas',
                    'E40-E46': 'Desnutrição',
                    'E50-E64': 'Outras deficiências nutricionais',
                    'E65-E68': 'Obesidade e outras formas de hiperalimentação',
                    'E70-E90': 'Distúrbios metabólicos'
                }
            },
            'F': {
                'letter': 'F',
                'title': 'Transtornos mentais e comportamentais (F00-F99)',
                'description': 'Depressão, ansiedade, esquizofrenia e outros transtornos psiquiátricos',
                'subcategories': {
                    'F00-F09': 'Transtornos mentais orgânicos',
                    'F10-F19': 'Transtornos mentais devido ao uso de substâncias psicoativas',
                    'F20-F29': 'Esquizofrenia, transtornos esquizotípicos e delirantes',
                    'F30-F39': 'Transtornos do humor [afetivos]',
                    'F40-F48': 'Transtornos neuróticos, relacionados ao estresse e somatoformes',
                    'F50-F59': 'Síndromes comportamentais associadas a perturbações fisiológicas',
                    'F60-F69': 'Transtornos da personalidade e do comportamento adulto',
                    'F70-F79': 'Retardo mental',
                    'F80-F89': 'Transtornos do desenvolvimento psicológico',
                    'F90-F98': 'Transtornos comportamentais e emocionais que aparecem na infância',
                    'F99': 'Transtorno mental não especificado'
                }
            },
            'G': {
                'letter': 'G',
                'title': 'Doenças do sistema nervoso (G00-G99)',
                'description': 'Epilepsia, Parkinson, Alzheimer e outras doenças neurológicas',
                'subcategories': {
                    'G00-G09': 'Doenças inflamatórias do sistema nervoso central',
                    'G10-G14': 'Atrofias sistêmicas que afetam principalmente o SNC',
                    'G20-G26': 'Doenças extrapiramidais e transtornos do movimento',
                    'G30-G32': 'Outras doenças degenerativas do sistema nervoso',
                    'G35-G37': 'Doenças desmielinizantes do sistema nervoso central',
                    'G40-G47': 'Transtornos episódicos e paroxísticos',
                    'G50-G59': 'Transtornos dos nervos, das raízes e dos plexos nervosos',
                    'G60-G64': 'Polineuropatias e outros transtornos do sistema nervoso periférico',
                    'G70-G73': 'Doenças da junção mioneural e dos músculos',
                    'G80-G83': 'Paralisia cerebral e outras síndromes paralíticas',
                    'G90-G99': 'Outros transtornos do sistema nervoso'
                }
            },
            'H': {
                'letter': 'H',
                'title': 'Doenças do olho e anexos / Doenças do ouvido (H00-H95)',
                'description': 'Problemas de visão, audição e estruturas relacionadas',
                'subcategories': {
                    'H00-H06': 'Transtornos da pálpebra, do aparelho lacrimal e da órbita',
                    'H10-H13': 'Transtornos da conjuntiva',
                    'H15-H22': 'Transtornos da esclerótica, da córnea, da íris e do corpo ciliar',
                    'H25-H28': 'Transtornos do cristalino',
                    'H30-H36': 'Transtornos da coróide e da retina',
                    'H40-H42': 'Glaucoma',
                    'H43-H45': 'Transtornos do corpo vítreo e do globo ocular',
                    'H46-H48': 'Transtornos do nervo óptico e das vias ópticas',
                    'H49-H52': 'Transtornos dos músculos oculares',
                    'H53-H54': 'Transtornos visuais e cegueira',
                    'H55-H59': 'Outros transtornos do olho e anexos',
                    'H60-H62': 'Doenças do ouvido externo',
                    'H65-H75': 'Doenças do ouvido médio e da mastóide',
                    'H80-H83': 'Doenças do ouvido interno',
                    'H90-H95': 'Outros transtornos do ouvido'
                }
            },
            'I': {
                'letter': 'I',
                'title': 'Doenças do aparelho circulatório (I00-I99)',
                'description': 'Hipertensão, infarto, AVC e outras doenças cardiovasculares',
                'subcategories': {
                    'I00-I02': 'Febre reumática aguda',
                    'I05-I09': 'Doenças reumáticas crônicas do coração',
                    'I10-I15': 'Doenças hipertensivas',
                    'I20-I25': 'Doenças isquêmicas do coração',
                    'I26-I28': 'Doença cardiopulmonar e doenças da circulação pulmonar',
                    'I30-I52': 'Outras formas de doença do coração',
                    'I60-I69': 'Doenças cerebrovasculares',
                    'I70-I79': 'Doenças das artérias, das arteríolas e dos capilares',
                    'I80-I89': 'Doenças das veias, dos vasos linfáticos',
                    'I95-I99': 'Outros transtornos do aparelho circulatório'
                }
            },
            'J': {
                'letter': 'J',
                'title': 'Doenças do aparelho respiratório (J00-J99)',
                'description': 'Pneumonia, asma, DPOC e outras doenças respiratórias',
                'subcategories': {
                    'J00-J06': 'Infecções agudas das vias aéreas superiores',
                    'J09-J18': 'Influenza [gripe] e pneumonia',
                    'J20-J22': 'Outras infecções agudas das vias aéreas inferiores',
                    'J30-J39': 'Outras doenças das vias aéreas superiores',
                    'J40-J47': 'Doenças crônicas das vias aéreas inferiores',
                    'J60-J70': 'Doenças pulmonares devidas a agentes externos',
                    'J80-J84': 'Outras doenças respiratórias que afetam principalmente o interstício',
                    'J85-J86': 'Afecções necróticas e supurativas das vias aéreas inferiores',
                    'J90-J94': 'Outras doenças da pleura',
                    'J95-J99': 'Outras doenças do aparelho respiratório'
                }
            },
            'K': {
                'letter': 'K',
                'title': 'Doenças do aparelho digestivo (K00-K93)',
                'description': 'Gastrite, úlceras, hepatite e outras doenças digestivas',
                'subcategories': {
                    'K00-K14': 'Doenças da cavidade oral, das glândulas salivares e dos maxilares',
                    'K20-K31': 'Doenças do esôfago, do estômago e do duodeno',
                    'K35-K37': 'Doenças do apêndice',
                    'K40-K46': 'Hérnias',
                    'K50-K52': 'Enterites e colites não-infecciosas',
                    'K55-K63': 'Outras doenças dos intestinos',
                    'K65-K67': 'Doenças do peritônio',
                    'K70-K77': 'Doenças do fígado',
                    'K80-K87': 'Transtornos da vesícula biliar, das vias biliares e do pâncreas',
                    'K90-K93': 'Outras doenças do aparelho digestivo'
                }
            },
            'L': {
                'letter': 'L',
                'title': 'Doenças da pele e do tecido subcutâneo (L00-L99)',
                'description': 'Dermatites, eczemas, psoríase e outras doenças da pele',
                'subcategories': {
                    'L00-L08': 'Infecções da pele e do tecido subcutâneo',
                    'L10-L14': 'Afecções bolhosas',
                    'L20-L30': 'Dermatite e eczema',
                    'L40-L45': 'Afecções papuloescamosas',
                    'L50-L54': 'Urticária e eritema',
                    'L55-L59': 'Afecções da pele e do tecido subcutâneo relacionadas com a radiação',
                    'L60-L75': 'Afecções dos anexos da pele',
                    'L80-L99': 'Outras afecções da pele e do tecido subcutâneo'
                }
            },
            'M': {
                'letter': 'M',
                'title': 'Doenças do sistema osteomuscular (M00-M99)',
                'description': 'Artrite, artrose, osteoporose e outras doenças dos ossos e músculos',
                'subcategories': {
                    'M00-M25': 'Artropatias',
                    'M30-M36': 'Transtornos sistêmicos do tecido conjuntivo',
                    'M40-M54': 'Dorsopatias',
                    'M60-M79': 'Transtornos dos tecidos moles',
                    'M80-M94': 'Osteopatias e condropatias',
                    'M95-M99': 'Outros transtornos do sistema osteomuscular'
                }
            },
            'N': {
                'letter': 'N',
                'title': 'Doenças do aparelho geniturinário (N00-N99)',
                'description': 'Infecções urinárias, doenças renais e problemas genitais',
                'subcategories': {
                    'N00-N08': 'Doenças glomerulares',
                    'N10-N16': 'Doenças renais túbulo-intersticiais',
                    'N17-N19': 'Insuficiência renal',
                    'N20-N23': 'Urolitíase',
                    'N25-N29': 'Outros transtornos do rim e do ureter',
                    'N30-N39': 'Outras doenças do aparelho urinário',
                    'N40-N51': 'Doenças dos órgãos genitais masculinos',
                    'N60-N64': 'Transtornos da mama',
                    'N70-N77': 'Doenças inflamatórias dos órgãos pélvicos femininos',
                    'N80-N98': 'Transtornos não-inflamatórios do trato genital feminino',
                    'N99': 'Outros transtornos do aparelho geniturinário'
                }
            },
            'O': {
                'letter': 'O',
                'title': 'Gravidez, parto e puerpério (O00-O99)',
                'description': 'Complicações da gravidez, parto e período pós-parto',
                'subcategories': {
                    'O00-O08': 'Gravidez que termina em aborto',
                    'O10-O16': 'Transtornos hipertensivos na gravidez, parto e puerpério',
                    'O20-O29': 'Outros transtornos maternos relacionados principalmente à gravidez',
                    'O30-O48': 'Assistência prestada à mãe por motivos ligados ao feto',
                    'O60-O75': 'Complicações do trabalho de parto e do parto',
                    'O80-O84': 'Parto',
                    'O85-O92': 'Complicações relacionadas principalmente ao puerpério',
                    'O94-O99': 'Outras afecções obstétricas'
                }
            },
            'P': {
                'letter': 'P',
                'title': 'Afecções originadas no período perinatal (P00-P96)',
                'description': 'Problemas que afetam o recém-nascido',
                'subcategories': {
                    'P00-P04': 'Feto e recém-nascido afetados por fatores maternos',
                    'P05-P08': 'Transtornos relacionados com a duração da gestação',
                    'P10-P15': 'Traumatismo de parto',
                    'P20-P29': 'Transtornos respiratórios e cardiovasculares específicos do período perinatal',
                    'P35-P39': 'Infecções específicas do período perinatal',
                    'P50-P61': 'Transtornos hemorrágicos e hematológicos do feto e do recém-nascido',
                    'P70-P74': 'Transtornos endócrinos e metabólicos transitórios específicos do feto',
                    'P75-P78': 'Transtornos do aparelho digestivo do feto e do recém-nascido',
                    'P80-P83': 'Afecções comprometendo o tegumento e a regulação térmica do feto',
                    'P90-P96': 'Outros transtornos originados no período perinatal'
                }
            },
            'Q': {
                'letter': 'Q',
                'title': 'Malformações congênitas (Q00-Q99)',
                'description': 'Defeitos de nascimento e malformações',
                'subcategories': {
                    'Q00-Q07': 'Malformações congênitas do sistema nervoso',
                    'Q10-Q18': 'Malformações congênitas do olho, do ouvido, da face e do pescoço',
                    'Q20-Q28': 'Malformações congênitas do aparelho circulatório',
                    'Q30-Q34': 'Malformações congênitas do aparelho respiratório',
                    'Q35-Q37': 'Fenda labial e fenda palatina',
                    'Q38-Q45': 'Outras malformações congênitas do aparelho digestivo',
                    'Q50-Q56': 'Malformações congênitas dos órgãos genitais',
                    'Q60-Q64': 'Malformações congênitas do aparelho urinário',
                    'Q65-Q79': 'Malformações e deformidades congênitas do sistema osteomuscular',
                    'Q80-Q89': 'Outras malformações congênitas',
                    'Q90-Q99': 'Anomalias cromossômicas'
                }
            },
            'R': {
                'letter': 'R',
                'title': 'Sintomas, sinais e achados anormais (R00-R99)',
                'description': 'Sintomas não classificados em outras categorias',
                'subcategories': {
                    'R00-R09': 'Sintomas e sinais relativos aos aparelhos circulatório e respiratório',
                    'R10-R19': 'Sintomas e sinais relativos ao aparelho digestivo e abdome',
                    'R20-R23': 'Sintomas e sinais relativos à pele e ao tecido subcutâneo',
                    'R25-R29': 'Sintomas e sinais relativos aos sistemas nervoso e osteomuscular',
                    'R30-R39': 'Sintomas e sinais relativos ao aparelho urinário',
                    'R40-R46': 'Sintomas e sinais relativos à cognição, percepção, estado emocional',
                    'R47-R49': 'Sintomas e sinais relativos à fala e à voz',
                    'R50-R69': 'Sintomas e sinais gerais',
                    'R70-R79': 'Achados anormais de exames de sangue',
                    'R80-R82': 'Achados anormais de exames de urina',
                    'R83-R89': 'Achados anormais de exames de outros líquidos',
                    'R90-R94': 'Achados anormais de exames por imagem',
                    'R95-R99': 'Causas de morte mal definidas e desconhecidas'
                }
            },
            'S': {
                'letter': 'S',
                'title': 'Lesões, envenenamento (S00-S99)',
                'description': 'Traumatismos e lesões por causas externas',
                'subcategories': {
                    'S00-S09': 'Traumatismos da cabeça',
                    'S10-S19': 'Traumatismos do pescoço',
                    'S20-S29': 'Traumatismos do tórax',
                    'S30-S39': 'Traumatismos do abdome, do dorso, da coluna lombar e da pelve',
                    'S40-S49': 'Traumatismos do ombro e do braço',
                    'S50-S59': 'Traumatismos do cotovelo e do antebraço',
                    'S60-S69': 'Traumatismos do punho e da mão',
                    'S70-S79': 'Traumatismos do quadril e da coxa',
                    'S80-S89': 'Traumatismos do joelho e da perna',
                    'S90-S99': 'Traumatismos do tornozelo e do pé'
                }
            },
            'T': {
                'letter': 'T',
                'title': 'Lesões, envenenamento (T00-T98)',
                'description': 'Envenenamentos e efeitos tóxicos',
                'subcategories': {
                    'T00-T07': 'Traumatismos envolvendo múltiplas regiões do corpo',
                    'T08-T14': 'Traumatismos de localização não especificada',
                    'T15-T19': 'Efeitos da penetração de corpo estranho',
                    'T20-T32': 'Queimaduras e corrosões',
                    'T33-T35': 'Geladura',
                    'T36-T50': 'Envenenamento por drogas, medicamentos e substâncias biológicas',
                    'T51-T65': 'Efeitos tóxicos de substâncias de origem predominantemente não-medicinal',
                    'T66-T78': 'Outros efeitos de causas externas e os não especificados',
                    'T79': 'Algumas complicações precoces de traumatismo',
                    'T80-T88': 'Complicações de cuidados médicos e cirúrgicos',
                    'T90-T98': 'Sequelas de traumatismos, envenenamentos e outras consequências'
                }
            },
            'V': {
                'letter': 'V',
                'title': 'Causas externas de morbidade (V01-V99)',
                'description': 'Acidentes de transporte',
                'subcategories': {
                    'V01-V09': 'Pedestre traumatizado em acidente de transporte',
                    'V10-V19': 'Ciclista traumatizado em acidente de transporte',
                    'V20-V29': 'Motociclista traumatizado em acidente de transporte',
                    'V30-V39': 'Ocupante de triciclo motorizado traumatizado em acidente',
                    'V40-V49': 'Ocupante de automóvel traumatizado em acidente',
                    'V50-V59': 'Ocupante de caminhonete traumatizado em acidente',
                    'V60-V69': 'Ocupante de veículo de transporte pesado traumatizado',
                    'V70-V79': 'Ocupante de ônibus traumatizado em acidente',
                    'V80-V89': 'Outros acidentes de transporte terrestre',
                    'V90-V94': 'Acidentes de transporte por água',
                    'V95-V97': 'Acidentes de transporte aéreo e espacial',
                    'V98-V99': 'Outros acidentes de transporte e os não especificados'
                }
            },
            'W': {
                'letter': 'W',
                'title': 'Causas externas de morbidade (W00-W99)',
                'description': 'Quedas, exposições e outros acidentes',
                'subcategories': {
                    'W00-W19': 'Quedas',
                    'W20-W49': 'Exposição a forças mecânicas inanimadas',
                    'W50-W64': 'Exposição a forças mecânicas animadas',
                    'W65-W74': 'Afogamento e submersão acidentais',
                    'W75-W84': 'Outros riscos acidentais à respiração',
                    'W85-W99': 'Exposição à corrente elétrica, radiação e temperaturas'
                }
            },
            'X': {
                'letter': 'X',
                'title': 'Causas externas de morbidade (X00-X99)',
                'description': 'Exposições e lesões intencionais',
                'subcategories': {
                    'X00-X09': 'Exposição à fumaça, ao fogo e às chamas',
                    'X10-X19': 'Contato com uma fonte de calor ou substâncias quentes',
                    'X20-X29': 'Contato com animais e plantas venenosos',
                    'X30-X39': 'Exposição às forças da natureza',
                    'X40-X49': 'Envenenamento acidental por e exposição a substâncias nocivas',
                    'X50-X57': 'Excesso de esforços, viagens e privações',
                    'X58-X59': 'Exposição acidental a outros fatores e aos não especificados',
                    'X60-X84': 'Lesões autoprovocadas intencionalmente',
                    'X85-X99': 'Agressões'
                }
            },
            'Y': {
                'letter': 'Y',
                'title': 'Causas externas de morbidade (Y00-Y98)',
                'description': 'Eventos de intenção indeterminada e complicações',
                'subcategories': {
                    'Y00-Y09': 'Agressões',
                    'Y10-Y34': 'Eventos cuja intenção é indeterminada',
                    'Y35-Y36': 'Intervenções legais e operações de guerra',
                    'Y40-Y59': 'Efeitos adversos de drogas, medicamentos e substâncias biológicas',
                    'Y60-Y69': 'Acidentes durante a prestação de cuidados médicos e cirúrgicos',
                    'Y70-Y82': 'Incidentes adversos durante cuidados médicos e cirúrgicos',
                    'Y83-Y84': 'Reação anormal em paciente ou complicação tardia',
                    'Y85-Y89': 'Sequelas de causas externas de morbidade e mortalidade',
                    'Y90-Y98': 'Fatores suplementares relacionados com as causas de morbidade'
                }
            },
            'Z': {
                'letter': 'Z',
                'title': 'Fatores que influenciam o estado de saúde (Z00-Z99)',
                'description': 'Contatos com serviços de saúde para exames e procedimentos',
                'subcategories': {
                    'Z00-Z13': 'Pessoas em contato com os serviços de saúde para exame',
                    'Z20-Z29': 'Pessoas com riscos potenciais relacionados com doenças transmissíveis',
                    'Z30-Z39': 'Pessoas em contato com os serviços de saúde em circunstâncias relacionadas com a reprodução',
                    'Z40-Z54': 'Pessoas em contato com os serviços de saúde para procedimentos específicos',
                    'Z55-Z65': 'Pessoas com riscos potenciais relacionados com circunstâncias socioeconômicas',
                    'Z70-Z76': 'Pessoas em contato com os serviços de saúde em outras circunstâncias',
                    'Z80-Z87': 'Pessoas com riscos potenciais relacionados com história familiar e pessoal',
                    'Z88-Z99': 'Pessoas com riscos potenciais relacionados com história pessoal de certos fatores'
                }
            }
        }
    
    def get_categories(self) -> List[Dict]:
        """Retorna todas as categorias CID-10 com contagem de doenças."""
        result = []
        
        for letter, category_info in self.categories.items():
            count = len([d for d in self.cid10_data if d.get('code', '').startswith(letter)])
            
            result.append({
                'letter': letter,
                'title': category_info['title'],
                'description': category_info['description'],
                'count': count,
                'subcategories': category_info.get('subcategories', {})
            })
        
        return sorted(result, key=lambda x: x['letter'])
    
    def get_diseases_by_category(self, category_letter: str) -> List[Dict]:
        """Retorna doenças de uma categoria específica."""
        category_letter = category_letter.upper()
        diseases = [d for d in self.cid10_data if d.get('code', '').startswith(category_letter)]
        return sorted(diseases, key=lambda x: x.get('code', ''))
    
    def search_by_name(self, query: str, limit: int = 20) -> List[Dict]:
        """Busca doenças por nome com algoritmo aprimorado."""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        results = []
        
        # Função para calcular relevância
        def calculate_relevance(disease_name: str, search_query: str) -> int:
            disease_name = disease_name.lower()
            score = 0
            
            # Correspondência exata (maior pontuação)
            if search_query == disease_name:
                score += 100
            
            # Começa com a query
            if disease_name.startswith(search_query):
                score += 80
            
            # Contém a query completa
            if search_query in disease_name:
                score += 60
            
            # Palavras individuais da query
            query_words = search_query.split()
            disease_words = disease_name.split()
            
            for query_word in query_words:
                if len(query_word) >= 3:  # Ignorar palavras muito pequenas
                    for disease_word in disease_words:
                        if query_word == disease_word:
                            score += 40
                        elif query_word in disease_word:
                            score += 20
                        elif disease_word.startswith(query_word):
                            score += 30
            
            # Penalizar diferenças de tamanho muito grandes
            length_diff = abs(len(disease_name) - len(search_query))
            if length_diff > 20:
                score -= 10
            
            return score
        
        # Buscar e pontuar todas as doenças
        for disease in self.cid10_data:
            description = disease.get('description', '')
            if description:
                relevance = calculate_relevance(description, query)
                if relevance > 0:
                    results.append({
                        'code': disease.get('code'),
                        'description': description,
                        'relevance': relevance
                    })
        
        # Ordenar por relevância e limitar resultados
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def search_by_code(self, code: str) -> Optional[Dict]:
        """Busca doença por código CID exato."""
        code = code.upper().strip()
        for disease in self.cid10_data:
            if disease.get('code', '').upper() == code:
                return disease
        return None
    
    def search_by_code_pattern(self, pattern: str, limit: int = 20) -> List[Dict]:
        """Busca doenças por padrão de código (ex: 'I10', 'F2', 'A0')."""
        pattern = pattern.upper().strip()
        results = []
        
        for disease in self.cid10_data:
            code = disease.get('code', '').upper()
            if code.startswith(pattern):
                results.append(disease)
        
        return sorted(results, key=lambda x: x.get('code', ''))[:limit]
    
    def add_custom_cid(self, code: str, description: str, user_type: str = 'doctor') -> Dict:
        """Permite que médicos adicionem códigos CID personalizados."""
        if user_type != 'doctor':
            raise ValueError("Apenas médicos podem adicionar códigos CID personalizados")
        
        code = code.upper().strip()
        description = description.strip()
        
        # Validar formato do código
        if not re.match(r'^[A-Z]\d{2}(\.\d)?$', code):
            raise ValueError("Formato de código CID inválido. Use formato como 'A00' ou 'A00.1'")
        
        # Verificar se já existe
        existing = self.search_by_code(code)
        if existing:
            raise ValueError(f"Código CID {code} já existe: {existing.get('description')}")
        
        # Adicionar à lista local (em produção, salvaria no banco de dados)
        new_disease = {
            'code': code,
            'description': description,
            'custom': True,
            'added_by': 'doctor'
        }
        
        self.cid10_data.append(new_disease)
        
        return new_disease
    
    def get_subcategory_info(self, code: str) -> Optional[Dict]:
        """Retorna informações da subcategoria de um código CID."""
        if not code:
            return None
        
        category_letter = code[0].upper()
        category = self.categories.get(category_letter)
        
        if not category:
            return None
        
        # Extrair número do código para determinar subcategoria
        code_num = re.findall(r'\d+', code)
        if not code_num:
            return None
        
        code_number = int(code_num[0])
        
        # Encontrar subcategoria correspondente
        for range_key, description in category.get('subcategories', {}).items():
            if '-' in range_key:
                start_range, end_range = range_key.split('-')
                start_num = int(re.findall(r'\d+', start_range)[0])
                end_num = int(re.findall(r'\d+', end_range)[0])
                
                if start_num <= code_number <= end_num:
                    return {
                        'range': range_key,
                        'description': description,
                        'category': category['title']
                    }
        
        return {
            'category': category['title'],
            'description': 'Subcategoria não especificada'
        }

