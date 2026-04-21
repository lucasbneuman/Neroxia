# Guía: Integración de Sincronización de Etapas

## Objetivo

Integrar la sincronización automática de etapas entre el bot y el CRM cuando el usuario progresa en la conversación.

## Cuándo Implementar

Esta integración debe hacerse cuando tengas nodos en el bot que cambien explícitamente el `User.stage`. Actualmente, el bot no tiene cambios explícitos de stage en los nodos, por lo que esta integración es **opcional** hasta que implementes esa lógica.

## Cómo Integrar

### Opción 1: En los Nodos del Bot

Si agregas lógica para cambiar `user.stage` en algún nodo:

```python
# En apps/bot-engine/src/graph/nodes.py

from neroxia_database import crud

async def qualifying_node(state: ConversationState):
    \"\"\"Node that qualifies the lead.\"\"\"
    # ... lógica del nodo ...
    
    # Actualizar stage del usuario
    await crud.update_user(db, user.id, stage="qualifying")
    
    # Sincronizar con CRM (solo si no fue calificado manualmente)
    await crud.sync_deal_stage_from_user(
        db,
        user_id=user.id,
        new_user_stage="qualifying"
    )
    
    return state
```

### Opción 2: En el Workflow Principal

Alternativamente, puedes agregar la sincronización en el workflow después de procesar el mensaje:

```python
# En apps/bot-engine/src/graph/workflow.py

async def process_message(...):
    # ... procesamiento del mensaje ...
    
    # Si el stage cambió, sincronizar con CRM
    if user.stage != previous_stage:
        await crud.sync_deal_stage_from_user(
            db,
            user_id=user.id,
            new_user_stage=user.stage
        )
```

## Mapeo de Etapas

El mapeo está definido en `crud.py`:

```python
STAGE_MAPPING = {
    "welcome": "new_lead",
    "qualifying": "qualified",
    "closing": "in_conversation",
    "sold": "proposal_sent",
}
```

Ajusta este mapeo según las etapas que uses en tu bot.

## Protección Manual

Una vez que un deal se marca como `manually_qualified = True` (cuando se edita desde el CRM), el bot **no podrá** actualizar su etapa automáticamente. Esto previene que el bot sobrescriba decisiones manuales del equipo de ventas.

Si necesitas forzar una actualización, puedes usar:

```python
await crud.sync_deal_stage_from_user(
    db,
    user_id=user.id,
    new_user_stage="qualifying",
    force=True  # Fuerza la actualización incluso si manually_qualified=True
)
```

## Testing

Para probar la sincronización:

1. Crea un nuevo contacto (se crea deal automáticamente)
2. Verifica que `manually_qualified = False`
3. Cambia el `user.stage` desde el bot
4. Verifica que el `deal.stage` se actualizó
5. Edita el deal manualmente desde el CRM
6. Verifica que `manually_qualified = True`
7. Intenta cambiar el `user.stage` desde el bot
8. Verifica que el `deal.stage` NO cambió (protegido)

## Notas

- La sincronización es **unidireccional**: Bot → CRM
- No hay sincronización CRM → Bot (para evitar loops)
- Los deals en etapa "won" o "lost" no se sincronizan
- Solo se sincroniza el deal activo más reciente del usuario
