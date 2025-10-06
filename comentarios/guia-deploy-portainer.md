# 🚀 Guia de Deploy - Projeto Vanlu no Portainer

## 📋 Análise das Opções de Deploy

### **Recomendação: 🥇 UPLOAD (Melhor Opção)**

| Método | Prós | Contras | Nota |
|--------|------|---------|------|
| **Upload** ⭐ | ✅ Mantém formatação original<br>✅ Mais seguro para credenciais<br>✅ Rápido e confiável | ❌ Precisa do arquivo local | **RECOMENDADO** |
| **Web Editor** | ✅ Direto no navegador<br>✅ Não precisa upload | ❌ Risco de erros de formatação<br>❌ Menos seguro para API keys | Alternativa |
| **Custom Template** | ✅ Reutilizável<br>✅ Parametrizável | ❌ Mais complexo inicialmente | Para uso futuro |

---

## 🎯 **MÉTODO RECOMENDADO: Upload**

### **Por que Upload é a melhor opção:**
1. **Segurança:** Variáveis de ambiente ficam separadas do arquivo
2. **Confiabilidade:** Usa o arquivo docker-compose.yml original testado
3. **Simplicidade:** Deploy direto sem riscos de erro manual
4. **Manutenção:** Fácil de atualizar no futuro

---

## 📦 Preparação para Deploy

### **1. Arquivo para Upload**
Use o arquivo: `docker-compose.production.yml` (criado especialmente para produção)

**Diferenças da versão de produção:**
- ✅ Usa imagem pré-construída (não build local)
- ✅ Volume persistente para logs
- ✅ Limites de recursos definidos
- ✅ Health check otimizado
- ✅ Sem dependência de arquivos locais

### **2. Variáveis de Ambiente Necessárias**
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGSMITH_API_KEY=ls__xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔧 Passo a Passo - Deploy via Upload

### **Passo 1: Preparar a Imagem Docker**
Antes do deploy no Portainer, você precisa construir e enviar a imagem:

```bash
# 1. Construir a imagem localmente
docker build -t vanlu-agent:latest .

# 2. Fazer tag para registry (se usar Docker Hub)
docker tag vanlu-agent:latest seuusuario/vanlu-agent:latest

# 3. Enviar para registry
docker push seuusuario/vanlu-agent:latest
```

**OU usar registry local da VPS:**
```bash
# Se tiver registry local na VPS
docker tag vanlu-agent:latest localhost:5000/vanlu-agent:latest
docker push localhost:5000/vanlu-agent:latest
```

### **Passo 2: Configurar no Portainer**

#### **2.1 Acessar Portainer**
- Acesse: `http://sua-vps-ip:9000`
- Login com suas credenciais

#### **2.2 Criar Stack**
1. **Stacks** → **Add Stack**
2. **Name:** `vanlu-agent`
3. **Build method:** **Upload**

#### **2.3 Upload do Arquivo**
1. Clique em **Select file**
2. Selecione: `docker-compose.production.yml`
3. Upload será feito automaticamente

#### **2.4 Configurar Environment Variables**
Na seção **Environment variables**, adicione:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGSMITH_API_KEY=ls__xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **IMPORTANTE:** Nunca coloque as chaves reais no arquivo docker-compose!

#### **2.5 Deploy**
1. Clique em **Deploy the stack**
2. Aguarde o download da imagem e inicialização
3. Verifique os logs em **Containers**

---

## ✅ Verificação do Deploy

### **1. Status do Container**
- **Portainer** → **Containers** → Verificar se `vanlu-luciano-agent` está **running**

### **2. Health Check**
- Status deve mostrar **healthy** após ~40 segundos

### **3. Teste da API**
```bash
# Teste direto na VPS
curl http://sua-vps-ip:2024/docs

# Ou no navegador
http://sua-vps-ip:2024/docs
```

### **4. Teste do Agente**
```bash
curl -X POST "http://sua-vps-ip:2024/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, preciso de informações sobre lavagem"}'
```

---

## 🔒 Configurações de Segurança

### **1. Firewall da VPS**
```bash
# Permitir apenas porta 2024
sudo ufw allow 2024/tcp
sudo ufw enable
```

### **2. Nginx Reverse Proxy (Opcional)**
Para usar domínio personalizado:

```nginx
server {
    listen 80;
    server_name vanlu.seudominio.com;
    
    location / {
        proxy_pass http://localhost:2024;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **3. SSL/HTTPS (Recomendado)**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d vanlu.seudominio.com
```

---

## 📊 Monitoramento

### **1. Logs do Container**
- **Portainer** → **Containers** → `vanlu-luciano-agent` → **Logs**

### **2. Métricas de Performance**
- **Portainer** → **Containers** → `vanlu-luciano-agent` → **Stats**

### **3. Health Checks**
- Verificação automática a cada 30 segundos
- Endpoint: `http://localhost:2024/docs`

---

## 🔄 Atualizações Futuras

### **Método Simples:**
1. Construir nova versão da imagem
2. **Portainer** → **Stacks** → `vanlu-agent` → **Editor**
3. Alterar tag da imagem (ex: `:v1.1`)
4. **Update the stack**

### **Método Avançado:**
1. Usar CI/CD com GitHub Actions
2. Auto-deploy via webhook do Portainer
3. Rollback automático em caso de falha

---

## 🚨 Troubleshooting

### **Container não inicia:**
```bash
# Verificar logs
docker logs vanlu-luciano-agent

# Verificar variáveis de ambiente
docker exec vanlu-luciano-agent env | grep API_KEY
```

### **API não responde:**
```bash
# Verificar se porta está aberta
netstat -tlnp | grep 2024

# Teste interno do container
docker exec vanlu-luciano-agent curl localhost:2024/docs
```

### **Health check falha:**
```bash
# Verificar se curl está instalado no container
docker exec vanlu-luciano-agent which curl

# Teste manual do health check
docker exec vanlu-luciano-agent curl -f http://localhost:2024/docs
```

---

## 📈 Próximos Passos

### **Imediato:**
- ✅ Deploy básico funcionando
- ✅ Monitoramento ativo
- ✅ Backup das configurações

### **Curto Prazo:**
- 🔄 Configurar domínio personalizado
- 🔄 Implementar SSL/HTTPS
- 🔄 Configurar alertas de monitoramento

### **Médio Prazo:**
- 🔄 CI/CD automatizado
- 🔄 Backup automático dos dados
- 🔄 Load balancer (se necessário)

---

## 💡 Dicas Importantes

1. **Sempre teste localmente** antes do deploy em produção
2. **Mantenha backups** das configurações do Portainer
3. **Monitore recursos** da VPS (CPU, RAM, Disk)
4. **Configure alertas** para falhas do container
5. **Documente mudanças** para facilitar troubleshooting

---

**Status:** ✅ **Guia Completo para Deploy via Upload no Portainer**

*Método recomendado: Upload com configuração segura de variáveis de ambiente*