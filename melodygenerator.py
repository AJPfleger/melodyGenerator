# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 20:13:17 2022

@author: AJPfleger
"""


import numpy as np
from scipy.io import wavfile

 


concertPitch = 440 # a^1
fs = 44100 # sample rate
bpm = 50

class intervalls:
    P1 = 1 # Perfect unison
    m2 = 2**(1/12) # Minor second
    M2 = 2**(2/12) # Major second
    m3 = 2**(3/12) # Minor third
    M3 = 2**(4/12) # Major third
    P4 = 2**(5/12) # Perfect fourth
    T5 = 2**(6/12) # Tritone
    P5 = 2**(7/12) # Perfect fifth
    m6 = 2**(8/12) # Minor sixth
    M6 = 2**(9/12) # Major sixth
    m7 = 2**(10/12) # Minor seventh
    M7 = 2**(11/12) # Major seventh
    O8 = 2 # Perfect octave
    pause = 0

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
    

iv = intervalls

basenote = concertPitch/iv.M6
melody = [
    (1,iv.P1),
    (1,iv.M3),
    (1,iv.P5),
    (1/2,iv.O8),
    (1/2,iv.pause),
    (1/2,iv.O8),
    (1/2,iv.pause),
    (1/2,iv.O8),
    (1/2,iv.pause),
    (1/2,iv.O8),
    (1/2,iv.pause),
    (1,iv.P5),
    (1,iv.M3),
    (1.5,iv.P1),
    ]
y = createTone(0, 1, bpm, fs)

for n in range(len(melody)):
    currentNote = melody[n]
    if currentNote[1] != 0:
        note = createToneOvertones(currentNote[0], currentNote[1]*basenote, bpm, fs)
    else:
        note = createTone(currentNote[0], currentNote[1]*basenote, bpm, fs)
    
    y = np.append(y,fadeOut(note))


wavfile.write('melody.wav', fs, y)
