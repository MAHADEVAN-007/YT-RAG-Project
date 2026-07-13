from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Textfrom
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Databases.UserDB import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    img_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    password_hashed: Mapped[str | None] = mapped_column(String(200), nullable=False)
    
    @property
    def img_path(self) -> str:
        if self.img_file:
            return f""



