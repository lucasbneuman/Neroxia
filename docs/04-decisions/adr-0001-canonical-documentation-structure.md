# ADR-0001 - Canonical Documentation Structure

## Estado

Aprobada

## Fecha

2026-04-17

## Contexto

El repo acumulaba documentacion durable en la raiz y en `.claude/`, mezclando conocimiento de producto, arquitectura, runbooks, reportes historicos y tracking operativo. Esto aumentaba el costo de exploracion y hacia que `AGENTS.md` y otros entrypoints duplicaran demasiado contexto.

## Decision

- La verdad durable del proyecto vive en `docs/`.
- `AGENTS.md` queda como router minimo.
- La raiz del repo conserva solo `README.md` y `AGENTS.md` como entrypoints documentales.
- Se eliminan documentos deprecados, reportes historicos y tracking transaccional en `.claude/`.
- Las referencias detalladas que siguen siendo utiles se reubican en `docs/` con nombres orientados a su funcion.

## Consecuencias

- Agentes y developers tienen un recorrido de lectura explicito.
- La documentacion tecnica detallada sigue disponible, pero ya no compite con `SRS`, `SAD` y `SDD`.
- Los reportes historicos dejan de contaminar la base documental activa.
