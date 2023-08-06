===============================================
Titley - A python script to download subtitles.
===============================================

The problem -
=============

You download a foreign language movie. You look for a subtitle in one of the subtitle sites. But you can't find the subtitle with exact name of the copy of the movie you have. So you blindly download one subtitle, extract it and start the movie with it. But the timings are not in sync. Frustrated, you download another subtitle, only to find that it is the same subtitle as the first one. If the site has 30 subtitles for the movie, you ll have to download and check each of those manually before you find the exact one or give up in frustration.

How titley helps-
=================

Titley helps you in this situation by.

1. You call titley with an IMDB id or a part of the movie name (In which case it will search OMDB database for the matching movies and you will be able to select the movie from the list shown).
1. One the right movie is selected, it will go and fetch all available subtitles for a movie from a subtitle site.
2. Extract all of them and search for a medium length and non-repeating dialog among subtitles. It will then list all the retrieved subtitles with the time that particular dialog appear in each of them. You can play your movie and find the time that dialog plays. Once you find the approximate time, you can select the subtitle with the closest time.

Please see the sample run where subtitles for the movie 'Ferris Bueller's Day Off' is being downloaded.

Sample run
============
::
   
    >python titley-get.py --name=ferris 
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): www.omdbapi.com
    
    The following movies were found matching your search key 'ferris'
    
    1) Ferris Bueller's Day Off (1986), IMDB: tt0091042
    2) Ferris Bueller (19901991), IMDB: tt0098795
    3) The Night Ferris Bueller Died (1999), IMDB: tt0240760
    4) Ferris Wheels & Funky Breath (2013), IMDB: tt2223660
    5) The Ferris Wheel (1977), IMDB: tt0743732
    6) The Black Ferris (1990), IMDB: tt0683206
    7) Inside Story: Ferris Bueller's Day Off (2011), IMDB: tt2150301
    8) Ferris Bueller's Day Off (2010), IMDB: tt1877452
    9) The Ferris Wheel (1958), IMDB: tt0910758
    10) Pam Ferris (1991), IMDB: tt0721863
    
    Select the correct one.  Enter a number between 1 and 10. Enter "x" to exit
    1
    INFO:titley:Downloading subtitles for movie 'Ferris Bueller's Day Off'(1986), IMDB:tt0091042
    INFO:titley:Fetching http://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-tt0091042/offset-0/xml
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): www.opensubtitles.org
    INFO:titley:Fetching http://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-tt0091042/offset-40/xml
    INFO:titley:Fetching http://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-tt0091042/offset-80/xml
    INFO:titley:Fetching http://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-tt0091042/offset-120/xml
    INFO:titley:Downloading 17 subtitles
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3212297
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): dl.opensubtitles.org
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/66485
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/4458597
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3659099
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3557846
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3523972
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3438100
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3215718
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3603116
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/5456752
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/4801531
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/66484
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/5116427
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/4617238
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/5249775
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/4801528
    INFO:titley:Getting subs from http://dl.opensubtitles.org/en/download/sub/3490076
    INFO:titley:writing file ferris-bueller-s-day-off-1986\10\extraction__2\Ferris.Bueller's.Day.Off.1986.720p.BluRay.x264-ESiR [PublicHD].srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\11\extraction__3\Ferris Bueller's Day Off.Eng (SDH).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\12\extraction__4\Ferris Bueller's Day Off (ENG) (Director's Commentary).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\12\extraction__4\Ferris Bueller's Day Off CD1 (ENG) (Director's commentary).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\12\extraction__4\Ferris Bueller's Day Off CD2 (ENG) (Director's Commentary).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\13\extraction__5\Ferris Bueller's Day Off.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\15\extraction__7\fbdo-cg.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\16\extraction__8\Ferris Bueller's Day Off.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\17\extraction__9\Ferris.Buellers.Day.Off.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\2\extraction__10\Ferris Bueller's Day Off (ENG) (Hearing Impaired).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\2\extraction__10\Ferris Bueller's Day Off CD1 (ENG) (Hearing Impaired).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\2\extraction__10\Ferris Bueller's Day Off CD2 (ENG) (Hearing Impaired).srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\3\extraction__11\Ferris.Bueller's.Day.Off.1986.576p.BDRip.x264.AC3-gx.en.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\5\extraction__13\Ferris.Buellers.Day.Off.1986.1080p.BluRay.x264-CiNEFiLE.ENG.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\6\extraction__14\Ferris.Bueller's.Day.Off.1986.720P.BDRip.X264-TLF.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\7\extraction__15\Ferris Bueller's Day Off Eng.srt
    INFO:titley:writing file ferris-bueller-s-day-off-1986\9\extraction__17\Ferris Bueller's Day Off_BDrip_aviM1280_en.srt
    ====================
    
    13 Subtitles found/retrived. You can use the following dialogue and the time it appears to find the matching subtitle.
    -------------------
    
    "Whatever miles we put on,we'll take off."
    
    00:26:45,800 | ferris-bueller-s-day-off-1986\7\extraction__15
    00:27:58,718 | ferris-bueller-s-day-off-1986\15\extraction__7
    00:27:57,842 | ferris-bueller-s-day-off-1986\11\extraction__3
    00:27:57,843 | ferris-bueller-s-day-off-1986\5\extraction__13
    00:27:57,840 | ferris-bueller-s-day-off-1986\10\extraction__2
    00:26:48,000 | ferris-bueller-s-day-off-1986\12\extraction__4
    00:27:58,194 | ferris-bueller-s-day-off-1986\6\extraction__14
    00:26:48,484 | ferris-bueller-s-day-off-1986\13\extraction__5
    00:26:48,440 | ferris-bueller-s-day-off-1986\2\extraction__10
    00:27:57,842 | ferris-bueller-s-day-off-1986\16\extraction__8
    00:27:57,842 | ferris-bueller-s-day-off-1986\3\extraction__11
    00:27:58,194 | ferris-bueller-s-day-off-1986\9\extraction__17
    00:26:33,484 | ferris-bueller-s-day-off-1986\17\extraction__9
    -------------------

============
Installation
============

You can install Titley using pip.

$pip install titley
$titley-get.py --name ferris
or
$titley-get.py --name ferris --langauge=french

=============================================
Using Titley for already downloaded subtitles
=============================================
You can use Titley if you have already downloaded some subtitle files as zips. Just run titley with the --source
option and specify the directory in which to look for subtitles. Titley will extract the srt files from them and will
show the report so that you can select the right one.

$titley-get.py --source=/home/mysubs/ferris
