# coding: utf-8

import os, mimetypes
import timeside
from timeside.core import get_processor

live_decoder = get_processor('live_decoder')
decoder = live_decoder(num_buffers=8*128, input_src='jackaudiosrc')
decoder.output_samplerate = 11025

echo_analyzer = get_processor('echonest_identifier')
analyzer = echo_analyzer()

pipe = (decoder | analyzer)

while True:
    pipe.run()
    if analyzer.metadata:
        songs = analyzer.metadata['songs']
        if songs:
            print songs
            print songs[0]['artist_name'] + ' - ' + songs[0]['title']
        else:
            print 'Unknown'
