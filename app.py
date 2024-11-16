from robyn import Robyn, Request, Response
from loguru import logger

app = Robyn(__file__)



@app.get("/")
async def h(request: Request):
    return "Hello, world"

@app.get("/info")
async def get_json():
    """Returns data about the running server"""
    return "Test"


app.start(port=8080, host="0.0.0.0")
