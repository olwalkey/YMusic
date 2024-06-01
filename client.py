from typer import Typer, Option, Argument
from requests.exceptions import RequestException
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, ValidationError
from typing import Optional
from munch import munchify
from loguru import logger
import requests
import yaml
from sys import stderr


debug = False
trace = False


obj = munchify({})


def debug_init(trace, debug):
    logger.remove()
    if debug:
        logger.add(stderr, level='DEBUG')
    elif trace:
        logger.add(stderr, level='TRACE')
    else:
        logger.add(stderr, level='INFO')
        pass
    pass


def spliturl(urls):
    logger.debug(urls)
    url = []
    for x in urls:
        parsed_url = urlparse(x)

        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v')
        playlist_id = query_params.get('list')
        if not playlist_id == None:
            url.append(playlist_id)
        else:
            url.append(video_id)
        continue
    logger.debug('Done Splitting Urls')
    logger.debug(url)
    return url


app = Typer(no_args_is_help=True, add_completion=False)

with open('config.yaml') as stream:
    try:
        yamlfile = yaml.safe_load(stream)
        if yamlfile is not None:
          loadedyaml = munchify(yamlfile)
        else:
          raise FileNotFoundError('File Either does not exist, or it is formatted incorrectly')
    except yaml.YAMLError as exc:
        print(exc)
        raise ValueError('Config failed to load Properly!')



class config:
    class AppConfig(BaseModel):
        host: str
        port: int
        username: str
        password: str
        debug: bool = False
        trace: bool = False

    def __init__(self):
        pass

    def verify_conf(self):
        try:
            self.config=self.AppConfig(**self.conf)
            return self.config
        except ValidationError:
            logger.error('Conf configured incorrectly')

    def get(self):
        with open('.yt-dlfConfig.yaml', 'r+') as config:
            self.conf= yaml.safe_load(stream=config)
        self.verify_conf()
        print(self.config.port)
        return self.config


@app.command()
def getconf():
    Cclass=config()
    print(Cclass.get())


@app.command()
def download(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enables debug-level debugging'),
    audio: Optional[bool] = Option(True, '-a', '--audio', is_flag=True, help='Whether to download Audio'),
    video: Optional[bool] = Option(False, '-v', '--video', is_flag=True, help='Whether to download Video'),
    urls: list[str] = Argument(),
    
):
    debug_init(trace, debug)
    if video:
      audio=False
    if audio:
      dltype = 'audio'
    else: 
      dltype = 'video'
      print('Video Downloading is not yet supported, consider making a pull request to change this!')
      
    try:
      r = requests.get(f'http://{config.host}:{config.port}/ping')
      r = munchify(r.json())
      logger.info(f'Pinging server: {r.ping}') #type: ignore
      logger.debug(r)
    except RequestException as e:
      logger.warning('Failed to connect to webserver run in debug to see more info')
      logger.info("Try making sure the webserver is up and your calling the right host and port!")
      logger.info(f"current host:{config.host} port:{config.port}")
      logger.debug(e)
      sys.exit()
        
    url = spliturl(urls)
    if url == []:
      logger.error('Url Is empty! exiting')
      sys.exit()
    else:
      pass
    
    logger.trace(f'Full Urls: {urls}')
    for x in url:
        logger.debug(f'http://{config.host}:{config.port}/download/{dltype}/{x[0]}')
        response = requests.get(f'http://{config.host}:{config.port}/download/{dltype}/{x[0]}', auth=(config.username, config.password))
        if response.status_code == 200:
            logger.info(response.json())
        else:
            print(f'Failure: {response.status_code}')
        pass


if __name__ == "__main__":
    app()

