from sqlalchemy.orm import Session
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import desc
from sqlalchemy.future import select
from . import models, schemas
from pydantic import parse_obj_as
from typing import List
from loguru import logger


async def add_scraped_data(db: Session, scraped_urls: list) -> None:
    """
    Write or Update scraped data in RDB
    :param db: SQLAlchemy Session object
    :param scraped_urls: list: [schemas.ScrapedURLs, ...]
    :return: None
    """
    try:
        scraped_urls = parse_obj_as(List[schemas.ScrapedURLs], scraped_urls)
        db_items = [item.dict() for item in scraped_urls]

        insert_obj = insert(models.ScrapedURLs).values(db_items)
        insert_obj = insert_obj.on_conflict_do_update(
            constraint="scraped_urls_pkey",
            set_={
                "scrap_datetime": insert_obj.excluded.scrap_datetime,
                "redirect_to": insert_obj.excluded.redirect_to,
                "status_code": insert_obj.excluded.status_code,
                "title": insert_obj.excluded.title,
                "error": insert_obj.excluded.error,
            }
        )
        await db.execute(insert_obj)
        await db.commit()

        logger.success(f"{len(db_items)} rows written/updated successfully")
    except Exception:
        logger.exception("Cant save scraped data to db")
    finally:
        await db.close()


async def get_by_domain(engine: create_async_engine, domain: str) -> List[Row]:
    """
    Async Select Query to RDB for getting data by domain column
    :param engine: sqlalchemy.ext.asyncio.create_async_engine
    :param domain: str: filter column value
    :return: list: [sqlalchemy.engine.row.Row, ...]
    """
    async with engine.connect() as conn:
        result = await conn.execute(select(
                                           models.ScrapedURLs.url,
                                           models.ScrapedURLs.visit_datetime,
                                           models.ScrapedURLs.status_code,
                                          )
                                    .where(models.ScrapedURLs.domain == domain))
        return result.fetchall()


async def get_last_visit(engine: create_async_engine, by_url: str = None, by_domain: str = None) -> Row:
    """
    Async Select Query to RDB for getting data with older visiting date by domain or url column
    :param engine: sqlalchemy.ext.asyncio.create_async_engine
    :param by_url: str: optional
    :param by_domain: strL optional
    :return: sqlalchemy.engine.row.Row
    """
    search_by_column = models.ScrapedURLs.url if by_url else models.ScrapedURLs.domain
    equal_to = by_url if by_url else by_domain

    async with engine.connect() as conn:
        result = await conn.execute(select(
                                            models.ScrapedURLs.url,
                                            models.ScrapedURLs.domain,
                                            models.ScrapedURLs.visit_datetime,
                                            models.ScrapedURLs.status_code,
                                            models.ScrapedURLs.redirect_to,
                                            models.ScrapedURLs.title,
                                            models.ScrapedURLs.scrap_datetime,
                                          )
                                    .where(search_by_column == equal_to)
                                    .order_by(desc(models.ScrapedURLs.visit_datetime))
                                    )
        return result.first()
