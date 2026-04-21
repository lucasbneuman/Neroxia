# Agents

## Objetivo

Dar a los agentes una ruta de entrada corta, clara y reusable sin convertir `AGENTS.md` en una base de conocimiento larga.

## Como arrancar una tarea

1. Leer `../03-process/working-agreement.md`
2. Leer `../03-process/task-lifecycle.md`
3. Elegir la fuente de verdad adecuada:
   - funcional: `../00-product/srs.md`
   - estructural: `../01-architecture/sad.md`
   - tecnica: `../01-architecture/sdd.md`
4. Leer `../05-qa/README.md` si la tarea requiere validacion
5. Revisar `../08-developers/README.md` solo si hace falta contexto operativo adicional

## Checklist minimo

- entender primero el tipo de cambio
- leer la minima superficie documental necesaria
- no duplicar arquitectura o setup en `AGENTS.md`
- no usar el repo como backlog durable
- no guardar verdad durable en `.claude/` ni en directorios equivalentes de tooling
- mantener cambios pequenos y verificables

## Contrato de agentes

El contrato portable y las aclaraciones sobre `.claude/` viven en `agent-contract.md`.
