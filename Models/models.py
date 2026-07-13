from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Databases.UserDB.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    img_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    password_hashed: Mapped[str | None] = mapped_column(String(200), nullable=False)

    @property
    def img_path(self) -> str:
        return f"/uploads/{self.img_file}" if self.img_file else ""
        
    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(back_populates="user", cascade="all, delete-orphan")



class PasswordResetToken(Base):
    __tablename__ = 'password_reset_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    user: Mapped[User] = relationship(back_populates='reset_tokens')

