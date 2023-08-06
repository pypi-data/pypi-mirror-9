"""Module to import subtitles from opensubtitles.org"""
from  ..lib.Bot.bot import Bot
import os
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger('titley')

BOT = Bot()
LANGUAGES = ({'afrikaans': {'iso': ' afr', 'iso639': 'af'},
              'albanian': {'iso': 'alb', 'iso639': 'sq'},
              'arabic': {'iso': 'ara', 'iso639': 'ar'},
              'armenian': {'iso': 'arm', 'iso639': 'hy'},
              'basque': {'iso': 'baq', 'iso639': 'eu'},
              'belarusian': {'iso': 'bel', 'iso639': 'be'},
              'bengali': {'iso': 'ben', 'iso639': 'bn'},
              'bosnian': {'iso': 'bos', 'iso639': 'bs'},
              'breton': {'iso': 'bre', 'iso639': 'br'},
              'bulgarian': {'iso': 'bul', 'iso639': 'bg'},
              'burmese': {'iso': 'bur', 'iso639': 'my '},
              'catalan': {'iso': 'cat', 'iso639': 'ca'},
              'chinese (simplified) ': {'iso': 'chi', 'iso639': 'zh'},
              'chinese (traditional)': {'iso': 'zht', 'iso639': 'zt'},
              'chinese bilingual': {'iso': 'zhe', 'iso639': 'ze'},
              'croatian': {'iso': 'hrv', 'iso639': 'hr'},
              'czech': {'iso': 'cze', 'iso639': 'cs'},
              'danish': {'iso': 'dan', 'iso639': 'da'},
              'dutch': {'iso': 'dut', 'iso639': 'nl'},
              'english': {'iso': 'eng', 'iso639': 'en'},
              'esperanto': {'iso': 'epo', 'iso639': 'eo'},
              'estonian': {'iso': 'est', 'iso639': 'et'},
              'finnish': {'iso': 'fin', 'iso639': 'fi'},
              'french': {'iso': 'fre', 'iso639': 'fr'},
              'galician': {'iso': 'glg', 'iso639': 'gl'},
              'georgian': {'iso': 'geo', 'iso639': 'ka'},
              'german': {'iso': 'ger', 'iso639': 'de'},
              'greek': {'iso': 'ell', 'iso639': 'el'},
              'hebrew': {'iso': 'heb', 'iso639': 'he'},
              'hindi': {'iso': 'hin', 'iso639': 'hi'},
              'hungarian': {'iso': 'hun', 'iso639': 'hu'},
              'icelandic': {'iso': 'ice', 'iso639': 'is'},
              'indonesian': {'iso': 'ind', 'iso639': 'id'},
              'italian': {'iso': 'ita', 'iso639': 'it'},
              'japanese': {'iso': 'jpn', 'iso639': 'ja'},
              'kazakh': {'iso': 'kaz', 'iso639': 'kk'},
              'khmer': {'iso': 'khm', 'iso639': 'km'},
              'korean': {'iso': 'kor', 'iso639': 'ko'},
              'latvian': {'iso': 'lav', 'iso639': 'lv'},
              'lithuanian': {'iso': 'lit', 'iso639': 'lt'},
              'luxembourgish': {'iso': 'ltz', 'iso639': 'lb'},
              'macedonian': {'iso': 'mac', 'iso639': 'mk'},
              'malay': {'iso': 'may', 'iso639': 'ms'},
              'malayalam': {'iso': 'mal', 'iso639': 'ml'},
              'manipuri': {'iso': 'mni', 'iso639': 'ma'},
              'mongolian': {'iso': 'mon', 'iso639': 'mn'},
              'montenegrin': {'iso': 'mne', 'iso639': 'me'},
              'norwegian': {'iso': 'nor', 'iso639': 'no'},
              'occitan': {'iso': 'oci', 'iso639': 'oc'},
              'persian': {'iso': 'per', 'iso639': 'fa'},
              'polish': {'iso': 'pol', 'iso639': 'pl'},
              'portuguese': {'iso': 'por', 'iso639': 'pt'},
              'portuguese-br': {'iso': 'pob', 'iso639': 'pb'},
              'romanian': {'iso': 'rum', 'iso639': 'ro'},
              'russian': {'iso': 'rus', 'iso639': 'ru'},
              'serbian': {'iso': 'scc', 'iso639': 'sr'},
              'sinhalese': {'iso': 'sin', 'iso639': 'si'},
              'sl ovenian': {'iso': 'slv', 'iso639': 'sl'},
              'slovak': {'iso': 'slo', 'iso 639': 'sk'},
              'spanish': {'iso': 'spa', 'iso639': 'es'},
              'swahili': {'iso': 'swa', 'iso639': 'sw'},
              'swedish': {'iso': 'swe', 'iso639': 'sv'},
              'syriac': {'iso': 'syr', 'iso639': 'sy'},
              'tagalog': {'iso': 'tgl', 'iso63 9': 'tl'},
              'tamil': {'iso': 'tam', 'iso639': 'ta'},
              'telugu': {'iso': 'tel', 'iso639': 'te'},
              'thai': {'iso': 'tha', 'iso639': 'th'},
              'turkish': {'iso': 'tur', 'iso639': 'tr'},
              'ukrainian': {' iso639': 'uk', 'iso': 'ukr'},
              'urdu': {'iso': 'urd', 'iso639': 'ur'},
              'vietnamese': {'iso': 'vie', 'iso639': 'vi'}})

def _get_download_links(movie_id, language):
    """Get links to to the subtitle files in the language specified by
    'language'
    """
    start_offset = 0
    result_set = set()
    if language in LANGUAGES:
        languageiso = LANGUAGES[language]['iso']
    else:
        raise Exception('Language {} not found'.format(language))
    while True:
        url = ('http://www.opensubtitles.org/en/'
               'search/sublanguageid-{}/imdbid-'
               '{}/offset-{}/xml').format(languageiso, movie_id, start_offset)
        logger.info('Fetching %s', url)
        xml_str = BOT.get(url)
        root = ET.fromstring(xml_str.text)
        results = root.find('search').find('results')
        total_items = results.attrib['itemsfound']
        for rei in results:
            sub_id = rei.find('IDSubtitle')
            if sub_id != None:
                link = sub_id.attrib['LinkDownload']
                start_offset += 1
                result_set.add(link)
        if start_offset >= int(total_items):
            break
    return result_set

def get_subs_for(movie_id, language, destination):
    """Fetches the zip files that contains the subtitles for 'movie_id' and
       langague from the site and put them in separate folders under
       'destination' folder"""
    links = _get_download_links(movie_id, language)
    count = 0
    if not os.path.isdir(destination):
        os.mkdir(destination)
    logger.info('Downloading %s subtitles', len(links))
    for link in links:
        count += 1
        full_path = os.path.join(destination, str(count))
        link = link.replace('/subad/', '/sub/')
        logger.info("Getting subs from %s", link)
        if not os.path.isdir(full_path):
            os.mkdir(full_path)
        BOT.download_file(link, os.path.join(full_path, 'sub.zip'))
