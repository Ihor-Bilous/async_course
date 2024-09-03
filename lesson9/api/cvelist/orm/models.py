from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class Cve(Base):
    __tablename__ = "cve"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    problem_types: Mapped[str] = mapped_column(String)
    published_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reserved_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Cve(id={self.id}, title={self.title})"
