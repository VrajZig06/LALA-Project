from pydantic import BaseModel

class NotificationBlock(BaseModel):
    title: str
    body: str
    token: str