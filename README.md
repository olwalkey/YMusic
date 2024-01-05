# Page_boy

## ***IMPORTANT***

Please do Note that this Runs using a fast-api server, the server has <ins>**No way To authenticate**</ins>, That means
if you have the port open to the public, anyone can send requests. This is not something you want, as far as i'm
aware, there are no errors in my code that would allow anyone to execute any destructive code or something else malicious.
That's only as far as I know, just be careful with this.

### Prefers Playlist over individual videos

This Project starts a web-server and take url requests to download the youtube videos onto a remote server.

Also Please note that this was designed to play nice with albums only, It was not designed for use with individual videos,
I made this to have an easier time downloading music to my media server.

## Plans for the future

### Database

whenever request is gotten append to a postgresql table with the following property's
 name | type |
| --- | --- |
| url | str |
| Queued | bool |
| downloaded | str |
| downloaded_data | relational to the download data from  download |

After finished downloaded set Queued to False on the Download
then set a relation from wherever it got saved in the downloads table to download_data
for easy access to the information from this table.
