# SDD - Software Design Description

## Resumen tecnico

Este documento describe como esta implementado hoy el sistema y que decisiones tecnicas ya estan tomadas. Complementa al `SAD` con detalle operativo, comandos, convenciones y ubicacion de piezas concretas.

## Stack vigente

- Backend: Python 3.11+, FastAPI, SQLAlchemy async, Pydantic
- Bot engine: LangGraph, LangChain, OpenAI GPT-4o y GPT-4o-mini, ChromaDB
- Frontend: Next.js, React, TypeScript, Tailwind CSS, Zustand
- Persistencia: Supabase PostgreSQL como base canonica en desarrollo y produccion
- Integraciones: Twilio, HubSpot, OpenAI, Meta/Facebook segun configuracion

## Estructura de codigo

- `apps/api/`: routers, session management, auth y webhooks
- `apps/bot-engine/`: workflow, nodos y servicios del bot
- `apps/web/`: app router, componentes, stores y cliente API
- `packages/database/`: modelos, CRUD y migraciones
- `packages/shared/`: logging y helpers comunes
- `scripts/`: utilidades y arranque local

## Bootstrap y ejecucion

### Instalacion base

```bash
cd packages/shared && pip install -e .
cd ../database && pip install -e .
cd ../../apps/api && pip install -r requirements.txt
cd ../bot-engine && pip install -r requirements.txt
cd ../web && npm install
```

### Desarrollo

```bash
cp .env.example .env
./scripts/start_dev.ps1
```

Alternativa manual:

```bash
cd apps/api && python -m uvicorn src.main:app --reload --port 8000
cd apps/web && npm run dev
```

### Produccion o entorno containerizado

```bash
docker-compose up --build
```

## Convenciones y patrones vigentes

- La `api` importa el `bot-engine` como libreria.
- La persistencia compartida debe consumirse desde `whatsapp_bot_database`.
- El estado LangGraph se trata con patron inmutable: los nodos devuelven estado actualizado.
- Las integraciones opcionales deben degradar sin romper el baseline del producto.
- El repo usa documentacion canonica en `docs/`; los markdown del root quedan como apoyo o legado durante la transicion.

## Workflow conversacional implementado

Nodos principales del bot:

1. `welcome_node`
2. `intent_classifier_node`
3. `sentiment_analyzer_node`
4. `data_collector_node`
5. `router_node`
6. `conversation_node`
7. `closing_node`
8. `payment_node`
9. `follow_up_node`
10. `handoff_node`
11. `summary_node`

## Validaciones tecnicas relevantes

- nombre: sin saludos y normalizado
- email: formato valido con TLD
- telefono: minimo 7 digitos
- necesidades y pain points: longitud minima y contenido concreto
- presupuesto: referencia monetaria o numerica

## Variables de entorno

- `.env.example` es la unica plantilla canonica de variables de entorno.
- El archivo real `.env` vive en la raiz y no debe commitearse.
- El frontend puede usar `apps/web/.env.local`; `scripts/start_dev.ps1` lo crea desde `.env` cuando falta.
- `SUPABASE_DATABASE_URL` es la variable canonica de conexion a base de datos.
- `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `HUBSPOT_API_KEY`, `JWT_SECRET` y `SECRET_KEY` son nombres heredados y no deben agregarse a nuevas configuraciones.

## Base de datos e integraciones

- Supabase PostgreSQL es la base de datos vigente para desarrollo y produccion
- ChromaDB persiste embeddings para RAG
- HubSpot sincroniza contactos, lifecycle stage y notas cuando esta configurado
- Twilio gestiona el canal WhatsApp

## Testing y validacion minima

### API

```bash
cd apps/api && pytest
cd apps/api && pytest -m unit
cd apps/api && pytest -m integration
```

### Bot engine

```bash
cd apps/bot-engine && pytest -m unit
cd apps/bot-engine && pytest -m integration
```

### Frontend

```bash
cd apps/web && npm run lint
cd apps/web && npm run build
```

### Integracion

```bash
python scripts/test_integration.py
```

## Fuentes de migracion y apoyo

- `AGENTS.md` anterior
- `../08-developers/api-reference.md`
- `../08-developers/deployment-render-and-docker.md`
- `../08-developers/deployment-coolify.md`
- `../08-developers/hubspot-setup.md`
- `../08-developers/stage-sync-integration.md`
