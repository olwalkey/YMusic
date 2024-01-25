from typer import Typer, Option, Argument
from requests.exceptions import RequestException
from urllib.parse import urlparse, parse_qs
from typing import Optional
from munch import munchify
from loguru import logger
import requests
import yaml
import sys

debug = False
trace = False


obj = munchify({})
assert isinstance(obj, Munch)
port = obj['port']


def debug_init(trace, debug):
    logger.remove()
    if debug:
        logger.add(sys.stderr, level='DEBUG')
    elif trace:
        logger.add(sys.stderr, level='TRACE')
    else:
        logger.add(sys.stderr, level='INFO')
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



@app.command()
def download(
    trace: Optional[bool] = Option(False, '-t', '--trace', is_flag=True, help='Enable trace-level debugging.'),
    debug: Optional[bool] = Option(False, '-d', '--debug', is_flag=True, help='Enables debug'),
    audio: Optional[bool] = Option(True, '-a', '--audio', is_flag=True, help='Weather to downloade audio or video'),
    urls: list[str] = Argument(),
    
):
  #? 0: Audio
  #? 1: Video
    debug_init(trace, debug)
    if audio:
      dltype = 'audio'
    else: 
      dltype = 'video'
      
    try:
      r = requests.get(f'http://{loadedyaml.host}:{loadedyaml.port}/ping')
      r = munchify(r.json())
      logger.info(f'Pinging server: {r.ping}')
      logger.debug(r)
    except RequestException as e:
      logger.warning('Failed to connect to webserver run in debug to see more info')
      logger.info("Try making sure the webserver is up and your calling the right host and port!")
      logger.info(f"current host:{loadedyaml.host} port:{loadedyaml.port}")
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
        logger.debug(f'http://{loadedyaml.host}:{loadedyaml.port}/download/{dltype}/{x[0]}')
        response = requests.get(f'http://{loadedyaml.host}:{loadedyaml.port}/download/{dltype}/{x[0]}', auth=(loadedyaml.username, loadedyaml.password))
        if response.status_code == 200:
            logger.info(response.json())
        else:
            print(f'Failure: {response.status_code}')
        pass


if __name__ == "__main__":
    app()
