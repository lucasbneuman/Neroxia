# Documentación - Correcciones Necesarias

**Fecha**: 2025-12-02

## 🔴 Crítico

1. **Sección Agent Coordination eliminada** - CLAUDE.md referencia `.agents/*` que fue borrado del repo
2. **Routers sin documentar** - `/users`, `/subscriptions`, `/webhook` existen pero no están en API_DOCUMENTATION.md
3. **Pytest markers incompletos** - Faltan `config` y `bot` en CLAUDE.md

## 🟡 Importante

4. **Campos Twilio en User** - No documentados en CLAUDE.md
5. **ConversationState** - Solo mencionado, no documentado completamente
6. **Endpoints CRM** - Faltan `POST /crm/deals/{id}/won` y `/lost`
7. **Multi-tenancy** - Implementado pero no explicado
8. **Scripts utilities** - Solo 5 documentados, hay 15+ en `/scripts`

## ✅ Acciones Completadas

- [x] Reporte generado
- [x] Remover sección Agent Coordination
- [x] Documentar routers faltantes (/users, /subscriptions, /webhook)
- [x] Actualizar pytest markers
- [x] Documentar campos Twilio
- [x] Documentar ConversationState completamente
- [x] Completar docs CRM (endpoints won/lost ya estaban)

## ⏳ Pendientes (otro agente trabajando)

- [ ] Temas de modelos de BD (agente de BD trabajando en esto)
- [ ] Explicar multi-tenancy (requiere revisión de modelos)
- [ ] Listar scripts utilities

**Nota**: Temas de modelos de BD y estructura de paquetes están siendo manejados por otro agente.
