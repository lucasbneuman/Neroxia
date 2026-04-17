# QA

## Objetivo

Centralizar la validacion minima recomendada para cambios en este repo y reducir busqueda de comandos dispersos.

## Checks recomendados

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

## Criterio de seleccion

- cambios de API: correr al menos tests de API relacionados
- cambios del workflow conversacional: validar bot engine y, si aplica, integracion
- cambios frontend: validar lint y build
- cambios documentales: verificar navegabilidad, enlaces y jerarquia documental

## Fuentes heredadas utiles

- `manual-testing-checklist.md`
- `../08-developers/api-reference.md`
- `../08-developers/deployment-render-and-docker.md`

## Documento detallado

- Checklist manual multi-canal: `manual-testing-checklist.md`
