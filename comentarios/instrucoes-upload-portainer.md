# 📦 Instruções para Upload no Portainer

## ✅ Arquivo Pronto para Upload

**Arquivo criado:** `vanlu-agent-portainer.zip` (21KB)

### 📋 Conteúdo do Pacote:
- ✅ `docker-compose.yml` (otimizado para Portainer)
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ Todos os arquivos Python (.py)
- ✅ `langgraph.json`
- ✅ `.dockerignore`

---

## 🚀 Passo a Passo no Portainer

### 1. **Acessar Portainer**
- Abra: `http://sua-vps-ip:9000`
- Faça login

### 2. **Criar Nova Stack**
- **Stacks** → **Add Stack**
- **Name:** `vanlu-agent`

### 3. **Método Upload (Selecionado)**
- ✅ **Upload** já está selecionado
- Clique em **"Select file"**
- Selecione: `vanlu-agent-portainer.zip`

### 4. **Configurar Environment Variables**
Na seção **Environment variables**, adicione:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGSMITH_API_KEY=ls__xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **CRÍTICO:** Substitua pelos seus valores reais das API keys!

### 5. **Access Control**
- ✅ **Administrators** (já selecionado)
- Mantenha como está

### 6. **Deploy**
- Clique em **"Deploy the stack"**
- Aguarde o build e inicialização (~2-3 minutos)

---

## 🔍 Verificação do Deploy

### **1. Status da Stack**
- **Stacks** → `vanlu-agent` → Deve mostrar **"running"**

### **2. Container Status**
- **Containers** → `vanlu-luciano-agent` → **"running"** + **"healthy"**

### **3. Teste da API**
```bash
# No navegador ou curl
http://sua-vps-ip:2024/docs
```

### **4. Teste do Agente**
```bash
curl -X POST "http://sua-vps-ip:2024/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, preciso de informações sobre lavagem"}'
```

---

## 🔧 Troubleshooting

### **Se o build falhar:**
1. **Stacks** → `vanlu-agent` → **Logs**
2. Verificar se todas as API keys estão corretas
3. Verificar se a VPS tem recursos suficientes

### **Se o container não iniciar:**
1. **Containers** → `vanlu-luciano-agent` → **Logs**
2. Verificar variáveis de ambiente
3. Verificar se a porta 2024 está disponível

### **Se o health check falhar:**
1. Aguardar 40 segundos (start_period)
2. Verificar se o FastAPI está respondendo
3. Verificar logs do container

---

## 📊 Recursos Configurados

### **Limites de Recursos:**
- **CPU:** Máximo 0.5 cores, Reservado 0.25 cores
- **RAM:** Máximo 1GB, Reservado 512MB

### **Volumes:**
- **Logs:** Volume persistente `vanlu-logs`

### **Network:**
- **Rede:** `vanlu-network` (bridge)

### **Health Check:**
- **Endpoint:** `/docs`
- **Intervalo:** 30 segundos
- **Timeout:** 10 segundos
- **Retries:** 3 tentativas

---

## 🎯 Próximos Passos Após Deploy

### **Imediato:**
1. ✅ Verificar se API está respondendo
2. ✅ Testar conversa com o agente
3. ✅ Configurar firewall da VPS (porta 2024)

### **Recomendado:**
1. 🔄 Configurar domínio personalizado
2. 🔄 Implementar SSL/HTTPS
3. 🔄 Configurar backup automático

---

## 💡 Dicas Importantes

1. **Backup das Configurações:**
   - Salve as variáveis de ambiente em local seguro
   - Mantenha cópia do arquivo `vanlu-agent-portainer.zip`

2. **Monitoramento:**
   - Verifique logs regularmente
   - Monitore uso de recursos (CPU/RAM)

3. **Atualizações:**
   - Para atualizar: modifique o código, recrie o zip, e faça re-deploy
   - Use **"Update the stack"** no Portainer

4. **Segurança:**
   - Nunca compartilhe as API keys
   - Configure firewall adequadamente
   - Use HTTPS em produção

---

**Status:** ✅ **Arquivo pronto para upload no Portainer!**

*Arquivo: `vanlu-agent-portainer.zip` - Tamanho: 21KB - 10 arquivos essenciais*