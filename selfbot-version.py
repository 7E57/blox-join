import selfcord
import urllib.parse
import requests
import demoji

TOKEN = 'USER TOKEN'
ROBLOSECURITY_COOKIE = 'ROBLOX COOKIE'

bot = selfcord.Bot()

def generate_url(game_id, private_code):
    query_params = {'game_id': str(game_id)}
    if private_code:
        query_params['private_code'] = private_code
    query_string = urllib.parse.urlencode(query_params)
    unique_url = f'http://blox-join.x10.mx/redirect.html?{query_string}'

    return unique_url

def remove_emojis(text):
    return demoji.replace(text, '')

def get_game_info(game_id, ROBLOSECURITY_COOKIE, info_type):
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

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                game_data = data[0]
                if info_type == 'name':
                    return remove_emojis(game_data.get('name'))
                elif info_type == 'builder':
                    return remove_emojis(game_data.get('builder'))
                elif info_type == 'builderId':
                    return game_data.get('builderId')
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None

def get_owner_info(game_id, ROBLOSECURITY_COOKIE, info_type):
    if game_id is None:
        return None

    headers = {
        'Cookie': f'.ROBLOSECURITY={ROBLOSECURITY_COOKIE}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    builderId = get_game_info(game_id, ROBLOSECURITY_COOKIE, 'builderId')

    group_url = f'https://groups.roblox.com/v1/groups/{builderId}'
    try:
        response = requests.get(group_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict):
                game_data = data.get('owner')
                if info_type == 'displayName':
                    return game_data.get('displayName')
                elif info_type == 'userId':
                    return game_data.get('userId')
    except Exception as e:
        print(f"An error occurred while checking the group: {str(e)}")

    user_url = f'https://www.roblox.com/users/{builderId}'
    try:
        response = requests.get(user_url, headers=headers)
        if response.status_code == 200:
            if info_type == 'displayName':
                return None
            elif info_type == 'userId':
                return builderId
    except Exception as e:
        print(f"An error occurred while checking the user: {str(e)}")

    return None

@bot.on("ready")
async def ready(time):
    print(f"Connected To {bot.user.name}\n Startup took {time:0.2f} seconds")

@bot.on("message")
async def responder(message):
    if any(url.startswith(("http://", "https://")) and "roblox.com/games/" in url for url in message.content.split()):
        urls = extract_urls(message.content)
        for url in urls:
            parsed_url = urllib.parse.urlparse(url)
            game_id, private_code = extract_game_id_and_private_code(parsed_url)
            if game_id is not None:
                game_url = generate_url(game_id, private_code)
                name = get_game_info(game_id, ROBLOSECURITY_COOKIE, 'name')
                builder = get_game_info(game_id, ROBLOSECURITY_COOKIE, 'builder')
                builderId = get_game_info(game_id, ROBLOSECURITY_COOKIE, 'builderId')
                ownerName = get_owner_info(game_id, ROBLOSECURITY_COOKIE, 'displayName')
                owner = get_owner_info(game_id, ROBLOSECURITY_COOKIE, 'userId')
                if game_url:
                    if ownerName is None:
                        owner_url = f"https://www.roblox.com/users/{builderId}"
                        await message.channel.send(
                            f"**GRABBED INFORMATION:**\n> Game: [{name}]({game_url})\n> Owner: [{builder}]({owner_url})"
                        )
                    else:
                        await message.channel.send(
                            f"**GRABBED INFORMATION:**\n> Game: [{name}]({game_url})\n> Group: [{builder}](https://www.roblox.com/groups/{builderId})\n> Owner: [{ownerName}](https://www.roblox.com/users/{owner})"
                        )
                else:
                    await message.channel.send(f"**GRABBED INFORMATION:**\n> Game: {game_url}")
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
