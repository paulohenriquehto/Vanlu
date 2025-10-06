"""
Business logic and services for Vanlu API
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from models import (
    VehicleInfo, ServiceInfo, ServiceType, VehicleCategory,
    ChatResponse, AppointmentRequest, AppointmentResponse,
    ScrapeRequest, ScrapeResponse, CrawlRequest, CrawlResponse,
    SearchResult, CompetitorAnalysis
)
import os
import json
import hashlib

logger = logging.getLogger(__name__)

class LucianoAgentService:
    """Service for managing Luciano agent interactions"""

    def __init__(self, graph, tools):
        self.graph = graph
        self.tools = tools
        self.sessions: Dict[str, Dict] = {}
        self.service_pricing = self._load_service_pricing()

    def _load_service_pricing(self) -> Dict[str, ServiceInfo]:
        """Load service pricing and information"""
        return {
            "Preventiva": ServiceInfo(
                name="Preventiva",
                category=VehicleCategory.PEQUENO,
                price_p=45.0,
                price_g=60.0,
                duration_minutes=30,
                description="Limpeza básica com aspiração, limpeza de painéis e vidros"
            ),
            "Premium": ServiceInfo(
                name="Premium",
                category=VehicleCategory.PEQUENO,
                price_p=120.0,
                price_g=150.0,
                duration_minutes=90,
                description="Limpeza completa com hidratação de plásticos e tratamento de pneus"
            ),
            "Master": ServiceInfo(
                name="Master",
                category=VehicleCategory.PEQUENO,
                price_p=200.0,
                price_g=250.0,
                duration_minutes=180,
                description="Serviço completo incluindo polimento leve e revitalização"
            ),
            "Polimento": ServiceInfo(
                name="Polimento Comercial",
                category=VehicleCategory.PEQUENO,
                price_p=400.0,
                price_g=500.0,
                duration_minutes=240,
                description="Polimento para remoção de arranhões leves e oxidação"
            ),
            "Vitrificação": ServiceInfo(
                name="Vitrificação",
                category=VehicleCategory.PEQUENO,
                price_p=800.0,
                price_g=1000.0,
                duration_minutes=480,
                description="Proteção de longa duração com verniz cerâmico"
            ),
            "Limpeza Interna": ServiceInfo(
                name="Limpeza Interna Completa",
                category=VehicleCategory.PEQUENO,
                price_p=150.0,
                price_g=180.0,
                duration_minutes=120,
                description="Higienização completa do interior incluindo estofados"
            ),
            "Higienização de Bancos": ServiceInfo(
                name="Higienização de Bancos",
                category=VehicleCategory.PEQUENO,
                price_p=80.0,
                price_g=100.0,
                duration_minutes=60,
                description="Limpeza profunda e higienização de bancos"
            )
        }

    async def chat(self, message: str, session_id: Optional[str] = None) -> ChatResponse:
        """Process chat message with Luciano agent"""
        try:
            # Generate or use existing session ID
            if not session_id:
                session_id = self._generate_session_id()

            # Get or create session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "messages": [],
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "stage": "initial",  # initial, system_choice, whatsapp_attendance, completed
                    "customer_data": {}
                }

            session = self.sessions[session_id]
            session["last_activity"] = datetime.now()

            # Add message to session
            from langchain_core.messages import HumanMessage, AIMessage
            session["messages"].append(HumanMessage(content=message))

            # Get response from agent
            config = {"configurable": {"thread_id": session_id}}
            result = self.graph.invoke(
                {"messages": session["messages"]},
                config=config
            )

            # Extract response
            agent_response = result["messages"][-1].content
            session["messages"].append(AIMessage(content=agent_response))

            # Analyze intent and detect next action
            intent_detected = self._detect_intent(message)
            next_action = self._determine_next_action(session, agent_response)

            return ChatResponse(
                response=agent_response,
                session_id=session_id,
                intent_detected=intent_detected,
                next_action=next_action
            )

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            raise

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(datetime.now().timestamp())
        hash_object = hashlib.md5(timestamp.encode())
        return f"session_{hash_object.hexdigest()[:12]}"

    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()

        # Price-related intents
        if any(word in message_lower for word in ['quanto', 'preço', 'valor', 'custa', 'sai']):
            return 'price_inquiry'

        # Service-related intents
        if any(word in message_lower for word in ['serviço', 'fazem', 'faz', 'tipo']):
            return 'service_inquiry'

        # Scheduling intents
        if any(word in message_lower for word in ['agendar', 'horário', 'agenda', 'vaga', 'marcar']):
            return 'scheduling'

        # Information intents
        if any(word in message_lower for word in ['endereço', 'localização', 'contato', 'telefone']):
            return 'contact_info'

        # General inquiry
        return 'general_inquiry'

    def _determine_next_action(self, session: Dict, agent_response: str) -> Optional[str]:
        """Determine next action based on session and response"""
        # Check if user is being directed to system
        if 'vanluagendamento.online' in agent_response and 'sistema' in agent_response.lower():
            return 'redirect_to_system'

        # Check if appointment is being completed
        if 'agendado para' in agent_response and 'te espero' in agent_response.lower():
            return 'appointment_confirmed'

        # Check if more information is needed
        if '?' in agent_response and agent_response.strip().endswith('?'):
            return 'request_more_info'

        return None

    def get_service_price(self, service_name: str, category: VehicleCategory) -> float:
        """Get price for service based on vehicle category"""
        if service_name in self.service_pricing:
            service = self.service_pricing[service_name]
            return service.price_g if category == VehicleCategory.GRANDE else service.price_p
        return 0.0

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> Dict[str, Dict]:
        """Get all active sessions"""
        return self.sessions

    def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > timedelta(hours=timeout_hours):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

class WebScrapingService:
    """Service for web scraping operations using MCP Firecrawl"""

    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.base_url = "https://api.firecrawl.dev/v1"

    async def scrape_url(self, request: ScrapeRequest) -> ScrapeResponse:
        """Scrape a single URL"""
        try:
            if not self.api_key:
                return ScrapeResponse(
                    success=False,
                    message="FIRECRAWL_API_KEY not configured",
                    url=request.url,
                    content={}
                )

            # TODO: Implement MCP Firecrawl integration
            # This is a placeholder implementation
            return ScrapeResponse(
                success=True,
                message="MCP Firecrawl integration coming soon",
                url=request.url,
                content={"status": "placeholder"}
            )

        except Exception as e:
            logger.error(f"Error in scrape service: {str(e)}")
            raise

    async def crawl_website(self, request: CrawlRequest) -> CrawlResponse:
        """Crawl an entire website"""
        try:
            if not self.api_key:
                return CrawlResponse(
                    success=False,
                    message="FIRECRAWL_API_KEY not configured",
                    crawl_id="",
                    status="failed"
                )

            # TODO: Implement MCP Firecrawl crawling
            # This is a placeholder implementation
            crawl_id = f"crawl_{datetime.now().timestamp()}"

            return CrawlResponse(
                success=True,
                message="Crawl started successfully",
                crawl_id=crawl_id,
                status="started"
            )

        except Exception as e:
            logger.error(f"Error in crawl service: {str(e)}")
            raise

class CompetitorAnalysisService:
    """Service for competitor analysis and market research"""

    def __init__(self, scraping_service: WebScrapingService):
        self.scraping_service = scraping_service

    async def analyze_competitor(self, competitor_url: str) -> CompetitorAnalysis:
        """Analyze a competitor website"""
        try:
            # Scrape competitor website
            scrape_request = ScrapeRequest(
                url=competitor_url,
                formats=["markdown"],
                only_main_content=True
            )

            scrape_result = await self.scraping_service.scrape_url(scrape_request)

            if not scrape_result.success:
                return CompetitorAnalysis(
                    success=False,
                    message="Failed to scrape competitor website",
                    competitor_name="Unknown",
                    website=competitor_url,
                    services_offered=[],
                    price_ranges={},
                    contact_info={},
                    strengths=[],
                    weaknesses=[]
                )

            # TODO: Implement competitor analysis logic
            # Extract services, prices, contact info, etc.
            content = scrape_result.content

            return CompetitorAnalysis(
                success=True,
                competitor_name="Analysis Pending",
                website=competitor_url,
                services_offered=[],
                price_ranges={},
                contact_info={},
                strengths=[],
                weaknesses=[]
            )

        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            raise

    async def search_competitors(self, location: str = "Aracaju") -> List[Dict[str, Any]]:
        """Search for competitors in a specific location"""
        try:
            # Use Tavily search to find competitors
            from langchain_community.tools.tavily_search import TavilySearchResults

            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                raise ValueError("TAVILY_API_KEY not configured")

            search_tool = TavilySearchResults(max_results=10, api_key=tavily_api_key)
            query = f"estética automotiva detalhe carros {location} concorrentes empresas"

            results = search_tool.invoke(query)

            # Process and structure results
            competitors = []
            for result in results if isinstance(results, list) else [results]:
                if isinstance(result, dict) and 'url' in result:
                    competitors.append({
                        'name': result.get('title', 'Unknown'),
                        'url': result.get('url'),
                        'snippet': result.get('content', ''),
                        'source': 'tavily_search'
                    })

            return competitors

        except Exception as e:
            logger.error(f"Error searching competitors: {str(e)}")
            raise

class AnalyticsService:
    """Service for analytics and reporting"""

    def __init__(self, agent_service: LucianoAgentService):
        self.agent_service = agent_service

    def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get conversation analytics"""
        sessions = self.agent_service.get_all_sessions()

        total_conversations = len(sessions)
        completed_appointments = 0

        intents = {}
        vehicle_models = {}

        for session in sessions.values():
            # Count intents
            for message in session.get("messages", []):
                if hasattr(message, 'content'):
                    intent = self.agent_service._detect_intent(message.content)
                    intents[intent] = intents.get(intent, 0) + 1

            # Check if appointment was completed
            customer_data = session.get("customer_data", {})
            if customer_data.get("appointment_confirmed"):
                completed_appointments += 1

        conversion_rate = (completed_appointments / total_conversations * 100) if total_conversations > 0 else 0

        return {
            "total_conversations": total_conversations,
            "completed_appointments": completed_appointments,
            "conversion_rate": round(conversion_rate, 2),
            "top_intents": sorted(intents.items(), key=lambda x: x[1], reverse=True)[:5],
            "popular_vehicles": sorted(vehicle_models.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        session = self.agent_service.get_session_info(session_id)

        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "message_count": len(session.get("messages", [])),
            "duration": (session["last_activity"] - session["created_at"]).total_seconds(),
            "stage": session.get("stage", "unknown"),
            "has_customer_data": bool(session.get("customer_data"))
        }

# Service instances
luciano_service = None
scraping_service = None
competitor_service = None
analytics_service = None

def initialize_services(graph, tools):
    """Initialize all service instances"""
    global luciano_service, scraping_service, competitor_service, analytics_service

    luciano_service = LucianoAgentService(graph, tools)
    scraping_service = WebScrapingService()
    competitor_service = CompetitorAnalysisService(scraping_service)
    analytics_service = AnalyticsService(luciano_service)

    logger.info("All services initialized successfully")

def get_services():
    """Get all service instances"""
    return {
        "luciano": luciano_service,
        "scraping": scraping_service,
        "competitor": competitor_service,
        "analytics": analytics_service
    }