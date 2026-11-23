from fastapi import FastAPI , Request
from mockdata import products
from DTO import productDTO

app = FastAPI()

@app.get("/")
def home():
    return "welcome to home page!!"

@app.get("/products")
def get_products():
    return products

# below is example of path parameter routing
@app.get("/products/{product_id}")
def getProductWithID(product_id:int):
    for oneProduct in products:
        if oneProduct.get("id") == product_id:
            return oneProduct
    return{
        "no product found with the given id"
    }


@app.get("/greet")
def getDetailsProduct(request : Request):
    query_params = dict(request.query_params)
    return{
        "greet": f"hello {query_params.get('name')}, how are you, ik you're {query_params.get('age')} years old!"
    }

@app.post("/create_product")
def createProduct(productData:productDTO):
    print(productData)
    return {
        "status" : "product created succesfully"
    }

@app.put("/update_product/{product_id}")
def update_product(product_data:productDTO , product_id:id):
    for index, one_product in enumerate(products):
        if(one_product.get("id") == product_id+1):
            products[index] = product_data.model_dump()
            return {"status" : "Product updated successfully"}

    return{"status" : "Product not found!"}

