# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 20:13:17 2022

@author: AJPfleger
"""


import numpy as np
from scipy.io import wavfile
import intervalls
iv = intervalls.intervalls

concertPitch = 440 # a^1
fs = 44100 # sample rate
bpm = 50

# notevalue compared to bpm. Every beat is of length 1
def createTone(notevalue, pitch, bpm,fs=44100):
    duration = notevalue * 60 / bpm
    t = np.linspace(0, duration, int(fs * duration))
    return np.sin(pitch * 2 * np.pi * t)

# notevalue compared to bpm. Every beat is of length 1
def createToneOvertones(notevalue, pitch, bpm,fs=44100):
    duration = notevalue * 60 / bpm
    t = np.linspace(0, duration, int(fs * duration))
    
    tone = np.sin(pitch * 2 * np.pi * t)
    weight = 1/5
    ot = 0
    while pitch < fs/2:
        ot += 1
        pitch *= 2
        tone += np.sin(pitch * 2 * np.pi * t) * weight**ot
    
    return tone/max(tone)

# to cut the wave, close to a zerocrossing
def shortenToZeroCrossing(note):
    t = 0
    for t in np.arange(len(note)-1,1,-1):
        if note[t] * note[t-1] <= 0:
            break
    if t < len(note)*0.9:
        print('No zero-crossings found without cutting too much. Returned original note')
        return note
    
    return note[0:t]

def fadeOut(note, t=0.9):
    length = len(note)
    unchanged = int(0.9*length)
    rest = length - unchanged
    weight = np.ones(unchanged)
    weight = np.append(weight,np.linspace(1,0,rest))
    
    return note * weight


#from melodyOdeToJoy import *
from melodyArpeggio import *

y = createTone(0, 1, bpm, fs)
for n in range(len(melody)):
    currentNote = melody[n]
    if currentNote[1] != 0:
        note = createToneOvertones(currentNote[0], currentNote[1]*basenote, bpm, fs)
    else:
        note = createTone(currentNote[0], currentNote[1]*basenote, bpm, fs)
    
    y = np.append(y,fadeOut(note))


wavfile.write('melody.wav', fs, y)
