from .lib.Bot.bot import Bot
import json

def safe_enc(inp):
    """Limit the output to ascii to prevent
       encoding errors when output to console"""
    return inp.encode('ascii', errors='ignore').decode('ascii')

def search_movie_name(title):
    """Search omdb for a name or part of it"""
    bot = Bot()
    response = json.loads(bot.get('http://www.omdbapi.com', params={'s':title, 'r':'json'}).text)
    if 'Error' not in response:
        return [tuple(map(safe_enc, (r['Title'], r['Year'], r['imdbID']))) for r in response['Search']]
    else:
        return None

def get_movie_info(imdbid):
    """Find movie info for an imdbid"""
    bot = Bot()
    response = json.loads(bot.get('http://www.omdbapi.com', params={'i':imdbid, 'r':'json'}).text)
    if 'Error' not in response:
        return response['Title'], response['Year']
    else:
        raise Exception('Movie not found')


