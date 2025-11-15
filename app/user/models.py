from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database import Base
from sqlalchemy import String, text
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models import Blog

class User(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)
    is_user: Mapped[bool] = mapped_column(default=True, server_default=text('true'), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)
    is_super_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    role: Mapped["Role"] = relationship(back_populates='users')
    blogs: Mapped[List["Blog"]] = relationship(back_populates='user', uselist=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Role(Base):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates='role')

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
