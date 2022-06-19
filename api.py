from fastapi import FastAPI, HTTPException

from sql_app import crud, schemas
from sql_app.database import engine

app = FastAPI()


@app.get("/")
async def index():
    return 'FastAPI is working'


@app.post("/domain_search", response_model=schemas.DomainData)
async def get_data_by_domain(domain: schemas.RequestDomainDataPost):
    db_data_by_domain = await crud.get_by_domain(engine, domain=domain.domain_name)
    if not db_data_by_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    to_return = {
        "last_visit_date": max([row.visit_datetime for row in db_data_by_domain]),
        "first_visit_date": min([row.visit_datetime for row in db_data_by_domain]),
        "page_count": len(db_data_by_domain),
        "active_page_count": len([row for row in db_data_by_domain if row.status_code == 200]),
        "url_list": [row.url for row in db_data_by_domain]
    }

    return to_return


@app.post("/get_last_visit_url/domain", response_model=schemas.LastVisitData)
async def get_last_visit_by_domain(domain: schemas.RequestDomainDataPost):
    last_visit_by_domain = await crud.get_last_visit(engine, by_domain=domain.domain_name)
    if last_visit_by_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    to_return = {
        "requested_url": last_visit_by_domain.url,
        "visit_datetime": last_visit_by_domain.visit_datetime,
        "final_url": last_visit_by_domain.redirect_to,
        "status_code": last_visit_by_domain.status_code,
        "title": last_visit_by_domain.title,
        'domain_name': last_visit_by_domain.domain,
        'scrap_datetime': last_visit_by_domain.scrap_datetime,
    }
    return to_return


@app.post("/get_last_visit_url/url", response_model=schemas.LastVisitData)
async def get_last_visit_by_url(url: schemas.RequestURLDataPost):
    last_visit_by_url = await crud.get_last_visit(engine, by_url=url.url)
    if last_visit_by_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    to_return = {
        "requested_url": last_visit_by_url.url,
        "visit_datetime": last_visit_by_url.visit_datetime,
        "final_url": last_visit_by_url.redirect_to,
        "status_code": last_visit_by_url.status_code,
        "title": last_visit_by_url.title,
        'domain_name': last_visit_by_url.domain,
        'scrap_datetime': last_visit_by_url.scrap_datetime,
    }
    return to_return
