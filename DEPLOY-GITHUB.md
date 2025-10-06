# 🚀 Deploy VanLu Agent via GitHub

## 📋 Pré-requisitos

- Conta no GitHub
- Portainer instalado e configurado
- Chaves de API: OpenAI, Tavily, LangSmith

## 🔗 Passo 1: Conectar ao GitHub

### 1.1 Criar Repositório no GitHub
```bash
# Acesse: https://github.com/new
# Nome sugerido: vanlu-agent
# Descrição: AI Assistant with LangGraph - FastAPI REST API
# Público: ✅ Sim (para deploy direto no Portainer)
```

### 1.2 Conectar Repositório Local ✅ CONCLUÍDO
```bash
# ✅ Repositório já conectado e enviado!
# URL: https://github.com/paulohenriquehto/Vanlu.git
# Branch: main
# Status: 32 objetos enviados (49.25 KiB)

# Para verificar:
git remote -v
git status
```

## 🐳 Passo 2: Deploy no Portainer via GitHub

### 2.1 Método Recomendado: Deploy Direto do GitHub

1. **Acesse Portainer** → `Stacks` → `Add Stack`

2. **Configurações do Stack:**
   - **Name:** `vanlu-agent`
   - **Build method:** `Repository`
   - **Repository URL:** `https://github.com/paulohenriquehto/Vanlu.git`
   - **Repository reference:** `refs/heads/main`
   - **Compose path:** `docker-compose.yml`

3. **Environment Variables (OBRIGATÓRIO):**
   ```env
   OPENAI_API_KEY=sk-proj-sua_chave_aqui
   TAVILY_API_KEY=tvly-sua_chave_aqui
   LANGSMITH_API_KEY=lsv2_sua_chave_aqui
   ```

4. **Deploy:** Clique em `Deploy the stack`

### 2.2 Método Alternativo: Upload de Arquivo

Se preferir, ainda pode usar o arquivo `vanlu-agent-portainer.zip`:

1. **Acesse Portainer** → `Stacks` → `Add Stack`
2. **Build method:** `Upload`
3. **Upload:** `vanlu-agent-portainer.zip`
4. **Environment Variables:** (mesmas do método anterior)
5. **Deploy:** Clique em `Deploy the stack`

## 🔧 Passo 3: Configuração das APIs

### 3.1 OpenAI API Key
```bash
# Obter em: https://platform.openai.com/api-keys
# Formato: sk-proj-...
```

### 3.2 Tavily API Key
```bash
# Obter em: https://tavily.com/
# Formato: tvly-...
```

### 3.3 LangSmith API Key (Opcional)
```bash
# Obter em: https://smith.langchain.com/
# Formato: lsv2_...
```

## 📊 Passo 4: Verificação do Deploy

### 4.1 Verificar Container
- **Portainer** → `Containers` → Verificar `vanlu-luciano-agent`
- **Status:** Running ✅
- **Health:** Healthy ✅

### 4.2 Testar API
```bash
# Substituir SEU_IP pela IP do servidor
curl http://SEU_IP:2024/docs

# Ou acessar no navegador:
http://SEU_IP:2024/docs
```

### 4.3 Endpoints Disponíveis
- **Documentação:** `http://SEU_IP:2024/docs`
- **Health Check:** `http://SEU_IP:2024/health`
- **Chat:** `POST http://SEU_IP:2024/chat`
- **Status:** `GET http://SEU_IP:2024/status`

## 🔄 Passo 5: Atualizações Futuras

### 5.1 Atualizar Código
```bash
# Fazer alterações no código
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
```

### 5.2 Atualizar no Portainer
1. **Portainer** → `Stacks` → `vanlu-agent`
2. **Editor** → `Pull and redeploy`
3. **Update the stack** ✅

## 🚨 Troubleshooting

### Problema: Container não inicia
```bash
# Verificar logs
docker logs vanlu-luciano-agent

# Verificar variáveis de ambiente
docker exec vanlu-luciano-agent env | grep API
```

### Problema: API Keys inválidas
- Verificar formato das chaves
- Regenerar chaves se necessário
- Atualizar environment variables no Portainer

### Problema: Porta 2024 não acessível
- Verificar firewall do servidor
- Confirmar mapeamento de porta no docker-compose.yml
- Testar localmente: `curl http://localhost:2024/health`

## 📈 Monitoramento

### Logs em Tempo Real
```bash
# Via Docker
docker logs -f vanlu-luciano-agent

# Via Portainer
Containers → vanlu-luciano-agent → Logs
```

### Métricas de Performance
- **CPU/Memory:** Portainer → Containers → Stats
- **API Calls:** LangSmith Dashboard (se configurado)
- **Health Status:** `http://SEU_IP:2024/health`

## 🔐 Segurança

### ✅ Implementado
- Environment variables para API keys
- .gitignore protegendo arquivos sensíveis
- .env.example como template
- Health checks configurados
- Restart policy: unless-stopped

### 🔒 Recomendações Adicionais
- Usar HTTPS em produção (Nginx reverse proxy)
- Implementar rate limiting
- Monitorar logs de acesso
- Backup regular dos dados

---

## 📞 Suporte

**Repositório:** https://github.com/paulohenriquehto/Vanlu.git
**Documentação:** README.md
**Issues:** GitHub Issues

**Status do Deploy:** ✅ Pronto para produção