import discord
import re
from subprocess import check_output
import os
import fileinput

client = discord.Client()
channel = client.get_channel(578639591628734484)
ini_dir = '/home/steam/pavlovserver/Pavlov/Saved/Config/LinuxServer/Game.ini'
script_dir = '/home/steam/pavlovserver/PavlovServer.sh'
proc_name = '/home/steam/pavlovserver/Pavlov/Binaries/Linux/PavlovServer'
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!help'):
        await message.channel.send('''
Commands: (case insensitive)
!Help
!StartServer
!StopServer
!RestartServer
!AddMap <UGC> <GAMEMODE>
!RemoveMap <UGC>
!ReportCPU
!ReportMemory
!ReportDisk
!SetServerName
!SetServerPlayerCount
''')

    if message.content.lower().startswith('!addmap'):
        content = re.split('\s+', message.content)
        ugc = content[1]
        gamemode = content[2].upper()
        print(content)
        if len(content) < 3:
            await message.channel.send('Invalid command, usage: !AddMap <UGC> <GAMEMODE>')
        else:
            if len(ugc) < 10:
                await message.channel.send('Invalid UGC')
            else:
                print(ugc)
                print(gamemode)
                config = open("Game.ini", "a")
                config.write(f'MapRotation=(MapId="{ugc}", GameMode="{gamemode}")\n')
                config.close()
                await message.channel.send(f'Adding entry: MapRotation=(MapId="{ugc}", GameMode="{gamemode}")')


    if message.content.lower().startswith('!removemap'):
        content = re.split('\s+', message.content)
        ugc = content[1]
        found = False
        for line in fileinput.input(ini_dir,inplace=1):
            line = line.strip()
            if not ugc in line:
                print(line)
            else:
                await message.channel.send(f'Removing entry: {line}')
                found = True
        if not found:
            await message.channel.send('Entry not found')            

    if message.content.lower().startswith('!restartserver'):
        result = restart_server()
        print(result)
        await message.channel.send(result)

    if message.content.lower().startswith('!startserver'):
        result = start_server()
        print(result)
        await message.channel.send(result)

    if message.content.lower().startswith('!stopserver'):
        result = stop_server()
        print(result)
        await message.channel.send(result)

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


    #pid = os.popen("pgrep -u steam -f pavlov").read()

    # for guild in client.guilds:
    #     for channel in guild.channels:
    #         print(channel.id)


def start_server():
    pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
    if not pid:
        os.popen(script_dir)
        return('Starting server')        
    else:
        return('Server already running')


def stop_server():
    pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
    print(pid)
    if not pid:
        return('Server not running')
    else:
        os.system(f'kill {pid}')
        return('Server stopped')


def restart_server():
    pid = os.popen(f"pgrep -u steam -fx {proc_name}").read()
    print(pid)
    if not pid:
        os.popen(script_dir)
        return('Server not running, starting now')        
    else:
        os.system(f'kill {pid}')
        os.popen(script_dir)
        return('Server restarting')

client.run('NTc4NjM2NTc1NzM1NTQ1ODU3.XN2fdg.iBhASIonUqo1wHEGNLQLg22-YPA')
