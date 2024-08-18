import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class Cve(Base):
    __tablename__ = "cve"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    cve_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    reserved_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    published_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    description: Mapped[str] = mapped_column(String)
    problem_types: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"<Cve(cve_id={self.cve_id})"
