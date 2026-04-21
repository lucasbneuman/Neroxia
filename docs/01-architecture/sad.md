# SAD - Software Architecture Document

## Resumen estructural

La solucion esta partida como monorepo con microservicios y paquetes compartidos. El backend API expone contratos HTTP y usa el bot engine como libreria; ambos dependen de paquetes compartidos para modelo de datos y utilidades.

## Modulos y responsabilidades

### `apps/web`

- Interfaz de usuario con Next.js
- Dashboard, onboarding, integraciones, CRM, perfil, configuracion y testing
- Consume la API como superficie principal

### `apps/api`

- API REST con FastAPI
- Autenticacion, configuracion, conversaciones, bot processing, webhooks e integraciones
- Orquesta acceso a base de datos y llama al bot engine cuando corresponde

### `apps/bot-engine`

- Orquestacion conversacional con LangGraph
- Analisis de intencion y sentimiento, recoleccion de datos, RAG, cierre, handoff, follow-up y resumen
- Se importa como libreria desde la API

### `packages/database`

- Modelos SQLAlchemy, CRUD y migraciones
- Fuente unica de verdad para persistencia y esquema compartido

### `packages/shared`

- Utilidades y logging compartido

## Limites y contratos estables

- La `web` no accede directo a la base de datos; consume contratos de la `api`.
- La `api` concentra la superficie HTTP y la integracion con auth, webhooks y configuracion por tenant.
- El `bot-engine` no es un servicio independiente en esta arquitectura actual; se usa como libreria invocada por la `api`.
- Los modelos y operaciones de persistencia compartidas viven en `packages/database`.

## Integraciones relevantes

- `OpenAI`: LLMs, embeddings y TTS
- `Twilio`: ingreso y salida por WhatsApp
- `HubSpot`: sincronizacion CRM
- `Supabase`: auth y base Postgres en produccion
- `ChromaDB`: almacenamiento vectorial para RAG

## Flujos estructurales clave

### Flujo conversacional

1. Un mensaje entra por endpoint de bot o webhook.
2. La API resuelve tenant y usuario.
3. La API invoca el workflow del bot engine.
4. El workflow actualiza estado conversacional y datos.
5. La API persiste resultados y responde o despacha salida por canal.

### Flujo de configuracion

1. El usuario autenticado modifica configuraciones desde `web`.
2. La API valida y persiste configuracion.
3. El bot engine usa esa configuracion al procesar conversaciones.

### Flujo RAG

1. El tenant carga documentos por API.
2. El sistema procesa chunks y embeddings.
3. El bot recupera contexto relevante durante la conversacion.

## Decisiones estructurales estables

- Mantener separacion `web` / `api` / `bot-engine`
- Mantener `packages/database` y `packages/shared` como dependencias locales compartidas
- Conservar el workflow LangGraph como pieza central del comportamiento conversacional
- Tratar la documentacion arquitectonica como canonica en `docs/01-architecture/`, no en `AGENTS.md`

## Superficies sensibles a no romper

- Contratos HTTP documentados por la API
- Estado compartido del workflow conversacional
- Modelos y CRUD compartidos del paquete de base de datos
- Integraciones externas condicionadas por configuracion y credenciales

## Fuentes utilizadas en esta consolidacion

- `architecture-notes-legacy.md`
- `README.md`
- estructura actual de `apps/`, `packages/` y `scripts/`
