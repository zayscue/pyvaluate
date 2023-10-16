import sys
from typing import Annotated, Protocol

import cowsay
from fastapi import Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from kink import di
from mangum import Mangum


class Messanger(Protocol):
    def get_message(self, **kwargs) -> str:
        ...


class CowSayMessanger:
    def get_message(self, **kwargs) -> str:
        message = ""
        if "message" in kwargs:
            message = kwargs["message"]
        return cowsay.get_output_string("cow", message)


di[Messanger] = CowSayMessanger()

app = FastAPI(title="pyvaluate")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


@app.put("/message", response_class=HTMLResponse)
def put_message(
    message: Annotated[str, Form()],
    request: Request,
    service: Messanger = Depends(lambda: di[Messanger]),
) -> Response:
    cow_say_message = service.get_message(message=message)
    response = templates.TemplateResponse(
        "cowsay.html", {"request": request, "cow_say_message": cow_say_message}
    )
    return response


@app.get("/message", response_class=HTMLResponse)
def get_message(request: Request) -> Response:
    response = templates.TemplateResponse("edit_cowsay.html", {"request": request})
    return response


handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    reload = "--reload" in sys.argv
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=reload)
