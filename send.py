from discord.utils import get

from bot import bot


# --------------------------------------------------------------------------- #

@bot.command()
async def send(ctx):
    guild = bot.guilds[0]
    member = get(guild.members, name=ctx.author.name)
    if not member or not member.guild_permissions.administrator:
        # You are not an admin of given guild
        text = '> `!send` - Access denied'
        await member.send(text)
        return

    aux = ctx.message.content.split(maxsplit=3)
    if len(aux) != 4:
        # Command usage
        text = '> `!send` - Send bot text message to member or channel\n' \
                '> • Usage: `!send member <member> <text>`' \
                '> • Usage: `!send channel <channel> <text>`'
        await ctx.author.send(text)
        return

    type, name, text = aux[1:4]
    if type == 'member':
        # Send bot message to member
        member = get(guild.members, name=name)
        if not member:
            text = '> `!send` - Member not found :('
            await ctx.author.send(text)
            return
        await member.send(text)

    elif type == 'channel':
        # Send bot message to channel
        channel = get(guild.channels, name=name)
        if not channel:
            text = '> `!send` - Channel not found :('
            await ctx.author.send(text)
            return
        await channel.send(text)