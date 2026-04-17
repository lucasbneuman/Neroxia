# Documentacion del Repo

Este directorio concentra la documentacion durable del proyecto y explicita el orden de lectura recomendado para personas y agentes.

## Orden de lectura

1. `03-process/working-agreement.md`
2. `03-process/task-lifecycle.md`
3. `00-product/srs.md`
4. `01-architecture/sad.md`
5. `01-architecture/sdd.md`
6. `04-decisions/`
7. `07-agents/README.md`
8. `08-developers/README.md`
9. `../README.md`

## Modelo de verdad

- `SRS`: verdad funcional del producto
- `SAD`: verdad estructural y arquitectonica
- `SDD`: verdad tecnica e implementacion vigente

## Mapa de carpetas

- `00-product/`: producto, alcance y comportamiento esperado
- `01-architecture/`: estructura del sistema y diseno tecnico vigente
- `03-process/`: reglas operativas y ciclo de trabajo
- `04-decisions/`: decisiones estables y excepciones formalizadas
- `05-qa/`: validacion, comandos y recorridos de prueba
- `07-agents/`: contrato, prompts y checklists para agentes
- `08-developers/`: onboarding tecnico y enlaces a documentacion heredada

## Referencias detalladas

- Guia de usuario: `00-product/user-guide.md`
- Notas arquitectonicas heredadas: `01-architecture/architecture-notes-legacy.md`
- Referencia de API: `08-developers/api-reference.md`
- Runbooks de despliegue: `08-developers/deployment-render-and-docker.md` y `08-developers/deployment-coolify.md`
- Integraciones operativas: `08-developers/hubspot-setup.md` y `08-developers/stage-sync-integration.md`
- QA manual: `05-qa/manual-testing-checklist.md`

## Regla de precedencia

- Proceso prevalece para reglas de trabajo
- `SRS` prevalece para alcance funcional
- `SAD` prevalece para estructura y limites
- `SDD` prevalece para implementacion vigente
- La ADR mas reciente prevalece si formaliza una excepcion estable

## Estado de la migracion

La documentacion del root fue reducida a `README.md` y `AGENTS.md`. La verdad durable y las referencias tecnicas detalladas viven ahora en `docs/`.
