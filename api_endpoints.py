"""
FastAPI endpoints for Vanlu API
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from models import (
    ChatMessage, ChatResponse, ScrapeRequest, ScrapeResponse,
    CrawlRequest, CrawlResponse, SearchRequest, SearchResponse,
    AppointmentRequest, AppointmentResponse, SessionInfo, SessionList,
    HealthStatus, CompetitorAnalysis
)
from services import get_services

logger = logging.getLogger(__name__)

# Create routers
api_router = APIRouter(prefix="/api/v1")
chat_router = APIRouter(prefix="/chat", tags=["chat"])
scraping_router = APIRouter(prefix="/scraping", tags=["web-scraping"])
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])
admin_router = APIRouter(prefix="/admin", tags=["administration"])

# Chat endpoints
@chat_router.post("/", response_model=ChatResponse)
async def chat_with_luciano(
    message: ChatMessage,
    background_tasks: BackgroundTasks
):
    """Chat com o agente Luciano"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        # Process message
        response = await luciano_service.chat(message.message, message.session_id)

        # Add cleanup task in background
        background_tasks.add_task(luciano_service.cleanup_expired_sessions)

        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/sessions", response_model=SessionList)
async def list_chat_sessions():
    """List all active chat sessions"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        sessions = luciano_service.get_all_sessions()

        session_list = []
        for session_id, session_data in sessions.items():
            session_info = SessionInfo(
                session_id=session_id,
                created_at=session_data["created_at"],
                last_activity=session_data["last_activity"],
                message_count=len(session_data.get("messages", [])),
                status="active"
            )
            session_list.append(session_info)

        return SessionList(
            total_sessions=len(sessions),
            sessions=session_list
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_details(session_id: str):
    """Get details of a specific session"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        session_data = luciano_service.get_session_info(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionInfo(
            session_id=session_id,
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            message_count=len(session_data.get("messages", [])),
            status="active"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        sessions = luciano_service.get_all_sessions()
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        del sessions[session_id]

        return {"message": f"Session {session_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(appointment: AppointmentRequest):
    """Create a new appointment from chat session"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        # Verify session exists
        session_data = luciano_service.get_session_info(appointment.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Calculate price
        price = luciano_service.get_service_price(
            appointment.service.value,
            appointment.vehicle.category
        )

        # Create appointment confirmation message
        confirmation_message = (
            f"Pronto! Agendado para {appointment.preferred_date} às {appointment.preferred_time}, "
            f"{appointment.service.value} no seu {appointment.vehicle.model} {appointment.vehicle.year}. "
            f"Te espero aqui na Vanlu! 🚗"
        )

        # Update session with appointment data
        session_data["customer_data"] = {
            "appointment": appointment.dict(),
            "appointment_confirmed": True,
            "total_price": price
        }

        return AppointmentResponse(
            success=True,
            appointment_id=f"apt_{appointment.session_id}_{int(datetime.now().timestamp())}",
            confirmation_message=confirmation_message,
            scheduled_date=datetime.strptime(appointment.preferred_date, '%Y-%m-%d'),
            service=appointment.service,
            vehicle=appointment.vehicle,
            total_price=price
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Web scraping endpoints
@scraping_router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest):
    """Scrape a single website"""
    try:
        services = get_services()
        scraping_service = services["scraping"]

        if not scraping_service:
            raise HTTPException(status_code=503, detail="Scraping service not available")

        result = await scraping_service.scrape_url(request)
        return result

    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@scraping_router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest):
    """Crawl an entire website"""
    try:
        services = get_services()
        scraping_service = services["scraping"]

        if not scraping_service:
            raise HTTPException(status_code=503, detail="Scraping service not available")

        result = await scraping_service.crawl_website(request)
        return result

    except Exception as e:
        logger.error(f"Error in crawl endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@scraping_router.post("/search", response_model=SearchResponse)
async def search_competitors(
    query: str = Query(..., description="Search query"),
    location: str = Query(default="Aracaju", description="Location for search"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results")
):
    """Search for competitors and market information"""
    try:
        services = get_services()
        competitor_service = services["competitor"]

        if not competitor_service:
            raise HTTPException(status_code=503, detail="Competitor service not available")

        competitors = await competitor_service.search_competitors(location)

        # Filter and limit results
        filtered_competitors = competitors[:limit]

        return SearchResponse(
            success=True,
            query=query,
            results=filtered_competitors,
            total_found=len(competitors)
        )

    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@scraping_router.post("/analyze", response_model=CompetitorAnalysis)
async def analyze_competitor(url: str = Query(..., description="Competitor website URL")):
    """Analyze a specific competitor"""
    try:
        services = get_services()
        competitor_service = services["competitor"]

        if not competitor_service:
            raise HTTPException(status_code=503, detail="Competitor service not available")

        result = await competitor_service.analyze_competitor(url)
        return result

    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@analytics_router.get("/conversations")
async def get_conversation_analytics():
    """Get conversation analytics and statistics"""
    try:
        services = get_services()
        analytics_service = services["analytics"]

        if not analytics_service:
            raise HTTPException(status_code=503, detail="Analytics service not available")

        analytics = analytics_service.get_conversation_analytics()
        return analytics

    except Exception as e:
        logger.error(f"Error getting conversation analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/sessions/{session_id}")
async def get_session_analytics(session_id: str):
    """Get analytics for a specific session"""
    try:
        services = get_services()
        analytics_service = services["analytics"]

        if not analytics_service:
            raise HTTPException(status_code=503, detail="Analytics service not available")

        analytics = analytics_service.get_session_analytics(session_id)
        return analytics

    except Exception as e:
        logger.error(f"Error getting session analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints
@admin_router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check for all services"""
    try:
        services = get_services()

        # Check each service
        service_status = {}
        for name, service in services.items():
            if service:
                service_status[name] = "running"
            else:
                service_status[name] = "stopped"

        # Determine overall health
        all_running = all(status == "running" for status in service_status.values())
        overall_status = "healthy" if all_running else "degraded"

        return HealthStatus(
            status=overall_status,
            version="1.0.0",
            uptime="N/A",  # TODO: implement uptime tracking
            services=service_status
        )

    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return HealthStatus(
            status="unhealthy",
            version="1.0.0",
            uptime="N/A",
            services={"error": "unhealthy"}
        )

@admin_router.post("/cleanup")
async def cleanup_expired_sessions():
    """Manually cleanup expired sessions"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        # Clean up sessions
        luciano_service.cleanup_expired_sessions()

        return {"message": "Cleanup completed successfully"}

    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        services = get_services()
        luciano_service = services["luciano"]

        if not luciano_service:
            raise HTTPException(status_code=503, detail="Agent service not available")

        sessions = luciano_service.get_all_sessions()
        total_messages = sum(len(session.get("messages", [])) for session in sessions.values())

        return {
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "services_count": len(services),
            "active_services": len([s for s in services.values() if s]),
            "version": "1.0.0"
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include routers in main API router
api_router.include_router(chat_router)
api_router.include_router(scraping_router)
api_router.include_router(analytics_router)
api_router.include_router(admin_router)

# Export the main router
__all__ = ["api_router"]