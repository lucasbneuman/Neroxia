# Guía de Usuario - Neroxia

## 📋 Índice

1. [Registro y Onboarding](#registro-y-onboarding)
2. [Perfil de Usuario](#perfil-de-usuario)
3. [Integraciones](#integraciones)
4. [Gestión de Suscripción](#gestión-de-suscripción)
5. [Flujo Completo del Usuario](#flujo-completo-del-usuario)

---

## 🎯 Registro y Onboarding

### Crear una Cuenta Nueva

1. **Accede a la página de registro**: `/signup`

2. **Completa el formulario de registro**:
   - Nombre completo
   - Email (será tu usuario de acceso)
   - Contraseña (mínimo 8 caracteres)
   - Confirmar contraseña

3. **Validaciones automáticas**:
   - Las contraseñas deben coincidir
   - La contraseña debe tener al menos 8 caracteres
   - El email debe ser válido

4. **Redirección automática**: Una vez creada la cuenta, serás redirigido al wizard de onboarding

### Wizard de Onboarding (4 Pasos)

#### Paso 1: Información de Empresa
- **Nombre de la empresa**: Identifica tu negocio
- **Teléfono de contacto**: Número principal de tu empresa

#### Paso 2: Configuración Regional
- **Zona horaria**: Selecciona tu ubicación
  - México (GMT-6)
  - Nueva York (GMT-5)
  - Los Ángeles (GMT-8)
  - Bogotá (GMT-5)
  - Buenos Aires (GMT-3)
  - Madrid (GMT+1)
  - UTC (GMT+0)
- **Idioma**: Español o English

#### Paso 3: Selección de Plan
- **Starter** (Gratis):
  - 100 mensajes/mes
  - 1 bot
  - Soporte por email

- **Professional** ($49/mes) - Recomendado:
  - 5,000 mensajes/mes
  - 3 bots
  - Integraciones HubSpot/Twilio
  - Soporte prioritario

- **Enterprise** ($199/mes):
  - Mensajes ilimitados
  - Bots ilimitados
  - Todas las integraciones
  - Soporte 24/7

#### Paso 4: ¡Todo listo!
- Resumen de configuración completada
- Próximos pasos recomendados
- Botón para ir al Dashboard

---

## 👤 Perfil de Usuario

### Acceder al Perfil

**Ubicación**: `/dashboard/profile`

**Navegación**: Desde el sidebar → "Mi Perfil" (sección Configuración)

### Pestaña: Perfil

#### Foto de Perfil
- Click en "Cambiar foto"
- Selecciona una imagen (máx. 2MB)
- Formatos aceptados: JPG, PNG
- Se muestra la inicial de tu empresa mientras no haya foto

#### Información Personal
- **Nombre de la empresa**: Editable
- **Teléfono**: Número de contacto
- **Zona horaria**: Ajusta tu huso horario
- **Idioma**: Español o English

#### Guardar Cambios
- Click en "Guardar cambios"
- Los cambios se sincronizan automáticamente con el servidor

### Pestaña: Seguridad

#### Cambiar Contraseña
1. Ingresa tu **contraseña actual**
2. Ingresa la **nueva contraseña** (mínimo 8 caracteres)
3. **Confirma** la nueva contraseña
4. Click en "Cambiar contraseña"

**Validaciones**:
- La contraseña actual debe ser correcta
- Las contraseñas nuevas deben coincidir
- Mínimo 8 caracteres

### Pestaña: Zona de Peligro

#### Eliminar Cuenta
⚠️ **ADVERTENCIA**: Esta acción es permanente e irreversible.

**Proceso**:
1. Click en "Eliminar mi cuenta"
2. Confirma en el diálogo de alerta
3. Escribe "ELIMINAR" para confirmar
4. Tu cuenta y todos los datos asociados serán eliminados permanentemente

**Datos que se eliminan**:
- Perfil de usuario
- Conversaciones
- Configuraciones
- Suscripciones
- Mensajes históricos
- Datos de CRM

---

## 🔌 Integraciones

### Acceder a Integraciones

**Ubicación**: `/dashboard/integrations`

**Navegación**: Desde el sidebar → "Integraciones" (sección Configuración)

### Integración con Twilio WhatsApp

#### Estado de Conexión
- **Conectado**: Badge verde con checkmark
- **No conectado**: Badge gris con X

#### Paso a Paso para Configurar Twilio

**1. Crear cuenta en Twilio**
- Ve a [Twilio Console](https://www.twilio.com/console)
- Crea una cuenta o inicia sesión
- Obtén un número de WhatsApp Business

**2. Obtener credenciales**
Necesitas copiar:
- **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Auth Token**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **WhatsApp Number**: `whatsapp:+14155238886`

**3. Configurar variables de entorno**
Agrega estas líneas a tu archivo `.env` en el servidor:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**4. Configurar Webhook en Twilio**
- Ve a la configuración de tu número WhatsApp en Twilio
- En "When a message comes in":
  - **URL**: Copia el webhook URL mostrado en la página
  - **Método HTTP**: POST
- Click en "Copiar" para copiar la URL del webhook

**5. Reiniciar servidor**
- Reinicia el servidor API para aplicar los cambios
- Las variables de entorno se cargarán automáticamente

#### Documentación Adicional
- Link directo a [Twilio WhatsApp Quickstart](https://www.twilio.com/docs/whatsapp/quickstart)

### Integración con HubSpot CRM

#### Estado de Conexión
- **Conectado**: Badge verde con checkmark
- **No conectado**: Badge gris con X

#### Paso a Paso para Configurar HubSpot

**1. Acceder a HubSpot**
- Ve a [HubSpot](https://app.hubspot.com)
- Inicia sesión en tu cuenta

**2. Crear Private App**
- Ve a: **Settings → Integrations → Private Apps**
- Click en "Create a private app"

**3. Configurar permisos**
Selecciona los siguientes scopes:

✓ **crm.objects.contacts** (Read & Write)
✓ **crm.objects.deals** (Read & Write)
✓ **crm.schemas.contacts** (Read & Write)
✓ **crm.schemas.deals** (Read & Write)

**4. Generar Access Token**
- Click en "Create app"
- Copia el **Access Token** generado
- Formato: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**5. Configurar variable de entorno**
Agrega esta línea a tu archivo `.env`:

```env
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**6. Reiniciar servidor**
- Reinicia el servidor API para aplicar los cambios

#### ¿Qué se sincroniza automáticamente?

✓ **Contactos** con nombre, email, teléfono
✓ **Intent Score** (puntuación de intención de compra)
✓ **Sentiment** (sentimiento del cliente)
✓ **Needs & Pain Points** (necesidades identificadas)
✓ **Budget** (presupuesto mencionado)
✓ **Lifecycle Stage** (etapa del cliente)
✓ **Notas de conversación** automáticas

#### Documentación Adicional
- Link directo a [HubSpot Private Apps](https://developers.hubspot.com/docs/api/private-apps)

### 💡 Nota Importante sobre Variables de Entorno

Las variables de entorno (`TWILIO_*`, `HUBSPOT_*`) deben configurarse en el **servidor** donde está desplegada la API.

**Plataformas comunes**:
- **Render**: Settings → Environment Variables
- **Docker**: `docker-compose.yml` o `.env`
- **Vercel**: Settings → Environment Variables
- **Local**: Archivo `.env` en la raíz del proyecto

---

## 💳 Gestión de Suscripción

### Acceder a Suscripción

**Ubicación**: `/dashboard/subscription`

**Navegación**: Desde el sidebar → "Suscripción" (sección Configuración)

### Vista General del Plan

#### Información del Plan Actual
- **Nombre del plan**: Starter, Professional o Enterprise
- **Estado**: Activo o Inactivo
- **Precio mensual**: Mostrado prominentemente
- **Fecha de renovación**: Próximo cargo

#### Alertas Importantes
Si tu plan está programado para cancelarse:
- Banner amarillo con advertencia
- Fecha límite de acceso
- Opción para reactivar

### Métricas de Uso del Período Actual

#### Mensajes Enviados
- Barra de progreso visual
- Contador: `[usado] / [límite]`
- Colores indicativos:
  - 🟢 Verde: 0-69% de uso
  - 🟡 Amarillo: 70-89% de uso
  - 🔴 Rojo: 90-100% de uso

#### Bots Creados
- Muestra cuántos bots has creado vs el límite de tu plan
- Misma lógica de colores que mensajes

#### Almacenamiento RAG
- Muestra espacio usado en MB
- Límite según tu plan
- Importante para documentos subidos

### Acciones sobre la Suscripción

#### Actualizar Plan
- Click en "Actualizar plan"
- Muestra opciones de upgrade/downgrade
- Cambios se aplican en el próximo ciclo de facturación

#### Cancelar Plan
⚠️ **Importante**: Mantendrás acceso hasta el final del período pagado

**Proceso**:
1. Click en "Cancelar plan"
2. Confirma en el diálogo
3. El plan se marca como "cancelado al final del período"
4. Puedes seguir usando el servicio hasta la fecha de renovación
5. Opción de reactivar antes de que expire

### Historial de Pagos

#### Información de Cada Pago
- **Monto**: Precio cobrado
- **Fecha**: Cuándo se realizó el cargo
- **Estado**:
  - 🟢 Pagado
  - 🟡 Pendiente
- **Factura**: Link de descarga (si disponible)

#### Ver Historial Completo
- Los últimos 5 pagos se muestran por defecto
- Click en "Ver todos los pagos" para ver el historial completo

### Panel de Upgrade

Si necesitas más funcionalidades:
- Banner morado con sugerencia
- Click en "Ver planes disponibles"
- Comparación de características
- Upgrade con un solo click

---

## 🔄 Flujo Completo del Usuario

### Primera Vez (Usuario Nuevo)

```
1. /signup
   → Crear cuenta

2. /onboarding
   → Paso 1: Información de empresa
   → Paso 2: Configuración regional
   → Paso 3: Selección de plan
   → Paso 4: Confirmación

3. /dashboard
   → Acceso al panel principal
```

### Usuario Existente (Login)

```
1. /login
   → Iniciar sesión con email/contraseña

2. /dashboard/chat
   → Vista principal de chats

3. Navegación disponible:
   - Chats
   - CRM
   - Configuración Bot
   - Pruebas
   - Mi Perfil
   - Integraciones
   - Suscripción
```

### Configuración Inicial Recomendada

**Orden sugerido después del onboarding**:

1. **Mi Perfil** (`/dashboard/profile`)
   - Completar información de la empresa
   - Subir foto de perfil
   - Verificar zona horaria

2. **Integraciones** (`/dashboard/integrations`)
   - Conectar Twilio para WhatsApp
   - Conectar HubSpot para CRM (opcional)

3. **Configuración Bot** (`/dashboard/config`)
   - Personalizar prompts del sistema
   - Configurar voz TTS
   - Subir documentos para RAG

4. **Pruebas** (`/dashboard/test`)
   - Probar conversaciones
   - Validar flujo del bot
   - Ajustar configuración según resultados

5. **Chats** (`/dashboard/chat`)
   - Empezar a recibir mensajes reales
   - Monitorear conversaciones
   - Intervenir cuando sea necesario

### Navegación en el Sidebar

El sidebar del dashboard está organizado en dos secciones:

#### Sección: Principal
- **Chats**: Conversaciones en tiempo real
- **CRM**: Pipeline de ventas y contactos
- **Configuración Bot**: Prompts, TTS, RAG
- **Pruebas**: Simulador de conversaciones

#### Sección: Configuración
- **Mi Perfil**: Información personal y seguridad
- **Integraciones**: Twilio y HubSpot
- **Suscripción**: Plan, uso y facturación

#### Elemento Fijo (Footer)
- **Mini perfil**: Avatar y nombre de empresa
- **Cerrar Sesión**: Logout seguro

---

## ✨ Características Destacadas

### 🔐 Seguridad
- Autenticación con JWT tokens
- Refresh tokens automáticos
- Sesiones persistentes
- Logout seguro

### 🎨 Experiencia de Usuario
- Diseño responsive (mobile-friendly)
- Modo oscuro/claro
- Transiciones suaves
- Feedback visual en tiempo real

### 📊 Transparencia
- Métricas de uso en tiempo real
- Alertas proactivas de límites
- Historial completo de facturación
- Estado de integraciones visible

### 🚀 Onboarding Inteligente
- Wizard paso a paso
- Guardado automático de progreso
- Sugerencias contextuales
- Configuración guiada

---

## 🆘 Soporte

### Documentación Técnica
- **`../01-architecture/sad.md`**: Arquitectura canónica del sistema
- **`../08-developers/api-reference.md`**: Referencia completa de endpoints
- **`../08-developers/README.md`**: Guía de onboarding técnico

### Enlaces Útiles
- **Twilio Docs**: https://www.twilio.com/docs/whatsapp/quickstart
- **HubSpot Docs**: https://developers.hubspot.com/docs/api/private-apps

### Contacto
- **Email**: Configurado en tu plan
- **Soporte prioritario**: Planes Professional y Enterprise
- **Soporte 24/7**: Plan Enterprise

---

**Última actualización**: 2025-11-27
**Versión de la guía**: 1.0.0
