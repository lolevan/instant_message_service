from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Message, User
from app.database import SessionLocal
from datetime import datetime
from app.tasks import celery_app
from typing import List
from sqlalchemy.future import select

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")
        # Обрабатывать сохранение сообщений и уведомлять получателя


@router.post("/send-message")
async def send_message(sender_id: int, recipient_id: int, content: str, db: AsyncSession = Depends(SessionLocal)):
    sender = await db.get(User, sender_id)
    recipient = await db.get(User, recipient_id)
    if not sender or not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content, timestamp=datetime.utcnow())
    db.add(message)
    await db.commit()
    celery_app.send_task("tasks.notify_user", args=[recipient.telegram_id, content])
    return {"msg": "Message sent"}


@router.get("/message-history/{user_id}/{recipient_id}", response_model=List[Message])
async def get_message_history(user_id: int, recipient_id: int, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(
        select(Message).where(
            ((Message.sender_id == user_id) & (Message.recipient_id == recipient_id)) |
            ((Message.sender_id == recipient_id) & (Message.recipient_id == user_id))
        ).order_by(Message.timestamp.asc())
    )
    messages = result.scalars().all()
    return messages
