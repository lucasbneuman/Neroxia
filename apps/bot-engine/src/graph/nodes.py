"""LangGraph nodes for sales conversation workflow."""

from datetime import datetime, timedelta
from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage

from .state import ConversationState
from services.llm_service import get_llm_service
from services.rag_service import get_rag_service
from services.hubspot_sync import get_hubspot_service
from whatsapp_bot_shared import get_logger

logger = get_logger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def build_enhanced_system_prompt(config: Dict[str, Any]) -> str:
    """
    Build an enhanced system prompt that includes product/service information.

    Args:
        config: Configuration dictionary with system_prompt and product info

    Returns:
        Enhanced system prompt string or None if not configured
    """
    base_prompt = config.get("system_prompt", "").strip()

    # If no base prompt, return None to signal configuration error
    if not base_prompt:
        return None

    # Get product information
    product_name = config.get("product_name", "").strip()
    product_description = config.get("product_description", "").strip()
    product_features = config.get("product_features", "").strip()
    product_benefits = config.get("product_benefits", "").strip()
    product_price = config.get("product_price", "").strip()
    product_target = config.get("product_target_audience", "").strip()

    # If no product info is available, return base prompt
    if not product_name and not product_description:
        return base_prompt

    # Build enhanced prompt with product context
    enhanced_prompt = f"{base_prompt}\n\n"
    enhanced_prompt += "=== INFORMACIÓN DEL PRODUCTO/SERVICIO ===\n"

    if product_name:
        enhanced_prompt += f"Producto/Servicio: {product_name}\n"

    if product_description:
        enhanced_prompt += f"\nDescripción:\n{product_description}\n"

    if product_features:
        enhanced_prompt += f"\nCaracterísticas principales:\n{product_features}\n"

    if product_benefits:
        enhanced_prompt += f"\nBeneficios para el cliente:\n{product_benefits}\n"

    if product_price:
        enhanced_prompt += f"\nPrecio: {product_price}\n"

    if product_target:
        enhanced_prompt += f"\nPúblico objetivo: {product_target}\n"

    enhanced_prompt += "\n=== INSTRUCCIONES ===\n"
    enhanced_prompt += "Usa esta información para responder preguntas sobre el producto/servicio de manera natural y conversacional. "
    enhanced_prompt += "NO menciones que tienes esta información directamente, simplemente úsala para dar respuestas precisas y útiles."

    return enhanced_prompt


# ============================================================================
# NODE 1: WELCOME
# ============================================================================


async def welcome_node(state: ConversationState) -> Dict[str, Any]:
    """
    Send welcome message and ask initial qualifying questions.

    Uses the welcome_message from configuration and adds questions
    to start collecting user information (name, needs, expectations).
    """
    logger.info("Executing welcome_node")

    # Check if this is first message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if len(user_messages) <= 1:
        # Validate configuration is set
        welcome_message = state["config"].get("welcome_message", "").strip()
        system_prompt = state["config"].get("system_prompt", "").strip()

        # If no configuration is set, return error message
        if not welcome_message and not system_prompt:
            error_msg = "⚠️ ERROR: El bot no está configurado. Por favor, ve a la pestaña '⚙️ Configuración' y completa al menos el 'System Prompt' y el 'Mensaje de Bienvenida' antes de iniciar conversaciones."
            logger.warning("Bot not configured - welcome_message and system_prompt are empty")
            return {
                "current_response": error_msg,
                "stage": "error",
            }

        # If only welcome_message is missing, use a default one
        if not welcome_message:
            welcome_message = "¡Hola! 👋 Soy tu asistente virtual."
            logger.warning("No welcome_message configured, using fallback")

        # Add initial questions to start conversation
        product_name = state["config"].get("product_name", "nuestros servicios")
        use_emojis = state["config"].get("use_emojis", True)

        # Build complete welcome with questions
        if use_emojis:
            full_welcome = f"{welcome_message}\n\nPara poder ayudarte mejor, me gustaría conocerte un poco. 😊 ¿Podrías decirme tu nombre?"
        else:
            full_welcome = f"{welcome_message}\n\nPara poder ayudarte mejor, me gustaría conocerte un poco. ¿Podrías decirme tu nombre?"

        logger.info(f"Sending welcome message with initial questions")

        return {
            "current_response": full_welcome,
            "stage": "welcome",
        }

    # Not first message, skip welcome
    return {}


# ============================================================================
# NODE 2: INTENT CLASSIFIER
# ============================================================================


async def intent_classifier_node(state: ConversationState) -> Dict[str, Any]:
    """
    Classify user intent and update intent score.

    Runs on EVERY turn. Uses GPT-4o-mini for efficiency.
    Supports custom intent_prompt from configuration.
    """
    logger.info("Executing intent_classifier_node")

    llm_service = get_llm_service()

    # Get last user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not user_messages:
        return {}

    last_message = user_messages[-1].content

    # Classify intent with config support
    intent_data = await llm_service.classify_intent(
        last_message,
        state["messages"],
        config=state.get("config")  # Pass config for custom prompts
    )

    logger.info(f"Intent: {intent_data['category']}, Score: {intent_data['score']}")

    return {
        "intent_score": intent_data["score"],
    }


# ============================================================================
# NODE 3: SENTIMENT ANALYZER
# ============================================================================


async def sentiment_analyzer_node(state: ConversationState) -> Dict[str, Any]:
    """
    Analyze sentiment of user's message.

    Runs on EVERY turn. Uses GPT-4o-mini for efficiency.
    Triggers handoff if negative sentiment persists.
    """
    logger.info("Executing sentiment_analyzer_node")

    llm_service = get_llm_service()

    # Get last user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not user_messages:
        return {}

    last_message = user_messages[-1].content

    # Analyze sentiment
    sentiment = await llm_service.analyze_sentiment(last_message)

    logger.info(f"Sentiment: {sentiment}")

    # Check for consecutive negative sentiments
    updates = {"sentiment": sentiment}

    # If negative and previous was also negative, trigger handoff
    if sentiment == "negative":
        # Count recent negative sentiments
        recent_messages = state["messages"][-4:]  # Last 4 messages
        negative_count = sum(
            1
            for m in recent_messages
            if isinstance(m, HumanMessage) and getattr(m, "metadata", {}).get("sentiment") == "negative"
        )

        if negative_count >= 2:
            logger.warning("Multiple negative sentiments detected, will trigger handoff")
            updates["conversation_mode"] = "NEEDS_ATTENTION"

    return updates


# ============================================================================
# NODE 4: DATA COLLECTOR
# ============================================================================


async def data_collector_node(state: ConversationState) -> Dict[str, Any]:
    """
    Extract structured data from user messages.

    Priority order for data collection:
    1. Twilio data (whatsapp_profile_name, phone) - highest priority
    2. LLM extraction (email, needs, budget, pain_points) - fallback
    
    Does NOT block the sale waiting for complete data.
    """
    logger.info("Executing data_collector_node")

    llm_service = get_llm_service()

    # Get last user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not user_messages:
        return {}

    last_message = user_messages[-1].content
    
    # Initialize updates dict
    updates = {}
    collected_data = state.get("collected_data", {})
    
    # PRIORITY 1: Check if we have Twilio data from db_user
    db_user = state.get("db_user")
    if db_user:
        # Use WhatsApp profile name from Twilio if available and name not already set
        if db_user.whatsapp_profile_name and not state.get("user_name"):
            logger.info(f"✅ Using WhatsApp profile name from Twilio: {db_user.whatsapp_profile_name}")
            updates["user_name"] = db_user.whatsapp_profile_name
            collected_data["name"] = db_user.whatsapp_profile_name
            collected_data["source_name"] = "twilio"  # Mark source
        
        # Use phone from Twilio if available
        if db_user.phone and "phone" not in collected_data:
            collected_data["phone"] = db_user.phone
            collected_data["source_phone"] = "twilio"
        
        # Use country code if available
        if db_user.country_code and "country_code" not in collected_data:
            collected_data["country_code"] = db_user.country_code

    # PRIORITY 2: Extract data with LLM (for email, needs, budget, etc.)
    # Only extract name if we don't have it from Twilio
    extracted_data = await llm_service.extract_data(
        last_message,
        state["messages"],
        config=state.get("config")  # Pass config for custom prompts
    )

    if extracted_data:
        logger.info(f"Extracted data from LLM: {extracted_data}")

        # Merge with existing collected data
        # But DON'T overwrite Twilio data with LLM data
        for key, value in extracted_data.items():
            if key == "name":
                # Only use LLM-extracted name if we don't have Twilio name
                if not db_user or not db_user.whatsapp_profile_name:
                    collected_data[key] = value
                    collected_data["source_name"] = "llm"
                    updates["user_name"] = value
                    logger.info(f"Using LLM-extracted name (no Twilio data): {value}")
                else:
                    logger.info(f"Skipping LLM-extracted name, using Twilio data instead")
            else:
                # For other fields (email, needs, budget, etc.), use LLM data
                collected_data[key] = value
                if key == "email":
                    updates["user_email"] = value

        updates["collected_data"] = collected_data

        # Async sync to HubSpot (non-blocking)
        hubspot_service = get_hubspot_service()
        if hubspot_service.enabled:
            # Generate incremental notes from collected data
            notes_parts = []

            # Add collected data to notes
            if collected_data.get("needs"):
                notes_parts.append(f"Necesidades: {collected_data['needs']}")
            if collected_data.get("pain_points"):
                notes_parts.append(f"Pain Points: {collected_data['pain_points']}")
            if collected_data.get("budget"):
                notes_parts.append(f"Presupuesto: {collected_data['budget']}")

            # Add current stage and sentiment
            current_stage = state.get("stage", "unknown")
            current_sentiment = state.get("sentiment", "neutral")
            notes_parts.append(f"Etapa: {current_stage} | Sentimiento: {current_sentiment}")
            
            # Add data source info
            if collected_data.get("source_name") == "twilio":
                notes_parts.append("Nombre verificado desde WhatsApp")

            # Use existing summary if available, otherwise use generated notes
            conversation_notes = state.get("conversation_summary") or " | ".join(notes_parts)

            user_data = {
                "phone": state["user_phone"],
                "name": state.get("user_name"),
                "email": state.get("user_email"),
                "needs": collected_data.get("needs"),
                "pain_points": collected_data.get("pain_points"),
                "budget": collected_data.get("budget"),
                "intent_score": state.get("intent_score"),
                "sentiment": state.get("sentiment"),
                "stage": state.get("stage"),
                "conversation_summary": conversation_notes,
                "whatsapp_profile_name": db_user.whatsapp_profile_name if db_user else None,
                "country_code": db_user.country_code if db_user else None,
            }
            try:
                # Get db_user from state if available
                result = await hubspot_service.sync_contact(user_data, db_user=db_user)

                # Update our DB with HubSpot contact_id and lifecyclestage
                if result and db_user:
                    db_user.hubspot_contact_id = result["contact_id"]
                    db_user.hubspot_lifecyclestage = result["lifecyclestage"]
                    db_user.hubspot_synced_at = result["synced_at"]
                    logger.info(f"✅ Updated DB with HubSpot data: {result['action']} contact {result['contact_id']}")

            except Exception as e:
                logger.error(f"HubSpot sync failed (non-blocking): {e}")
                import traceback
                traceback.print_exc()

        return updates

    return {}


# ============================================================================
# NODE 5: ROUTER
# ============================================================================


def calculate_routing_scores(state: ConversationState) -> Dict[str, float]:
    """
    Calculate probabilistic routing scores for each possible route.

    Multi-factor analysis considers:
    - Intent score (40% weight)
    - Sentiment (20% weight)
    - Data completeness (15% weight)
    - Conversation momentum (25% weight)

    Args:
        state: Current conversation state

    Returns:
        Dict with scores for each route
    """
    scores = {
        "conversation": 0.3,  # Base score for continuing conversation
        "closing": 0.0,
        "payment": 0.0,
        "follow_up": 0.0,
        "handoff": 0.0,
    }

    # Factor 1: Intent Score (40% weight)
    intent_score = state.get("intent_score", 0.5)
    scores["closing"] += intent_score * 0.4
    scores["follow_up"] += (1 - intent_score) * 0.2
    scores["conversation"] += (1 - abs(intent_score - 0.5)) * 0.2  # Moderate intent stays in conversation

    # Factor 2: Sentiment (20% weight)
    sentiment = state.get("sentiment", "neutral")
    if sentiment == "negative":
        scores["handoff"] += 0.5
        scores["conversation"] -= 0.1
    elif sentiment == "positive":
        scores["closing"] += 0.2
        scores["conversation"] += 0.1

    # Factor 3: Data Completeness (15% weight)
    collected_data = state.get("collected_data", {})
    data_fields = ["name", "email", "phone", "needs"]
    completeness = sum(1 for field in data_fields if collected_data.get(field)) / len(data_fields)

    if completeness > 0.75:
        scores["closing"] += 0.3
    elif completeness < 0.25:
        scores["conversation"] += 0.2  # Need more info

    # Factor 4: Conversation Momentum (25% weight)
    messages = state.get("messages", [])
    user_messages = [m for m in messages if isinstance(m, HumanMessage)]
    message_count = len(user_messages)

    # Calculate momentum based on message count and intent progression
    if message_count > 10:
        momentum = 0.8  # High momentum
    elif message_count > 5:
        momentum = 0.6  # Medium momentum
    else:
        momentum = 0.3  # Low momentum

    scores["closing"] += momentum * 0.25
    scores["conversation"] += (1 - momentum) * 0.15

    # Normalize scores to ensure they're valid probabilities
    total = sum(scores.values())
    if total > 0:
        scores = {k: v / total for k, v in scores.items()}

    logger.info(f"Routing scores calculated: {scores}")
    return scores


def router_node(state: ConversationState) -> str:
    """
    Probabilistic router with multi-factor analysis.

    This is a CONDITIONAL EDGE function, not a regular node.
    Returns the name of the next node to execute.

    Strategy:
    1. Check deterministic cases first (NEEDS_ATTENTION, payment flow)
    2. Use probabilistic scoring for ambiguous cases
    3. Log decision reasoning for debugging

    Routing logic:
    - DETERMINISTIC: conversation_mode == NEEDS_ATTENTION → handoff
    - DETERMINISTIC: stage == closing + no payment link → payment
    - PROBABILISTIC: Multi-factor scoring for conversation/closing/follow_up
    """
    logger.info("Executing router_node (probabilistic)")

    # DETERMINISTIC CASE 1: Explicit handoff request
    if state.get("conversation_mode") == "NEEDS_ATTENTION":
        logger.info("Routing to handoff_node (NEEDS_ATTENTION)")
        return "handoff"

    # DETERMINISTIC CASE 2: Payment flow
    if state.get("stage") == "closing" and not state.get("payment_link_sent"):
        logger.info("Routing to payment_node (closing stage)")
        return "payment"

    # DETERMINISTIC CASE 3: Persistent negative sentiment (handoff)
    sentiment = state.get("sentiment", "neutral")
    user_messages = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]

    if sentiment == "negative" and len(user_messages) >= 3:
        # Strong negative signal → handoff
        logger.info("Routing to handoff_node (persistent negative sentiment)")
        return "handoff"

    # PROBABILISTIC ROUTING: Use multi-factor scoring
    scores = calculate_routing_scores(state)

    # Select route with highest score
    best_route = max(scores, key=scores.get)
    best_score = scores[best_route]

    # Add threshold for closing (require high confidence)
    if best_route == "closing" and best_score < 0.4:
        logger.info(f"Closing score too low ({best_score:.2f}), routing to conversation instead")
        best_route = "conversation"

    # Add threshold for handoff (require high confidence)
    if best_route == "handoff" and best_score < 0.5:
        logger.info(f"Handoff score too low ({best_score:.2f}), routing to conversation instead")
        best_route = "conversation"

    logger.info(f"Probabilistic routing: {best_route} (score: {best_score:.2f})")
    logger.info(f"All scores: {scores}")

    return best_route


# ============================================================================
# NODE 6: CONVERSATION
# ============================================================================


async def conversation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Generate main conversational response.

    Uses GPT-4o + RAG if enabled.
    Applies all configurations (emojis, tone, system prompt).
    Includes product/service context automatically.
    """
    logger.info("Executing conversation_node")

    llm_service = get_llm_service()
    rag_service = get_rag_service()

    # Get configuration with enhanced product context
    enhanced_prompt = build_enhanced_system_prompt(state["config"])

    # Check if configuration is missing
    if enhanced_prompt is None:
        error_msg = "⚠️ ERROR: El bot no está configurado. Por favor, ve a la pestaña '⚙️ Configuración' y completa el 'System Prompt' antes de continuar."
        logger.warning("Bot not configured - system_prompt is empty")
        return {
            "current_response": error_msg,
            "stage": "error",
        }

    # Apply adaptive personalization based on conversation trends
    current_sentiment = state.get("sentiment", "neutral")
    current_intent = state.get("intent_score", 0.5)

    # Analyze conversation trends
    trends = llm_service.analyze_conversation_trends(
        state["messages"],
        current_sentiment=current_sentiment,
        current_intent=current_intent
    )

    # Build adaptive system prompt
    enhanced_prompt = llm_service.build_adaptive_system_prompt(
        enhanced_prompt,
        trends=trends,
        current_sentiment=current_sentiment,
        current_intent=current_intent
    )

    logger.info(f"Adaptive personalization applied: {trends['recommendation']}")

    use_emojis = state["config"].get("use_emojis", True)

    # Auto-enable RAG if there are documents in the collection
    rag_stats = rag_service.get_collection_stats()
    rag_enabled = rag_stats['total_chunks'] > 0

    # Get last user message for RAG
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    last_message = user_messages[-1].content if user_messages else ""

    # Check if user is requesting to speak with a human
    human_request_keywords = ["humano", "persona", "supervisor", "agente", "operador", "hablar con alguien", "hablar con un", "hablar con una", "asistente real", "persona real"]
    last_message_lower = last_message.lower()
    if any(keyword in last_message_lower for keyword in human_request_keywords):
        logger.info("Human request detected - triggering handoff")
        # Get product name for personalized response
        product_name = state["config"].get("product_name", "nuestros servicios")
        handoff_response = f"¡Claro que sí! 😊 Dame unos minutos para avisar a mi supervisor. Mientras tanto, ¿te gustaría saber más sobre {product_name}?"

        return {
            "current_response": handoff_response,
            "conversation_mode": "NEEDS_ATTENTION",
            "stage": "handoff",
        }

    # Retrieve RAG context if enabled
    rag_context = None
    if rag_enabled and last_message:
        try:
            rag_context = await rag_service.retrieve_context(last_message, k=3)
            if rag_context:
                logger.info(f"Retrieved RAG context ({rag_stats['total_chunks']} chunks available)")
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")

    # Generate response with product-aware prompt
    response = await llm_service.generate_response(
        messages=state["messages"],
        system_prompt=enhanced_prompt,
        use_emojis=use_emojis,
        rag_context=rag_context,
        config=state["config"],
    )

    # Update stage based on conversation
    current_stage = state.get("stage", "welcome")
    if current_stage == "welcome":
        new_stage = "qualifying"
    else:
        new_stage = current_stage

    return {
        "current_response": response,
        "stage": new_stage,
    }


# ============================================================================
# NODE 7: CLOSING
# ============================================================================


async def closing_node(state: ConversationState) -> Dict[str, Any]:
    """
    Handle closing/purchase intent.

    Validates minimum data and routes to payment if ready.
    """
    logger.info("Executing closing_node")

    # Check if we have at least name
    if not state.get("user_name"):
        logger.info("Missing user name, requesting it")
        return {
            "current_response": "¡Perfecto! Me encantaría ayudarte a completar tu compra. ¿Podrías decirme tu nombre primero?",
            "stage": "closing",
        }

    # Ready to send payment
    logger.info("User ready for payment, routing to payment_node")
    return {
        "stage": "closing",
    }


# ============================================================================
# NODE 8: PAYMENT
# ============================================================================


async def payment_node(state: ConversationState) -> Dict[str, Any]:
    """
    Send payment link to customer.

    Marks payment_link_sent and schedules follow-up.
    Uses product context for personalized closing message.
    """
    logger.info("Executing payment_node")

    llm_service = get_llm_service()
    payment_link = state["config"].get("payment_link", "https://example.com/pay")

    # Build product context for closing message
    product_name = state["config"].get("product_name", "nuestro producto")

    # Generate closing message with payment link
    user_data = {
        "name": state.get("user_name", "there"),
        "product_name": product_name,
    }

    response = await llm_service.generate_closing_message(user_data, payment_link)

    return {
        "current_response": response,
        "payment_link_sent": True,
        "stage": "closing",
    }


# ============================================================================
# NODE 9: FOLLOW-UP
# ============================================================================


async def follow_up_node(state: ConversationState) -> Dict[str, Any]:
    """
    Handle follow-up scheduling.

    Strategy:
    - count = 0: Schedule in 2 hours
    - count = 1: Schedule in 24 hours
    - count >= 2: Change to NEEDS_ATTENTION, no automatic follow-up
    """
    logger.info("Executing follow_up_node")

    follow_up_count = state.get("follow_up_count", 0)

    if follow_up_count >= 2:
        logger.info("Max follow-ups reached, escalating to NEEDS_ATTENTION")
        return {
            "current_response": "¡Entendido! No dudes en contactarme cuando estés listo. ¡Estoy aquí para ayudarte!",
            "conversation_mode": "NEEDS_ATTENTION",
            "stage": "follow_up",
        }

    # Schedule follow-up
    if follow_up_count == 0:
        delay_hours = 2
        response = "¡No hay problema! Te contactaré en un par de horas. ¡Tómate tu tiempo!"
    else:  # count == 1
        delay_hours = 24
        response = "¡Por supuesto! Te contactaré mañana. ¡Que tengas un excelente día!"

    scheduled_time = datetime.utcnow() + timedelta(hours=delay_hours)

    logger.info(f"Scheduled follow-up #{follow_up_count + 1} for {scheduled_time}")

    return {
        "current_response": response,
        "follow_up_scheduled": scheduled_time,
        "follow_up_count": follow_up_count + 1,
        "stage": "follow_up",
    }


# ============================================================================
# NODE 10: HANDOFF
# ============================================================================


async def handoff_node(state: ConversationState) -> Dict[str, Any]:
    """
    Hand off conversation to human agent.

    Changes mode to NEEDS_ATTENTION and pauses bot.
    Responds with a friendly message letting user know a human will assist.
    """
    logger.info("Executing handoff_node - User requested human assistance")

    # Get product name for personalized response
    product_name = state["config"].get("product_name", "nuestros servicios")

    response = f"¡Claro que sí! 😊 Dame unos minutos para avisar a mi supervisor. Mientras tanto, ¿te gustaría saber más sobre {product_name}?"

    return {
        "current_response": response,
        "conversation_mode": "NEEDS_ATTENTION",
        "stage": "handoff",
    }


# ============================================================================
# NODE 11: CONVERSATION SUMMARY
# ============================================================================


async def summary_node(state: ConversationState) -> Dict[str, Any]:
    """
    Generate conversation summary when user leaves or reaches milestone.

    Creates summary and syncs to HubSpot.
    """
    logger.info("Executing summary_node")

    llm_service = get_llm_service()
    hubspot_service = get_hubspot_service()

    # Build conversation text
    conversation_text = []
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            conversation_text.append(f"Cliente: {msg.content}")
        elif isinstance(msg, AIMessage):
            conversation_text.append(f"Bot: {msg.content}")

    full_conversation = "\n".join(conversation_text)

    # Generate summary
    summary_prompt = f"""Genera un resumen conciso de esta conversación de ventas.

Conversación:
{full_conversation}

El resumen debe incluir:
1. Tema principal de la conversación
2. Necesidades o intereses del cliente
3. Productos o servicios discutidos
4. Objeciones o preocupaciones mencionadas
5. Próximos pasos o estado actual

Genera SOLO el resumen en formato de párrafo conciso (máximo 150 palabras)."""

    try:
        summary = await llm_service.generate_response(
            messages=[HumanMessage(content=summary_prompt)],
            system_prompt="Eres un asistente que genera resúmenes concisos de conversaciones de ventas.",
            use_emojis=False,
        )

        logger.info(f"Summary generated: {summary[:100]}...")

        # Sync to HubSpot if available
        user_phone = state.get("user_phone", "")
        user_data = {
            "name": state.get("user_name", ""),
            "email": state.get("user_email", ""),
            "phone": user_phone,
            "conversation_summary": summary,
            "intent_score": state.get("intent_score", 0.0),
            "sentiment": state.get("sentiment", "neutral"),
            "stage": state.get("stage", "unknown"),
        }

        try:
            await hubspot_service.sync_contact(user_data)
            logger.info(f"Summary synced to HubSpot for {user_phone}")
        except Exception as e:
            logger.warning(f"Failed to sync to HubSpot: {e}")

        return {
            "conversation_summary": summary,
            "stage": "completed",
        }

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {
            "conversation_summary": "Error al generar resumen",
        }
