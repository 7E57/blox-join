import discord
from discord.ext import commands
import urllib.parse

TOKEN = 'ADD_BOT_TOKEN'
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

def generate_url(game_id, private_code):
    query_params = {'game_id': str(game_id)}
    if private_code:
        query_params['private_code'] = private_code
    query_string = urllib.parse.urlencode(query_params)
    unique_url = f'http://blox-join.x10.mx/redirect.html?{query_string}'
    return unique_url

@bot.command()
async def public(ctx, game_id: int):
    game_url = generate_url(game_id, None)
    ugc_url = "http://blox-join.x10.mx/waiting.html"
    embed = discord.Embed(title="Open Public Roblox Game", description=f"Click the link below to open the public Roblox game:\n[Join Game]({game_url}) | [Available UGCs]({ugc_url})", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def private(ctx, game_id: int, private_code: str):
    game_url = generate_url(game_id, private_code)
    ugc_url = "http://blox-join.x10.mx/waiting.html"
    embed = discord.Embed(title="Open Private Roblox Game", description=f"Click the link below to open the private Roblox game:\n[Join Game]({game_url}) | [Available UGCs]({ugc_url})", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def url(ctx, *, url: str):
    parsed_url = urllib.parse.urlparse(url)
    
    if "roblox.com" not in parsed_url.netloc:
        await ctx.send("Invalid Roblox URL.")
        return
    
    path_parts = parsed_url.path.split("/")
    game_id = path_parts[2]
    query_params = urllib.parse.parse_qs(parsed_url.query)
    private_code = query_params.get("privateServerLinkCode")
    
    if private_code:
        private_code = private_code[0]
    if game_id:
        game_url = generate_url(game_id, private_code)
        ugc_url = "http://blox-join.x10.mx/waiting.html"
        embed = discord.Embed(title="Open Roblox Game from URL", description=f"Click the link below to open the Roblox game from the URL:\n[Join Game]({game_url}) | [Available UGCs]({ugc_url})", color=discord.Color.gold())
        await ctx.send(embed=embed)
    else:
        await ctx.send("Unable to extract game ID and private code from the URL.")

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000  # Convert to milliseconds
    await ctx.send(f"Pong! Latency: {latency:.2f} ms")

bot.run(TOKEN)
