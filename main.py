import discord # regular discord import needed for bot
from discord.ext import commands # discord commands
import logging # allows logging to the discord.log
from dotenv import load_dotenv # allows script to grab data from .env file
import os # allows script to read data from origin file path
import asyncio # allows the bot to wait a certain amount of time
import json # allows you to read and write to json files
import requests # allows you to send requests to links to receive data
from medal_api import MedalAPI # medal API functions grabbed from other repository since they're smarter than me :(
from discord.ext import commands, tasks # command that allows looping every set amount of time within the bot
from datetime import datetime # allows getting the date
import aiohttp # better http requests for api

# loads the .env file
load_dotenv()

# grabs discord bot token from .env file
token = os.getenv('DISCORD_TOKEN')

# set file for log messages
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# declaring of intents such as the discord default, ability to read message content (i think), and ability to see members
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# sets the bot command prefix and sets the intents
bot = commands.Bot(command_prefix='g!', intents=intents)

# set up riot API key so it can be called for league data
riot_api_key = os.getenv('RIOT_API_KEY')

# bot booting up event
@bot.event
async def on_ready():

    '''
    # if data.json file doesn't exist, create one with all the required data storage outline
    if not os.path.exists('data.json'):
        data = {
            "registered_league_users": {},
            "settings": {}
        }
        
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)
    '''
    
    # changes the bot status message to be a custom message
    await bot.change_presence(activity=discord.CustomActivity(name="wait, im coded ( ͡° ͜ʖ ͡°)"))
    
    # once all done, bot says it's ready
    print(f"{bot.user.name}, is ready to be a chud")


# logs with bot has any changes with Discord's web socket
@bot.event
async def on_disconnect():
    print(f"[{datetime.now()}] Bot disconnected from Discord")

@bot.event
async def on_resumed():
    print(f"[{datetime.now()}] Bot reconnected to Discord")

@bot.event
async def on_connect():
    print(f"[{datetime.now()}] Bot connected to Discord")

'''
# on member join, make the bot do something
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server chud, {member.name}")
'''

# on message sent to a channel the bot is apart of
@bot.event
async def on_message(message):
    '''
    # makes sure that the bot doesn't recursively send messages if it sees a message sent by itself
    if message.author == bot.user:
        return

    # grabs the specific text channel from the message sent
    channel = message.channel

    # set up for my message to myself :3
    message_to_me_one = "I'll... I'll spread the word"
    message_to_me_two = f"HOP ONNNNNN <@{my_user_id}>!!!!!!"
    
    # checks for if someone says something along the lines of "play league" or "hop on league" to @ me :3
    if ("play" in message.content.lower() or "hop on" in message.content.lower() or "hoppin" in message.content.lower()) and "league" in message.content.lower() and message.author.id != my_user_id:
        await channel.send(f"DID SOMEBODY SAY LEAGUE???")
        await asyncio.sleep(0.5)
        await channel.send(message_to_me_one)
        await asyncio.sleep(0.5)
        await channel.send(message_to_me_two)

    # checks for if someone says something along the lines of "play roblox" or "hop on roblox" to @ me :3
    if ("play" in message.content.lower() or "hop on" in message.content.lower() or "hoppin" in message.content.lower()) and "roblox" in message.content.lower() and message.author.id != my_user_id:
        await channel.send(f"DID SOMEBODY SAY BOBLOX???")
        await asyncio.sleep(0.5)
        await channel.send(message_to_me_one)
        await asyncio.sleep(0.5)
        await channel.send(message_to_me_two)
    '''

    # always needed for on_message
    await bot.process_commands(message)


# regular ping command just to test bot
@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def registerLeague(ctx, *, riotName):
    channel = ctx.channel

    poundIndex = riotName.find("#")

    if poundIndex == -1 or poundIndex == len(riotName) - 1:
        await channel.send("Not a valid name, try again")
        return

    name = riotName[0:poundIndex]
    tagLine = riotName[poundIndex + 1:len(riotName)]

    response = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tagLine}?api_key={riot_api_key}")
    
    responseCode = response.status_code

    responseData = response.json()

    if responseCode != 200:
        await channel.send("Invalid Riot name twin")

    await channel.send(responseData)


# -- Helper Functions --

# checks if the guild is None, meaning the command was not sent in server. Sends True if so
async def notInServer(ctx):
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server")
        return True
    return False


# registers the channel to the specific channel type located in data.json. Should be pretty self explanatory from 
# everything already made within here
async def registerChannel(ctx, channelType):
    with open('data.json', 'r') as f:
        data = json.load(f)

    serverId = str(ctx.guild.id)
    channelId = str(ctx.channel.id)

    if serverId not in data[channelType]:
        data[channelType][serverId] = []

    if channelId in data[channelType][serverId]:
        await ctx.send(f"Channel has already been registered")
        return

    data[channelType][serverId].append(channelId)

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# unregisters channel from channel type in data.json
async def unregisterChannel(ctx, channelType):
    with open('data.json', 'r') as f:
        data = json.load(f)

    serverId = str(ctx.guild.id)
    channelId = str(ctx.channel.id)

    if serverId not in data[channelType]:
        await ctx.send("This channel has not been registered")
        return
    elif channelId not in data[channelType][serverId]:
        await ctx.send("This channel has not been registered")
        return
    
    data[channelType][serverId].remove(channelId)

    if data[channelType][serverId] == []:
        del data[channelType][serverId]

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)


'''
@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("You have the secret role woahg")
    
    return

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have permission for dat twin")
    
    return


@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"you wanted me to send you: {msg}")




@bot.command()
async def reply(ctx):
    await ctx.reply("this is a reply twin")




@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("❤️")
    await poll_message.add_reaction("🧡")
    await poll_message.add_reaction("💚")
    await poll_message.add_reaction("💙")


@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name="whatevarole")
    if role:
      await ctx.author.add_roles(role)
      await ctx.send(f"{ctx.author.mention} is now assigned to whatevarole")
    else:
      await ctx.send("Role doesn't exist")
    
    return

@bot.command()
async def unassign(ctx):
    role = discord.utils.get(ctx.guild.roles, name="whatevarole")
    if role:
      await ctx.author.remove_roles(role)
      await ctx.send(f"Removed whatevarole from {ctx.author.mention}")
    else:
      await ctx.send("Role doesn't exist")
    
    return
'''


# needed at the end of main.py for bot to run
bot.run(token, log_handler=handler, log_level=logging.DEBUG)