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

debug = False
trace = False

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


def store_token(token):
    import json
    data = {"token": token}
    with open('.token.json', 'w') as f:
        f.write(json.dumps(data))
        f.close()

def read_token():
    """Returns Authorization Headers for a requests using pythons request library"""
    try:
        import json
        with open('.token.json', 'r') as f:
            data = json.loads(f.read())
            data = munchify(data)

        headers = {
            "Authorization": f"Bearer {data.token}" # type: ignore
        }

        return headers
    
    except FileNotFoundError as e:
        logger.debug(e)
        return False



def login(apiurl, username, password):
    formed_data = {
    "username": username,
    "password": password
}

    logger.debug(f"""
        username: {username}
        password: {password}
        apiurl: {apiurl}
    """)
    logger.trace("logging in")
    try:
        logger.trace("Checking current token validity")
        token = read_token()
        if token:
            request= requests.get(f'{apiurl}/getjson', headers=token)
            logger.debug(request.json())
            return token
        else:
            response = requests.post(f'{apiurl}/login', data=formed_data)
            response = munchify(response.json())
            logger.debug(response)
            store_token(response.access_token) # type: ignore
            token = read_token()
            logger.debug(token)
            logger.debug(requests.get(f'{apiurl}/getjson', headers=token)) # type: ignore

    except Exception as e:
        logger.error(e)




app = Typer(no_args_is_help=True, add_completion=False)


class config:
    class AppConfig(BaseModel):
        host: str
        ssl: bool = False
        port: int
        username: str
        password: str

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
                localconf=self.AppConfig(host='None', port=0, ssl=False, username='None', password='None')
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


    def fetch_data(self, apiurl, headers):
        self.get()
        r = requests.get(f'{apiurl}/getjson', headers=headers) #type: ignore
        if r.status_code == 200:
            return r
        else:
            return None

@app.command()
def follow(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enables debug-level debugging'),
):
    debug_init(trace, debug)
    Cclass= config()
    console = Console()
    conf = Cclass.get()
    if conf.ssl:
        protocol = "https"
    else:
        protocol = "http"
    if not conf.port == '80' or conf.port == '443':
        apiurl=f'{protocol}://{conf.host}:{conf.port}'   
    else:
        apiurl=f'{protocol}://{conf.host}'
    headers = login(apiurl, conf.username, conf.password)
    r = requests.get(f'{apiurl}/getjson', headers=headers)
    if r.status_code == 200:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                data = Cclass.fetch_data(apiurl, headers)
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
            logger.error('Unauthenticated! Check username and password')
        elif r.status_code == 400:
            logger.error('Failed to communicate with server')

@app.command()
def getconf():
    Cclass=config()
    print(Cclass.get())

@app.command()
def editconf(
    host: Optional[str] = Option(None, '-h', '--host', help='change host ex; youtube.downloader.com'),
    port: Optional[int] = Option(None, '-p', '--port', help='Change port ex; 5000'),
    ssl: Optional[bool] = Option(None, '-ssl', help='change ssl usage or not'),
    username: Optional[str] = Option(None, '-u', '--username', help='change username ex; MyUsername'),
    password: Optional[str] = Option(None, '-pa', '--password', help='change password ex; SuperSecretPassword'),
    
    ):
    Cclass=config()
    mydict={'host': host, 'port': port, 'ssl': ssl, 'username': username, 'password': password}
    for x, y in mydict.items():
        if y:
            Cclass.update(x, y)
        else:
            pass

@app.command()
def download(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enables debug-level debugging'),
    urls: list[str] = Argument(),
    
):
    debug_init(trace, debug)
    Cclass=config()
    conf=Cclass.get()
    if conf.ssl:
        protocol = "https"
    else:
        protocol = "http"
    if not conf.port == '80' or conf.port == '443':
        apiurl=f'{protocol}://{conf.host}:{conf.port}'
    else:
        apiurl=f'{protocol}://{conf.host}'
    try:
      headers=login(apiurl, conf.username, conf.password)
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
        logger.debug(f'{apiurl}/download/{x[0]}')
        response = requests.post(f'{apiurl}/download/{x[0]}', headers=headers)
        if response.status_code == 200:
            logger.info(response.json())
        else:
            logger.error(f'Failure: {response.status_code}')
            logger.error(response)
        pass


if __name__ == "__main__":
    app()

