# Working Agreement

## Objetivo

Definir como se trabaja en este repo y en que orden se consulta la documentacion antes de tocar codigo o contenido durable.

## Prioridad documental

1. Este documento
2. `task-lifecycle.md`
3. `../00-product/srs.md`
4. `../01-architecture/sad.md`
5. `../01-architecture/sdd.md`
6. `../04-decisions/`
7. `../07-agents/README.md`
8. `../08-developers/README.md`
9. `../../README.md`

## Reglas de trabajo

- Empezar por proceso antes de leer detalle tecnico.
- Leer solo la superficie documental minima necesaria.
- Usar `SRS` para decisiones funcionales.
- Usar `SAD` para limites y responsabilidades estructurales.
- Usar `SDD` para implementacion vigente, setup y convenciones tecnicas.
- Mantener cambios pequenos, verificables y trazables.
- Documentar decisiones estables en `docs/04-decisions/` en lugar de inflar `AGENTS.md`.

## Contradicciones

- Proceso prevalece para reglas de trabajo.
- `SRS` prevalece para alcance funcional.
- `SAD` prevalece para decisiones estructurales.
- `SDD` prevalece para implementacion vigente.
- La ADR mas reciente prevalece cuando formaliza una excepcion estable.

## Regla sobre tracking

- No usar el repo como tablero manual de tareas, backlog vivo o tracking transaccional durable.
- Si existe coordinacion operativa puntual, debe tratarse como soporte de trabajo y no como fuente principal de verdad del producto o la arquitectura.
- No guardar documentacion durable en directorios especificos de una herramienta como `.claude/`.
