from robyn import Robyn, Request, Response, jsonify
from loguru import logger

app = Robyn(__file__)



@app.get("/info")
async def get_server_info():
    """Gets Info about the running server
    eg.  
    version  
    uptime  
    Important lib Versions  
    How many songs have been downloaded
    """
    return "Test"

@app.get("/downloading")
async def downloading_info():
    """Gets info About the current downloading item"""
    pass

@app.get("/latest/:num")
async def get_latest_downloads(request, path_params):
    """Get last 10 downloaded items"""
    num: int = path_params['num']
    return jsonify({"num": num})


@app.post("/download/:app/:url")
async def download(request, path_params):
    """Takes a url and downloads the supplied video/song/playlist"""
    app: str = path_params['app']
    url: str = path_params['url']
    return jsonify({"url": url, "app": app})


@app.post("/login")
async def login():
    """Logs the user into the app and supplies them with a jwt"""
    pass

@app.post("/register")
async def register():
    """Register a new user and add them to the database"""
    pass





app.start(port=8000, host="0.0.0.0")
