# Task Lifecycle

## Como encarar una tarea

1. Leer `working-agreement.md`.
2. Identificar si la tarea es funcional, estructural, tecnica, QA o de agentes.
3. Leer solo los documentos canonicos correspondientes.
4. Implementar cambios pequenos y facilmente verificables.
5. Validar con checks proporcionales al cambio.
6. Actualizar documentacion canonica cuando cambie una verdad durable.

## Que leer segun el tipo de tarea

- Producto o alcance: `../00-product/srs.md`
- Arquitectura o limites entre modulos: `../01-architecture/sad.md`
- Implementacion, setup o integraciones: `../01-architecture/sdd.md`
- Validacion: `../05-qa/README.md`
- Flujo de agentes: `../07-agents/README.md`

## Cuando una tarea exige actualizacion documental

- Si cambia el comportamiento esperado del producto, actualizar `SRS`.
- Si cambia la organizacion entre modulos, contratos o limites, actualizar `SAD`.
- Si cambia stack, comandos, convenciones o wiring tecnico, actualizar `SDD`.
- Si cambia el proceso de trabajo o el contrato para agentes, actualizar `03-process/` o `07-agents/`.

## Criterio de cierre

- El cambio queda implementado y validado con el nivel de prueba adecuado.
- La documentacion canonica refleja la nueva realidad si hubo cambio durable.
- `AGENTS.md` y otros routers no duplican detalle que ahora vive en `docs/`.
