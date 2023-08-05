# coding: utf-8

import os, mimetypes
import timeside
from timeside.core import get_processor

# dir = '/home/momo/music_local/flac/Daft Punk/Discovery'
dir = '/home/momo/music_local/mp3/Disclosure - Settle (Deluxe Version) 2013 [MP3]'

file_decoder = get_processor('file_decoder')
echo_analyzer = get_processor('echonest_identifier')

for filename in os.listdir(dir):
    mimetype = mimetypes.guess_type(filename)[0]
    if mimetype:
        if 'audio' in mimetype and not 'mpegurl' in mimetype:
            name, ext = os.path.splitext(filename)
            print name
            uri = dir + os.sep + filename
            decoder = file_decoder(uri=uri, start=0, duration=20)
            analyzer = echo_analyzer(start=0)
            decoder.output_samplerate = 11025
            pipe = (decoder | analyzer)
            pipe.run()
            songs = analyzer.metadata['songs']
            if songs:
                print songs[0]['artist_name'] + ' - ' + songs[0]['title']
            else:
                print 'Unknown'
