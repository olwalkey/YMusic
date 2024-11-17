from robyn import Robyn, Request, Response, jsonify
from robyn.robyn import QueryParams
from robyn.types import PathParams

from datetime import datetime

from loguru import logger

from apscheduler.schedulers.background import BackgroundScheduler

import utils


app = Robyn(__file__)

startTime = datetime.now()
app.inject_global(starttime=startTime)

@app.startup_handler
async def startup_handler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(scanDatabase, 'interval', seconds=5)
    scheduler.start()


def scanDatabase():
    next_item = utils.interaction.fetchNextItem()
    logger.info(next_item)
    if next_item is not None:
        utils.youtube.start_download(next_item[2])




@app.get("/info")
async def get_server_info(global_dependencies):
    """Gets Info about the running server
    eg.  
    version  
    uptime  
    Important lib Versions  
    How many songs have been downloaded
    """
    uptime = datetime.now() - global_dependencies['starttime']
    return jsonify({"uptime": f"{uptime}"})

@app.get("/downloading")
async def downloading_info():
    """Gets info About the current downloading item"""
    pass

@app.get("/latest/:num")
async def get_latest_downloads(request, path_params: PathParams):
    """Get latest downloaded items
    Gets same number of recent as you provide with num var
    """
    num: int = int(path_params['num'])
    return jsonify({"num": num})

@app.get("/ping")
async def ping():
    return jsonify({"ping": "pong!"})




@app.post("/download/:app/:url")
async def download(request, path_params: PathParams):
    """Takes a url and downloads the supplied video/song/playlist"""
    app: str = path_params['app']
    url: str = path_params['url']

    return utils.interaction.createEntry(url, app)


@app.post("/login")
async def login():
    """Logs the user into the app and supplies them with a jwt"""
    pass

@app.post("/register")
async def register():
    """Register a new user and add them to the database"""
    pass





app.start(port=8000, host="0.0.0.0")
