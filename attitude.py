

import discord
import asyncio
import json
import urllib.request
import random
from datetime import datetime, timedelta, timezone
from math import floor
from affix import affixes
from dict import DictionaryReader

file = open("token.json",'r')
tokenObj = json.load(file)
file.close()

client = discord.Client()

officersID = [
    '204420413814472704', #Alex
    '229757511715127296', #Sammy
    '218079956888977409', #Bruise
    '90170201890394112'  #Nate
]

#'90170201890394112',  #Nate
#'216036936433795084', #Caleb
#'187392035890659328', #Gummy
#'229981371928412160', #Kyo

## IDs for Attitude
server_id = '245634401046626304' 
## Voice Channels
lads_voice = '396058528600817674'
raid_voice = '246053446287884298'
## Roles
officer_role = '245636355311403008'
## Text Channel
lads_text = '396058468479664138'

## Setup variables -------------------------
prefix = '!'
revolver = [0,0,0,0,0,0]
index = 0
baseURL = 'https://us.api.battle.net/'
# -------------------------------------------

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    #global officersID
    global revolver
    global index

    # Ignore and messages made by the bot
    if message.author.bot:
        return

    # Ignore any message that does not have the prefix
    if not message.content.startswith(prefix):
        return

    d = DictionaryReader()

    # This list will contain the author's roles to check against later, only works in a server (ie not with PMs)
    try:
        roles = []
        for role in message.author.roles:
            roles.append(role.name)
        #print(roles)
    except:
        pass


# ----------------------------------------------------------------------------------------
## Available to Officers Only
# ----------------------------------------------------------------------------------------

    # can use this to move clients around in "guild" aka "server"
    if (message.content.startswith(prefix+'summon')) and ('Officers' in roles):
        Guild = message.server
        print(Guild)
        for channel in Guild.channels:
            print(channel)
            if channel.name != 'Raid':
                print(channel.voice_members)
                for member in list(channel.voice_members):
                    print('Moving ' + member.display_name)
                    await client.move_member(client.get_server(server_id).get_member(member.id), client.get_channel(raid_voice))
        await client.delete_message(message)

    elif (message.content.startswith(prefix+'up')) and ('Officers' in roles): 
        print(officersID)
        for x in officersID:
            #print(officersID)
            # Moves everyone in officersID list to Officer channel 
            await client.move_member(client.get_server(server_id).get_member(x), client.get_channel(lads_voice))
        await client.delete_message(message)

    elif (message.content.startswith(prefix+'down')) and ('Officers' in roles) :
        for x in officersID:
            # Moves everyone in officersID list to Raid channel 
            await client.move_member(client.get_server(server_id).get_member(x), client.get_channel(raid_voice))
        await client.delete_message(message)

# ----------------------------------------------------------------------------------------
## Available to everyone else
# ----------------------------------------------------------------------------------------

    # List guild warcraft log page, and latest log
    elif message.content.startswith(prefix + 'logs'):
        logs = urllib.request.urlopen('https://www.warcraftlogs.com:443/v1/reports/guild/Lads/Illidan/us?api_key='+tokenObj['logsapi'])
        ljdata = json.load(logs)
        await client.send_message(message.channel, 'Guild Page: https://www.warcraftlogs.com/guilds/339520\nLatest Log: https://www.warcraftlogs.com/reports/' + str(ljdata[len(ljdata) - 1]['id']))


    # Will display the current WoW Token price on AuctionHouse
    elif message.content.startswith(prefix+'token'):
        wowTokenRes = urllib.request.urlopen(baseURL+'data/wow/token/?namespace=dynamic-us&locale=en_US&access_token='+tokenObj['apiToken'])
        #wowToken is an int representing the gold price of a token
        wowToken = str(json.load(wowTokenRes)['price'])
        length = len(wowToken)
        await client.send_message(message.channel, 'Current WoW Token price is: ' + wowToken[:length-4]+'g '+wowToken[-4:-2]+'s '+wowToken[-2:]+'c')

    
    # Lists current week affixes, as well as next week's affixes
    elif message.content.startswith(prefix + 'affix'):
        d1 = datetime(2017, 3, 28)
        d2 = datetime.now()
        currentAffix = affixes[floor(((d2 - d1).days / 7) % 12)]
        nextAffix = affixes[floor((((d2 - d1).days / 7) + 1) % 12)]
        output = 'This weeks affixes are: {}, {}, {}\nNext weeks affixes are: {}, {}, {}'.format(currentAffix[0], currentAffix[1], currentAffix[2],nextAffix[0], nextAffix[1], nextAffix[2])
        await client.send_message(message.channel, output)


    # Shows current invasion status, and time until end or next invasion
    elif message.content.startswith(prefix + 'invasion'):
        #start = Mon july 10 2017 @ 6.30pm CST
        start = datetime(2017, 7, 10, 23, 30, 0, 0, timezone.utc)
        # remove the timedelta when DST is over :P
        now = datetime.now(timezone.utc)
        loop = True
        enabled = True
        # Check to see if an invasion is up or not
        while loop:
            if enabled:
                start = start + timedelta(hours=6)
                if now < start: # Exits loop, invasion is happening
                    loop = False
                    nexttime = start - now
                    await client.send_message(message.channel,"There is an invasion active now!\nTime left: " + str(nexttime).split('.',2)[0])
                else:
                    enabled = False
            else:
                start = start + timedelta(hours=12, minutes=30)
                if now < start: # Exits loop, invasion not happening
                    loop = False
                    nexttime = start-now
                    await client.send_message(message.channel,"There is no invasion active.\nTime until next invasion: " + str(nexttime).split('.',2)[0])
                    
                else:
                    enabled = True

# ----------------------------------------------------------------------------------------
## Games section
# ----------------------------------------------------------------------------------------

    # Russian Roulette Game!
    elif message.content.startswith(prefix+'roulette'):
        if (1 in revolver):
            if (revolver[index] == 1):
                await client.send_message(message.channel,'--BANG--')
                #await message.channel.send('*BANG*')
                revolver = [0,0,0,0,0,0]
            else:
                await client.send_message(message.channel,'*Click*')
                #await message.channel.send('*click*')
            index += 1
        else:
            await client.send_message(message.channel,'Time to reload, use !Spin to reload!')
            #await message.channel.send('Time to reload, use !spin to reload')

    # Russian Roulette helper
    elif message.content.startswith(prefix+'spin'):
        revolver = [0,0,0,0,0,0]
        revolver[random.randint(0,5)] = 1
        index = 0
        await client.send_message(message.channel,'Reloaded!')
        #await message.channel.send('Reloaded!')

# ----------------------------------------------------------------------------------------
## Read Dictionary for additional commands
# ----------------------------------------------------------------------------------------

    # Handle all other commands in dictionary list
    elif message.content.startswith(prefix):
        #print(message.content)
        terms = message.content[1:].split()
        command = terms[0].lower()
        msg = d.readDict(command)
        # this should check if the string is empty or not.
        if msg:   
            await client.send_message(message.channel,msg)

#END IF

client.run(tokenObj['token'])

#END FILE

