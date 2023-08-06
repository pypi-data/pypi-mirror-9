import os
import re
import pysrt
import logging

encodings = ['utf-8', 'iso-8859-1']
logger = logging.getLogger('titley')

def compact(text):
    return re.sub('[^a-z0-9]', '-', str(text).lower()).strip('-')

def generate_subs_for_dirs(path):
    dir_wise_subs = {}
    for info in os.walk(path):
        for file_name in info[2]:
            _, ext = os.path.splitext(file_name)
            if ext == '.srt':
                full_path = os.path.join(info[0], file_name)
                subs = None
                for encoding in encodings:
                    try:
                        subs = pysrt.open(full_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                if subs == None:
                    logger.error("Decoding error for file %s", full_path)
                    continue
                if info[0] in dir_wise_subs:
                    dir_wise_subs[info[0]] += subs
                else:
                    dir_wise_subs[info[0]] = subs
    return dir_wise_subs

def calculate_histogram(dir_wise_subs):
    histogram = {}
    for _, subs in dir_wise_subs.items():
        seen = {}
        for sub in subs:
            sub_hash = compact(sub.text)
            #avoid items that may appear multiple
            #times in the same subtitle
            if sub_hash not in seen:
                seen[sub_hash] = True
                #avoid very short dialogues to
                #eliminate ambiguity for user
                if len(sub_hash) > 20:
                    if sub_hash in histogram:
                        histogram[sub_hash] += 1
                    else:
                        histogram[sub_hash] = 1
    return histogram
                    
def generate_report(path):
    dir_wise_subs = generate_subs_for_dirs(path)
    histogram = calculate_histogram(dir_wise_subs)
    max_frequency = max(histogram.values())

    def find_candidate_sub():
        #among the subtitles with maximum frequency, find the one that
        #comes first
        for _, subs in dir_wise_subs.items():
            for sub in subs:
                sub_hash = compact(sub.text)
                if (sub_hash in histogram and histogram[sub_hash] == max_frequency):
                    return sub
                
    candidate_sub = find_candidate_sub()
    times = {}
    
    def find_candidate_sub_time(subs):
        for sub in subs:
            if compact(sub.text) == compact(candidate_sub.text):
                return str(sub.start)

    for dir_name, subs in dir_wise_subs.items():
        time = find_candidate_sub_time(subs)
        if time != None:
            times[dir_name] = time
            
    candidate_text = candidate_sub.text
    if candidate_text != None:
        return candidate_text, times
    else:
        raise Exception('No subtitles to report')
