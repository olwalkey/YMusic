from typer import Typer, Option, Argument
from requests.exceptions import RequestException
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, ValidationError
from rich.console import Console
from rich.table import Table
from rich.live import Live
from typing import Optional
from munch import munchify
from loguru import logger
import requests
import yaml
from sys import stderr
from time import sleep

debug = False
trace = False
confpath='.yt-dlfConfig.yaml'

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


class config:
    class AppConfig(BaseModel):
        host: str
        protocol: str
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
        except ValidationError as e:
            logger.error('Conf configured incorrectly')
            logger.error(e)
            exit()

    def get(self):
        with open(confpath, 'r+') as config:
            self.conf= yaml.safe_load(stream=config)
            self.munchconf = munchify(self.conf)
        self.verify_conf()
        return self.config

    def update(self, key, value):
        """Opens config file in write mode to edit config"""
        self.get()
        localconf=self.conf
        localconf[key] = value
        self.conf = localconf
        self.verify_conf()
        with open(confpath, 'w+') as f:
            f.write(yaml.dump(self.conf))

    def make_table(self, data):
        table = Table(title="Download Info")
        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        if data:
            for key, value in data["info"].items():
                table.add_row(key, str(value))

        return table


    def fetch_data(self, apiurl):
        self.get()
        r = requests.get(f'{apiurl}/getjson', auth=(self.munchconf.username, self.munchconf.password)) #type: ignore
        if r.status_code == 200:
            return r
        else:
            return None

@app.command()
def follow():
    Cclass= config()
    console = Console()
    conf = Cclass.get()
    if not conf.port == '80' or conf.port == '443':
        apiurl=f'{conf.protocol}://{conf.host}:{conf.port}'   
    else:
        apiurl=f'{conf.protocol}://{conf.host}'
    r = requests.get(f'{apiurl}/getjson', auth=(conf.username, conf.password))
    if r.status_code == 200:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                data = Cclass.fetch_data(apiurl)
                data = data.json() #type: ignore
                if data:
                    table = Cclass.make_table(data)
                    live.update(table)
                else:
                    console.log("[red]Failed to fetch data from the API[/red]")
                sleep(1)
    else:
        pass

@app.command()
def getconf():
    Cclass=config()
    print(Cclass.get())

@app.command()
def editconf(
    host: Optional[str] = Option(None, '-h', '--host', help='change host ex; youtube.downloader.com'),
    port: Optional[int] = Option(None, '-p', '--port', help='Change port ex; 5000'),
    protocol: Optional[str] = Option(None, '-pr', '--protocol', help='change protocol ex; http'),
    username: Optional[str] = Option(None, '-u', '--username', help='change username ex; MyUsername'),
    password: Optional[str] = Option(None, '-pa', '--password', help='change password ex; SuperSecretPassword'),
    
    ):
    Cclass=config()
    mydict={'host': host, 'port': port, 'protocol': protocol, 'username': username, 'password': password}
    for x, y in mydict.items():
        if y:
            Cclass.update(x, y)
        else:
            pass

@app.command()
def download(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enables debug-level debugging'),
    audio: Optional[bool] = Option(True, '-a', '--audio', is_flag=True, help='Whether to download Audio'),
    video: Optional[bool] = Option(False, '-v', '--video', is_flag=True, help='Whether to download Video'),
    urls: list[str] = Argument(),
    
):
    debug_init(trace, debug)
    Cclass=config()
    conf=Cclass.get()
    if video:
      audio=False
    if audio:
      dltype = 'audio'
    else: 
      dltype = 'video'
      logger.error('Video Downloading is not yet supported, consider making a pull request to change this!')
      exit()
    if not conf.port == '80' or conf.port == '443':
        apiurl=f'{conf.protocol}://{conf.host}:{conf.port}'   
    else:
        apiurl=f'{conf.protocol}://{conf.host}'   
    try:
      r = requests.get(f'{apiurl}/ping')
      r = munchify(r.json())
      logger.info(f'Pinging server: {r.ping}') #type: ignore
      logger.debug(r)
    except RequestException as e:
      logger.warning('Failed to connect to webserver run in debug to see more info')
      logger.info("Try making sure the webserver is up and your calling the right host and port!")
      logger.info(f"current host:{conf.host} port:{conf.port}")
      logger.info(f'api path: {apiurl}')
      logger.debug(e)
      exit()
        
    url = spliturl(urls)
    if url == []:
      logger.error('Url Is empty! exiting')
      exit()
    else:
      pass
    
    logger.trace(f'Full Urls: {urls}')
    for x in url:
        logger.debug(f'{apiurl}/download/{dltype}/{x[0]}')
        response = requests.get(f'{apiurl}/download/{dltype}/{x[0]}', auth=(conf.username, conf.password))
        if response.status_code == 200:
            logger.info(response.json())
        else:
            print(f'Failure: {response.status_code}')
        pass


if __name__ == "__main__":
    app()

