# 🗄️ Supabase Database Setup - Guía Definitiva

## Problema Actual

El API retorna errores 500 porque **las tablas no existen en Supabase**.

## Solución Definitiva

### Paso 1: Abrir Supabase SQL Editor

1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto: `oveixhmndwrtymuymdxm`
3. En el menú lateral, haz clic en **SQL Editor**
4. Haz clic en **New Query**

### Paso 2: Ejecutar el Script SQL

1. Abre el archivo: `scripts/supabase_schema.sql`
2. Copia **TODO** el contenido del archivo
3. Pégalo en el SQL Editor de Supabase
4. Haz clic en **Run** (o presiona Ctrl+Enter)

### Paso 3: Verificar Creación

El script mostrará al final:

```
✅ Database schema created successfully!
All tables, indexes, and triggers are in place.
```

También verás una tabla con el conteo de filas:
- users: 0
- messages: 0
- follow_ups: 0
- configs: 20 (configuraciones por defecto)

### Paso 4: Verificar en Table Editor

1. Ve a **Table Editor** en el menú lateral
2. Deberías ver 4 tablas:
   - ✅ users
   - ✅ messages
   - ✅ follow_ups
   - ✅ configs

### Paso 5: Reiniciar el API

El servidor debería funcionar automáticamente. Si no:

```bash
# Detén el servidor (Ctrl+C)
# Reinicia:
cd apps/api
python -m uvicorn src.main:app --reload --port 8000
```

## ¿Qué Crea el Script?

### Tablas

1. **users** - Usuarios/contactos de WhatsApp
   - Información básica (phone, name, email)
   - Estado de conversación (intent_score, sentiment, stage)
   - Integración HubSpot
   - Tracking de actividad

2. **messages** - Historial de mensajes
   - Texto del mensaje
   - Sender (user/bot)
   - Timestamp
   - Metadata (intent, sentiment)

3. **follow_ups** - Seguimientos programados
   - Mensaje a enviar
   - Tiempo programado
   - Estado (pending/sent/cancelled)
   - Job ID para APScheduler

4. **configs** - Configuraciones del sistema
   - Prompts del sistema
   - Configuración de TTS
   - Información del producto
   - Configuraciones de comportamiento

### Índices

- Índices en campos frecuentemente consultados
- Mejora el rendimiento de queries

### Triggers

- Auto-actualización de `updated_at` en users y configs
- Se ejecuta automáticamente en cada UPDATE

### Datos Iniciales

- 20 configuraciones por defecto
- Listas para usar inmediatamente

## Verificación Post-Setup

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Debería retornar:
```json
{"status": "healthy"}
```

### Test 2: Get Config

```bash
curl http://localhost:8000/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Debería retornar las configuraciones.

### Test 3: Test Chat

Ve a http://localhost:3000/dashboard/test y envía un mensaje de prueba.

## Troubleshooting

### Error: "relation does not exist"

- Las tablas no se crearon correctamente
- Vuelve a ejecutar el script SQL

### Error: "permission denied"

- Tu usuario de Supabase no tiene permisos
- Usa el usuario `postgres` o verifica los permisos

### Error: "already exists"

- Las tablas ya existen
- El script las elimina primero con `DROP TABLE IF EXISTS`
- Es seguro ejecutarlo múltiples veces

## Próximos Pasos

Una vez que las tablas estén creadas:

1. ✅ El API funcionará correctamente
2. ✅ Podrás usar el test chat
3. ✅ Las conversaciones se guardarán en Supabase
4. ✅ Las configuraciones se cargarán desde la base de datos

## Migración Futura

Si necesitas agregar nuevas columnas o tablas:

1. Crea un nuevo archivo SQL en `scripts/migrations/`
2. Ejecútalo en Supabase SQL Editor
3. Actualiza los modelos en `packages/database/whatsapp_bot_database/models.py`

## Backup

Supabase hace backups automáticos, pero puedes hacer uno manual:

1. Dashboard > Database > Backups
2. Click en "Create backup"
