from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    email_address: Mapped[str] = mapped_column(String(50), unique=True)
    fullname: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.username!r}, fullname={self.fullname!r})'
