import logging
from fastapi import APIRouter, Header, Request, status, HTTPException, BackgroundTasks
from app.models.github import PullRequestEvent
from app.core.config import get_settings
from app.core.security import verify
from app.services.processor import process_pull_request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook", tags=["webhook"], status_code=status.HTTP_200_OK)
async def webhook(request: Request, x_github_event: str = Header(default=""), x_hub_signature_256: str | None = Header(default=None), background_tasks: BackgroundTasks = BackgroundTasks()):
    settings = get_settings()
    raw_body = await request.body()

    if not verify(raw_body, settings.github_webhook_secret, x_hub_signature_256):
        logger.debug("Not valid request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request not valid",
        )

    if x_github_event == "ping":
        logger.info("Ping recieved")
        return {"msg": "pong!"}

    if x_github_event != "pull_request":
        logger.debug("Event '%s' ignored", x_github_event)
        return {"msg": f"ignored: '{x_github_event}'"}

    payload = await request.json()
    event = PullRequestEvent.model_validate(payload)

    if not event.is_actionable:
        logger.debug("Event '%s' not actionable", x_github_event)
        return {"msg": f"ignored: '{x_github_event}'"}

    logger.info("Pull request #%s of %s recieved (action: %s)",
                event.number, event.repository.full_name, event.action
    )
    background_tasks.add_task(process_pull_request, event)

    return {"msg": "Pull request recieved", "pr": event.number}