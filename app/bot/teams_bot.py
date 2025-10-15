from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, ActivityTypes
from sqlalchemy.orm import Session
from app.entities.services.conversations_service import ConversationsService
from app.monitoring.logging import get_logger

logger = get_logger(__name__)


class TeamsBot(ActivityHandler):
    """Simple bot to handle 1:1 chat messages from Teams."""

    def __init__(self, db: Session):
        self.db = db
        self.conversations_service = ConversationsService(db)

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming message activities from Teams.
        Extracts user info and message, sends to conversation service.
        """
        try:
            # Get user email from Teams activity
            user_email = turn_context.activity.from_property.aad_object_id or turn_context.activity.from_property.id
            message_text = turn_context.activity.text

            # Ignore system/debug messages from Bot Framework Emulator
            if message_text and message_text.startswith("/INSPECT"):
                logger.info(f"Ignoring system message: {message_text}")
                return

            logger.info(f"Received message from Teams user: {user_email}, message: {message_text}")

            # Use existing conversation service to generate response
            response = await self.conversations_service.answer(message_text, user_email)

            # Send response back to Teams
            await turn_context.send_activity(response)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await turn_context.send_activity("Sorry, I encountered an error processing your message.")
