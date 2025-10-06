"""
Pydantic models for Vanlu API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums
class VehicleCategory(str, Enum):
    PEQUENO = "P"  # Hatch, Sedã, Coupé, Compactos
    GRANDE = "G"   # SUV, Caminhonete, Pickup, Utilitários

class ServiceType(str, Enum):
    PREVENTIVA = "Preventiva"
    PREMIUM = "Premium"
    MASTER = "Master"
    POLIMENTO = "Polimento"
    VITRIFICACAO = "Vitrificação"
    INTERNA = "Limpeza Interna"
    HIGIENIZACAO = "Higienização"

class AttendanceType(str, Enum):
    WHATSAPP = "whatsapp"
    SYSTEM = "system"

# Base Models
class BaseResponse(BaseModel):
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = None

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: str
    error_detail: Optional[str] = None

# Chat Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem do cliente")
    session_id: Optional[str] = Field(None, description="ID da sessão para continuidade")
    user_id: Optional[str] = Field(None, description="ID do usuário")

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Mensagem não pode ser vazia')
        return v.strip()

class ChatResponse(BaseResponse):
    response: str = Field(..., description="Resposta do agente Luciano")
    session_id: str = Field(..., description="ID da sessão")
    intent_detected: Optional[str] = Field(None, description="Intenção detectada pelo agente")
    next_action: Optional[str] = Field(None, description="Próxima ação sugerida")

# Session Models
class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    user_id: Optional[str] = None
    status: Literal["active", "completed", "abandoned"] = "active"

class SessionList(BaseResponse):
    total_sessions: int
    sessions: List[SessionInfo]

# Appointment Models
class VehicleInfo(BaseModel):
    model: str = Field(..., min_length=2, description="Modelo do veículo")
    year: int = Field(..., ge=2000, le=2025, description="Ano do veículo")
    category: Optional[VehicleCategory] = Field(None, description="Categoria do veículo (calculada automaticamente)")

    @validator('category', always=True)
    def calculate_category(cls, v, values):
        if 'model' in values:
            model = values['model'].lower()
            # Categoria G: SUV, Caminhonete, Pickup, Utilitários
            suv_keywords = ['suv', 'hr-v', 'compass', 't-cross', 'tracker', 'creta', 'duster', 'renegade', 'tucson']
            pickup_keywords = ['hilux', 'ranger', 's10', 'saveiro', 'strada', 'toro']
            truck_keywords = ['amarok', 'l200', 'fiorino', 'ducato']

            if (any(keyword in model for keyword in suv_keywords) or
                any(keyword in model for keyword in pickup_keywords) or
                any(keyword in model for keyword in truck_keywords)):
                return VehicleCategory.GRANDE

        return VehicleCategory.PEQUENO

class CustomerInfo(BaseModel):
    name: str = Field(..., min_length=3, description="Nome completo do cliente")
    phone: str = Field(..., description="Telefone de contato")
    email: Optional[str] = Field(None, description="Email do cliente")

    @validator('phone')
    def validate_phone(cls, v):
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, v))
        if len(clean_phone) < 10 or len(clean_phone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return v

class AppointmentRequest(BaseModel):
    vehicle: VehicleInfo
    service: ServiceType
    preferred_date: str = Field(..., description="Data preferida (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Horário preferido (HH:MM)")
    customer: CustomerInfo
    notes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    session_id: str = Field(..., description="ID da sessão de chat")

    @validator('preferred_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Data deve estar no formato YYYY-MM-DD')
        return v

    @validator('preferred_time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('Horário deve estar no formato HH:MM')
        return v

class AppointmentResponse(BaseResponse):
    appointment_id: str
    confirmation_message: str
    scheduled_date: datetime
    service: ServiceType
    vehicle: VehicleInfo
    total_price: float

# Service Models
class ServiceInfo(BaseModel):
    name: str
    category: VehicleCategory
    price_p: float = Field(..., description="Preço para categoria P")
    price_g: float = Field(..., description="Preço para categoria G")
    duration_minutes: int = Field(..., description="Duração em minutos")
    description: Optional[str] = None

class ServiceList(BaseResponse):
    services: List[ServiceInfo]

# Web Scraping Models
class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL para fazer scraping")
    formats: List[Literal["markdown", "html", "rawHtml", "json", "screenshot", "links"]] = Field(
        default=["markdown"], description="Formatos de saída desejados"
    )
    only_main_content: bool = Field(default=True, description="Extrair apenas conteúdo principal")
    wait_for: Optional[int] = Field(None, description="Tempo de espera em ms")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Ações a executar antes do scraping")

    @validator('url')
    def validate_url(cls, v):
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL deve começar com http:// ou https://')
        return v

class ScrapeResponse(BaseResponse):
    url: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class CrawlRequest(BaseModel):
    url: str = Field(..., description="URL base para crawling")
    limit: int = Field(default=10, ge=1, le=100, description="Número máximo de páginas")
    max_depth: int = Field(default=3, ge=1, le=10, description="Profundidade máxima")
    include_paths: Optional[List[str]] = Field(None, description="Paths para incluir")
    exclude_paths: Optional[List[str]] = Field(None, description="Paths para excluir")
    scrape_options: Optional[ScrapeRequest] = Field(None, description="Opções de scraping")

class CrawlResponse(BaseResponse):
    crawl_id: str
    status: Literal["started", "completed", "failed"]
    results: Optional[List[ScrapeResponse]] = None

# Search Models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Termo de busca")
    sources: List[Literal["web", "news", "images"]] = Field(default=["web"], description="Fontes de busca")
    limit: int = Field(default=10, ge=1, le=50, description="Número máximo de resultados")
    scrape_results: bool = Field(default=False, description="Fazer scraping dos resultados")

class SearchResponse(BaseResponse):
    query: str
    results: List[Dict[str, Any]]
    total_found: int

# Analytics Models
class ConversationAnalytics(BaseResponse):
    total_conversations: int
    completed_appointments: int
    conversion_rate: float
    average_response_time: float
    most_requested_services: List[Dict[str, Any]]
    popular_vehicles: List[Dict[str, Any]]

class CompetitorAnalysis(BaseResponse):
    competitor_name: str
    website: str
    services_offered: List[str]
    price_ranges: Dict[str, Any]
    contact_info: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]

# Health Check Models
class HealthStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    uptime: str
    services: Dict[str, Literal["running", "stopped", "error"]]

# Configuration Models
class APIConfiguration(BaseModel):
    openai_model: str = "gpt-4.1-mini"
    max_sessions: int = 1000
    session_timeout: int = 3600  # seconds
    max_message_length: int = 1000
    enable_analytics: bool = True
    enable_scraping: bool = True