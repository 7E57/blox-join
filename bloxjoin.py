import discord
from discord.ext import commands
import urllib.parse
import requests

TOKEN = 'BOT TOKEN'
ROBLOSECURITY_COOKIE = 'ROBLOX COOKIE'
GUILD_ID = 'DISCORD SERVER'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)

def generate_url(game_id, private_code):
    query_params = {'game_id': str(game_id)}
    if private_code:
        query_params['private_code'] = private_code
    query_string = urllib.parse.urlencode(query_params)
    unique_url = f'http://blox-join.x10.mx/redirect.html?{query_string}'
    return unique_url

def get_game_name(game_id):
    if game_id is None:
        return None

    headers = {
        'Cookie': f'.ROBLOSECURITY={ROBLOSECURITY_COOKIE}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    params = {
        'placeIds': game_id
    }

    url = 'https://games.roblox.com/v1/games/multiget-place-details'

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            game_name = data[0].get('name')
            return game_name

    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(url.startswith(("http://", "https://")) and "roblox.com/games/" in url for url in message.content.split()):
        urls = extract_urls(message.content)
        for url in urls:
            parsed_url = urllib.parse.urlparse(url)
            game_id, private_code = extract_game_id_and_private_code(parsed_url)
            if game_id is not None:
                game_url = generate_url(game_id, private_code)
                ugc_url = "http://blox-join.x10.mx/waiting.html"
                git_url = "https://github.com/7E57/blox-join/blob/main/bloxjoin.py"
                embed = discord.Embed(title="Open Roblox Game from URL", description=f"Click the link below to open the Roblox game from the URL:\n[Join Game]({game_url}) | [Available UGCs]({ugc_url}) | [GitHub]({git_url})", color=discord.Color.gold())
                await message.channel.send(embed=embed)

                game_name = get_game_name(game_id)
                if game_name:
                    await bot.change_presence(activity=discord.Game(name=game_name))
                else:
                    await bot.change_presence(activity=None)
            else:
                await message.channel.send("Unable to extract game ID and private code from the URL.")
    
    return

def extract_urls(text):
    return [word for word in text.split() if word.startswith(("http://", "https://"))]

def extract_game_id_and_private_code(url):
    path_parts = url.path.split("/")
    query_params = urllib.parse.parse_qs(url.query)
    game_id = None
    private_code = None

    if path_parts and "roblox.com" in url.netloc and "games" in path_parts:
        for part in path_parts:
            if part.isdigit():
                game_id = int(part)
                break

    if "privateServerLinkCode" in query_params:
        private_code = query_params["privateServerLinkCode"][0]

    return game_id, private_code

bot.run(TOKEN)
