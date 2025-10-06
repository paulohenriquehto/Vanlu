
Voltar para a biblioteca
7 min de leitura
10 de abril de 2025
Nova era de Agentes de IA com Langgraph - Método Fácil
Construa um agente ReAct com Langgraph e vá além do básico.

Nova era dos Agentes de IA
Você está cansado de Agentes de IA que funcionam só em demonstração e com baixo volume de uso?

Se você está acostumado com ferramentas nocode, já deve ter notado que é muito fácil bater no teto.

O futuro é daqueles que constroem ferramentas robustas e que vão além do básico.

Para não ficar parado no que funcionava em 2023, está na hora de criar como os grandes fazem.

Esse projeto foi criado para que você possa começar criar agentes com langgraph e dê seus primeiros passos rumo ao topo.

LangGraph 101: Agente ReAct com Busca Web
Langgraph é uma ferramenta espetacular para criação de agentes.

Ela é usada pelo Replit (https://replit.com/) em sua solução. (Soluções profissionais requerem ferramentas profissionais)

Mas começar a fazer agentes no langgraph pode ser desafiador, já que o número de possibilidades é infinito.

Para te ajudar, criei esse projeto. Ele te guia de maneira prática na implementação de um agente ReAct e te dá acesso a uma interface visual para teste.

Este projeto demonstra a criação de um agente conversacional simples utilizando LangGraph, especificamente a função create_react_agent. O agente, chamado "Don Corleone", é capaz de raciocinar, utilizar uma ferramenta de busca na web (Tavily) e responder às perguntas do usuário, mantendo o contexto da conversa.

Conceitos Fundamentais
Antes de mergulhar no código, vamos entender as ferramentas envolvidas:

LangChain: É um framework abrangente para construir aplicações com LLMs. Ele fornece módulos para interagir com modelos, gerenciar prompts, conectar componentes (chains) e integrar ferramentas. Pense nele como a fundação.

LangSmith: É uma plataforma para depuração, teste, avaliação e monitoramento de aplicações construídas com LangChain (ou outras). Ajuda a entender o que está acontecendo dentro da sua aplicação LLM, visualizar os passos e otimizar o desempenho. É uma ferramenta de observabilidade e MLOps.

LangGraph: É uma extensão do LangChain focada na construção de aplicações LLM stateful (que mantêm estado) e multi-agentes, representando-as como grafos. É ideal para fluxos complexos que envolvem ciclos, múltiplos passos e gerenciamento explícito do estado da aplicação. Ele se baseia nos componentes do LangChain.

Neste projeto, usamos LangGraph para orquestrar o fluxo do agente, LangChain para os componentes básicos (modelo, ferramentas, prompt) e poderíamos usar LangSmith para debugar e monitorar (abordarei em outro artigo).

Agora você já se localizou. Vamos construir.

Estrutura do Projeto
Crie os seguintes arquivos:

.
âââ .env                  # Arquivo para variÃ¡veis de ambiente
âââ langgraph-101.py      # Script principal com a lÃ³gica do agente
âââ langgraph.json        # ConfiguraÃ§Ã£o para a ferramenta `langgraph dev`

Detalhamento do Código (langgraph-101.py)
O script langgraph-101.py implementa o agente passo a passo:

Importações:

from langgraph.prebuilt import create_react_agent # FunÃ§Ã£o principal do LangGraph para criar agentes ReAct
from langchain_core.messages import SystemMessage # Para definir a mensagem de sistema (persona)
from langchain_core.tools import tool # Decorador para definir ferramentas
from langchain_google_genai import ChatGoogleGenerativeAI # Modelo LLM do Google (Gemini)
from langchain_community.tools.tavily_search import TavilySearchResults # Ferramenta de busca Tavily
import os
from dotenv import load_dotenv # Para carregar variÃ¡veis de ambiente

Importamos os componentes necessários do LangGraph, LangChain Core, LangChain Community (para ferramentas) e Google GenAI.
Configuração do Ambiente:

load_dotenv()
API_KEY = os.getenv("API_KEY") # Chave da API do Google Gemini
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") # Chave da API da Tavily Search

Carrega as variáveis de ambiente definidas no arquivo .env. É crucial criar este arquivo! (Veja a seção de Configuração).
Inicialização do Modelo:

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", # Modelo especÃ­fico do Gemini
    temperature=0, # Controla a criatividade (0 = mais determinÃ­stico)
    api_key=API_KEY
)

Configura o LLM que o agente usará, neste caso, o Gemini 1.5 Flash do Google.
Definição da Persona (System Prompt):

system_message = SystemMessage(content="""VocÃª Ã© o Don Corleone.
                                VocÃª tem acesso a ferramentas para buscar informaÃ§Ãµes na web.
                                VocÃª deve usar essas ferramentas para buscar informaÃ§Ãµes sobre o assunto que o usuÃ¡rio perguntar.
                                VocÃª deve responder de forma clara e objetiva.""")


Instrui o LLM sobre como ele deve se comportar e qual ferramenta ele tem disponível.
Definição da Ferramenta (search_web):

@tool
def search_web(query: str = "") -> str:
    """Busca informaÃ§Ãµes na web baseada na consulta fornecida."""
    tavily_search = TavilySearchResults(max_results=3, api_key=TAVILY_API_KEY)
    search_docs = tavily_search.invoke(query)
    return search_docs

    O decorador @tool transforma a função Python search_web em uma ferramenta que o LangChain/LangGraph pode reconhecer e usar.
A função utiliza a TavilySearchResults para buscar na web e retorna os resultados.
Criação do Agente ReAct:

tools = [search_web] # Lista de ferramentas disponÃ­veis para o agente

graph = create_react_agent(
    model,
    tools=tools,
    prompt=system_message # Aplica a persona/instruÃ§Ãµes
)

Esta é a função central do LangGraph neste exemplo.
create_react_agent monta automaticamente um grafo que implementa o padrão ReAct (Reason + Act).
O agente recebe o model, a lista de tools e a system_message. Ele agora sabe como raciocinar, quando usar a ferramenta search_web e como se comportar (Don Corleone).

O Arquivo langgraph.json

{
    "dependencies": ["."],
    "graphs": {
        "agent": "langgraph-101:graph"
    }
}

Importância: Este arquivo é usado pela interface de linha de comando langgraph-cli, especificamente pelo comando langgraph dev.

dependencies: Indica os diretórios que o langgraph dev deve monitorar para recarregar automaticamente quando houver alterações. "." significa o diretório atual.

graphs: Mapeia um nome amigável ("agent") para o objeto do grafo LangGraph no seu código Python.

"agent": "langgraph-101:graph" informa ao langgraph dev que o grafo que ele deve servir e interagir se chama graph e está localizado no módulo Python langgraph-101.py.

Em resumo: langgraph.json configura o ambiente de desenvolvimento interativo do LangGraph, permitindo que você teste e depure seu grafo facilmente através de uma interface web local.

Configuração e Instalação
Agora que você já tem o código e os arquivos necessários, siga os próximos passos:

Pré-requisitos: Python 3.10 ou superior.
Criar Ambiente Virt

python3.12 -m venv .venv
source .venv/bin/activate # Linux/macOS
# .\.venv\Scripts\activate # Windows

Instalar Dependências:

# Pacotes principais
pip install -U langgraph langchain-core langchain-google-genai langchain-community tavily-python python-dotenv

# Pacotes para desenvolvimento (langgraph dev)
pip install -U "langgraph-cli[in-men]"

Criar Arquivo .env:
Crie um arquivo chamado .env na raiz do projeto.
Adicione suas chaves de API:

# .env
API_KEY="SUA_CHAVE_API_GOOGLE_GEMINI" # Chave da API do Google Gemini
TAVILY_API_KEY="SUA_CHAVE_API_TAVILY" # Chave da API do Tavily

IMPORTANTE: Substitua "SUA_CHAVE_API_..." pelas suas chaves reais. Obtenha-as nos respectivos sites (Google AI Studio, Tavily). Nunca envie este arquivo para o controle de versão (Git)! Adicione .env ao seu arquivo .gitignore.

Como Executar
Ative o Ambiente Virtual: (Se ainda não estiver ativo)

source .venv/bin/activate

Inicie o Servidor de Desenvolvimento LangGraph:
langgraph dev


Acesse a Interface: Abra seu navegador e vá para a URL fornecida pelo comando.
Interaja: Use o playground para enviar mensagens ao agente "Don Corleone" e veja como ele raciocina e usa a ferramenta de busca.

Conclusão e próximos passos
Este projeto serve como um ponto de partida para entender como LangGraph, através do create_react_agent, simplifica a criação de agentes LLM que podem usar ferramentas e manter o estado da conversa.

A estrutura de grafo permite controle e extensibilidade para construir aplicações mais complexas.

Este projeto - do jeito que está - pode ser colocado no ar usando langgraph cloud e com algumas adaptações poderíamos fazer deploy em um servidor privado.