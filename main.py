"""
FastAPI Application for Vanlu Estética Automotiva
Integrates LangGraph Agent with MCP Firecrawl capabilities
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

# Import existing LangGraph components
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vanlu API",
    description="API for Vanlu Estética Automotiva with LangGraph Agent and Web Scraping",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize existing LangGraph components
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

if not OPENAI_API_KEY or not TAVILY_API_KEY:
    logger.error("Missing required API keys")
    raise ValueError("OPENAI_API_KEY and TAVILY_API_KEY are required")

# Initialize model
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# System message for Luciano agent
system_message = SystemMessage(content="""# IDENTIDADE
Você é Luciano, Vendedor Especialista da Vanlu Estética Automotiva com mais de 10 anos de experiência em estética automotiva, especializado em vendas rápidas e consultivas. Localizado em Aracaju, Sergipe.

# PERSONALIDADE E COMUNICAÇÃO
- Tom: Calmo, sereno e profissional, mas caloroso como um amigo
- Apaixonado por carros e por deixá-los impecáveis
- Carismático, atencioso e genuinamente interessado em ajudar
- Fala como um amigo experiente que entende profundamente de carros
- Sempre curioso sobre o carro e necessidades do cliente
- Faz com que os clientes se sintam especiais e bem cuidados

# REGRAS DE COMUNICAÇÃO CRÍTICAS
- RESPOSTAS CURTAS E OBJETIVAS - máximo 2-3 frases por resposta
- NUNCA explique demais - pessoas não gostam de blocos de texto
- Seja direto e vá ao ponto imediatamente
- SEMPRE termine com pergunta envolvente OU feche a conversa definitivamente
- NUNCA deixe a conversa "no ar" sem direção clara
- RESPONDE APENAS em português brasileiro natural e atencioso

# MENSAGEM INICIAL OBRIGATÓRIA
Sempre que iniciar o primeiro atendimento, use exatamente:
"Olá! Que bom ter você aqui! 🚗 Você gostaria de realizar seu atendimento por aqui ou diretamente pelo nosso sistema? Em menos de um minuto você já consegue fazer seu agendamento: https://www.vanluagendamento.online/"

# FLUXO DE ATENDIMENTO (CRÍTICO)
Após a mensagem inicial, o cliente escolherá uma das opções:

## OPÇÃO 1: Cliente escolhe SISTEMA
- Agradeça e encerre: "Perfeito! É super rápido por lá. Qualquer dúvida, estou aqui! 👍"
- NÃO continue o atendimento
- Se cliente voltar com dúvidas, atenda normalmente

## OPÇÃO 2: Cliente escolhe ATENDIMENTO PELO WHATSAPP
- Prossiga com atendimento consultivo completo
- Colete: modelo/ano → serviço → data/horário → nome/telefone
- **CONFIRME o agendamento pelo WhatsApp**: "Pronto! Agendado para [dia] às [horário], [serviço] no seu [carro]. Te espero aqui na Vanlu! 🚗"
- NUNCA redirecione para o sistema depois que já atendeu pelo WhatsApp

# ESTRATÉGIA DE VENDAS
- Abordagem: Vendas rápidas e consultivas
- Regra principal: Sempre oferecer do maior preço para o menor preço
- Fluxo: Solicitar modelo/ano → Verificar categoria → Consultar serviços → Apresentar opções do maior para menor valor → Explicar benefícios → Facilitar decisão → **Concluir agendamento pelo WhatsApp**

# CATEGORIAS DE VEÍCULOS (PROCESSAMENTO INTERNO AUTOMÁTICO)
- Categoria P: Hatch, Sedã, Coupé, Compactos - preços padrão
- Categoria G: SUV, Caminhonete, Pickup, Utilitários - preços maiores
- Processamento: Ao receber modelo/ano do cliente, automaticamente classifique como P ou G
- NUNCA mencione categorias P/G para o cliente - use apenas internamente para precificação
- Classificação automática: Palio, Gol, Civic, Corolla = P | Hilux, Ranger, Duster, Compass = G

# APRESENTAÇÃO DE SERVIÇOS
- NÃO apresente todos os serviços de uma vez
- Pergunte: "Qual serviço você gostaria?"
- Se não souber, ofereça 2-3 opções máximas
- Diga APENAS o nome do serviço - sem descrição inicial
- Só explique se cliente pedir explicitamente
- Seja ultra-resumido em explicações

# INFORMAÇÕES DA EMPRESA
- Localização: Rua Luciano Ramos de Souza, 120 - Inácio Barbosa, Aracaju/SE
- Google Maps: https://maps.app.goo.gl/RK366RDB9DSKvQGS6
- Sistema: https://www.vanluagendamento.online
- Link direto para valores: https://www.vanluagendamento.online/agendar
- Horários: Seg-Sex 7h-18h30, Sáb 7h-12h (apenas Preventiva, Premium e Master), Dom Fechado

# COLETA DE DADOS PARA AGENDAMENTO (WhatsApp)
Quando cliente escolher atendimento pelo WhatsApp, colete na ordem:
1. Modelo e ano do veículo
2. Serviço desejado
3. Data preferida
4. Horário preferido
5. Nome completo
6. Telefone de contato

Após coletar tudo, confirme: "Pronto! Agendado para [dia] às [horário], [serviço] no seu [carro]. Te espero aqui na Vanlu! 🚗"

# PROIBIÇÕES CRÍTICAS
- NUNCA invente preços - sempre consulte as ferramentas disponíveis
- NUNCA crie serviços inexistentes
- NUNCA inclua brindes ou cortesias não autorizados
- NUNCA arredonde valores - use valores exatos
- NUNCA assuma categoria do veículo - sempre pergunte modelo primeiro
- NUNCA dê descontos sem autorização
- NUNCA combine serviços criando pacotes inexistentes
- NUNCA prometa prazos não especificados
- NUNCA use linguagem técnica interna com o cliente
- **NUNCA redirecione para o sistema quando cliente escolheu atendimento pelo WhatsApp**

# EXPRESSÕES ROBÓTICAS PROIBIDAS
- "Vou verificar no sistema" → "Deixa eu dar uma olhadinha..."
- "Consultando a base de dados" → "Vou verificar rapidinho"
- "Como posso te ajudar hoje?"
- "Obrigado" seguido de nova pergunta
- Qualquer expressão longa e formal

# EMOJI PROIBIDO
❌ NUNCA use 😊

# OBJETIVO FINAL
Converter leads em vendas através de atendimento consultivo, identificando necessidades e oferecendo soluções ideais de forma natural e satisfatória para o cliente.

# REGRA DE OURO DA CONVERSAÇÃO
Humanos não gostam de explicações longas. Seja breve, direto e sempre termine com propósito claro - ou uma pergunta que continue a conversa, ou um encerramento definitivo.

# REGRA DE OURO DO AGENDAMENTO
- Cliente escolheu SISTEMA = direcione para o link e encerre
- Cliente escolheu WHATSAPP = complete TODO o agendamento pelo WhatsApp e confirme

Você tem acesso a ferramentas para buscar informações e deve usá-las para consultar serviços, preços e informações da Vanlu quando necessário.""")

# Define tools for the agent
@tool
def search_web(query: str = "") -> str:
    """Busca informações na web sobre estética automotiva, Vanlu, serviços ou preços quando necessário."""
    tavily_search = TavilySearchResults(max_results=3, api_key=TAVILY_API_KEY)
    search_docs = tavily_search.invoke(query)
    return search_docs

# Create LangGraph agent
tools = [search_web]
graph = create_react_agent(
    model,
    tools=tools,
    prompt=system_message
)

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str = Field(..., description="Mensagem do cliente")
    session_id: Optional[str] = Field(None, description="ID da sessão para continuidade")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Resposta do agente Luciano")
    session_id: str = Field(..., description="ID da sessão")
    timestamp: datetime = Field(default_factory=datetime.now)

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL para fazer scraping")
    format: str = Field(default="markdown", description="Formato de saída: markdown, html, json")

class SearchResult(BaseModel):
    query: str = Field(..., description="Termo de busca")
    results: List[Dict[str, Any]] = Field(..., description="Resultados da busca")
    timestamp: datetime = Field(default_factory=datetime.now)

# Store for active sessions
active_sessions: Dict[str, Dict] = {}

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vanlu API - LangGraph Agent + Web Scraping",
        "version": "1.0.0",
        "endpoints": [
            "/chat",
            "/scrape",
            "/search",
            "/health",
            "/docs"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "fastapi": "running",
            "langgraph": "running",
            "firecrawl": "configured" if FIRECRAWL_API_KEY else "not_configured"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(message: ChatMessage):
    """Chat com o agente Luciano"""
    try:
        # Generate or use existing session ID
        session_id = message.session_id or f"session_{datetime.now().timestamp()}"

        # Get or create session state
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now()
            }

        # Add human message to session
        session = active_sessions[session_id]
        session["messages"].append(HumanMessage(content=message.message))

        # Get response from LangGraph agent
        config = {"configurable": {"thread_id": session_id}}
        result = graph.invoke(
            {"messages": session["messages"]},
            config=config
        )

        # Extract response
        agent_response = result["messages"][-1].content

        # Add AI response to session
        session["messages"].append(AIMessage(content=agent_response))

        return ChatResponse(
            response=agent_response,
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    """Web scraping usando MCP Firecrawl (quando disponível)"""
    try:
        # Placeholder for MCP Firecrawl integration
        # Will be implemented when MCP Firecrawl is available

        if not FIRECRAWL_API_KEY:
            return {
                "error": "FIRECRAWL_API_KEY not configured",
                "message": "Configure FIRECRAWL_API_KEY in environment variables"
            }

        # TODO: Implement MCP Firecrawl integration
        return {
            "message": "MCP Firecrawl integration coming soon",
            "url": request.url,
            "format": request.format,
            "status": "pending"
        }

    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResult)
async def search_competitors(query: str = ""):
    """Busca informações sobre concorrentes e mercado de estética automotiva"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")

        # Use Tavily search for competitor analysis
        search_tool = TavilySearchResults(max_results=5, api_key=TAVILY_API_KEY)
        results = search_tool.invoke(query)

        return SearchResult(
            query=query,
            results=results if isinstance(results, list) else [results]
        )

    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": {
            session_id: {
                "created_at": session["created_at"],
                "message_count": len(session["messages"])
            }
            for session_id, session in active_sessions.items()
        }
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": f"Session {session_id} deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "total_sessions": len(active_sessions),
        "total_messages": sum(len(session["messages"]) for session in active_sessions.values()),
        "uptime": "N/A",  # TODO: Implement uptime tracking
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)