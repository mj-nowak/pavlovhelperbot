# pavlovhelperbot
Discord bot for managing dedicated Pavlov servers

Requirements:
- Python 3.6+
- Running on same machine as the dedicated server to control

Setup:
- Follow this guide up to setup a new bot and get a token and channel ID:
https://github.com/Chikachi/DiscordIntegration/wiki/How-to-get-a-token-and-channel-ID-for-Discord
- Set "token" and "channelid" variables in bot_settings.ini
- Change any file references where necessariy if not installed to default location in bot_settings.ini
- "sudo su -l steam"
- "pip3 install discord"
- "python3 path_to_pavlovbot.py"

NOTE: All commands require the caller to be in the [ADMINS] group EXCEPT getdiscordid, you can use this to acquire your own ID or to get someone elses.  An initial ID will HAVE to be in place in the [ADMINS] section of the bot_settings.ini before any other commands can be called.  These are valueless keys in the file, an example is:

[ADMINS]
148928469923790848 = 


-------------------------------------------------------------------
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
-------------------------------------------------------------------
