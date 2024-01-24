# Page_boy

## ***IMPORTANT***

~~Please do Note that this Runs using a fast-api server, the server has <ins>**No way To authenticate**</ins>, That means
if you have the port open to the public, anyone can send requests. This is not something you want, as far as i'm
aware, there are no errors in my code that would allow anyone to execute any destructive code or something else malicious.
That's only as far as I know, just be careful with this.~~

We Now have a way to authenticate, just make sure to configure it in your config.yaml. It is only using very basic HTTP
authentication, so don't trust it with your life, if You plan on using this app in the real world, I would just suggest
setting up a wireguard vpn or something and then using that to connect and run these commands.

### Prefers Playlist over individual videos

This Project starts a web-server and take url requests to download the youtube videos onto a remote server.

Also Please note that this was designed to play nice with albums only, It was not designed for use with individual videos,
I made this to have an easier time downloading music to my media server.
