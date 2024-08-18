import asyncio
import datetime

from app.database import get_engine, make_session_class
from app.repositories import cve as cve_repo
from app.models import Cve


async def main():
    engine = get_engine()
    _Session = make_session_class(engine)

    async with _Session() as session:
        print("Fetching cve")

        cve = await cve_repo.get_by_cve_id(session, "CVE-2024-7853")
        print(cve, "by cve_id: CVE-2024-7853")

        cve = await cve_repo.get_by_id(session, cve.id)
        print(cve, f"by id: {cve.id}")

        # please change filters to work with results
        print("First page:")
        async for cve in cve_repo.filter_(
            session, [Cve.published_date >= datetime.datetime(2024, 1, 1)], limit=25, offset=0
        ):
            print(cve.published_date)

        print("Second page:")
        async for cve in cve_repo.filter_(
            session, [Cve.published_date >= datetime.datetime(2024, 1, 1)], limit=25, offset=25
        ):
            print(cve.published_date)


if __name__ == "__main__":
    asyncio.run(main())
