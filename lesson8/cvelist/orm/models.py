from datetime import datetime

from sqlalchemy import String, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class Cve(Base):
    __tablename__ = "cve"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(400))
    problem_types: Mapped[str] = mapped_column(String(400))
    published_date: Mapped[datetime] = mapped_column(DateTime)
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deleted_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    @staticmethod
    async def generate_id(session: AsyncSession, year: int) -> str:
        prefix = "CVE"
        stmt = (
            select(Cve)
            .where(Cve.id.like(f"CVE_{year}_%"))
            .order_by(Cve.id.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        latest_cve = result.scalar_one_or_none()

        if latest_cve:
            latest_id_num = int(latest_cve.id.split("_")[2])
            new_id_num = latest_id_num + 1
        else:
            new_id_num = 1

        return f"{prefix}_{year}_{new_id_num:04d}"

    def __repr__(self):
        return f"<Cve(id={self.id}, title={self.title})"
