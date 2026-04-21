"""LLM service with intelligent model routing."""

import os
import re
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from neroxia_shared import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for managing LLM interactions with intelligent model routing."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize LLM service.

        Args:
            openai_api_key: OpenAI API key (if not provided, reads from env)
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment")

        # Initialize both models
        self.gpt4o_mini = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=self.api_key,
            temperature=0.7,
        )

        self.gpt4o = ChatOpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0.8,
        )

        logger.info("LLM service initialized with GPT-4o and GPT-4o-mini")

    def prepare_optimized_context(
        self,
        messages: List[BaseMessage],
        max_messages: int = 12,
        preserve_start: int = 2,
        preserve_end: int = 6
    ) -> List[BaseMessage]:
        """
        Optimize conversation context by intelligently truncating long histories.

        Strategy:
        - Always preserve first N messages (welcome + initial interaction)
        - Always preserve last M messages (recent context)
        - If total > max_messages, summarize the middle section

        Args:
            messages: Full conversation history
            max_messages: Maximum messages to keep without summarization
            preserve_start: Number of initial messages to always keep
            preserve_end: Number of recent messages to always keep

        Returns:
            Optimized list of messages
        """
        if len(messages) <= max_messages:
            # Short enough, return as is
            return messages

        logger.info(f"Optimizing context: {len(messages)} messages -> truncating to ~{max_messages}")

        # Separate messages
        start_messages = messages[:preserve_start]
        end_messages = messages[-preserve_end:]
        middle_messages = messages[preserve_start:-preserve_end]

        if not middle_messages:
            # Edge case: start and end overlap
            return messages

        # Create summary of middle section
        middle_summary = self._create_quick_summary(middle_messages)
        summary_message = SystemMessage(
            content=f"[Resumen de {len(middle_messages)} mensajes anteriores: {middle_summary}]"
        )

        # Combine: start + summary + end
        optimized = start_messages + [summary_message] + end_messages

        logger.info(f"Context optimized: {len(messages)} -> {len(optimized)} messages (saved {len(messages) - len(optimized)} messages)")
        return optimized

    def analyze_conversation_trends(
        self,
        messages: List[BaseMessage],
        current_sentiment: str = "neutral",
        current_intent: float = 0.5
    ) -> Dict[str, Any]:
        """
        Analyze conversation trends for personalization.

        Examines:
        - Sentiment progression (improving/declining/stable)
        - Intent momentum (increasing/decreasing)
        - User engagement level

        Args:
            messages: Conversation history
            current_sentiment: Current sentiment
            current_intent: Current intent score

        Returns:
            Dict with trend analysis
        """
        # Extract message count
        user_messages = [m for m in messages if isinstance(m, HumanMessage)]
        message_count = len(user_messages)

        # Default trends for new conversations
        if message_count < 3:
            return {
                "sentiment_trend": "new_conversation",
                "intent_trend": "initial",
                "engagement_level": "high" if message_count >= 1 else "none",
                "message_count": message_count,
                "recommendation": "welcome_warmly"
            }

        # Analyze sentiment trend (simplified - check last few messages metadata)
        # In real implementation, this would track sentiment history
        sentiment_trend = "stable"
        if current_sentiment == "negative":
            sentiment_trend = "declining"
        elif current_sentiment == "positive":
            sentiment_trend = "improving"

        # Analyze intent momentum
        intent_trend = "increasing" if current_intent > 0.6 else "stable" if current_intent > 0.3 else "decreasing"

        # Engagement level based on message count and recent activity
        if message_count > 10:
            engagement_level = "high"
        elif message_count > 5:
            engagement_level = "medium"
        else:
            engagement_level = "low"

        # Generate recommendation
        if sentiment_trend == "declining":
            recommendation = "empathize_and_support"
        elif intent_trend == "increasing":
            recommendation = "introduce_urgency"
        elif engagement_level == "high":
            recommendation = "maintain_momentum"
        else:
            recommendation = "standard_approach"

        return {
            "sentiment_trend": sentiment_trend,
            "intent_trend": intent_trend,
            "engagement_level": engagement_level,
            "message_count": message_count,
            "recommendation": recommendation
        }

    def build_adaptive_system_prompt(
        self,
        base_prompt: str,
        trends: Dict[str, Any],
        current_sentiment: str,
        current_intent: float
    ) -> str:
        """
        Build adaptive system prompt based on conversation trends.

        Modifies base prompt with dynamic instructions based on:
        - Sentiment progression
        - Intent momentum
        - User engagement

        Args:
            base_prompt: Original system prompt
            trends: Trend analysis from analyze_conversation_trends
            current_sentiment: Current sentiment
            current_intent: Current intent score

        Returns:
            Enhanced system prompt with adaptive instructions
        """
        enhanced_prompt = base_prompt

        # Add tone modifiers based on sentiment trend
        if trends["recommendation"] == "empathize_and_support":
            enhanced_prompt += "\n\n=== AJUSTE DE TONO ===\n"
            enhanced_prompt += "El cliente muestra signos de frustración o desinterés. Ajusta tu tono:\n"
            enhanced_prompt += "- Sé más empático y comprensivo\n"
            enhanced_prompt += "- Pregunta directamente cómo puedes ayudar mejor\n"
            enhanced_prompt += "- Ofrece alternativas o soluciones específicas\n"
            enhanced_prompt += "- Considera sugerir hablar con un humano si persiste la frustración"

        elif trends["recommendation"] == "introduce_urgency":
            enhanced_prompt += "\n\n=== ESTRATEGIA DE CIERRE ===\n"
            enhanced_prompt += f"El cliente tiene alto interés (intent: {current_intent:.2f}). Acciones recomendadas:\n"
            enhanced_prompt += "- Introduce un llamado a la acción claro\n"
            enhanced_prompt += "- Menciona beneficios inmediatos de actuar ahora\n"
            enhanced_prompt += "- Ofrece próximos pasos concretos (demo, prueba, compra)\n"
            enhanced_prompt += "- Mantén el momentum, no lo pierdas con información innecesaria"

        elif trends["recommendation"] == "maintain_momentum":
            enhanced_prompt += "\n\n=== MANTENER ENGAGEMENT ===\n"
            enhanced_prompt += f"Conversación activa ({trends['message_count']} mensajes). Estrategia:\n"
            enhanced_prompt += "- Mantén el ritmo de la conversación\n"
            enhanced_prompt += "- Sé más casual y entusiasta (el cliente está receptivo)\n"
            enhanced_prompt += "- Haz preguntas que profundicen en sus necesidades\n"
            enhanced_prompt += "- Comparte casos de éxito relevantes"

        # Add engagement level modifier
        if trends["engagement_level"] == "low":
            enhanced_prompt += "\n\n=== INICIO DE CONVERSACIÓN ===\n"
            enhanced_prompt += "Cliente recién iniciando. Establece rapport:\n"
            enhanced_prompt += "- Sé particularmente amigable y acogedor\n"
            enhanced_prompt += "- Haz preguntas abiertas para conocerlo\n"
            enhanced_prompt += "- Construye confianza antes de vender"

        logger.info(f"Adaptive prompt built: recommendation={trends['recommendation']}, engagement={trends['engagement_level']}")

        return enhanced_prompt

    def _create_quick_summary(self, messages: List[BaseMessage]) -> str:
        """
        Create a quick summary of messages without calling LLM.

        Extracts key information from middle messages:
        - Topics mentioned
        - Key data points
        - Sentiment progression

        Args:
            messages: Messages to summarize

        Returns:
            Brief summary string
        """
        # Extract user and AI messages
        user_msgs = []
        ai_msgs = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_msgs.append(msg.content[:100])  # First 100 chars
            elif hasattr(msg, 'content'):
                from langchain_core.messages import AIMessage
                if isinstance(msg, AIMessage):
                    ai_msgs.append(msg.content[:100])

        # Build concise summary
        summary_parts = []
        if user_msgs:
            summary_parts.append(f"Cliente mencionó: {'; '.join(user_msgs[:2])}")  # First 2 user messages
        if ai_msgs:
            summary_parts.append(f"Bot respondió sobre: {'; '.join(ai_msgs[:2])}")  # First 2 AI messages

        summary = " | ".join(summary_parts) if summary_parts else "Conversación general"

        # Truncate to max 200 chars
        if len(summary) > 200:
            summary = summary[:197] + "..."

        return summary

    def split_into_parts(self, text: str, max_words: int = 50) -> List[str]:
        """
        Split text into parts respecting complete sentences.

        Divides text into parts with max_words per part, ensuring complete sentences
        are kept together.

        Args:
            text: Text to split
            max_words: Maximum words per part (default: 50)

        Returns:
            List of text parts
        """
        # Split into sentences using regex (handles . ! ? followed by space or end)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        parts = []
        current_part = []
        current_word_count = 0

        for sentence in sentences:
            # Count words in this sentence
            sentence_words = len(sentence.split())

            # If adding this sentence exceeds max_words, save current part and start new one
            if current_word_count + sentence_words > max_words and current_part:
                parts.append(' '.join(current_part))
                current_part = [sentence]
                current_word_count = sentence_words
            else:
                current_part.append(sentence)
                current_word_count += sentence_words

        # Add remaining part
        if current_part:
            parts.append(' '.join(current_part))

        logger.debug(f"Text split into {len(parts)} parts (max {max_words} words per part)")
        return parts

    def get_llm_for_task(self, task_type: str) -> ChatOpenAI:
        """
        Router to select appropriate LLM based on task type.

        Strategy:
        - extraction, classification, analysis → GPT-4o-mini (faster, cheaper)
        - response, closing, welcome → GPT-4o (better quality)

        Args:
            task_type: Type of task (extraction/classification/analysis/response/closing/welcome)

        Returns:
            Appropriate ChatOpenAI instance
        """
        lightweight_tasks = ["extraction", "classification", "analysis", "sentiment", "intent"]
        heavyweight_tasks = ["response", "closing", "welcome", "conversation"]

        if task_type.lower() in lightweight_tasks:
            logger.debug(f"Using GPT-4o-mini for task: {task_type}")
            return self.gpt4o_mini
        elif task_type.lower() in heavyweight_tasks:
            logger.debug(f"Using GPT-4o for task: {task_type}")
            return self.gpt4o
        else:
            # Default to GPT-4o-mini for unknown tasks
            logger.warning(f"Unknown task type '{task_type}', defaulting to GPT-4o-mini")
            return self.gpt4o_mini

    async def classify_intent(self, message: str, conversation_history: Optional[List[BaseMessage]] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify user intent and calculate intent score.

        Args:
            message: User's message
            conversation_history: Previous messages for context
            config: Optional configuration dict with custom intent_prompt

        Returns:
            Dict with intent category and score (0-1)
        """
        llm = self.get_llm_for_task("classification")

        # Check if custom intent_prompt is provided in config
        if config and config.get("intent_prompt"):
            # Use custom prompt from configuration
            custom_prompt = config["intent_prompt"]
            # Inject message and context variables
            prompt = custom_prompt.replace("{message}", message)
            if conversation_history:
                history_length = len([m for m in conversation_history if isinstance(m, HumanMessage)])
                prompt = prompt.replace("{context}", f"Esta es la interacción #{history_length + 1} del cliente.")
            else:
                prompt = prompt.replace("{context}", "Este es el primer mensaje del cliente (inicio de conversación).")

            logger.info("Using custom intent_prompt from configuration")
        else:
            # Use improved default prompt
            # Build context indicator
            history_context = ""
            if conversation_history and len(conversation_history) > 0:
                history_length = len([m for m in conversation_history if isinstance(m, HumanMessage)])
                history_context = f"\nContexto: Esta es la interacción #{history_length + 1} del cliente."
            else:
                history_context = "\nContexto: Este es el primer mensaje del cliente (inicio de conversación)."

            prompt = f"""Analiza el siguiente mensaje de un cliente potencial y clasifica su intención REAL considerando el contexto completo.

Mensaje actual: "{message}"{history_context}

Clasifica en una de estas categorías:
- browsing: Solo está mirando, no muestra señales de compra (puntuación: 0.0-0.3)
- interested: Muestra interés genuino, hace preguntas sobre el producto/servicio (puntuación: 0.3-0.6)
- ready_to_buy: Señales claras de compra inmediata ("quiero comprar", "cómo pago", etc.) (puntuación: 0.6-0.9)
- objection: Tiene dudas u objeciones que necesitan resolverse (puntuación: 0.4-0.6)
- leaving: Quiere terminar o posponer la conversación ("luego vuelvo", "después te escribo") (puntuación: 0.0-0.2)

CRITERIOS DE CLASIFICACIÓN:
1. Si es el PRIMER mensaje:
   - Saludo simple ("hola", "buenos días") → interested (0.4-0.5) - cliente inicia contacto
   - Pregunta específica → interested (0.5-0.6) - cliente con necesidad clara
   - Expresión de interés directo → ready_to_buy (0.7+) - cliente muy motivado

2. Si hay HISTORIAL previo:
   - Analiza la PROGRESIÓN de la conversación (¿está aumentando o disminuyendo el interés?)
   - Considera el MOMENTUM actual (¿el cliente está cada vez más comprometido?)
   - La clasificación debe reflejar la INTENCIÓN ACTUAL, no solo las palabras

3. Señales de alta intención (0.7+):
   - Preguntas sobre precio, pago, entrega
   - "Quiero", "necesito", "me interesa comprar"
   - Solicitud de información para concretar

Responde SOLO con JSON válido en este formato exacto:
{{"category": "nombre_categoria", "score": 0.0}}"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)

            # Parse response
            import json
            result = json.loads(response.content)
            logger.info(f"Intent classified: {result}")
            return result
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {"category": "browsing", "score": 0.3}

    async def analyze_sentiment(self, message: str) -> str:
        """
        Analyze sentiment of user's message.

        Args:
            message: User's message

        Returns:
            Sentiment: positive/neutral/negative
        """
        llm = self.get_llm_for_task("sentiment")

        prompt = f"""Analiza el sentimiento de este mensaje del cliente.

Mensaje: "{message}"

Responde con UNA SOLA PALABRA: positive, neutral, o negative"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)
            sentiment = response.content.strip().lower()

            if sentiment not in ["positive", "neutral", "negative"]:
                sentiment = "neutral"

            logger.info(f"Sentiment analyzed: {sentiment}")
            return sentiment
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral"

    async def extract_data(self, message: str, conversation_history: Optional[List[BaseMessage]] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract user data from message (name, email, needs, budget, etc.).

        Args:
            message: User's message
            conversation_history: Previous messages for context
            config: Optional configuration dict with custom data_extraction_prompt

        Returns:
            Dict with extracted data
        """
        llm = self.get_llm_for_task("extraction")

        # Check if custom data_extraction_prompt is provided in config
        if config and config.get("data_extraction_prompt"):
            # Use custom prompt from configuration
            custom_prompt = config["data_extraction_prompt"]
            prompt = custom_prompt.replace("{message}", message)
            logger.info("Using custom data_extraction_prompt from configuration")
        else:
            # Use improved default prompt
            prompt = f"""Extrae ÚNICAMENTE información EXPLÍCITA del cliente de este mensaje. NO inventes ni asumas datos.

Mensaje: "{message}"

REGLAS CRÍTICAS:
- Solo extraer datos que el cliente MENCIONE EXPLÍCITAMENTE
- Si el dato no está presente, usar null
- NO asumir ni inferir información
- Validar cuidadosamente cada extracción

Campos a extraer:
- name: Nombre completo del cliente
- email: Dirección de email
- phone: Número de teléfono
- needs: Lo que el cliente busca o necesita
- budget: Presupuesto o rango de precio
- pain_points: Problemas que quiere resolver

VALIDACIÓN ESTRICTA (ejemplos):

✅ name - VÁLIDO:
  "Me llamo María" → {{"name": "María"}}
  "Soy Juan Pérez" → {{"name": "Juan Pérez"}}
  "Mi nombre es Dr. García" → {{"name": "Dr. García"}}

❌ name - INVÁLIDO (retornar null):
  "Hola" → NO es un nombre, es un saludo
  "Buenos días" → NO es un nombre
  "Señor" → NO es un nombre completo

✅ email - VÁLIDO:
  "Mi email es juan@gmail.com" → {{"email": "juan@gmail.com"}}
  "Escríbeme a maria.lopez@empresa.co" → {{"email": "maria.lopez@empresa.co"}}

❌ email - INVÁLIDO (retornar null):
  "juan@" → Incompleto
  "email.com" → Falta usuario

✅ phone - VÁLIDO:
  "Mi número es +54 11 1234-5678" → {{"phone": "+54 11 1234-5678"}}
  "Llámame al 1234567890" → {{"phone": "1234567890"}}
  "+1-555-123-4567" → {{"phone": "+1-555-123-4567"}}

❌ phone - INVÁLIDO (retornar null):
  "teléfono" → Solo una palabra, no un número
  "123" → Muy corto para ser teléfono válido

✅ needs - VÁLIDO:
  "Necesito un sistema de gestión" → {{"needs": "sistema de gestión"}}
  "Busco mejorar mis ventas" → {{"needs": "mejorar ventas"}}

❌ needs - INVÁLIDO (retornar null):
  "hola" → No expresa una necesidad
  "información" → Muy vago, no es una necesidad específica

IMPORTANTE: Sé MUY conservador. Si tienes alguna duda sobre la validez del dato, retorna null.

Responde SOLO con JSON válido:
{{"name": null, "email": null, "phone": null, "needs": null, "budget": null, "pain_points": null}}"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)

            import json
            import re
            result = json.loads(response.content)

            # Filter out null values
            result = {k: v for k, v in result.items() if v is not None and v != ""}

            # Lightweight post-processing (trust the LLM, only catch extreme edge cases)
            validated_result = {}

            # Name: Light cleanup and capitalization
            if "name" in result and result["name"]:
                name = result["name"].strip()
                if len(name) >= 2:  # Allow short names like "Li", "Jo"
                    validated_result["name"] = name.title()

            # Email: Basic format check only
            if "email" in result and result["email"]:
                email = result["email"].strip().lower()
                # Only validate it has @ and domain
                if "@" in email and "." in email.split("@")[-1]:
                    validated_result["email"] = email

            # Phone: Minimal validation (trust LLM)
            if "phone" in result and result["phone"]:
                phone = result["phone"].strip()
                # Just verify it has some digits
                if any(char.isdigit() for char in phone):
                    validated_result["phone"] = phone

            # Needs: Accept anything meaningful (trust LLM validation)
            if "needs" in result and result["needs"]:
                needs = result["needs"].strip()
                if len(needs) >= 3:  # Very minimal length check
                    validated_result["needs"] = needs

            # Budget: Trust LLM extraction
            if "budget" in result and result["budget"]:
                budget = result["budget"].strip()
                if len(budget) >= 1:
                    validated_result["budget"] = budget

            # Pain points: Trust LLM extraction
            if "pain_points" in result and result["pain_points"]:
                pain_points = result["pain_points"].strip()
                if len(pain_points) >= 3:
                    validated_result["pain_points"] = pain_points

            logger.info(f"Data extracted and validated: {validated_result}")
            return validated_result

        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return {}

    async def generate_response(
        self,
        messages: List[BaseMessage],
        system_prompt: str,
        use_emojis: bool = True,
        rag_context: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate conversational response.

        Args:
            messages: Conversation history
            system_prompt: System prompt with instructions
            use_emojis: Whether to include emojis
            rag_context: Optional RAG context to include
            config: Configuration dict with multi_part_messages and max_words_per_response

        Returns:
            Generated response text (may include [PAUSA] separators if multi_part_messages is enabled)
        """
        llm = self.get_llm_for_task("response")

        # Extract config values with defaults
        config = config or {}
        multi_part_messages = config.get("multi_part_messages", False)
        max_words_per_response = config.get("max_words_per_response", 150)

        # Build enhanced system prompt
        enhanced_prompt = system_prompt

        # Add word limit instruction
        enhanced_prompt += f"\n\nIMPORTANTE: Limita tu respuesta a máximo {max_words_per_response} palabras."

        # Add emoji instruction
        if use_emojis:
            enhanced_prompt += "\n\nIMPORTANTE: Usa emojis de manera natural en tus respuestas para hacerlas más amigables y expresivas."
        else:
            enhanced_prompt += "\n\nIMPORTANTE: NO uses emojis en tus respuestas."

        # Enhanced RAG context injection with clear instructions
        if rag_context:
            enhanced_prompt += f"""

=== 📚 DOCUMENTACIÓN OFICIAL DEL PRODUCTO/SERVICIO ===

La siguiente información proviene de los documentos oficiales cargados en el sistema. Esta información es PRIORITARIA y AUTORITATIVA sobre cualquier otro conocimiento:

{rag_context}

=== INSTRUCCIONES DE USO DE LA DOCUMENTACIÓN ===

1. **PRIORIDAD ABSOLUTA**: Si la pregunta del cliente se relaciona con información en estos documentos, úsala DIRECTAMENTE como fuente de verdad.

2. **CITACIÓN NATURAL**: Incorpora la información de manera conversacional, no copies textualmente a menos que sean especificaciones técnicas exactas.
   - ✅ Correcto: "Según nuestra documentación, el precio incluye..."
   - ❌ Incorrecto: Copiar párrafos completos sin adaptar

3. **TRANSPARENCIA**: Si los documentos NO cubren la pregunta específica del cliente:
   - Aclara que la información no está en la documentación oficial
   - Ofrece ayuda con lo que sí sabes o sugiere escalar a un humano

4. **COHERENCIA**: Si hay contradicciones entre estos documentos y tu conocimiento base:
   - SIEMPRE prioriza los documentos oficiales
   - Los documentos reflejan información actualizada y específica del producto

5. **NATURALIDAD**: Mantén un tono conversacional y amigable, no suenes como un manual técnico a menos que el cliente pida especificaciones detalladas.

===
"""

        # Optimize context for long conversations (only for main conversation, not analysis tasks)
        optimized_messages = self.prepare_optimized_context(messages)

        # Prepare messages - convert BaseMessage objects to proper format
        full_messages = [SystemMessage(content=enhanced_prompt)]

        # Ensure all messages are properly formatted BaseMessage objects
        for msg in optimized_messages:
            if isinstance(msg, BaseMessage):
                full_messages.append(msg)
            elif isinstance(msg, dict):
                # If message is a dict, convert to proper BaseMessage
                if msg.get("role") == "user" or msg.get("role") == "human":
                    full_messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant" or msg.get("role") == "ai":
                    from langchain_core.messages import AIMessage
                    full_messages.append(AIMessage(content=msg.get("content", "")))
                elif msg.get("role") == "system":
                    full_messages.append(SystemMessage(content=msg.get("content", "")))

        try:
            response = await llm.ainvoke(full_messages)
            response_text = response.content
            logger.info(f"Response generated (length: {len(response_text)})")

            # Apply multi-part message splitting if enabled
            if multi_part_messages:
                word_count = len(response_text.split())
                # Split if >= 20 words
                if word_count >= 20:
                    # Calculate words per part for 3 parts
                    words_per_part = word_count // 3 if word_count >= 30 else word_count // 2
                    parts = self.split_into_parts(response_text, max_words=words_per_part)

                    # Limit to 3 parts maximum
                    if len(parts) > 3:
                        # Merge extra parts into the last 3
                        parts = [parts[0], ' '.join(parts[1:-1]), parts[-1]]

                    if len(parts) > 1:
                        response_text = "\n\n[PAUSA]\n\n".join(parts)
                        logger.info(f"Response split into {len(parts)} parts for multi-part delivery")

            return response_text
        except Exception as e:
            logger.error(f"Response generation error: {e}", exc_info=True)
            return "I apologize, I'm having trouble responding right now. Could you please try again?"

    async def generate_closing_message(self, user_data: Dict[str, Any], payment_link: str) -> str:
        """
        Generate a closing message with payment link.

        Args:
            user_data: Collected user data
            payment_link: Payment link to include

        Returns:
            Closing message with payment link
        """
        llm = self.get_llm_for_task("closing")

        name = user_data.get("name", "")

        prompt = f"""Genera un mensaje de cierre cálido y natural para un cliente de WhatsApp que está listo para comprar.

Nombre del cliente: {name if name else ""}
Link de pago: {payment_link}

INSTRUCCIONES CRÍTICAS:

1. **TONO**: Escribe como si estuvieras continuando una conversación de WhatsApp, NO como un email formal
2. **PROHIBIDO**: NO uses plantillas formales, NO incluyas firmas, NO uses placeholders como "[Su Nombre/Empresa]", "[Nombre]", etc.
3. **ESTILO**: Usa emojis de manera natural (✨, 🎉, 😊, etc.) para hacer el mensaje más amigable
4. **PERSONALIZACIÓN**: 
   - Si hay nombre: úsalo de forma natural ("¡Perfecto, {name}!")
   - Si NO hay nombre: usa "¡Perfecto!" o "¡Excelente!" sin forzar un saludo genérico
5. **ESTRUCTURA**: 2-3 oraciones máximo, directas y amigables
6. **LINK**: Integra el link de pago de forma natural en la conversación

EJEMPLOS DE LO QUE DEBES HACER:

✅ CON nombre:
"¡Perfecto, María! 🎉 Aquí está tu link de pago: {payment_link}
Si tienes alguna duda, escríbeme sin problema. ¡Estoy aquí para ayudarte! 😊"

✅ SIN nombre:
"¡Excelente! 🎉 Te comparto el link para completar tu compra: {payment_link}
Cualquier duda que tengas, no dudes en escribirme. ¡Estoy para ayudarte! ✨"

EJEMPLOS DE LO QUE NO DEBES HACER:

❌ "Estimado cliente, gracias por su interés..."
❌ "Atentamente, [Su Nombre/Empresa]"
❌ Cualquier texto que parezca un email formal
❌ Firmas o despedidas formales

Genera SOLO el mensaje conversacional, sin comentarios adicionales."""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)
            logger.info("Closing message generated")
            return response.content
        except Exception as e:
            logger.error(f"Closing message generation error: {e}")
            return f"Great! Here's your payment link: {payment_link}\n\nFeel free to reach out if you have any questions!"

    async def generate_follow_up_message(self, user_data: Dict[str, Any], follow_up_count: int) -> str:
        """
        Generate a follow-up message based on follow-up count.

        Args:
            user_data: User data
            follow_up_count: Number of follow-ups sent so far

        Returns:
            Follow-up message
        """
        llm = self.get_llm_for_task("response")

        name = user_data.get("name", "there")
        stage = user_data.get("stage", "unknown")

        if follow_up_count == 0:
            context = "First follow-up after 2 hours. Be friendly and check if they have questions."
        elif follow_up_count == 1:
            context = "Second follow-up after 24 hours. Be understanding but remind them of the value."
        else:
            context = "Final automated follow-up. Be respectful and leave door open."

        prompt = f"""Generate a follow-up message for a customer.

Customer name: {name}
Stage: {stage}
Follow-up number: {follow_up_count + 1}
Context: {context}

The message should:
1. Be warm and non-pushy
2. Check in naturally
3. Offer help
4. Be brief (1-2 sentences)

Generate ONLY the message text."""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)
            logger.info(f"Follow-up message generated (count: {follow_up_count})")
            return response.content
        except Exception as e:
            logger.error(f"Follow-up message generation error: {e}")
            return f"Hi {name}! Just checking in to see if you had any questions. I'm here to help!"

    async def generate_conversation_notes(self, user_data: Dict[str, Any], conversation_history: List[BaseMessage]) -> str:
        """
        Generate intelligent conversation notes using GPT-4o-mini.

        Args:
            user_data: Collected user data (name, email, phone, needs, etc.)
            conversation_history: Full conversation history

        Returns:
            Concise summary of the conversation with key insights
        """
        llm = self.get_llm_for_task("analysis")

        # Build conversation text
        conversation_text = []
        for msg in conversation_history:
            if isinstance(msg, HumanMessage):
                conversation_text.append(f"Cliente: {msg.content}")
            elif isinstance(msg, (BaseMessage,)):
                from langchain_core.messages import AIMessage
                if isinstance(msg, AIMessage):
                    conversation_text.append(f"Bot: {msg.content}")

        full_conversation = "\n".join(conversation_text[-10:])  # Last 10 messages max

        # Extract user data
        name = user_data.get("name", "Sin nombre")
        email = user_data.get("email", "")
        phone = user_data.get("phone", "")
        needs = user_data.get("needs", "")
        intent = user_data.get("intent", "")
        sentiment = user_data.get("sentiment", "")
        stage = user_data.get("stage", "")
        requests_human = user_data.get("requests_human", False)

        prompt = f"""Genera un resumen conciso y profesional de esta conversación de ventas.

DATOS DEL CLIENTE:
- Nombre: {name}
- Email: {email if email else "No proporcionado"}
- Teléfono: {phone if phone else "No proporcionado"}
- Necesidades: {needs if needs else "No especificadas"}
- Intención: {intent}
- Sentimiento: {sentiment}
- Etapa: {stage}
- Solicita humano: {"Sí" if requests_human else "No"}

ÚLTIMOS MENSAJES:
{full_conversation}

Genera UN SOLO PÁRRAFO (máximo 3-4 oraciones) que resuma:
1. Quién es el cliente y qué busca
2. Nivel de interés/compromiso
3. Próximos pasos recomendados

Formato: Texto plano, sin bullets, sin emojis, estilo profesional."""

        try:
            messages = [HumanMessage(content=prompt)]
            response = await llm.ainvoke(messages)
            logger.info("Conversation notes generated with LLM")
            return response.content.strip()
        except Exception as e:
            logger.error(f"Notes generation error: {e}")
            # Fallback to basic format
            return f"Cliente: {name} | Email: {email} | Tel: {phone} | Interés: {needs} | Etapa: {stage} | Intención: {intent} | Sentimiento: {sentiment}"


# Global instance (will be initialized in app.py)
llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
