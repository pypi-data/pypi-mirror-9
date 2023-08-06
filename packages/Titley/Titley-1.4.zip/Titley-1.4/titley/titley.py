"A Script to download subtitles"
import logging
import sys
import argparse
import titley.sources.opensubtitles as opensub
from titley import report
from titley import imdb
from titley import omdb
from titley import unpacker

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('titley')

def main():
    try:
        _main()
    except Exception as exep:
        LOGGER.error(str(exep))
        
def _main():
    """Main entry point when invoked from command line"""
    LOGGER.setLevel(logging.INFO)
    arguments = _get_arguments_parser().parse_args()
    if not _validate_arguments(arguments):
        print('Invalid or missing arugments. Use -h for help')
        return None
    if arguments.source:
        source = arguments.source
    else:
        source = _download_subtitles(arguments)
    _print_report(*_get_report_from_directory(source))

def _download_subtitles(arguments):
    #get normalized 'movie_info' from arguments
    def _nst_get_movie_info(arguments):
        language = arguments.language if arguments.language != None else 'english'
        if arguments.imdb:
            imdbid = arguments.imdb
            movie_info = (imdbid,) +  _get_movie_info(imdbid) + (language,)
        elif arguments.name:
            movie_info = _resolve_movie(arguments.name) + (language,)
        return movie_info
    #make _make_dir_name` function to propogate
    #imdbid
    def _nst_make_dir_name(imdbid, name, year, language):
        return language, imdbid, _make_dir_name(imdbid, name, year)
    #use movie_info to do everything
    return _get_subs_for(
                *_nst_make_dir_name(
                    *_log_movie_info(
                        *_nst_get_movie_info(arguments))))

def _get_arguments_parser():
    parser = argparse.ArgumentParser(description="""Subtitle downloader and
                                                analyzer""")
    parser.add_argument('--name',
                        help="""Title of the movie or part of it
                                for searching in Open Media Database.
                                You'll be prompted to select the exact 
                                movie from the result.""")
    parser.add_argument('--imdb',
                        help="""IMDB code of the movie.
                                Either this argument or the 
                                source directory argument 
                                is required.""")
    parser.add_argument('--language',
                        help="""Language for search.
                                Optional. Defaults to English.""")
    parser.add_argument('--source',
                        help="""Source directory to read
                                the subtitle archives from,'
                                if you have manually downloaded the'
                                subtitles as zip files.""")
    return parser

def _log_movie_info(imdbid, name, year, language):
    LOGGER.info("Downloading %s subtitles for movie '%s'(%s), IMDB:%s",
                language, name, year, imdbid)
    return imdbid, name, year, language

def _validate_arguments(arguments):
    return arguments.imdb or arguments.name or arguments.source

def _make_dir_name(imdbid, name = None, year = None):
    if name is None:
        destination = imdbid
    else:
        destination = '{}({})'.format(name, year)
        destination = report.compact(destination)
    return destination

def _resolve_movie(name):
    search_result = omdb.search_movie_name(name)
    if search_result is None:
        raise Exception("No movies matching the name '%s' found", name)
    else:
        print('')
        print(("""The following movies were found"""
        """ matching your search key '{}'""").format(name))
        selected_movie = _get_selection_from_user(search_result)
        name, year, imdbid = selected_movie
        return imdbid, name, year

def _get_movie_info(imdbid):
    try:
        LOGGER.info("Geting movie info from OMDB")
        return omdb.get_movie_info(imdbid)
    except Exception:
        LOGGER.error("Failed getting movie info from OMDB")
        try:
            LOGGER.info("Geting movie info from IMDB")
            return imdb.get_movie_info(imdbid)
        except Exception:
            raise Exception("Failed getting movie info from IMDB")

def _get_selection_from_user(search_result):
    result_len = len(search_result)
    print('')
    for index, movie in enumerate(search_result):
        print("{}) {} ({}), IMDB: {} ".format(index + 1, movie[0],
                                              movie[1], movie[2]))
    print('')
    inp = (input(('Select the correct one. '
                  ' Enter a number between 1 and {}.'
                  ' Enter "x" to exit\n').format(result_len)))
    if inp == 'x':
        raise SystemExit
    selection = int(inp)
    if selection > result_len:
        print('You entered an invalid value, please try again')
        return _get_selection_from_user(search_result)
    return search_result[selection - 1]

def _get_subs_for(language, imdbid, destination):
    """Get subs for an imdbid/language pair and save it in a folder with the
    movie name
    """
    try:
        opensub.get_subs_for(imdbid, language, destination)
    except Exception as exep:
        LOGGER.error(exep)
        raise Exception("""No subtitles found or error retriving subtitles """
                        """opensubtitles.""")
    return destination

def _get_report_from_directory(source):
    """Generate report from the zip files that are present in the specified
    folder
    """
    try:
        unpacker.extract_all_archives_in(source)
        return report.generate_report(source)
    except Exception as exep:
        LOGGER.error(exep)
        raise Exception('Error while generating report.')

def _print_report(candidate_text, times):
    """Prints the final report"""
    print('====================')
    print("")
    print(("{} Subtitles found/retrived. You can use the following dialogue"
           " and the time it appears to find"
           " the matching subtitle.").format(len(times)))
    print('-------------------')
    print("")
    print('"{}"'.format(candidate_text.replace('\n', '')))
    print("")
    for k, loopv in times.items():
        print('{} | {}'.format(loopv, k))
    print('-------------------')
