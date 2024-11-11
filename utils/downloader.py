import yt_dlp
from munch import munchify
from typing import Optional
from loguru import logger
import sys
from .config import config

if __name__ != '__main__':
    try:
        from . import interaction as interactions
    except ImportError:
        try:
            from . import interaction as interactions
        except Exception as e:
            logger.error('Failed to import db')
            logger.error(e)
            interactions = None
            exit()
else:
    logger.warning("Didn't try to import db")
    pass



class MyLogger:
    def debug(self, msg):

        if msg.startswith('[debug] '):
            logger.debug(msg)
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        pass






try:
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

    debug_init(config.trace, config.debug)

    def progress_hook(self, d):
        d = munchify(d)

        if d.status == 'error':  # type: ignore
            pass

        if d.status == 'finished':  # type: ignore
            logger.trace(f'Done Downloading "{
                         d["filename"]}"')  # type: ignore
            self.StatusStarted = False  # type: ignore
            self.filename = d['filename']  # type: ignore
            self.time_elapse = d['elapsed']  # type: ignore
            self.PostProcessorStarted = False

        if d.status == 'downloading':  # type: ignore
            if not self.StatusStarted:
                logger.trace(f'Now Downloading "{
                             d["filename"]}"')  # type: ignore
                self.StatusStarted = True

            self.filename = d['filename']  # type: ignore
            self.percent = d['_percent_str']  # type: ignore
            self.eta = d['_eta_str']  # type: ignore
            self.speed = d['speed']  # type: ignore



    def postprocessor_hooks(self, d):

        d = munchify(d)
        if d.status == 'started':  # type: ignore
            info = munchify(d['info_dict'])  # type: ignore
            self.Album = info.album  # type: ignore
            self.url = info.webpage_url  # type: ignore
            self.title = info.title  # type: ignore
            self.download_path = info.filepath  # type: ignore
            self.Status = 'Started'
            logger.debug(f"""
                        {self.Album}
                        {self.url}
                        {self.title}
                         {self.download_path}
                         {self.Status}""")

        if d.status == 'finished':  # type: ignore
            logger.trace('PostProcessor Hook finished')
            if not self.PostProcessorStarted:
                self.db.markVideoDownloaded(
                    playlisturl=self.playlist_url,
                    url=self.url,  # type: ignore
                    title=self.title,
                    download_path=self.download_path,
                    elapsed=self.time_elapse)

                self.PostProcessorStarted = True
            self.Status = 'Finished'





    def ydl_opts(self):

        ydl_opts = {
            'ratelimit': config.ratelimit,  # Kilobytes
            'restrictfilenames': config.restrictfilenames,
            'logger': MyLogger(),
            'breakonexisting': True,
            'progress_hooks': [self.progress_hook],
            'postprocessor_hooks': [self.postprocessor_hooks],
            'writethumbnail': True,
            'skip_broken': True,
            'ignoreerrors': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio',
                 'preferredcodec': 'mp3',
                 'preferredquality': 'None'},
                {'add_metadata': 'True', 'key': 'FFmpegMetadata'},
                {'already_have_thumbnail': False, 'key': 'EmbedThumbnail'}
            ]}

        if config.restrictfilenames:
            ydl_opts["outtmpl"] = 'downloads/%(playlist_title)s/%(playlist_autonumber)s-%(title)s.%(ext)s'
        else:
            ydl_opts["outtmpl"] = 'downloads/%(playlist_title)s/%(playlist_autonumber)s - %(title)s.%(ext)s'

        return ydl_opts


    def playlist_title_opts(self):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True
        }
        return ydl_opts


    class Downloader:

        def __init__(self):
            pass





except Exception as e:
    logger.error(e)
    pass
