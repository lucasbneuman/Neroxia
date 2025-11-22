# Plan de Migración a Microservicios

## Objetivo
Reorganizar el proyecto whatsapp_sales_bot de arquitectura monolítica a microservicios **SIN romper funcionalidad existente**.

## Estado Actual del Proyecto

### Estructura Actual
```
whatsapp_sales_bot/
├── app.py                      # 35KB - Aplicación Gradio principal
├── main.py                     # 4KB - Entry point alternativo
├── whatsapp_webhook.py         # 8KB - Webhook de WhatsApp
├── reset_config.py             # 2KB - Script de reset
├── test_hubspot.py             # 6KB - Tests de HubSpot
├── graph/                      # LangGraph (11 nodos)
│   ├── nodes.py               # 24KB - Nodos del grafo
│   ├── state.py               # 1.5KB - Estado del grafo
│   └── workflow.py            # 5KB - Definición del workflow
├── services/                   # Servicios externos
│   ├── config_manager.py      # 5KB - Gestión de configuración
│   ├── hubspot_sync.py        # 18KB - Integración HubSpot
│   ├── llm_service.py         # 20KB - Servicio LLM
│   ├── rag_service.py         # 7KB - RAG con ChromaDB
│   ├── scheduler_service.py   # 4KB - Scheduler
│   ├── tts_service.py         # 3KB - Text-to-Speech OpenAI
│   └── twilio_service.py      # 4KB - Servicio Twilio
├── database/                   # Capa de datos
│   ├── models.py              # 4KB - Modelos SQLite
│   └── crud.py                # 11KB - Operaciones CRUD
├── utils/                      # Utilidades
│   ├── helpers.py             # 4KB - Funciones auxiliares
│   └── logging_config.py      # 1.7KB - Configuración de logs
├── gradio_ui/                  # Interfaz Gradio
│   ├── chat_component_v2.py   # 4KB - Componente de chat
│   ├── config_panel.py        # 11KB - Panel de configuración
│   ├── config_panel_v2.py     # 15KB - Panel v2
│   ├── conversations_panel.py # 9KB - Panel de conversaciones
│   ├── data_viewer.py         # 3KB - Visor de datos
│   └── live_chats_panel.py    # 12KB - Panel de chats en vivo
└── tests/                      # Tests
    ├── conftest.py            # 1.8KB - Configuración pytest
    ├── test_llm_service.py    # 6KB - Tests LLM
    ├── test_message_formatting.py # 4KB - Tests formateo
    └── test_nodes.py          # 5KB - Tests nodos
```

### Archivos de Configuración
- `.env` - Variables de entorno (856 bytes)
- `.env.example` - Template de variables (1.7KB)
- `.gitignore` - Exclusiones Git (651 bytes)
- `.python-version` - Versión Python
- `pytest.ini` - Configuración pytest
- `requirements.txt` - Dependencias (826 bytes)
- `runtime.txt` - Runtime info

### Documentación
- `README.md` - Documentación principal (10KB)
- `HUBSPOT_SETUP.md` - Setup de HubSpot (6KB)
- `TODO.md` - Lista de tareas (2KB)

### Datos
- `sales_bot.db` - Base de datos SQLite (64KB)
- `chroma_db/` - Base de datos vectorial ChromaDB

---

## Nueva Estructura de Microservicios

```
whatsapp_sales_bot/
├── apps/
│   ├── web/                    # Frontend Next.js (NUEVO)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   └── lib/
│   │   ├── package.json
│   │   └── next.config.js
│   │
│   ├── api/                    # Backend FastAPI
│   │   ├── src/
│   │   │   ├── routers/       # Endpoints REST
│   │   │   ├── middleware/
│   │   │   └── main.py        # FastAPI app
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── bot-engine/             # Motor LangGraph
│       ├── src/
│       │   ├── graph/         # Nodos y workflow
│       │   ├── services/      # Servicios externos
│       │   └── main.py        # Entry point
│       ├── requirements.txt
│       └── Dockerfile
│
├── packages/
│   ├── database/               # Modelos compartidos
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── setup.py
│   │
│   └── shared/                 # Utils compartidos
│       ├── __init__.py
│       ├── helpers.py
│       ├── logging_config.py
│       └── setup.py
│
├── infrastructure/
│   ├── docker/
│   │   └── docker-compose.yml
│   ├── k8s/                    # Kubernetes (futuro)
│   └── nginx/                  # Reverse proxy
│
├── legacy/
│   └── gradio/                 # Backup Gradio UI
│       └── (archivos actuales de gradio_ui/)
│
├── scripts/
│   ├── migrate.py              # Script de migración
│   ├── reset_config.py
│   └── test_hubspot.py
│
├── tests/                      # Tests integración
│   └── e2e/
│
├── .env
├── .gitignore
├── README.md
└── MIGRATION_PLAN.md (este archivo)
```

---

## Mapeo de Archivos: Actual → Nuevo

### 1. Bot Engine (apps/bot-engine/)

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `graph/nodes.py` | `apps/bot-engine/src/graph/nodes.py` | Sin cambios en lógica |
| `graph/state.py` | `apps/bot-engine/src/graph/state.py` | Sin cambios |
| `graph/workflow.py` | `apps/bot-engine/src/graph/workflow.py` | Sin cambios |
| `services/llm_service.py` | `apps/bot-engine/src/services/llm_service.py` | Sin cambios |
| `services/rag_service.py` | `apps/bot-engine/src/services/rag_service.py` | Sin cambios |
| `services/tts_service.py` | `apps/bot-engine/src/services/tts_service.py` | Sin cambios |
| `services/hubspot_sync.py` | `apps/bot-engine/src/services/hubspot_sync.py` | Sin cambios |
| `services/twilio_service.py` | `apps/bot-engine/src/services/twilio_service.py` | Sin cambios |
| `services/scheduler_service.py` | `apps/bot-engine/src/services/scheduler_service.py` | Sin cambios |
| `services/config_manager.py` | `apps/bot-engine/src/services/config_manager.py` | Sin cambios |
| `main.py` | `apps/bot-engine/src/main.py` | Adaptar como entry point |

### 2. API Backend (apps/api/)

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `whatsapp_webhook.py` | `apps/api/src/routers/webhook.py` | Convertir a router FastAPI |
| `app.py` (lógica API) | `apps/api/src/main.py` | Extraer lógica no-Gradio |
| - | `apps/api/src/routers/conversations.py` | NUEVO - Endpoints conversaciones |
| - | `apps/api/src/routers/config.py` | NUEVO - Endpoints configuración |
| - | `apps/api/src/routers/analytics.py` | NUEVO - Endpoints analytics |

### 3. Packages Compartidos

#### packages/database/

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `database/models.py` | `packages/database/models.py` | Sin cambios |
| `database/crud.py` | `packages/database/crud.py` | Sin cambios |
| - | `packages/database/__init__.py` | Exportar modelos |
| - | `packages/database/setup.py` | Para instalación local |

#### packages/shared/

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `utils/helpers.py` | `packages/shared/helpers.py` | Sin cambios |
| `utils/logging_config.py` | `packages/shared/logging_config.py` | Sin cambios |
| - | `packages/shared/__init__.py` | Exportar utils |
| - | `packages/shared/setup.py` | Para instalación local |

### 4. Legacy (Backup Gradio)

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `gradio_ui/` (todo) | `legacy/gradio/` | Backup completo |
| `app.py` | `legacy/gradio/app.py` | Backup app Gradio |

### 5. Scripts

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `reset_config.py` | `scripts/reset_config.py` | Sin cambios |
| `test_hubspot.py` | `scripts/test_hubspot.py` | Sin cambios |

### 6. Tests

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `tests/conftest.py` | `apps/bot-engine/tests/conftest.py` | Mover a bot-engine |
| `tests/test_llm_service.py` | `apps/bot-engine/tests/test_llm_service.py` | Tests de servicios |
| `tests/test_message_formatting.py` | `apps/bot-engine/tests/test_message_formatting.py` | Tests de formateo |
| `tests/test_nodes.py` | `apps/bot-engine/tests/test_nodes.py` | Tests de nodos |

### 7. Configuración y Docs

| Archivo Actual | Nueva Ubicación | Notas |
|----------------|-----------------|-------|
| `.env` | `.env` (raíz) | Mantener en raíz |
| `.env.example` | `.env.example` (raíz) | Mantener en raíz |
| `.gitignore` | `.gitignore` (raíz) | Actualizar con nuevas carpetas |
| `requirements.txt` | Dividir en 3 archivos | Ver sección siguiente |
| `README.md` | `README.md` (raíz) | Actualizar con nueva estructura |
| `HUBSPOT_SETUP.md` | `docs/HUBSPOT_SETUP.md` | Mover a docs/ |
| `TODO.md` | `TODO.md` (raíz) | Mantener en raíz |

### 8. Datos (NO MOVER)

| Archivo Actual | Acción | Notas |
|----------------|--------|-------|
| `sales_bot.db` | Mantener en raíz | NO mover, actualizar paths |
| `chroma_db/` | Mantener en raíz | NO mover, actualizar paths |

---

## Orden de Migración (Fases)

### FASE 0: Preparación ✅ (COMPLETADO)
- [x] Crear estructura de carpetas vacías
- [x] Crear MIGRATION_PLAN.md
- [x] Actualizar .gitignore
- [x] Commit inicial

### FASE 1: Packages Compartidos ✅ (COMPLETADO)
1. Crear `packages/database/`
   - Copiar `database/models.py`
   - Copiar `database/crud.py`
   - Crear `__init__.py` y `setup.py`
   - Instalar como package local: `pip install -e packages/database`

2. Crear `packages/shared/`
   - Copiar `utils/helpers.py`
   - Copiar `utils/logging_config.py`
   - Crear `__init__.py` y `setup.py`
   - Instalar como package local: `pip install -e packages/shared`

### FASE 2: Bot Engine
1. Crear estructura `apps/bot-engine/src/`
2. Copiar carpeta `graph/` completa
3. Copiar carpeta `services/` completa
4. Copiar `main.py` y adaptar
5. Crear `requirements.txt` específico
6. Actualizar imports para usar packages compartidos
7. Mover tests a `apps/bot-engine/tests/`
8. Verificar que funciona standalone

### FASE 3: API Backend ✅ (COMPLETADO)
1. Crear estructura `apps/api/src/`
2. Crear `main.py` con FastAPI
3. Convertir `whatsapp_webhook.py` a router
4. Crear routers adicionales (conversations, config, analytics)
5. Crear `requirements.txt` específico
6. Actualizar imports
7. Crear tests de API

### FASE 4: Frontend Web ✅ (COMPLETADO)
1. Inicializar proyecto Next.js en `apps/web/`
2. Crear componentes básicos
3. Integrar con API backend
4. Implementar autenticación
5. Migrar funcionalidad de Gradio UI

### FASE 5: Legacy Backup
1. Copiar `gradio_ui/` completo a `legacy/gradio/`
2. Copiar `app.py` a `legacy/gradio/`
3. Documentar cómo ejecutar versión legacy

### FASE 6: Infrastructure
1. Crear `docker-compose.yml`
2. Crear Dockerfiles para cada app
3. Configurar nginx como reverse proxy
4. Documentar deployment

### FASE 7: Limpieza Final
1. Eliminar archivos antiguos de la raíz
2. Actualizar README.md
3. Actualizar documentación
4. Tests end-to-end completos

---

## Cambios de Imports

### Antes (Monolito)
```python
# En cualquier archivo
from database.models import Conversation, Message
from database.crud import get_conversation, create_message
from utils.helpers import format_phone_number
from utils.logging_config import setup_logging
from services.llm_service import LLMService
from graph.nodes import process_message
```

### Después (Microservicios)

#### En apps/bot-engine/
```python
# Packages compartidos
from whatsapp_bot_database.models import Conversation, Message
from whatsapp_bot_database.crud import get_conversation, create_message
from whatsapp_bot_shared.helpers import format_phone_number
from whatsapp_bot_shared.logging_config import setup_logging

# Módulos locales
from src.services.llm_service import LLMService
from src.graph.nodes import process_message
```

#### En apps/api/
```python
# Packages compartidos
from whatsapp_bot_database.models import Conversation, Message
from whatsapp_bot_database.crud import get_conversation, create_message
from whatsapp_bot_shared.helpers import format_phone_number

# Módulos locales
from src.routers.webhook import router as webhook_router
```

---

## Dependencias (requirements.txt)

### Actual (Monolito)
```
langchain==0.3.13
langchain-openai==0.2.14
langgraph==0.2.59
gradio==5.9.1
chromadb==0.5.23
hubspot-api-client==9.4.0
twilio==9.4.0
python-dotenv==1.0.1
sqlalchemy==2.0.36
pytest==8.3.4
pytest-asyncio==0.24.0
```

### Nuevo (Dividido)

#### apps/bot-engine/requirements.txt
```
langchain==0.3.13
langchain-openai==0.2.14
langgraph==0.2.59
chromadb==0.5.23
hubspot-api-client==9.4.0
twilio==9.4.0
python-dotenv==1.0.1
openai>=1.0.0  # Para TTS
-e ../../packages/database
-e ../../packages/shared
```

#### apps/api/requirements.txt
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-dotenv==1.0.1
pydantic==2.10.0
twilio==9.4.0
-e ../../packages/database
-e ../../packages/shared
```

#### apps/web/package.json (Next.js)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.6.0"
  }
}
```

---

## Configuración de Variables de Entorno

### Estructura Actual (.env)
```
OPENAI_API_KEY=...
HUBSPOT_ACCESS_TOKEN=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

### Nueva Estructura (Compartida)
- Mantener `.env` en la raíz
- Cada app lo lee desde la raíz
- Usar `python-dotenv` con path relativo

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Romper imports existentes | Alto | Migrar por fases, mantener legacy funcionando |
| Perder datos de ChromaDB | Alto | NO mover `chroma_db/`, solo actualizar paths |
| Perder datos SQLite | Alto | NO mover `sales_bot.db`, solo actualizar paths |
| Incompatibilidad de versiones | Medio | Mantener mismas versiones en requirements |
| Tests fallando | Medio | Ejecutar tests después de cada fase |
| Gradio UI dejando de funcionar | Bajo | Mantener backup completo en `legacy/` |

---

## Checklist de Verificación Post-Migración

### Bot Engine
- [ ] LangGraph workflow funciona
- [ ] 11 nodos ejecutan correctamente
- [ ] RAG con ChromaDB funciona
- [ ] HubSpot sync funciona
- [ ] TTS genera audios
- [ ] Twilio envía mensajes
- [ ] Tests pasan

### API Backend
- [ ] Webhook de WhatsApp responde
- [ ] Endpoints de conversaciones funcionan
- [ ] Endpoints de configuración funcionan
- [ ] Base de datos SQLite accesible
- [ ] Tests de API pasan

### Packages
- [ ] `whatsapp_bot_database` instalado
- [ ] `whatsapp_bot_shared` instalado
- [ ] Imports funcionan en todas las apps

### General
- [ ] Variables de entorno se leen correctamente
- [ ] Logs se generan correctamente
- [ ] No hay errores de imports
- [ ] Versión legacy de Gradio funciona
- [ ] README actualizado

---

## Comandos Útiles

### Instalar packages locales
```bash
# Desde la raíz del proyecto
pip install -e packages/database
pip install -e packages/shared
```

### Ejecutar bot-engine standalone
```bash
cd apps/bot-engine
python -m src.main
```

### Ejecutar API backend
```bash
cd apps/api
uvicorn src.main:app --reload
```

### Ejecutar tests
```bash
# Bot engine
cd apps/bot-engine
pytest tests/

# API
cd apps/api
pytest tests/
```

### Docker Compose (futuro)
```bash
docker-compose up --build
```

---

## Notas Importantes

1. **NO ROMPER FUNCIONALIDAD**: La prioridad #1 es mantener todo funcionando
2. **MIGRACIÓN GRADUAL**: Hacer una fase a la vez, verificar antes de continuar
3. **MANTENER LEGACY**: El Gradio UI actual debe seguir funcionando hasta que el nuevo frontend esté listo
4. **DATOS INTACTOS**: NO mover `sales_bot.db` ni `chroma_db/`
5. **MISMAS VERSIONES**: Mantener las mismas versiones de dependencias
6. **TESTS PRIMERO**: Ejecutar tests después de cada cambio
7. **COMMITS FRECUENTES**: Hacer commit después de cada fase exitosa

---

## Próximos Pasos Inmediatos

1. ✅ Crear estructura de carpetas (COMPLETADO)
2. ✅ Crear MIGRATION_PLAN.md (COMPLETADO)
3. ⏳ Actualizar .gitignore
4. ⏳ Commit inicial
5. ✅ Iniciar FASE 1: Packages Compartidos
6. ✅ Iniciar FASE 3: API Backend
7. ✅ Iniciar FASE 4: Frontend Web

---

**Fecha de creación**: 2025-11-22  
**Rama**: saas-migration  
**Autor**: Architect Agent
