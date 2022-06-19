from sqlalchemy import Boolean, Column, BIGINT, String, SmallInteger, DateTime

from .database import Base


class ScrapedURLs(Base):
    __tablename__ = "scraped_urls"

    url = Column(String, primary_key=True)
    visit_datetime = Column(DateTime, index=True, primary_key=True)
    domain = Column(String, index=True)
    redirect_to = Column(String)
    status_code = Column(SmallInteger)
    title = Column(String)
    scrap_datetime = Column(DateTime)
    error = Column(Boolean)
