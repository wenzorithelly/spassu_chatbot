from fastapi import APIRouter, Request, Response, Depends
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from sqlalchemy.orm import Session
from app.core.config import settings
from app.clients.db.postgres_client import get_db
from app.bot.teams_bot import TeamsBot
from app.monitoring.logging import get_logger

logger = get_logger(__name__)

bot_router = APIRouter()

# Configure Bot Framework Adapter
# For local testing with Bot Framework Emulator, leave app_id and app_password empty
adapter_settings = BotFrameworkAdapterSettings(
    app_id=settings.MICROSOFT_APP_ID,
    app_password=settings.MICROSOFT_APP_PASSWORD
)
adapter = BotFrameworkAdapter(adapter_settings)


async def on_error(context, error):
    """Error handler for the bot adapter."""
    logger.error(f"Bot error: {error}")
    await context.send_activity("Sorry, something went wrong.")


adapter.on_turn_error = on_error


@bot_router.post("/messages")
async def messages(request: Request, db: Session = Depends(get_db)):
    """
    Main endpoint for Bot Framework to send activities.
    This is the webhook that Teams will call.
    """
    # Get the request body
    body = await request.json()

    # Create activity from request
    activity = Activity().deserialize(body)

    # Get authorization header
    auth_header = request.headers.get("Authorization", "")

    # Create bot instance
    bot = TeamsBot(db)

    # Process the activity
    async def call_bot(turn_context):
        await bot.on_turn(turn_context)

    await adapter.process_activity(activity, auth_header, call_bot)

    return Response(status_code=200)
