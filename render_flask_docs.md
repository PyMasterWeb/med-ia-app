# Documentação do Render para Deploy de Flask

## Configurações Básicas

**Language**: Python 3
**Build Command**: `pip install -r requirements.txt`
**Start Command**: `gunicorn app:app`

## Estrutura Esperada

O Render espera que o arquivo principal seja `app.py` com uma instância Flask chamada `app`.

## Exemplo Básico
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
```

## Problemas Identificados

1. **Arquivo Principal**: O Render espera `app.py` mas nosso arquivo é `main.py`
2. **Start Command**: Nosso Procfile usa `gunicorn main:app` mas pode precisar de ajustes
3. **Estrutura de Diretórios**: Pode haver problemas com a estrutura de pastas

## Próximos Passos

1. Verificar se o Start Command está correto no Procfile
2. Verificar se a estrutura de arquivos está adequada
3. Verificar se há problemas com arquivos estáticos



## Configurações Detalhadas do Render

### Valores durante a criação:
- **Language**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Observações importantes:
1. O Start Command padrão é `gunicorn app:app` (arquivo:instância)
2. Para usar seu próprio app, deve fornecer o comando correto para iniciá-lo
3. O serviço ficará disponível em URL `onrender.com` após o build
4. Cada push para a branch linkada automaticamente faz build e deploy
5. Se um build falha, o Render cancela o deploy e mantém a versão anterior rodando

### Problema Identificado:
Nosso Procfile está configurado como `gunicorn main:app` mas pode precisar de ajustes na estrutura de diretórios ou no comando de start.


## Informações Críticas sobre Web Services no Render

### Requisitos Obrigatórios:
1. **Bind to Port**: O serviço DEVE fazer bind na porta no host `0.0.0.0`
2. **Porta Padrão**: A porta padrão é `10000` (definida pela variável `PORT`)
3. **Variável PORT**: Recomenda-se usar `process.env.PORT || porta_padrão`

### Exemplo para Flask:
```python
import os
from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Configurações do Serviço:
- **Name**: Nome para identificar o serviço
- **Region**: Região geográfica onde o serviço rodará
- **Branch**: Branch do Git para usar no build
- **Language**: Linguagem de programação
- **Build Command**: Comando para fazer build (`pip install -r requirements.txt`)
- **Start Command**: Comando para iniciar o serviço (`gunicorn app:app`)

### Seção Advanced:
- Variáveis de ambiente
- Health check path
- Persistent disk
- Secrets

### PROBLEMA IDENTIFICADO:
Nosso aplicativo pode não estar fazendo bind corretamente na porta ou no host `0.0.0.0`!

