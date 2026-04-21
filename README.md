# WhatsApp Sales Bot SaaS Platform

Plataforma SaaS multi-tenant de ventas conversacionales para WhatsApp con arquitectura de microservicios. El repo contiene frontend web, API backend, motor conversacional con LangGraph y paquetes compartidos.

## Documentacion

La base documental canonica ahora vive en [`docs/`](docs/README.md).

- Proceso y jerarquia de lectura: [`docs/03-process/working-agreement.md`](docs/03-process/working-agreement.md)
- Verdad funcional (`SRS`): [`docs/00-product/srs.md`](docs/00-product/srs.md)
- Verdad estructural (`SAD`): [`docs/01-architecture/sad.md`](docs/01-architecture/sad.md)
- Verdad tecnica (`SDD`): [`docs/01-architecture/sdd.md`](docs/01-architecture/sdd.md)
- QA y validacion: [`docs/05-qa/README.md`](docs/05-qa/README.md)
- Contrato para agentes: [`docs/07-agents/README.md`](docs/07-agents/README.md)
- Onboarding tecnico y fuentes heredadas: [`docs/08-developers/README.md`](docs/08-developers/README.md)

## Estructura general

```text
apps/
  api/         FastAPI backend
  bot-engine/  LangGraph workflow
  web/         Next.js frontend
packages/
  database/    modelos, CRUD y migraciones
  shared/      utilidades compartidas
docs/          documentacion canonica
```

## Arranque rapido

### Dependencias

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Instalacion

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

## Validacion rapida

```bash
cd apps/api && pytest
cd apps/web && npm run build
python scripts/test_integration.py
```

## Documentacion heredada

Los markdown del root se conservan durante la transicion como material heredado o de apoyo. La lectura prioritaria debe hacerse desde `docs/`.
