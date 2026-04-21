# AGENTS.md

## Objetivo del repositorio

`neroxia` es una plataforma SaaS multi-tenant para ventas conversacionales por WhatsApp con arquitectura de microservicios. El repo contiene frontend web, API backend, motor conversacional con LangGraph y paquetes compartidos.

## Fuentes de verdad por prioridad

1. `docs/03-process/working-agreement.md`
2. `docs/03-process/task-lifecycle.md`
3. `docs/00-product/srs.md`
4. `docs/01-architecture/sad.md`
5. `docs/01-architecture/sdd.md`
6. `docs/04-decisions/`
7. `docs/07-agents/README.md`
8. `docs/08-developers/README.md`
9. `README.md`

Si hay contradicciones, prevalece el documento de mayor prioridad. Para excepciones estables, prevalece la ADR mas reciente en `docs/04-decisions/`.

## Como arranca un agente

- Empezar por proceso: leer `docs/03-process/working-agreement.md` y `docs/03-process/task-lifecycle.md`.
- Leer solo la superficie documental minima necesaria para la tarea.
- Usar `SRS` para verdad funcional.
- Usar `SAD` para verdad estructural.
- Usar `SDD` para verdad tecnica.

## Guia de lectura por tipo de tarea

- Cambios funcionales o de producto: `docs/00-product/srs.md`
- Cambios de arquitectura o limites entre modulos: `docs/01-architecture/sad.md`
- Implementacion, setup, comandos, integraciones y convenciones: `docs/01-architecture/sdd.md`
- Validacion y checks manuales/automaticos: `docs/05-qa/README.md`
- Contrato y flujo para agentes: `docs/07-agents/README.md`
- Onboarding tecnico y fuentes heredadas: `docs/08-developers/README.md`

## Reglas explicitas

- No usar `AGENTS.md` como base de conocimiento principal.
- No duplicar tracking transaccional o backlog dentro de la base documental durable del repo.
- Mantener cambios pequenos, verificables y trazables.
