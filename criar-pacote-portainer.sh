#!/bin/bash

# Script para criar pacote do projeto Vanlu para deploy no Portainer
# Autor: Claude AI
# Data: $(date)

echo "🚀 Criando pacote para deploy no Portainer..."

# Nome do arquivo de saída
PACKAGE_NAME="vanlu-agent-portainer.zip"

# Remover pacote anterior se existir
if [ -f "$PACKAGE_NAME" ]; then
    echo "📦 Removendo pacote anterior..."
    rm "$PACKAGE_NAME"
fi

# Criar diretório temporário
TEMP_DIR="temp_portainer"
mkdir -p "$TEMP_DIR"

echo "📋 Copiando arquivos essenciais..."

# Copiar arquivos essenciais
cp docker-compose.portainer.yml "$TEMP_DIR/docker-compose.yml"
cp Dockerfile "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp .dockerignore "$TEMP_DIR/"

# Copiar arquivos Python do projeto
cp *.py "$TEMP_DIR/"

# Copiar arquivo de configuração do LangGraph se existir
if [ -f "langgraph.json" ]; then
    cp langgraph.json "$TEMP_DIR/"
fi

echo "🗜️  Compactando arquivos..."

# Criar o arquivo ZIP
cd "$TEMP_DIR"
zip -r "../$PACKAGE_NAME" .
cd ..

# Limpar diretório temporário
rm -rf "$TEMP_DIR"

echo "✅ Pacote criado com sucesso: $PACKAGE_NAME"
echo ""
echo "📊 Informações do pacote:"
ls -lh "$PACKAGE_NAME"
echo ""
echo "📁 Conteúdo do pacote:"
unzip -l "$PACKAGE_NAME"
echo ""
echo "🎯 Próximos passos:"
echo "1. Acesse seu Portainer"
echo "2. Stacks → Add Stack"
echo "3. Build method: Upload"
echo "4. Selecione o arquivo: $PACKAGE_NAME"
echo "5. Configure as variáveis de ambiente (API keys)"
echo "6. Deploy!"
echo ""
echo "⚠️  IMPORTANTE: Não esqueça de configurar as variáveis de ambiente:"
echo "   - OPENAI_API_KEY"
echo "   - TAVILY_API_KEY"
echo "   - LANGSMITH_API_KEY"