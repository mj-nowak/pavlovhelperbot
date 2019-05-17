import discord
import re
from subprocess import check_output
import os
import fileinput

bot_token = 'discord_bot_token_here'
client = discord.Client()
#Channel ID to send messages to
channel = client.get_channel(discord_channel_id_here)
# for guild in client.guilds:
#     for channel in guild.channels:
#         print(channel.id)
ini_dir = '/home/steam/pavlovserver/Pavlov/Saved/Config/LinuxServer/Game.ini'
mods_dir = '/home/steam/pavlovserver/Pavlov/Saved/Config/mods.txt'
script_dir = '/home/steam/pavlovserver/PavlovServer.sh'
proc_name = '/home/steam/pavlovserver/Pavlov/Binaries/Linux/PavlovServer'
gamemodes = ['SND', 'TDM', 'DM', 'GUN', 'CTF']
help_text = '''
Commands: (case insensitive)
!Help
---------------------
!StartServer
!StopServer
!RestartServer
---------------------
!AddMap <UGC NUMBER> <GAMEMODE>
!RemoveMap <UGC>
---------------------
!ReportCPU
!ReportMemory
!ReportDisk
---------------------
!SetServerName <NAME>
!SetServerPlayerCount <NUMBER>
---------------------
!AddMod <STEAM ID>
!RemoveMod <STEAM ID>
---------------------
!PrintIni
!PrintMods
'''



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!help'):
        await message.channel.send(help_text)
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!addmap'):
        content = re.split('\s+', message.content)
        if len(content) < 3:
            await message.channel.send('Invalid command, usage: !AddMap <UGC NUMBER> <GAMEMODE>')
        elif content[2].upper() not in gamemodes:
            await message.channel.send(f'Invalid gamemode, available modes: {gamemodes}')
        else:
            ugc = content[1]
            gamemode = content[2].upper()
            if not ugc.isdigit():
                await message.channel.send('Invalid UGC number: contains non numeric characters')
            elif len(ugc) < 10:
                await message.channel.send('Invalid UGC number: too short')
            elif len(ugc) > 10:
                await message.channel.send('Invalid UGC number: too long')
            else:
                entry = f'MapRotation=(MapId="UGC{ugc}", GameMode="{gamemode}")'
                if entry in open(ini_dir).read():
                    await message.channel.send(f'Entry: {entry} already exists')
                else:
                    config = open(ini_dir, "a")
                    config.write(entry)
                    config.close()
                    await message.channel.send(f'Adding entry: MapRotation=(MapId="UGC{ugc}", GameMode="{gamemode}")')


    if message.content.lower().startswith('!removemap'):
        content = re.split('\s+', message.content)
        ugc = content[1]
        if not ugc.isdigit():
            await message.channel.send('Invalid UGC number: contains non digit characters')
        elif len(ugc) < 10:
            await message.channel.send('Invalid UGC number: too short')
        elif len(ugc) > 10:
            await message.channel.send('Invalid UGC number: too long')
        else:
            found_map = False
            for line in fileinput.input(ini_dir,inplace=True):
                line = line.strip()
                if not ugc in line:
                    print(line)
                else:
                    await message.channel.send(f'Removing entry: {line}')
                    found_map = True
            if not found_map:
                await message.channel.send('Entry not found')            
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!startserver'):
        pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
        if not pid:
            os.popen(script_dir)
            await message.channel.send('Starting server')        
        else:
            await message.channel.send('Server already running')


    if message.content.lower().startswith('!stopserver'):
        pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
        print(pid)
        if not pid:
            await message.channel.send('Server not running')
        else:
            os.system(f'kill {pid}')
            await message.channel.send('Server stopped')


    if message.content.lower().startswith('!restartserver'):
        pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
        print(pid)
        if not pid:
            os.popen(script_dir)
            await message.channel.send('Server not running, starting now')        
        else:
            os.system(f'kill {pid}')
            os.popen(script_dir)
            await message.channel.send('Server restarting')
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!reportcpu'):
        total = os.popen('cat /proc/loadavg | cut -f 3 -d \' \'').read().rstrip()
        cores = os.popen('grep -c ^processor /proc/cpuinfo').read().rstrip()
        result = os.popen(f'echo {total}*100/{cores} | bc').read().rstrip()
        await message.channel.send(f'{result.rstrip()}%')


    if message.content.lower().startswith('!reportdisk'):
        result = os.popen('df | grep ^\/dev.*/\$ | awk \'{print $5}\' | grep -Po \'[0-9]+\'').read()
        await message.channel.send(f'{result.rstrip()}%')


    if message.content.lower().startswith('!reportmemory'):
        result = os.popen('free | grep Mem | awk \'{print int($3/$2 * 100)}\'').read().rstrip()
        await message.channel.send(f'{result.rstrip()}%')
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!setservername'):
        content = content.split(" ", 1)
        name = f'ServerName={content[1]}'
        for line in fileinput.input(ini_dir, inplace=True):
            if line.startswith('ServerName=') :                
                print(name)
            else:
                print(line.rstrip())
        await message.channel.send(f'Server name set to: {name}')


    if message.content.lower().startswith('!setserverplayercount'):
        content = content.split(" ", 1)
        number = content[1]
        if not number.isdigit():
            await message.channel.send('Invalid number: contains non numeric characters')
        else:
            count = f'MaxPlayers={content[1]}'
            for line in fileinput.input(ini_dir, inplace=True):
                if line.startswith('MaxPlayers=') :                
                    print(count)
                else:
                    print(line.rstrip())
            await message.channel.send(f'Server max players set to: {count}')
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!addmod'):
        content = re.split('\s+', message.content)
        steam_id = content[1]
        if not steam_id.isdigit():
            await message.channel.send('Invalid steam ID: contains non numeric characters')
        elif len(steam_id) < 17:
            await message.channel.send('Invalid steam ID: too short')
        elif len(steam_id) > 17:
            await message.channel.send('Invalid steam ID: too long')
        else:
            if steam_id in open(mods_dir).read():
                await message.channel.send(f'Entry: {steam_id} already exists')
            else:
                config = open(mods_dir, "a")
                config.write(steam_id)
                config.close()
                await message.channel.send(f'Adding entry: {steam_id}')


    if message.content.lower().startswith('!removemod'):
        content = re.split('\s+', message.content)
        steam_id = content[1]
        print(steam_id)
        if not steam_id.isdigit():
            await message.channel.send('Invalid steam ID: contains non numeric characters')
        elif len(steam_id) < 17:
            await message.channel.send('Invalid steam ID: too short')
        elif len(steam_id) > 17:
            await message.channel.send('Invalid steam ID: too long')
        else:
            found_mod = False
            for line in fileinput.input(mods_dir,inplace=True):
                line = line.strip()
                if not steam_id in line:
                    print(line)
                else:
                    await message.channel.send(f'Removing entry: {line}')
                    found_mod = True
            if not found_mod:
                await message.channel.send('Entry not found')       
#######################################################################################
#######################################################################################
    if message.content.lower().startswith('!printini'):
        ini = open(ini_dir, 'r')
        await message.channel.send('Printing Game.ini:')
        await message.channel.send(ini.read())

    if message.content.lower().startswith('!printmods'):
        mods = open(mods_dir, 'r')
        await message.channel.send('Printing mods.txt')
        await message.channel.send(mods.read())
#######################################################################################
#######################################################################################


client.run(bot_token)
