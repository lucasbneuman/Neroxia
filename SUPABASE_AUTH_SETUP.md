# Guía de Configuración de Supabase Auth

## Problema Actual

Las claves de Supabase en tu `.env` no son válidas. Las claves actuales son:
- `SUPABASE_ANON_KEY=sb_publishable_8X3em...`
- `SUPABASE_SERVICE_KEY=sb_publishable_8X3em...`

Estas son placeholders. Las claves reales de Supabase son tokens JWT que comienzan con `eyJ...` y son mucho más largas.

## Solución: Obtener las Claves Correctas

### Paso 1: Accede a tu proyecto Supabase

1. Ve a https://supabase.com/dashboard
2. Haz clic en tu proyecto (debería ser el que tiene URL: `oveixhmndwrtymuymdxm.supabase.co`)

### Paso 2: Obtén las claves de API

1. En el menú lateral izquierdo, ve a **Settings** (⚙️)
2. Luego haz clic en **API**
3. Verás una sección llamada **Project API keys** con dos claves:
   - **anon** public - Esta es tu `SUPABASE_ANON_KEY`
   - **service_role** secret - Esta es tu `SUPABASE_SERVICE_KEY`

4. Copia ambas claves (haz clic en el ícono de copiar)

### Paso 3: Actualiza el archivo .env

Reemplaza las líneas en tu `.env`:

```env
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (tu clave real aquí)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (tu clave real aquí)
```

Las claves reales deberían verse algo así:
- Comienzan con `eyJ...`
- Son muy largas (más de 100 caracteres)
- Son tokens JWT válidos

### Paso 4: Verifica la configuración

Una vez actualizado el `.env`:

1. Reinicia el API:
   ```bash
   cd apps/api
   ../../venv/Scripts/python.exe -m uvicorn src.main:app --reload --port 8000
   ```

2. Crea un usuario de prueba:
   ```bash
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@gmail.com", "password": "admin123", "name": "Admin"}'
   ```

3. Si eso funciona, ahora podrás hacer login con:
   - Email: admin@gmail.com
   - Password: admin123

## Alternativa: Crear Usuario desde Dashboard

Si prefieres crear el usuario directamente en Supabase:

1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto
3. En el menú izquierdo, ve a **Authentication** → **Users**
4. Haz clic en **Add User** (botón verde)
5. Completa:
   - Email: admin@gmail.com (o el que prefieras)
   - Password: admin123
   - **IMPORTANTE**: Marca la opción **Auto Confirm User** = YES
6. Haz clic en **Create User**

Luego podrás hacer login desde tu aplicación con ese email y contraseña.

## Próximos Pasos

### Frontend - Actualizar para usar Email

El frontend actualmente tiene un campo "Username" pero debería ser "Email":

1. Editar `apps/web/src/app/login/page.tsx`
2. Cambiar el label del input de "Username" a "Email"
3. Agregar validación de email en el frontend
4. El placeholder debería decir "admin@gmail.com" en lugar de "admin"

### Base de Datos

Una vez que tengas autenticación funcionando, asegúrate de que:

1. La base de datos PostgreSQL de Supabase esté corriendo
2. Las tablas estén creadas (usa el script en `scripts/supabase_schema.sql`)
3. Puedes ejecutar:
   ```bash
   # Desde el dashboard de Supabase, ve a SQL Editor y corre:
   # El contenido de scripts/supabase_schema.sql
   ```

## Verificación Final

Para verificar que todo funciona:

1. **API health check**:
   ```bash
   curl http://localhost:8000/health
   # Debería retornar: {"status":"healthy"}
   ```

2. **Signup test**:
   ```bash
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@gmail.com","password":"test123","name":"Test"}'
   ```

3. **Login test**:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d 'username=test@gmail.com&password=test123'
   ```

4. **Frontend login**:
   - Ve a http://localhost:3000/login
   - Ingresa email y password
   - Deberías ser redirigido al dashboard

## Contacto

Si sigues teniendo problemas, verifica:
- ✅ Las claves de Supabase son correctas (comienzan con `eyJ...`)
- ✅ El `.env` se cargó correctamente (reinicia el API después de cambios)
- ✅ La URL de Supabase es correcta
- ✅ El usuario está confirmado en Supabase (Auto Confirm = YES)
