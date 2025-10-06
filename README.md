# 🤖 Vanlu Agent - Agente de IA com LangGraph

Um agente de IA inteligente construído com **LangGraph** e **FastAPI**, capaz de processar consultas complexas, realizar pesquisas na web e fornecer respostas contextualizadas.

## 🚀 Características

- **LangGraph**: Orquestração avançada de workflows de IA
- **FastAPI**: API REST moderna e performática
- **OpenAI GPT**: Processamento de linguagem natural
- **Tavily Search**: Pesquisa inteligente na web
- **LangSmith**: Observabilidade e monitoramento
- **Docker**: Containerização completa
- **Portainer**: Deploy simplificado

## 📋 Pré-requisitos

- Docker e Docker Compose
- Chaves de API:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Tavily API Key](https://tavily.com/)
  - [LangSmith API Key](https://smith.langchain.com/) (opcional)

## ⚡ Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/SEU_USUARIO/vanlu-agent.git
cd vanlu-agent
```

### 2. Configure as Variáveis de Ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas chaves de API:
```env
OPENAI_API_KEY="sk-proj-YOUR_OPENAI_API_KEY_HERE"
TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
LANGSMITH_API_KEY="lsv2_pt_YOUR_LANGSMITH_API_KEY_HERE"
```

### 3. Execute com Docker
```bash
docker-compose up -d
```

### 4. Acesse a API
- **Documentação Interativa**: http://localhost:2024/docs
- **API Base**: http://localhost:2024
- **Health Check**: http://localhost:2024/health

## 🐳 Deploy no Portainer

### Método 1: Deploy Direto do GitHub (Recomendado)

1. **Acesse Portainer** → Stacks → Add Stack
2. **Build method**: Repository
3. **Repository URL**: `https://github.com/SEU_USUARIO/vanlu-agent`
4. **Compose path**: `docker-compose.yml`
5. **Environment variables**:
   ```
   OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
   TAVILY_API_KEY=YOUR_TAVILY_KEY_HERE
   LANGSMITH_API_KEY=lsv2_pt_YOUR_LANGSMITH_KEY_HERE
   ```
6. **Deploy!**

### Método 2: Upload de Arquivo

1. Baixe o projeto como ZIP
2. **Portainer** → Stacks → Add Stack
3. **Build method**: Upload
4. Selecione o arquivo ZIP
5. Configure as variáveis de ambiente
6. **Deploy!**

## 📚 Uso da API

### Endpoint Principal
```bash
POST /chat
Content-Type: application/json

{
  "message": "Qual é a capital do Brasil?",
  "session_id": "user123"
}
```

### Resposta
```json
{
  "response": "A capital do Brasil é Brasília...",
  "session_id": "user123",
  "timestamp": "2024-01-06T14:27:00Z"
}
```

### Outros Endpoints
- `GET /health` - Status da aplicação
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## 🛠️ Desenvolvimento Local

### 1. Ambiente Virtual Python
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Executar Localmente
```bash
uvicorn main:app --host 0.0.0.0 --port 2024 --reload
```

## 📁 Estrutura do Projeto

```
vanlu-agent/
├── main.py              # Aplicação FastAPI principal
├── services.py          # Serviços e lógica de negócio
├── models.py            # Modelos Pydantic
├── api_endpoints.py     # Endpoints da API
├── langgraph-101.py     # Configuração LangGraph
├── requirements.txt     # Dependências Python
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração Docker
├── .env.example         # Exemplo de variáveis
├── .gitignore          # Arquivos ignorados
└── README.md           # Esta documentação
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente Opcionais
```env
# Configurações Python
PYTHONPATH=/app
PYTHONUNBUFFERED=1

# Configurações de Log
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Recursos Docker
- **CPU**: 0.5 cores (reservado), 1.0 core (limite)
- **RAM**: 512MB (reservado), 1GB (limite)
- **Volumes**: Logs persistentes em `/app/logs`
- **Network**: Rede isolada `vanlu-network`

## 🔍 Monitoramento

### Health Check
```bash
curl http://localhost:2024/health
```

### Logs
```bash
# Docker Compose
docker-compose logs -f vanlu-agent

# Portainer
Containers → vanlu-luciano-agent → Logs
```

### LangSmith (Observabilidade)
Configure `LANGSMITH_API_KEY` para monitoramento avançado:
- Traces de execução
- Métricas de performance
- Debug de workflows

## 🚨 Troubleshooting

### Problemas Comuns

**1. Erro de API Key**
```
Verifique se as chaves estão corretas no arquivo .env
```

**2. Porta em Uso**
```bash
# Verificar processo na porta 2024
lsof -i :2024
# Alterar porta no docker-compose.yml se necessário
```

**3. Problemas de Build**
```bash
# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📈 Performance

### Otimizações Implementadas
- **Async/Await**: Processamento assíncrono
- **Connection Pooling**: Reutilização de conexões
- **Caching**: Cache de respostas frequentes
- **Resource Limits**: Controle de recursos Docker

### Métricas Esperadas
- **Latência**: < 2s para consultas simples
- **Throughput**: ~50 req/s
- **Memória**: ~200-500MB em uso normal

## 🔐 Segurança

### Boas Práticas Implementadas
- ✅ Variáveis de ambiente para secrets
- ✅ .gitignore para arquivos sensíveis
- ✅ Rede Docker isolada
- ✅ Health checks configurados
- ✅ Logs estruturados

### Recomendações Adicionais
- Use HTTPS em produção
- Configure rate limiting
- Implemente autenticação se necessário
- Monitore logs de segurança

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/SEU_USUARIO/vanlu-agent/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/SEU_USUARIO/vanlu-agent/wiki)
- **Email**: seu-email@exemplo.com

---

**Desenvolvido com ❤️ usando LangGraph e FastAPI**