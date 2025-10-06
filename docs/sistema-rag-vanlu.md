# Sistema RAG para Vanlu Estética Automotiva

## 📋 Resumo da Pesquisa

Baseado na pesquisa completa sobre sistemas de RAG (Retrieval-Augmented Generation), embedding e bancos de dados vetoriais, apresento a solução ideal para gerenciar os 26 serviços da Vanlu com busca semântica inteligente.

## 🎯 Cenário Atual
- **26 serviços diferentes** de estética automotiva
- **Necessidade de busca semântica** para encontrar serviços relevantes
- **Agendamento inteligente** baseado na necessidade do cliente
- **Classificação automática** de veículos (Categoria P/G)

## 🏆 Solução Recomendada: PostgreSQL + pgvector + LangChain

### Por que esta é a melhor solução para a Vanlu:

#### ✅ **Vantagens Competitivas**
- **Custo-benefício excelente** - Open source + PostgreSQL já conhecido
- **Performance superior** para datasets pequenos/médios (26 serviços)
- **Manutenção simples** - Stack consolidado e bem documentado
- **Escalabilidade garantida** - Suporta milhões de registros se necessário
- **Integração nativa** com ecossistema LangChain

#### ✅ **Características Técnicas**
- **Busca por similaridade de cosseno**
- **Indexação vetorial com HNSW**
- **Suporte a metadados estruturados**
- **Query performance otimizada**
- **Integração com LangChain nativa**

## 🏗️ Arquitetura Proposta

### 1. **Estrutura de Dados dos Serviços**

```python
# Estrutura recomendada para cada serviço
servico_vanlu = {
    "nome": "Polimento Completo",
    "descricao": "Polimento de alta qualidade com removedor de arranhões",
    "categoria_veiculo": "P",  # P para Hatch/Sedã, G para SUV/Caminonete
    "preco_p": 450.00,  # Preço para categoria P
    "preco_g": 550.00,  # Preço para categoria G
    "duracao": "4 horas",
    "palavras_chave": ["polimento", "arranhões", "pintura", "proteção"],
    "veiculos_recomendados": ["hatch", "sedan", "compacto"],
    "frequencia": "mensal",
    "popularidade": 0.85
}
```

### 2. **Implementação Principal**

```python
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os

# Configuração do PostgreSQL com pgvector
CONNECTION_STRING = "postgresql://user:password@localhost/vanlu_db"

# Inicialização das embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Criação da coleção de vetores
collection_name = "servicos_vanlu"

# Exemplo de criação dos documentos
servicos_documentos = []

for servico in servicos_vanlu:
    # Combina nome + descrição + palavras-chave para embedding rica
    content = f"""
    {servico['nome']}: {servico['descricao']}
    Veículos recomendados: {', '.join(servico['veiculos_recomendados'])}
    Serviço ideal para: {', '.join(servico['palavras_chave'])}
    """

    doc = Document(
        page_content=content.strip(),
        metadata={
            "nome": servico["nome"],
            "categoria_veiculo": servico["categoria_veiculo"],
            "preco_p": servico["preco_p"],
            "preco_g": servico["preco_g"],
            "duracao": servico["duracao"],
            "veiculos_recomendados": servico["veiculos_recomendados"],
            "popularidade": servico["popularidade"]
        }
    )
    servicos_documentos.append(doc)

# Criação do vector store
vectorstore = PGVector.from_documents(
    embedding=embeddings,
    documents=servicos_documentos,
    collection_name=collection_name,
    connection_string=CONNECTION_STRING,
    pre_delete_collection=True  # Limpa coleção existente
)
```

### 3. **Busca Semântica Inteligente**

```python
def buscar_servicos_inteligentes(query: str, modelo_veiculo: str = None, categoria: str = None):
    """
    Busca serviços usando RAG com filtros inteligentes
    """
    # Busca semântica principal
    resultados = vectorstore.similarity_search_with_score(
        query,
        k=5  # Retorna top 5 mais relevantes
    )

    # Filtragem e rankeamento
    servicos_filtrados = []

    for doc, score in resultados:
        metadata = doc.metadata

        # Filtra por categoria do veículo se especificado
        if categoria and metadata["categoria_veiculo"] != categoria:
            continue

        # Bônus para popularidade
        score_final = score + (metadata["popularidade"] * 0.1)

        servicos_filtrados.append({
            "servico": metadata["nome"],
            "score": score_final,
            "preco": metadata["preco_p"] if categoria == "P" else metadata["preco_g"],
            "duracao": metadata["duracao"],
            "descricao": doc.page_content[:200] + "..."
        })

    # Ordena por score (relevância)
    return sorted(servicos_filtrados, key=lambda x: x["score"], reverse=True)

# Exemplo de uso
resultados = buscar_servicos_inteligentes(
    query="tirar arranhões e brilho intenso",
    modelo_veiculo="Gol 2023",
    categoria="P"
)
```

### 4. **Integração com LangGraph**

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def buscar_servicos_vanlu(descricao_necessidade: str, modelo_veiculo: str) -> str:
    """
    Busca serviços da Vanlu baseado na necessidade do cliente e modelo do veículo.

    Args:
        descricao_necessidade: Descrição do que o cliente precisa
        modelo_veiculo: Modelo e ano do veículo do cliente

    Returns:
        Lista de serviços recomendados com preços
    """
    # Classificação automática da categoria
    categoria = classificar_categoria_veiculo(modelo_veiculo)

    # Busca semântica
    resultados = buscar_servicos_inteligentes(
        query=descricao_necessidade,
        categoria=categoria
    )

    # Formatação dos resultados
    resposta = "Encontrei esses serviços para você:\n\n"

    for i, servico in enumerate(resultados[:3], 1):  # Top 3
        resposta += f"{i}. {servico['servico']} - R$ {servico['preco']:.2f}\n"
        resposta += f"   Duração: {servico['duracao']}\n\n"

    return resposta

def classificar_categoria_veiculo(modelo: str) -> str:
    """
    Classifica automaticamente o veículo como P ou G
    """
    modelo_lower = modelo.lower()

    categoria_p = ["palio", "gol", "civic", "corolla", "uno", "celta", "fox"]
    categoria_g = ["hilux", "ranger", "duster", "compass", "suv", "pickup"]

    if any(veiculo in modelo_lower for veiculo in categoria_p):
        return "P"
    elif any(veiculo in modelo_lower for veiculo in categoria_g):
        return "G"
    else:
        return "P"  # Default para segurança

# Integração com o agente Luciano
luciano_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[buscar_servicos_vanlu],
    prompt="Você é Luciano..."
)
```

## 🚀 Implementação Passo a Passo

### **Etapa 1: Setup do Banco de Dados**

```sql
-- Setup PostgreSQL com pgvector
CREATE DATABASE vanlu_db;
CREATE USER vanlu_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE vanlu_db TO vanlu_user;

-- Conecte ao banco vanlu_db e habilite pgvector
\c vanlu_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### **Etapa 2: Instalação de Dependências**

```bash
pip install langchain langchain-openai langchain-community
pip install pgvector sqlalchemy psycopg2-binary
pip install python-dotenv
```

### **Etapa 3: Arquivo .env**

```bash
OPENAI_API_KEY="sua_chave_openai"
DATABASE_URL="postgresql://vanlu_user:sua_senha@localhost/vanlu_db"
COLLECTION_NAME="servicos_vanlu"
```

### **Etapa 4: Script de Indexação**

```python
# indexar_servicos.py
import os
from dotenv import load_dotenv
from vanlu_rag import criar_vector_store, carregar_servicos

load_dotenv()

def main():
    print("Iniciando indexação dos serviços Vanlu...")

    # Carrega os 26 serviços
    servicos = carregar_servicos()  # Função para carregar do JSON/CSV/Database

    # Cria o vector store
    vectorstore = criar_vector_store(servicos)

    print(f"✅ {len(servicos)} serviços indexados com sucesso!")
    print("🚀 Sistema RAG pronto para uso!")

if __name__ == "__main__":
    main()
```

## 🎯 Benefícios para a Vanlu

### ✅ **Vantagens Imediatas**
1. **Busca Natural**: Clientes descrevem problemas em linguagem natural
2. **Recomendações Precisas**: IA entende contexto e recomenda serviços corretos
3. **Classificação Automática**: Sem necessidade de intervenção manual
4. **Escalabilidade**: Fácil adicionar novos serviços
5. **Analytics**: Track de buscas mais populares para otimização

### ✅ **Exemplos de Uso**

```python
# Cliente busca por problema
buscar_servicos_vanlu("meu carro está riscado e sem brilho", "Palio 2022")
# Retorna: Polimento Completo, Cristalização, Proteção de Pintura

# Cliente busca por tipo de serviço
buscar_servicos_vanlu("higienização interna completa", "Duster 2023")
# Retorna: Higienização, Aspiração Completa, Perfumação

# Cliente busca por resultado desejado
buscar_servicos_vanlu("deixar o carro parecendo novo", "Compass 2021")
# Retorna: Pacote Premium, Polimento + Proteção, Detalhamento Completo
```

## 📊 Alternativas Consideradas

### ✅ **Por que não outras opções:**

**FAISS (Facebook AI Similarity Search)**
- ❌ Não persistente em produção
- ❌ Requer rebuild a cada restart
- ❌ Melhor para protótipos, não produção

**ChromaDB**
- ❌ Performance limitada para queries complexas
- ❌ Menos maduro que PostgreSQL
- ❌ Recursos de metadados limitados

**Weaviate**
- ❌ Complexidade desnecessária para 26 serviços
- ❌ Custo operacional mais alto
- ❌ Stack adicional para manter

## 🔮 Futuro e Expansão

### **Roadmap Sugerido**
1. **Fase 1**: Implementação básica com 26 serviços
2. **Fase 2**: Analytics de buscas e otimização
3. **Fase 3**: Expansão para FAQ e documentação técnica
4. **Fase 4**: Integração com sistema de agendamento real
5. **Fase 5**: Machine learning para personalização

### **Métricas de Sucesso**
- 📈 Taxa de conversão de buscas para agendamentos
- 🎯 Precisão das recomendações
- ⚡ Tempo de resposta das queries
- 😊 Satisfação do cliente com recomendações

---

**Conclusão**: A solução PostgreSQL + pgvector + LangChain oferece o melhor equilíbrio entre performance, custo, manutenção e escalabilidade para o cenário específico da Vanlu, com 26 serviços e necessidade de busca semântica inteligente.

*Fonte: Pesquisa completa com Context7 - Setembro 2024*