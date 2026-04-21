# SRS - Software Requirements Specification

## Objetivo funcional

`neroxia` resuelve ventas conversacionales para empresas que atienden prospectos por WhatsApp y otros canales compatibles. El sistema debe ayudar a captar leads, calificar interes, sostener conversaciones comerciales, registrar contexto y sincronizar informacion relevante con CRM y configuraciones por tenant.

## Alcance

El producto cubre:

- autenticacion y acceso al dashboard del tenant
- configuracion del bot, integraciones y conocimiento RAG
- recepcion y procesamiento de mensajes entrantes
- clasificacion de intencion y sentimiento
- recoleccion y validacion de datos del lead
- seguimiento del estado conversacional y del pipeline CRM
- handoff a humano cuando corresponde
- gestion de suscripciones, uso e integraciones principales

Queda fuera de este SRS el detalle de despliegue, wiring tecnico interno y comandos operativos.

## Actores

- `Owner/Admin del tenant`: configura el sistema, revisa conversaciones, integra canales y CRM
- `Agente humano de ventas`: toma handoff o revisa el estado comercial
- `Lead/cliente final`: conversa por WhatsApp o canales soportados
- `Sistemas externos`: OpenAI, Twilio, HubSpot, Supabase y proveedores de despliegue

## Casos de uso principales

### 1. Onboarding y acceso

- El usuario crea cuenta, completa onboarding y accede al dashboard.
- El sistema debe permitir configurar empresa, zona horaria, idioma y plan.

### 2. Conversacion automatizada

- Un lead envia un mensaje por canal soportado.
- El sistema identifica o crea el usuario conversacional.
- El motor analiza intencion, sentimiento y datos faltantes.
- El bot responde segun stage, contexto RAG y configuracion del tenant.

### 3. Recoleccion de datos comerciales

- El sistema extrae nombre, email, telefono, necesidades, pain points y presupuesto cuando aplica.
- Los datos deben validarse antes de persistir o sincronizarse externamente.

### 4. Seguimiento y CRM

- El sistema mantiene historial de mensajes, resumen conversacional y estado del lead.
- Si la integracion CRM esta habilitada, debe sincronizar contactos, notas y etapas compatibles.

### 5. Configuracion y conocimiento

- El tenant puede ajustar prompts, voz TTS, relacion audio/texto y documentos RAG.
- El sistema debe reflejar esos cambios en el comportamiento operativo del bot.

### 6. Handoff y seguimiento

- El sistema puede marcar conversaciones para atencion humana.
- El sistema puede programar follow-ups y registrar actividad posterior.

## Reglas funcionales

- La plataforma es multi-tenant: la configuracion y datos deben resolverse por usuario autenticado o integracion correspondiente.
- El workflow conversacional usa stages de negocio y debe reflejar el progreso comercial del lead.
- La validacion de datos recolectados es estricta antes de sincronizar con CRM.
- El sistema debe funcionar aun cuando integraciones opcionales no esten configuradas, degradando de forma segura.
- El bot puede operar en modo automatico, manual o de atencion requerida.

## Restricciones funcionales

- El comportamiento depende de credenciales y configuracion externa disponibles.
- Algunos flujos avanzados dependen de integraciones opcionales como Twilio, HubSpot o Meta.
- La persistencia y autenticacion cambian entre desarrollo y produccion, pero el comportamiento esperado del producto debe mantenerse.

## Criterios de aceptacion de alto nivel

- Un agente nuevo puede identificar que hace el producto y para quien leyendo este documento.
- Un tenant puede autenticarse, configurar el sistema y usar el dashboard sin leer documentacion tecnica.
- Un mensaje entrante puede disparar un flujo conversacional con persistencia y estado.
- Los datos comerciales relevantes pueden persistirse y, si corresponde, sincronizarse con CRM.
- Las decisiones funcionales del producto quedan separadas de detalles de implementacion y despliegue.

## Fuentes utilizadas en esta consolidacion

- `README.md`
- `user-guide.md`
