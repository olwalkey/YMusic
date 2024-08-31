# Page_boy

We Now have a way to authenticate, just make sure to configure it in your config.yaml. It is only using very basic HTTP
authentication, so don't trust it with your life, if You plan on using this app in the real world, I would just suggest
setting up a wireguard vpn or something and then using that to connect and run these commands.

## Prefers Playlist/Albums over individual videos

This Project starts a web-server and take url requests to download the youtube videos onto a remote server.

Also Please note that this was designed to play nice with albums only, It was not designed for use with individual videos,
I made this to have an easier time downloading music to my media server.

## Weird bugs and other quirks

When using the client side of this program, if you try to downlaod videos like this
`py client.py https://music.youtube.com/watch?v=SPWsptIhKkM&list=RDAMVMSPWsptIhKkM`
you might get an error like this
```
[3] 10305
zsh: no matches found: https://music.youtube.com/watch?v=SPWsptIhKkM 
```

This is because the shell using stuff like ? and & to denote certain actions in the terminal
you can fix this by eiither wrapping the url in quotes like 

`py client.py 'https://music.youtube.com/watch?v=SPWsptIhKkM&list=RDAMVMSPWsptIhKkM"`

or by adding a backslsh to the end of the url 

`py client.py https://music.youtube.com/watch?v=SPWsptIhKkM&list=RDAMVMSPWsptIhKkM\`

## Activity

![Alt](https://repobeats.axiom.co/api/embed/155beec05c734960fcd4d8e0c428e7d3930d68d0.svg "Repobeats analytics image")
