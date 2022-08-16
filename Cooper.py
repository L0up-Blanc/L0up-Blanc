from ast import Return
from datetime import datetime
import discord
from discord.ext import commands, tasks
import random

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents = intents)

status = ["!help", "Bot Discord de Nethire", "Développeur LoupBlanc#9056", "https://discord.gg/wFrP8FT9DX"]

@bot.event
async def on_ready():
    print("Bot ready")
    changeStatus.start()

@bot.command()
async def interval(ctx, secondes = 5):
    changeStatus.change_interval(seconds = secondes)
#    changeStatus.restart()
#    changeStatus.stop()
#    changeStatus.cancel()
#    changeStatus.is_running()

@tasks.loop(seconds = 5)
async def changeStatus():
    game = discord.Game(random.choice(status))
    await bot.change_presence(status = discord.Status.dnd, activity = game)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="Arrivant", description=f"Bienvenu(e) {member.mention} sur Nethire. Nous sommes maintenant {member.guild.member_count}")
    embed.set_thumbnail(url="https://tse4.mm.bing.net/th?id=OIP.GfVALvGzUzfRCGI5nkEuFgHaDt&pid=Api&P=0")
    welcome_channel = discord.utils.get(member.guild.channels, name="aéroport")
    await welcome_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(title="Départ", description=f"Aurevoir {member.mention} au plaisir de vous revoir. Nous sommes désormais {member.guild.member_count}")
    embed.set_thumbnail(url="https://tse3.mm.bing.net/th?id=OIP.0IjskOaXShC2fUe-nLQb0gHaEn&pid=Api&P=0")
    welcome_channel = discord.utils.get(member.guild.channels, name="aéroport")
    await welcome_channel.send(embed=embed) 


@bot.event
async def on_message(message):
    logs_channel = discord.utils.get(message.guild.channels, name="logs")
    if message.author == bot.user:
        return
    await logs_channel.send(f"**{message.author}** à écrit \n > {message.content}")
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    logs_channel = discord.utils.get(message.guild.channels, name="logs")
    await logs_channel.send(f"**Le message de {message.author} a été supprimé** \n> {message.content}")

@bot.event
async def on_message_edit(before, after):
    logs_channel = discord.utils.get(before.guild.channels, name="logs")
    await logs_channel.send(f"**{before.author} a édité son message :**\n **Avant ->** {before.content}\n **Après ->** {after.content}")

@bot.event 
async def on_typing(channel, user, when):
    logs_channel = discord.utils.get(channel.guild.channels, name="logs")
    await logs_channel.send(f"{user.name} a commencé à écrire dans un channel le {when} + 2 heures")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user : discord.User, *, reason = "Aucune raison n'a été donné"):
    await ctx.guild.ban(user, reason = reason)
    embed = discord.Embed(title = "**Banissement**", description = "Un modérateur a frappé !", url = "https://discord.gg/Pkh7DQ2QAa", color=0xfa8072)
    embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url, url = "https://discord.gg/Pkh7DQ2QAa")
    embed.set_thumbnail(url = "https://discordemoji.com/assets/emoji/BanneHammer.png")
    embed.add_field(name = "Membre banni", value = user, inline = True)
    embed.add_field(name = "Raison", value = reason, inline = True)
    embed.add_field(name = "Modérateur", value = ctx.author.name, inline = True)
    logs_channel = discord.utils.get(ctx.guild.channels, name="logs")
    await logs_channel.send(embed = embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.User, *, reason = "Aucune raison n'a été donné"):
    await ctx.guild.kick(user, reason=reason)
    embed = discord.Embed(title = "**Kick**", descritpion = "Un modérateur à kick un membre", url="https://discord.gg/Pkh7DQ2QAa", color=0xfa8072)
    embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url, url = "https://discord.gg/Pkh7DQ2QAa")
    embed.set_thumbnail(url="https://tse2.mm.bing.net/th?id=OIP.hCyUInibYwIvRTvh1xLUfgHaDK&pid=Api&P=0")
    embed.add_field(name = "Membre kick", value = user, inline = True)
    embed.add_field(name = "Raison", value = reason, inline = True)
    embed.add_field(name = "Modérateur", value = ctx.author.name, inline = True)
    logs_channel = discord.utils.get(ctx.guild.channels, name="logs")
    await logs_channel.send(embed = embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    messages = await ctx.channel.history(limit=nombre + 1).flatten()
    for message in messages:
        await message.delete()

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user, *reason):
    reason = " ".join(reason)
    userName, userId = user.split("#")
    bannedUsers = await ctx.guild.bans()
    for i in bannedUsers:
        if i.user.name == userName and i.user.discriminator == userId:
            await ctx.guild.unban(i.user, reason=reason)
            await ctx.send(f"{user} à été unban.")
            return
    logs_channel = discord.utils.get(ctx.guild.channels, name="logs")
    await logs_channel.send(f"L'utilisateur {user} n'est pas dans la liste des bans")

async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name = "Muted", permissions = discord.Permissions(send_messages = False, speak = False), reason = "Crétation du role Muted pour mute des gens")
    for channel in ctx.guild.Channels:
        await channel.set_permissions(mutedRole, send_messages = False, speak = False)
    return mutedRole
async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Muted":
            return role
    return await createMutedRole(ctx)
@bot.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member : discord.Member, *, reason = "Aucune raison n'a été renseigné"):
    mutedRole = await getMutedRole(ctx)
    await member.add_roles(mutedRole, reason = reason)
    await ctx.send(f"{member.mention} a été mute")

@bot.command()
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member : discord.Member, *, reason = "Aucune raison n'a été renseigné"):
    mutedRole = await getMutedRole(ctx)
    await member.remove_roles(mutedRole, reason = reason)

bot.run("MTAwODMzMDg1NTA3ODQ0NTA4Ng.G3oXWO.ka76kAjrUm7k2Q8BfiRivl3Mpzn4qTFOcl4HcE")