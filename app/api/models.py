from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Text, UniqueConstraint
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.user.models import User

class Blog(Base):
    __tablename__ = "blogs"
    title: Mapped[str] = mapped_column(String, unique=True)
    author: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    short_description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(default="published", server_default='published')

    user: Mapped["User"] = relationship(back_populates="blogs")
    tags: Mapped[List["Tag"]] = relationship(back_populates='blogs', uselist=True, secondary='blogs_tags')


class Tag(Base):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String(50), unique=True)

    blogs: Mapped[List["Blog"]] = relationship(back_populates='tags', uselist=True, secondary='blogs_tags')

class BlogTag(Base):
    __tablename__ = "blogs_tags"
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # Уникальное ограничение для предотвращения дублирования
    __table_args__ = (
        UniqueConstraint('blog_id', 'tag_id', name='uq_blog_tag'),
    )

