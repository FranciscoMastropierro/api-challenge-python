from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import requests

app = FastAPI()

class Item(BaseModel):
    query : str
    id: str
    title: str
    price: float
    available_quantity: float
    condition: str
    permalink: str
    warranty: str

@app.get("/items/", status_code=201)
async def get_item():
    products = ["notebook apple", "notebook asus", "notebook hp"]  
    response = list()

    for product in products:
        firts_product_IDs = []
        results_first_product = []
        offset = 0

        while offset < 150:
            URL:str = f"https://api.mercadolibre.com/sites/MLA/search?q={product}&offset={offset}"
            data = requests.get(URL).json()
            firts_product_IDs += [elem['id'] for elem in data['results']]
            offset += 50

        for productID in firts_product_IDs:
            print(f"getting {productID} info")
            try:
                data = requests.get(f"https://api.mercadolibre.com/items/{productID}").json()
                if not 'price' in data:
                    continue
                results_first_product.append(data) 
            except requests.exceptions.RequestException as error:
                print(error)

        partialResponse = [
            {
            "query": product,  
            "id": item["id"],
            "title": item["title"],
            "price": item["price"],
            "available_quantity": item["available_quantity"],
            "condition": item["condition"],
            "permalink": item["permalink"] or "none",
            "warranty": item["warranty"] or "none"
            } for item in results_first_product]
        
        response += partialResponse

    fields = [
        {"label": "Query de Busqueda", "value": "query"},
        {"label": "ID", "value": "id"},
        {"label": "Titulo del producto", "value": "title"},
        {"label": "Precio", "value": "price"},
        {"label": "Cantidad disponible", "value": "available_quantity"},
        {"label": "Condicion", "value": "condition"},
        {"label": "Link al item", "value": "permalink"},
        {"label": "Garantia", "value": "warranty"}
    ]

    df = pd.DataFrame(response, columns=[x['value'] for x in fields])
    df.rename(columns={x['value']: x['label'] for x in fields}, inplace=True)
    csv = df.to_csv(index=False)

    try:
        with open("reporte-notebooks.csv", "w", encoding='utf-8') as file:
            file.write(csv)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="fail creating csv") 

    return csv