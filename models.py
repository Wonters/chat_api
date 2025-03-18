from sqlmodel import Field, Relationship, delete, BaseModel
from typing import List


class Account(BaseModel):
    __tablename__ = "account"
    name: str = "Account name"
    sended_messages: List["Message"] | None = Relationship(back_populate="sender")
    received_messages: List["Message"] | None = Relationship(back_populate="receiver")


class Message(BaseModel):
    __tablename__ = "message"
    account_id: int | None = Field(default=None, foreign_key="account.id")
    sender = Relationship(
        back_populates="sended_messages"
    )
    receiver = Relationship(back_populates="received_messages")
