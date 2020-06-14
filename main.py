from fastapi import FastAPI, Query, Body, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="./")

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None
    

@app.get("/")
def read_root():
    return {"Hello":"World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.put("/item/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.post("/create_item/")
def create_item(q: Item = Body(..., alias = "item-query",title = "Create item with id q", 			description = "Query item to create the item in the database",
    		deprecated = False
    		)):

    return {"new": q}

@app.get("/template/")
def read_template(request: Request, name: str):
    return templates.TemplateResponse("template.html", {"request":request, "name": name})
