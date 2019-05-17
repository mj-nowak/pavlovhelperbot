import discord
import re
from subprocess import check_output
import os
import fileinput
import configparser


client = discord.Client()
ini_config = configparser.ConfigParser(allow_no_value=True)
ini_config.read('bot_settings.ini')

print('--------------------------------')
print(f'Parsing config')
print('--------------------------------')
ini_dir = ini_config['PATHS']['GameINI']
mods_dir = ini_config['PATHS']['Mods']
script_dir = ini_config['PATHS']['PavlovScript']
proc_name = ini_config['PROC']['Name']
gamemodes = list(ini_config['GAMEMODES']['Gamemodes'].split(','))
admins = []
for a in ini_config['ADMINS']:
    admins.append(a)
bot_token = ini_config['DISCORD']['Token']
channel_id = ini_config['DISCORD']['ChannelID']
channel = client.get_channel(channel_id)

print(f'Game.ini: {ini_dir}')
print(f'mods.txt: {mods_dir}')
print(f'PavlovServer.sh: {script_dir}')
print(f'Process name: {proc_name}')
print(f'Game modes: {gamemodes}')
print(f'Admin IDs: {admins}')
print(f'Bot Token: {bot_token}')
print(f'Channel ID: {channel_id}')
print('--------------------------------')
print('Bot starting')
print('--------------------------------')

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
!AddBotAdmin
!RemoveBotAdmin
!ListBotAdmins
!GetDiscordId
---------------------
!PrintIni
!PrintMods
'''



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    
    global admins

    if message.author == client.user:
        return

    if message.content.lower().startswith('!getdiscordid'):
        await message.channel.send(f'Your Discord ID is: {message.author.id}')

    if str(message.author.id) not in admins:
        await message.channel.send(f'User {message.author.id} not authorized')
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
        content = message.content.split(" ", 1)
        name = f'ServerName={content[1]}'
        for line in fileinput.input(ini_dir, inplace=True):
            if line.startswith('ServerName=') :                
                print(name)
            else:
                print(line.rstrip())
        await message.channel.send(f'Server name set to: {name}')


    if message.content.lower().startswith('!setserverplayercount'):
        content = message.content.split(" ", 1)
        number = content[1]
        if not number.isdigit():
            await message.channel.send('Invalid number: contains non numeric characters')
        else:
            count = f'MaxPlayers={number}'
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
    if message.content.lower().startswith('!addbotadmin'):
        content = re.split('\s+', message.content)
        discord_id = content[1]
        if not discord_id.isdigit():
            await message.channel.send('Invalid Discord ID: contains non numeric characters')
        elif len(discord_id) < 18:
            await message.channel.send('Invalid Discord ID: too short')
        elif len(discord_id) > 18:
            await message.channel.send('Invalid Discord ID: too long')
        else:
            if discord_id not in admins:
                admins.append(discord_id)
                ini_config['ADMINS'] = {}
                for a in admins:           
                    ini_config['ADMINS'][a] = ''
                with open('bot_settings.ini', 'w') as configfile:
                    ini_config.write(configfile)
                admins.clear()
                for a in ini_config['ADMINS']:
                    admins.append(a)
                await message.channel.send(f'Discord ID {discord_id} added to admin list')
            else:
                await message.channel.send(f'Discord ID {discord_id} already in admin list')


    if message.content.lower().startswith('!removebotadmin'):
        content = re.split('\s+', message.content)
        discord_id = content[1]
        if not discord_id.isdigit():
            await message.channel.send('Invalid Discord ID: contains non numeric characters')
        elif len(discord_id) < 18:
            await message.channel.send('Invalid Discord ID: too short')
        elif len(discord_id) > 18:
            await message.channel.send('Invalid Discord ID: too long')
        else:
            if discord_id in admins:
                with open('bot_settings.ini', 'w') as configfile:
                    del ini_config['ADMINS'][discord_id]
                    ini_config.write(configfile)
                    admins.clear()
                for a in ini_config['ADMINS']:
                    admins.append(a)
                await message.channel.send(f'Discord ID {discord_id} removed from admin list')
            else:
                await message.channel.send(f'Discord ID {discord_id} not in admin list')


    if message.content.lower().startswith('!listbotadmins'):
        await message.channel.send(f'Admins: {admins}')


client.run(bot_token)
