from ast import Return
from datetime import datetime
import discord
from discord.ext import commands, tasks
import random
import youtube_dl
import asyncio

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents = intents)
bot.remove_command("help")

musics = {}
ytdl = youtube_dl.YoutubeDL()

status = ["!help", "Bot Discord de Nethire", "Développeur LoupBlanc#9056", "https://discord.gg/wFrP8FT9DX"]

@bot.event
async def on_ready():
    print("Bot ready")
    changeStatus.start()

class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download = False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()

@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()

@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []

@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()

def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_deplay_max 5"))
    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_corountine_threadsage(client.disconnect(), bot.loop)

    client.play(source, after=next)

@bot.command()
async def play(ctx, url):
    print("play")
    client = ctx.guild.voice_client
    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance: {video.url}")
        play_song(client, musics[ctx.guild], video)

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
    await ctx.send(f"{member.mention} a été unmute")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="Voici toute les commandes proposer par le bot \n !ban \n !clear \n !help \n !interval \n !kick \n !mute \n !unban \n !unmute")
    embed.set_thumbnail(url="https://tse1.mm.bing.net/th?id=OIP.R5NtROuWMQugf9qYKouA5gHaIU&pid=Api&P=0")
    await ctx.send(embed=embed)

bot.run("MTAwODMzMDg1NTA3ODQ0NTA4Ng.G3oXWO.ka76kAjrUm7k2Q8BfiRivl3Mpzn4qTFOcl4HcE")