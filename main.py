import io
import os
import re
import math
import asyncio
import logging
from dotenv import load_dotenv

import discord
from discord.utils import get
from discord.ext import commands

from bot import bot

# Get Discord token securely from environment variable
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Allow logging info
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------------------------------- #

# Get levels and answers for required level
f = open('levels.txt','r')
level_names = []
level_answer = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split(' ')
    level_names.append(data[0])
    level_answer.append(data[1])
f.close()

# Get levels and answers for secret level
f = open('secrets.txt','r')
secret_names = []
secret_entrance = []
secret_answers = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split(' ')
    secret_names.append(data[0])
    secret_entrance.append(data[1])
    secret_answers.append(data[2])
f.close()

# Get levels and answers for secret level
f = open('milestones.txt','r')
mile_index = []
mile_name = []
mile_channel = []
while True:
    line = f.readline().rstrip('\n')
    if not line:
        break
    data = line.split('|')
    mile_index.append(data[0])
    mile_name.append(data[1])
    mile_channel.append(data[2])
f.close()

# --------------------------------------------------------------------------- #

@bot.event
async def on_ready():
    print('Bot up and running!')
    global guild
    guild = discord.utils.get(bot.guilds, name='RNS Riddle') #Remember this one, always, and please change the value to the server you own.
    
# --------------------------------------------------------------------------- #

# Level - the current level that is being solved
# Level Names - list of level names on levels.txt
# Level Answer - list of level answers on levels.txt
# Answer - the answer for passing the level 

@bot.command( \
        name='solve', \
        help='Unlock channels and roles for main levels. \n\n\
            <level>: The level that you are trying to solve. \n\
            <answer>: The answer for the level, without the .htm or any other extension.'
    )
async def solve(ctx,level=None,answer=None): # syntax is !solve <level> <answer>

    if level == None or answer == None:
        await ctx.author.send("> For this command's information, please use `!help solve`.")
        return

     # Delete message of this command from other channels 
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = '> `!solve` must be sent by PM to **me**!'
        await author.send(text)
        return

    # If the user uses a wrong level
    if not (level in level_names):
        await ctx.send('> The level does not exist! Please use a valid level name')
        return    

    current_level = '01'
    member = discord.utils.get(guild.members, name=ctx.author.name)
    role = discord.utils.get(member.roles, name='reached-' + level)

    for role in member.roles:
        if role.name == 'rns-prodigies': # change the role.name value to your liking
            current_level = 'rns-prodigies' # change the role.name value to your liking
            break
        elif 'reached-' in role.name:
            current_level = role.name.strip('reached-') # the level number after 'reached-'
            break

    # checking conditions for the right answer
    if level_names.index(level) < level_names.index(current_level):
        await ctx.send('> You already solved this level!')
        return
    elif level_answer[level_names.index(level)] != answer:
        await ctx.send('> Your answer is wrong!')
        return
    elif level_answer[level_names.index(level)] == answer:
        # Remove current role 
        for role in member.roles:
            if 'reached-' in role.name:
                old_level = role.name.strip('reached-')
                if old_level in level_names:
                    await member.remove_roles(role)
                    break
        
        # Add new role
        new_level = None
        if level_names.index(level) + 1 == len(level_names):
            new_level = 'rns-prodigies'
        else:
            new_level = level_names[level_names.index(level) + 1]
        new_role = discord.utils.get(guild.roles, name='reached-' + new_level)
        await member.add_roles(new_role)

        # Change nicknames
        if level in level_names:
            if new_level == 'rns-prodigies': # change the new_level value to your liking
                s = '🏅'
            elif new_level.find('minus') != -1:
                s = new_level.replace('minus','')
                s = '[' + s + ']'
            elif new_level.find('false-') != -1:
                s = new_level.replace('false-','False ')
                s = '[' + s + ']'
            elif new_level.find('true-0') != -1 :
                s = new_level.replace('true-0','True 0')
                s = '[' + s + ']'
            elif new_level.find('true') != -1 :
                s = new_level.replace('true','True ')
                s = '[' + s + ']'
            elif new_level.find('null') != -1:
                s = new_level.replace('null','∅')
                s = '[' + s + ']'
            elif new_level.find('right-') != -1 :
                s = new_level.replace('right-','Right ')
                s = '[' + s + ']'
            else:
                s = '[' + new_level + ']'
        name = member.name
        total = len(name) + 1 + len(s)
        if total > 32:
            excess = total - 32
            name = name[:-(excess + 5)] + '(...)'
        nick = name + ' ' + s
        await member.edit(nick=nick)

        # Milestone Roles 
        mile_role = None

        # Normal level clear
        for x in mile_index:
            if level_names.index(new_level) >= mile_index[x] or new_level == 'rns-prodigies': # change the new_level value to your liking
                mile_role = discord.utils.get(guild.roles, name=mile_name[mile_index.index(x)])
                if not mile_role in member.roles:
                    await member.add_roles(mile_role)
                    channel = get(guild.channels, name=mile_channel[mile_index.index(x)])
                    text = '> <@!' + str(member.id) + '> has completed level **' + mile_channel[mile_index.index(x)] + '** and is now part of **' + mile_name[mile_index.index(x)] + '**. Congratulations!'
                    await channel.send(text)

        # Send confirmation message
        print('Member ' + member.name +  ' solved channel #'  + level)
        text = '> You successfuly solved channel #**' + level + '**!'
        if level in level_names:
            text += '\n> Your nickname is now **' + member.nick + '**'
        else:
            text += '\n> Your nickname is unchanged'
        if new_level == 'rns-prodigies':
            text += '\n Congratulations! You beat the game!'
        await ctx.author.send(text)
        return

# --------------------------------------------------------------------------- #

# Secret Level - the current secret level that is being found
# Entrance - the entrance of the secret level
# Secret Names - list of level names on levels.txt
# Secret Entrance - list of secret level entrances on secrets.txt
# Answer - the answer for passing the level 

@bot.command( \
        name='found', \
        help='Unlock channels and \'found\' roles for secret levels. \n\n\
            <secret_level>: The secret level that you are trying to unlock. \n\
            <entrance>: The answer you put before seeing the secret level, without the .htm or any other extension. In the case of username and password, format is <username>/<password>'
    )
async def found(ctx,secret_level=None,entrance=None): # syntax is !found <secret_level> <entrance>
    if secret_level == None or entrance == None:
        await ctx.author.send("> For this command's information, please use `!help found`.")
        return

     # Delete message of this command from other channels 
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = '> `!found` must be sent by PM to **me**!'
        await author.send(text)
        return

    if not (secret_level in secret_names):
        await ctx.send('> The secret level does not exist! Please use a valid secret level name!')
        return

    member = discord.utils.get(guild.members, name=ctx.author.name)
    found_role = discord.utils.get(member.roles, name='found-' + secret_level)
    solved_role = discord.utils.get(member.roles, name='solved-' + secret_level)

    for found_role in member.roles:
        if found_role.name == 'found-' + secret_level:
            await ctx.send('> You already found this secret level.')
            return
    
    for solved_role in member.roles:
        if solved_role.name == 'solved-' + secret_level:
            await ctx.send('> You already solved this secret level.')
            return

    if secret_entrance[secret_names.index(secret_level)] != entrance:
        await ctx.send('> Wrong entrance. Try again!')
        return

    if secret_entrance[secret_names.index(secret_level)] == entrance:
        new_secret_role = discord.utils.get(guild.roles, name='found-' + secret_level)
        await member.add_roles(new_secret_role)
        await ctx.send('> You found secret level **' + secret_level + '**!')
        return

# --------------------------------------------------------------------------- #

@bot.command( \
        name='secret', \
        help='Solve a secret level that you already found. \n\n\
            <secret_level>: The secret level that you are trying to unlock. \n\
            <secret_answer>: The answer you put, without the .htm or any other extension. In the case of username and password, format is <username>/<password>'
    )
async def found(ctx,secret_level=None,secret_answer=None): # syntax is !secret <secret_level> <secret_answer>
    if secret_level == None or secret_answer == None:
        await ctx.author.send("> For this command's information, please use `!help secret`.")
        return

    # Delete message of this command from other channels 
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = '> `!secret` must be sent by PM to **me**!'
        await author.send(text)
        return

    if not (secret_level in secret_names):
        await ctx.send('> The secret level does not exist! Please use a valid secret level name!')
        return
    
    member = discord.utils.get(guild.members, name=ctx.author.name)
    found_role = discord.utils.get(member.roles, name='found-' + secret_level)
    solved_role = discord.utils.get(member.roles, name='solved-' + secret_level)

    # If the level hasn't been found yet
    if not found_role in member.roles:
        await ctx.send('> You haven\'t found this level yet!')
        return

    # if the level has been solved already
    for solved_role in member.roles:
        if solved_role.name == 'solved-' + secret_level:
            await ctx.send('> You already solved this secret level.')
            return
    
    # If the arguments are valid, for both wrong and right answers.
    for found_role in member.roles:
        if (found_role.name == 'found-' + secret_level) and (secret_answers[secret_names.index(secret_level)] != secret_answer):
            await ctx.send('> Wrong answer for this secret. Try again!')
            return
        elif (found_role.name == 'found-' + secret_level) and (secret_answers[secret_names.index(secret_level)] == secret_answer):
            # Add solved role
            new_secret_role = discord.utils.get(guild.roles, name='solved-' + secret_level)
            await member.add_roles(new_secret_role)
            await ctx.send('> You completed secret level **' + secret_level + '**! Congratulations!')

            # Delete found role
            remove_role = get(guild.roles, name='found-' + secret_level)
            await member.remove_roles(remove_role)
            
            # Send a message to a specific channel
            channel = get(guild.channels, name=secret_level)
            text = '> <@!' + str(member.id) + '> has completed secret level **' + secret_level + '**. Congratulations!'
            await channel.send(text)
            return

# --------------------------------------------------------------------------- #

@bot.command( \
        name='id', \
        help='List the valid level IDs available in the game per category, for solve and secret commands use. \n\n\
            <category>: The secret level that you are trying to unlock. \n\
            Valid values: normal, secret' #night: night-side-a, night-side-b
    )
async def found(ctx,category=None): # syntax is !id <level>
    # Help
    if category == None:
        await ctx.author.send("> For this command's information, please use `!help id`.")
        return

    # Delete message of this command from other channels 
    if ctx.guild and not ctx.message.author.guild_permissions.administrator:
        author = ctx.message.author
        await ctx.message.delete()
        text = '> `!id` must be sent by PM to **me**!'
        await author.send(text)
        return

    # Conditional values for each valid values
    category = category.strip().lower()
    text = None

    # RNS Specific, might get changed soon. It lists the valid IDs for solve, found, and secret use.
    if category == 'normal':
        text = '> IDs: **' + ' '.join(level_names[0:20]) + '**'
    else:
        text = '> Category not valid. Please use `!help id` for information.'
    await ctx.author.send(text)
    return

# --------------------------------------------------------------------------- #

# @bot.command()
# async def ping(ctx):
#     # Ping-pong
#     await ctx.send('pong')

# --------------------------------------------------------------------------- #

# @bot.command()
# async def padoru(ctx):
#     # Hashire sori yo 
#     # Kaze no you ni
#     # Tsukimihara wo
#     # Padoru Padoru
#     await ctx.send('https://rnsriddle.com/extras/padoru.gif')

# --------------------------------------------------------------------------- #

bot.run(token)