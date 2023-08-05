# coding: utf-8

import os, mimetypes
import timeside
from timeside.core import get_processor

uri = '/home/momo/music_local/mp3/DeeFuzz/Charles_Schillings-UnderGround_House_III.mp3'
samplerate = 11025
seconds = 10

decoder = get_processor('file_decoder')(uri=uri)
decoder.output_samplerate = samplerate
decoder.output_blocksize = seconds*samplerate

analyzer = get_processor('echonest_identifier_mix')(verbose=True)

pipe = (decoder | analyzer)

pipe.run()
