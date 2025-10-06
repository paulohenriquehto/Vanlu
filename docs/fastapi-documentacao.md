# Documentação Oficial FastAPI

## 📋 **Visão Geral**

FastAPI é um framework web moderno e de alta performance para construção de APIs com Python, baseado nos padrões de tipo Python 3.6+.

### Características Principais
- **Alto desempenho**: Comparável a NodeJS e Go
- **Código rápido**: Acelera o desenvolvimento em 200-300%
- **Menos bugs**: Reduz bugs humanos em ~40%
- **Intuitivo**: Excelente suporte a editor com auto-completação
- **Fácil**: Projetado para ser fácil de usar e aprender
- **Curto**: Minimiza duplicação de código
- **Robusto**: Obtém código pronto para produção
- **Baseado em padrões**: Baseado em padrões abertos para APIs

---

## 🚀 **Conceitos Básicos**

### Instalação
```bash
pip install fastapi
pip install "uvicorn[standard]"
```

### Aplicação Mínima
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Executando a Aplicação
```bash
uvicorn main:app --reload
```

---

## 🛤️ **Rotas e Parâmetros**

### Parâmetros de Path
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### Parâmetros de Query
```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_item(q: Union[str, None] = None):
    return {"q": q}
```

### Parâmetros de Path com Validações
```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(title="The ID of the item to get", gt=0, le=1000)
):
    return {"item_id": item_id}
```

---

## 📝 **Request Body**

### Pydantic Models
```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
```

### Usando Pydantic Models
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

---

## 🔍 **Validação de Dados**

### Tipos de Dados
```python
from typing import Union
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
```

### Validação com Field
```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(None, max_length=300)
    price: float = Field(..., gt=0)
    tax: float = Field(None, ge=0)
```

---

## 🧪 **Testando sua API**

### TestClient
```python
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

### Executando Testes
```bash
pytest
```

---

## 🏗️ **Deploy**

### Requisitos de Produção
- **Servidor ASGI**: Uvicorn, Gunicorn com Uvicorn workers, Hypercorn
- **Process Manager**: Systemd, Docker, Kubernetes
- **Proxy de Produção**: Nginx, Traefik

### Docker Deployment
```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - DATABASE_URL=postgresql://user:password@db/db
    depends_on:
      - db

  db:
    image: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password

volumes:
  postgres_data:
```

---

## 🔧 **Configurações Avançadas**

### CORS
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Settings com Pydantic
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 📚 **Middleware e Injeção de Dependência**

### Middleware Personalizado
```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Injeção de Dependência
```python
from fastapi import Depends, FastAPI
from typing import Annotated

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

---

## 🚨 **Error Handling**

### HTTPException
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}
```

### Exception Handlers Personalizados
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
```

---

## 📊 **Background Tasks**

### BackgroundTasks
```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Some notification")
    return {"message": "Notification sent in the background"}
```

---

## 🔄 **WebSockets**

### WebSocket Handler
```python
from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

---

## 📖 **Documentação e Swagger**

### Informações Customizadas
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Acessando Documentação
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## ⚡ **Melhores Práticas**

### Estrutura de Projeto
```
app/
├── __init__.py
├── main.py
├── dependencies.py
├── routers/
│   ├── __init__.py
│   ├── items.py
│   └── users.py
└── models/
    ├── __init__.py
    ├── item.py
    └── user.py
```

### Roteamento Módular
```python
# routers/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_items():
    return [{"name": "Item Foo"}, {"name": "item Bar"}]

# main.py
from fastapi import FastAPI
from .routers import items, users

app = FastAPI()
app.include_router(items.router)
app.include_router(users.router)
```

### Logging
```python
import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    logger.info("Hello world endpoint called")
    return {"message": "Hello World"}
```

---

## 📝 **Conclusão**

FastAPI é um framework poderoso e moderno que combina simplicidade com performance. Suas principais vantagens são:

1. **Performance excepcional** baseada em Starlette e Pydantic
2. **Autocompletação automática** e validação de dados
3. **Documentação interativa** gerada automaticamente
4. **Suporte nativo a async/await**
5. **Ecossistema robusto** com extensões e middleware

**Recomendações para Produção:**
- Use servidores ASGI como Uvicorn ou Hypercorn
- Implemente CORS e headers de segurança
- Configure logging e monitoramento
- Utilize Docker para consistência de ambiente
- Configure process managers como systemd ou Kubernetes

---

*Documentação compilada da documentação oficial do FastAPI*
*Versão: FastAPI 0.104+*