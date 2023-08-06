"""Routines to extract .srt files from archive files in a source directory"""
import zipfile
import os
import logging

LOGGER = logging.getLogger('titley')

def _write_file(complete_file_name, source_fp):
    """write file 'complete_file_name' using data from 'source_fp'"""
    with open(complete_file_name.encode('utf-8', errors='ignore'), 'wb') as out:
        LOGGER.info('writing file %s', complete_file_name)
        out.write(source_fp.read())

def _extract_srt_in_zip(file_path, destination):
    """Extract .srt files in a zip file and place them in the 'destination' folder"""
    try:
        with zipfile.ZipFile(file_path, 'r') as czf:
            for zipf in czf.infolist():
                if zipf.filename[-4:] == '.srt':
                    complete_file_name = os.path.join(destination, os.path.basename(zipf.filename))
                    if not os.path.isdir(os.path.dirname(complete_file_name)):
                        os.mkdir(os.path.dirname(complete_file_name))
                    with czf.open(zipf.filename) as zfh:
                        _write_file(complete_file_name, zfh)
    except zipfile.BadZipFile:
        LOGGER.error('Bad zip file')

def _extract_srt(archive_path, destination):
    """Extract srt files in an archive and place them in 'destination' folder"""
    _extract_srt_in_zip(archive_path, destination)

def extract_all_archives_in(source):
    """Walk through the source directory looking for
       archive files. When one is found, the .srt files
       contained in it is extracted and is placed in a new
       folder named with prefix 'extraction_' followed by
       a count"""
    archive_count = 0
    for info in os.walk(source):
        for file_name in info[2]:
            _, ext = os.path.splitext(file_name)
            if ext == '.zip':
                archive_count += 1
                full_path = os.path.join(info[0], file_name)
                destination = os.path.join(os.path.dirname(full_path), '{}_{}'.format('extraction_', str(archive_count)))
                _extract_srt(full_path, destination)
