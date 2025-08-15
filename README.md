<div align="justify">

# Security Occurrence Handler

Sistema de atendimento inteligente de ocorrências de alarme usando agentes LLM que simula conversas entre atendente e cliente seguindo protocolos de segurança específicos.

Link para um curto vídeo demonstrativo: https://drive.google.com/file/d/13doFe2E2V6gDfwDxiMZGpLxxq-dAQgqQ/view?usp=sharing

## Funcionalidades

**Agente Atendente**: Segue protocolo de validação de segurança e toma decisões baseadas nas respostas do cliente
**Agente Cliente**: Simula diferentes cenários de resposta (palavra correta, pânico, perigo, etc.)
**Processamento Assíncrono**: Ocorrências são processadas em background
**API REST**: Endpoints para submissão e consulta de status
**Múltiplos Cenários**: Testa diferentes fluxos de conversação

## Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangGraph      │    │   OpenAI GPT    │
│   (REST API)    │◄──►│   (Orquestração) │◄──►│   (LLM)         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│   Storage       │    │   Agent Tools    │
│   (In-Memory)   │    │   (Validação)    │
└─────────────────┘    └──────────────────┘
```

### Fluxo de Processamento

1. **POST /handle_occurrence** → Gera hash único e inicia processamento assíncrono
2. **Agente Atendente** → Faz pergunta de segurança usando dados do responsável
3. **Agente Cliente** → Responde conforme cenário configurado
4. **Validação** → Tools verificam palavra-chave (correta/pânico/incorreta)
5. **Decisão** → Status final: `RESOLVIDO` ou `ESCALADO`
6. **GET /status_occurrence** → Consulta resultado e histórico de mensagens

## Estrutura do Projeto

```
src/
├── agents/                 # Lógica dos agentes LLM
│   ├── core/              # Classes base (Node, LLMNode, etc.)
│   ├── graph.py           # Orquestração LangGraph
│   ├── prompts.py         # Templates de prompt
│   ├── states.py          # Estados e modelos de dados
│   └── tools.py           # Ferramentas (validação, status)
├── api/                   # Endpoints REST
│   ├── endpoints.py       # Rotas da API
│   ├── models.py          # Schemas Pydantic
│   ├── storage.py         # Storage em memória
│   └── main.py            # App FastAPI
└── services/              # Lógica de negócio
    └── occurrence_processor.py  # Processamento assíncrono

data/                      # Dados de teste
tests/                     # Testes automatizados
```

## Cenários de Teste

| Cenário | Comportamento | Status Final |
|---------|---------------|--------------|
| `correct_password_ok` | Palavra correta → "Está tudo bem" | `RESOLVIDO` |
| `wrong_password` | Palavra incorreta | `ESCALADO` |
| `correct_password_danger` | Palavra correta → "Estou com perigo" | `ESCALADO` |
| `panic_word` | Palavra de pânico | `ESCALADO` |
| `who_is_auria` | Pergunta sobre empresa → Continua normal | `RESOLVIDO` |

## Configuração e Execução

### Requisitos

- Python 3.11+
- Chave API OpenAI

### Configuração

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd security-occurrence-handler
   ```

2. **Configure variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com sua chave OpenAI
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_LLM_MODEL_NAME=gpt-4o-mini
   ```

### Execução Local

**Opção 1: Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

**Opção 2: Docker**
```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`

## Uso da API

### Submeter Ocorrência

```bash
POST /handle_occurrence
Content-Type: application/json

{
  "test_cases": [...],          # Dados da ocorrência
  "test_suite_id": "test_001",
  "scenario": "correct_password_ok"  # Cenário a simular
}

# Resposta
{
  "hash": "9af0bcf5d94d555f88824acb41e6c355"
}
```

### Consultar Status

```bash
GET /status_occurrence?hash=9af0bcf5d94d555f88824acb41e6c355

# Resposta
{
  "status_final": "RESOLVIDO",
  "mensagens": [
    {"de": "atendente", "mensagem": "Olá, Carlos! Para começarmos..."},
    {"de": "cliente", "mensagem": "Caminhada."},
    ...
  ]
}
```

## Testes

### Execução Manual

```bash
# Subir a API
uvicorn src.api.main:app --reload

# Em outro terminal, executar testes
cd tests
python test_scenarios.py
```

### Exemplo de Teste com cURL

```bash
# Submeter ocorrência
curl -X POST "http://localhost:8000/handle_occurrence" \
  -H "Content-Type: application/json" \
  -d @data/occurrence_event_alarm.json

# Consultar status (substitua o hash)
curl "http://localhost:8000/status_occurrence?hash=YOUR_HASH_HERE"
```

## Exemplo de Conversação Completa

**Cenário: correct_password_ok**

```
atendente: Olá, Carlos! Para começarmos, por favor, me diga: qual é o seu hobby favorito?
cliente: Caminhada.
atendente: Aqui é da Auria AI. Houve um disparo na zona de acesso veicular. Está tudo bem?
cliente: Está tudo bem.
atendente: Obrigado, Carlos! Fico feliz em saber que está tudo bem. Atendimento finalizado.

Status Final: RESOLVIDO
```

## Tecnologias

- **FastAPI**: Framework web assíncrono
- **LangChain/LangGraph**: Orquestração de agentes LLM
- **OpenAI GPT**: Modelo de linguagem
- **Pydantic**: Validação de dados
- **Docker**: Containerização

## Estrutura de Dados

### Input (occurrence_event_alarm.json)

```json
{
  "test_cases": [{
    "client_context": {
      "client_details": {
        "responsibles_details": [{
          "name": "Carlos",
          "phone_number_1": "11987654321",
          "question": "Qual seu hobby favorito?",
          "correct_answer": "Caminhada",
          "panic_answer": "Natação",
          "function": "ZELADOR"
        }]
      }
    },
    "events_details": [{
      "name": "ALARME DE ZONA SENSOR PORTA VEICULAR",
      "description": "Disparo de alarme na zona de acesso veicular.",
      "zone_code": "6 - SENSOR PORTA VEICULAR"
    }]
  }]
}
```

### Output

```json
{
  "status_final": "RESOLVIDO",
  "mensagens": [
    {"de": "atendente", "mensagem": "..."},
    {"de": "cliente", "mensagem": "..."}
  ]
}
```

## Logs de Desenvolvimento

Durante execução, o sistema exibe logs detalhados do processamento:

```
output: {'attendant_node': {'messages': [AIMessage(content='Olá, Carlos!...')]}}
output: {'client_node': {'messages': [AIMessage(content='Caminhada.')]}}
...
```

</div>