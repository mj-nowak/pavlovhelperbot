# pavlovhelperbot
Discord bot for managing dedicated Pavlov servers

NOTE:  There is no user validation in place yet, anyone on the channel the bot is deployed to will be able to execute the commands, keep that in mind

Requirements:
- Python 3.6+
- Running on same machine as the dedicated server to control

Setup:
- Follow this guide up to setup a new bot and get a token and channel ID:
https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord
- Set "bot_token" and "channel" variables in pavlovbot.py
- Change any file references where necessariy if not installed to default location
- "sudo su -l steam"
- "pip3 install discord"
- "python3 path_to_pavlovbot.py"

Commands: (case insensitive) (prefix command with "!")

Help

StartServer

StopServer

RestartServer

AddMap <UGC NUMBER> <GAMEMODE>
  
RemoveMap <UGC>

ReportCPU

ReportMemory

ReportDisk

SetServerName <NAME>
  
SetServerPlayerCount <NUMBER>

AddMod <STEAM ID>
  
RemoveMod <STEAM ID>

AddBotAdmin

RemoveBotAdmin

ListBotAdmins

GetDiscordId
  
PrintIni

PrintMods
