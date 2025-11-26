# 📋 TODO: Tests Específicos para LLM

**Creado**: 2025-11-24 21:25:00  
**Asignado a**: QA Agent  
**Prioridad**: 🟠 Alta  
**Relacionado**: Bug #12 (Resuelto)

---

## 🎯 Objetivo

Crear tests específicos para verificar el comportamiento del LLM y el bot workflow, separados de los tests de integración rápidos que usan mocks.

## 📝 Contexto

Durante la resolución del Bug #12, implementamos mocks para:
- Base de datos (CRUD operations)
- Bot workflow (`process_message`)

Esto permite que los tests de integración corran rápido sin llamadas reales al LLM. Sin embargo, **necesitamos tests que verifiquen el comportamiento real del LLM**.

## ✅ Tests a Crear

### 1. Tests de LLM Service (`apps/bot-engine/tests/test_llm_real.py`)

```python
"""
Tests para verificar comportamiento real del LLM.
NOTA: Estos tests hacen llamadas reales a OpenAI y cuestan dinero.
Marcar con @pytest.mark.llm para ejecutar solo cuando sea necesario.
"""

@pytest.mark.llm
@pytest.mark.slow
async def test_intent_classification_real():
    """Verificar que el LLM clasifica intents correctamente."""
    # Test con mensajes reales
    # Verificar scores de intent
    pass

@pytest.mark.llm
@pytest.mark.slow
async def test_data_extraction_real():
    """Verificar que el LLM extrae datos correctamente."""
    # Test con conversaciones reales
    # Verificar extracción de nombre, email, teléfono
    pass

@pytest.mark.llm
@pytest.mark.slow
async def test_rag_context_injection_real():
    """Verificar que el RAG inyecta contexto correctamente."""
    # Test con documentos reales
    # Verificar que las respuestas usan el contexto
    pass
```

### 2. Tests de Workflow Completo (`apps/bot-engine/tests/test_workflow_e2e.py`)

```python
"""
Tests end-to-end del workflow completo con LLM real.
"""

@pytest.mark.e2e
@pytest.mark.slow
async def test_complete_sales_conversation():
    """Simular conversación de ventas completa."""
    # Simular flujo: saludo → interés → preguntas → cierre
    # Verificar transiciones de stage
    # Verificar respuestas coherentes
    pass

@pytest.mark.e2e
@pytest.mark.slow
async def test_adaptive_personalization():
    """Verificar personalización adaptativa."""
    # Simular múltiples mensajes
    # Verificar que el bot adapta su tono/estilo
    pass
```

### 3. Tests de Optimizaciones LLM (`apps/bot-engine/tests/test_llm_optimizations_real.py`)

```python
"""
Tests para verificar las optimizaciones implementadas en LLM_OPTIMIZATION_CHANGELOG.md
"""

@pytest.mark.llm
async def test_context_window_truncation():
    """Verificar que la truncación de contexto funciona."""
    # Crear conversación larga (>12 mensajes)
    # Verificar que se trunca correctamente
    # Verificar que preserva inicio y fin
    pass

@pytest.mark.llm
async def test_few_shot_learning_data_extraction():
    """Verificar que los ejemplos mejoran la extracción."""
    # Test con nombres cortos, internacionales
    # Verificar que se aceptan correctamente
    pass
```

## 🔧 Configuración Necesaria

### pytest.ini
```ini
[pytest]
markers =
    llm: Tests que hacen llamadas reales al LLM (costo $$$)
    slow: Tests lentos (>5 segundos)
    e2e: Tests end-to-end completos
```

### Ejecutar tests
```bash
# Tests rápidos (con mocks) - SIEMPRE
pytest apps/api/tests/

# Tests de LLM - SOLO cuando sea necesario
pytest -m llm apps/bot-engine/tests/

# Tests E2E - SOLO antes de deploy
pytest -m e2e apps/bot-engine/tests/

# Todos los tests excepto LLM
pytest -m "not llm"
```

## 📊 Métricas a Verificar

1. **Precisión de Intent Classification**: >85%
2. **Tasa de Extracción de Datos**: >80%
3. **Precisión de RAG**: >90%
4. **Tiempo de Respuesta**: <3 segundos
5. **Costo por Test**: <$0.05

## ⚠️ Consideraciones

- **Costo**: Cada test con LLM real cuesta dinero
- **Velocidad**: Tests lentos (2-5 segundos cada uno)
- **Variabilidad**: LLM puede dar respuestas ligeramente diferentes
- **CI/CD**: No ejecutar en cada commit, solo pre-deploy

## 📅 Plan de Implementación

1. **Semana 1**: Crear estructura de tests y markers
2. **Semana 2**: Implementar tests de LLM Service
3. **Semana 3**: Implementar tests de Workflow E2E
4. **Semana 4**: Implementar tests de Optimizaciones

## ✅ Criterios de Aceptación

- [ ] Tests de LLM creados con marker `@pytest.mark.llm`
- [ ] Tests E2E creados con marker `@pytest.mark.e2e`
- [ ] Documentación de cómo ejecutar tests
- [ ] Configuración de pytest.ini
- [ ] Tests pasan con LLM real
- [ ] Métricas documentadas

---

**Nota**: Este TODO fue creado como resultado de la resolución del Bug #12. Los tests con mocks están funcionando correctamente, pero necesitamos verificación con LLM real para asegurar calidad del bot.
