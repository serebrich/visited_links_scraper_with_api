import asyncio
try:
    from sql_app import crud, models
    from sql_app.database import SessionLocal, engine
    from scrapers.scraper import Scraper
except ImportError:
    import sys
    sys.path.append('../')
    from sql_app import crud, models
    from sql_app.database import SessionLocal, engine
    from scrapers.scraper import Scraper

from loguru import logger

scrap = Scraper()


async def create_tables() -> None:
    """
    Create all tables in RDB
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    logger.success("All tables created successfully")


async def main() -> None:
    """
    Main function, which create tables in RDB, scrap links
    and save scraped info in RDB
    """
    await create_tables()
    results = scrap.run()
    await crud.add_scraped_data(SessionLocal(), results)

if __name__ == '__main__':
    asyncio.run(main())
