# Agent Contract

## Rol de `AGENTS.md`

`AGENTS.md` es un router minimo. No debe duplicar arquitectura extensa, onboarding largo, comandos detallados ni historia del producto.

## Contrato portable

- empezar por proceso
- usar `SRS` para verdad funcional
- usar `SAD` para verdad estructural
- usar `SDD` para verdad tecnica
- leer solo lo necesario
- dejar trazabilidad documental cuando cambie una verdad durable

## Situacion actual del repo

Durante la migracion se detecto una inconsistencia documental:

- `AGENTS.md` apuntaba a `.Codex/`, pero esa carpeta no existe en este repo
- parte del contexto durable y reportes historicos vivian en `.claude/`

La regla a partir de ahora es:

- el contrato documental general vive en `docs/`
- los directorios especificos de tooling no deben contener documentacion durable, backlog ni tracking transaccional
- la coordinacion diaria debe resolverse fuera de la base de conocimiento activa del repo o mediante git/history, no con archivos paralelos en tooling

## Reglas de compatibilidad

- si una instruccion de tooling local contradice la base documental, primero resolver la contradiccion y luego actualizar el documento canonico correspondiente
- si una carpeta de tooling desaparece o cambia, `AGENTS.md` no debe depender de ella como fuente principal
