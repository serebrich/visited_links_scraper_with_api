from typing import Union, List
from datetime import datetime
from pydantic import BaseModel


class RequestDomainDataPost(BaseModel):
    domain_name: str


class RequestURLDataPost(BaseModel):
    url: str


class ScrapedURLs(BaseModel):
    url: str
    visit_datetime: datetime
    domain: Union[str, None]
    redirect_to: Union[str, None]
    status_code: Union[int, None]
    title: Union[str, None]
    scrap_datetime: datetime
    error: bool

    class Config:
        orm_mode = True


class LastVisitData(BaseModel):
    visit_datetime: datetime
    requested_url: str
    final_url: Union[str, None]
    status_code: Union[int, None]
    title: Union[str, None]
    scrap_datetime: datetime
    domain_name: Union[str, None]

    class Config:
        orm_mode = True


class DomainData(BaseModel):
    last_visit_date: datetime
    first_visit_date: datetime
    page_count: int
    active_page_count: int
    url_list: List[str]

    class Config:
        orm_mode = True
