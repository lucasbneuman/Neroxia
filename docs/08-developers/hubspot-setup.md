# 🔗 HubSpot CRM Integration Setup

## Campos Personalizados Requeridos en HubSpot

Para que la integración funcione correctamente, necesitas crear los siguientes campos personalizados en tu HubSpot CRM:

### 1. **Intent Score** (Puntuación de Intención)
- **Internal Name**: `intent_score`
- **Label**: Intent Score
- **Field Type**: Number
- **Description**: Puntuación de 0-1 que indica la probabilidad de compra del contacto
- **Group**: Contact Information

### 2. **Sentiment** (Sentimiento)
- **Internal Name**: `sentiment`
- **Label**: Sentiment
- **Field Type**: Dropdown select
- **Options**:
  - positive
  - neutral
  - negative
- **Description**: Sentimiento actual del contacto en la conversación
- **Group**: Contact Information

---

## Campos Estándar de HubSpot Utilizados

Estos campos ya existen en HubSpot y se mapean automáticamente:

| Campo Interno | Campo HubSpot | Descripción |
|---------------|---------------|-------------|
| `phone` | `phone` | Teléfono del contacto |
| `name` | `firstname` + `lastname` | Nombre completo (se divide automáticamente) |
| `email` | `email` | Email del contacto |
| `stage` | `lifecyclestage` | Etapa del ciclo de vida del lead |
| `conversation_summary` | `hs_content_membership_notes` | Resumen de la conversación |

---

## Mapeo de Lifecycle Stages

Nuestro sistema mapea automáticamente las etapas internas a las etapas de HubSpot:

| Etapa Interna | Lifecycle Stage HubSpot |
|---------------|-------------------------|
| `welcome` | `lead` |
| `qualifying` | `lead` |
| `nurturing` | `marketingqualifiedlead` |
| `closing` | `salesqualifiedlead` |
| `sold` | `customer` |
| `follow_up` | `opportunity` |

---

## Cómo Crear Campos Personalizados en HubSpot

### Paso 1: Acceder a Configuración
1. En HubSpot, hacer clic en el ⚙️ (icono de configuración) en la esquina superior derecha
2. Ir a **Properties** (Propiedades)

### Paso 2: Crear Nuevo Campo
1. Hacer clic en **Create property** (Crear propiedad)
2. Seleccionar **Contact properties** (Propiedades de contacto)
3. Completar los datos según la tabla anterior

### Paso 3: Configurar "Intent Score"
```
Object: Contact
Group: Contact Information
Label: Intent Score
Description: AI-generated score (0-1) indicating purchase intent
Field type: Number
Number format: Decimal places: 2
```

### Paso 4: Configurar "Sentiment"
```
Object: Contact
Group: Contact Information
Label: Sentiment
Description: Current sentiment in conversation
Field type: Dropdown select
Options:
  - positive
  - neutral
  - negative
```

---

## Obtener Access Token de HubSpot

### Para Aplicaciones Privadas (Recomendado)

1. **Ir a Settings** → **Integrations** → **Private Apps**
2. **Create a private app**
3. **Nombre**: Neroxia
4. **Scopes necesarios**:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.schemas.contacts.read`
5. **Create app** y copiar el **Access Token**
6. **Agregar a `.env`**:
   ```env
   HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxx-xxxxx-xxxxx
   ```

---

## Flujo de Sincronización

### 🔄 Proceso Automático

1. **Usuario envía mensaje** → Sistema extrae datos
2. **Sistema verifica**:
   - ¿Tenemos `hubspot_contact_id` en nuestra BD?
     - **SÍ** → Verifica que exista en HubSpot → **UPDATE**
     - **NO** → Busca por teléfono/email en HubSpot
       - **Encontrado** → Guarda `hubspot_contact_id` → **UPDATE**
       - **No encontrado** → **CREATE** nuevo contacto → Guarda `hubspot_contact_id`

3. **Datos que se sincronizan**:
   - ✅ Teléfono (siempre)
   - ✅ Nombre (si está disponible)
   - ✅ Email (si está disponible)
   - ✅ Intent Score (calculado por IA)
   - ✅ Sentiment (analizado por IA)
   - ✅ Lifecycle Stage (mapeado automáticamente)
   - ✅ Conversation Summary (resumen generado por IA)

---

## Campos en Nuestra Base de Datos

Agregamos 3 campos nuevos al modelo `User`:

```python
class User:
    # ... campos existentes ...

    # HubSpot Integration
    hubspot_contact_id: str         # ID del contacto en HubSpot
    hubspot_lifecyclestage: str     # Etapa del ciclo de vida
    hubspot_synced_at: DateTime     # Última sincronización
```

---

## Testing de la Integración

### 1. Sin HubSpot (Desarrollo Local)
```env
# No configurar HUBSPOT_ACCESS_TOKEN
# El sistema funcionará normalmente sin sincronizar
```

### 2. Con HubSpot (Testing)
```env
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxx
```

**Probar**:
1. Iniciar conversación en panel de pruebas
2. Proporcionar nombre y email
3. Verificar logs:
   ```
   ✅ HubSpot sync successful: created contact 12345
   ✅ Updated DB with HubSpot data: created contact 12345
   ```
4. Verificar en HubSpot que el contacto fue creado

---

## Logs y Debugging

### Logs Importantes

```bash
# Sync exitoso - Crear
✅ Created HubSpot contact: 12345 (stage: lead)
✅ Updated DB with HubSpot data: created contact 12345

# Sync exitoso - Actualizar
✅ Updated HubSpot contact 12345: ['intent_score', 'sentiment']
✅ Updated DB with HubSpot data: updated contact 12345

# Sync deshabilitado
⚠️ HubSpot sync skipped: API key not configured

# Error
❌ HubSpot sync failed (non-blocking): ...
```

### Verificar Sincronización

En HubSpot, buscar contacto por teléfono y verificar:
- ✅ Nombre y apellido correctos
- ✅ Email presente
- ✅ Intent Score visible
- ✅ Sentiment visible
- ✅ Lifecycle Stage correcto

---

## Solución de Problemas

### Error 401: Token Expirado
```
Failed to create HubSpot contact: 401 - token expired
```
**Solución**: Generar nuevo Access Token en HubSpot

### Error 400: Campo No Existe
```
Failed to create HubSpot contact: 400 - Property 'intent_score' does not exist
```
**Solución**: Crear el campo personalizado en HubSpot

### No Se Sincroniza
1. Verificar que `HUBSPOT_ACCESS_TOKEN` esté en `.env`
2. Verificar logs: debe mostrar "HubSpot service initialized"
3. Verificar que el usuario tenga al menos `phone` configurado

---

## Seguridad

⚠️ **IMPORTANTE**:
- **NUNCA** commitear `.env` con el Access Token
- Rotar tokens regularmente
- Usar Private Apps en lugar de OAuth para aplicaciones internas
- Revisar logs regularmente para detectar fallos

---

## Resumen de Configuración

✅ **Checklist para Setup Completo**:

- [ ] Crear campos personalizados en HubSpot (`intent_score`, `sentiment`)
- [ ] Crear Private App en HubSpot
- [ ] Copiar Access Token
- [ ] Agregar `HUBSPOT_ACCESS_TOKEN` a `.env`
- [ ] Reiniciar aplicación
- [ ] Probar con conversación de prueba
- [ ] Verificar contacto creado en HubSpot
- [ ] Verificar `hubspot_contact_id` guardado en BD local

---

**Documentación Actualizada**: 2025-11-21
**Versión**: v1.1 - HubSpot Integration
