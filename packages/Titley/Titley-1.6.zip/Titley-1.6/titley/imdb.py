from .lib.Bot.bot import Bot

def get_movie_info(imdbid):
    bot = Bot()
    bs4doc = bot.get_parsed_content('http://www.imdb.com/title/{}'.format(imdbid))
    tdele = bs4doc.find('td', id='overview-top')
    name_span = tdele.find('span', class_='itemprop', itemprop='name')
    year_span = tdele.find('span', class_='nobr').find('a')
    return name_span.text.strip(), year_span.text.strip()

