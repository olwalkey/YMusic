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
from json import loads
from pathlib import Path
from os import path
from pprint import pprint

debug = True
trace = True

pwd=Path(__file__).parent.resolve()
confpath = path.join(pwd, '.yt-dlfConfig.yaml')

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
        port: int
        username: str
        password: str
        debug: bool = False
        trace: bool = False
        ssl: bool
    def __init__(self):
        self.check_exist()

    def check_exist(self):
        import os.path
        if not os.path.isfile(confpath):
            logger.error('Config file not found!')
            logger.info('Generating new config')
            logger.warning('this will overwrite your current config if one exists!')
            genconf=input('Would you like to Generate a config? y/n  ')
            if genconf.lower() == 'y':
                localconf=self.AppConfig(host='None', port=0, username='None', password='None', ssl=False)
                jsondata=loads(localconf.model_dump_json())
                newconf={}
                for field in jsondata:
                    while True:
                        try:
                            if field == 'debug' or field == 'trace':
                                break
                            raw_input = input(f'{field}: ')
                            if field == "port":
                                raw_input = int(raw_input)
                            newconf[field] = raw_input
                            break
                        except ValueError:
                            print('Invalid value!')
                newconf['debug'] = False
                newconf['trace'] = False
                self.conf=newconf
                config=self.verify_conf()
                myconf=yaml.dump(self.conf, default_flow_style=False)

                with open(confpath, 'w+') as f:
                    logger.trace('writing new conf')
                    f.write(myconf)

    def verify_conf(self):
        try:
            logger.trace('verifying conf integrity')
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
        self.config.username = self.config.username.lower()
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
        r = requests.get(f'{apiurl}/getjson', auth=(self.munchconf.username.lower(), self.munchconf.password)) #type: ignore
        if r.status_code == 200:
            return r
        else:
            return None

@app.command()
def follow(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enable debug-level debugging'),
    ):

    Cclass= config()
    console = Console()
    conf = Cclass.get()
    debug_init(trace, debug)

    if conf.ssl is True:
        logger.trace('using ssl')
        apiurl=f'https://{conf.host}:{conf.port}'
    else:
        logger.trace('not using ssl')
        apiurl=f'http://{conf.host}:{conf.port}'
    logger.trace(apiurl) 
    r = requests.get(f'{apiurl}/getjson', auth=(conf.username.lower(), conf.password))
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
        logger.error(r.status_code)
        if r.status_code == 401:
            logger.error(f'Failure: {r.status_code} {r.json()['detail']}')
        elif r.status_code == 400:
            logger.error(f'Failure: {r.status_code} {r.json()['detail']}')

@app.command()
def getconf():
    Cclass=config()
    pprint(Cclass.get())

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
    if conf.ssl is True:
        apiurl=f'https://{conf.host}:{conf.port}'
    else:
        apiurl=f'http://{conf.host}:{conf.port}'
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
        logger.debug(conf)
        logger.trace(conf.username)
        logger.trace(conf.password)
        response = requests.get(f'{apiurl}/download/{dltype}/{x[0]}', auth=(conf.username, conf.password))
        if response.status_code == 200:
            logger.info(response.json())
        else:
            logger.error(f'Failure: {response.status_code} {response.json()['detail']}')
            #logger.error(response.json()['detail'])
        pass

if __name__ == "__main__":
    app()

