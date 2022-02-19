
from uuid import uuid4, UUID

import httpx
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import  Jinja2Templates

from models import DishClothGenerator


templates = Jinja2Templates("templates")
app = FastAPI()


@app.get("/dishcloth", response_class=RedirectResponse)
def randomize_dishcloth(settings: DishClothGenerator = Depends(DishClothGenerator)):
    res = str(settings.url(httpx.URL(f"/dishcloth/{uuid4()}")))
    return RedirectResponse(res)


@app.get("/dishcloth/customize", response_class=HTMLResponse)
def customize_dishcloth(request: Request, settings: DishClothGenerator = Depends(DishClothGenerator)):
    print(settings)
    return templates.TemplateResponse('customize.html', {
        'request': request,
        'settings': settings
    })


@app.get("/dishcloth/{seed}", response_class=HTMLResponse)
def dishcloth_pattern(seed: UUID, request: Request, settings: DishClothGenerator = Depends(DishClothGenerator)):
    # print(settings.url)
    return templates.TemplateResponse("pattern.html", {
        'seed': seed,
        'request': request,
        'scrubber': settings(seed),
        'shuffle_url': str(settings.url(httpx.URL("/dishcloth"))),
        'customize_url': str(settings.url(httpx.URL("/dishcloth/customize")))
    })

