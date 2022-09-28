# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 20:13:17 2022

@author: AJPfleger
"""


import numpy as np
from scipy.io import wavfile
#import intervalls
#iv = intervalls.intervalls


# notevalue compared to bpm. Every beat is of length 1
def createTone(notevalue, pitch, bpm,fs=44100):
    duration = notevalue * 60 / bpm
    t = np.linspace(0, duration, int(fs * duration))
    return np.sin(pitch * 2 * np.pi * t)

# notevalue compared to bpm. Every beat is of length 1
def createToneOvertones(notevalue, pitch, bpm, sound='sine', fs=44100):

    assert 20 < bpm and bpm < 400, "bpm out of bounds. It should be between 20 and 400."
    assert pitch < fs/2 or np.isnan(pitch), "pitch > fs/2: tone can not be generated with this sampling frequence."

    duration = notevalue * 60 / bpm
    samples =  int(fs * duration)
    tone = np.zeros(samples)

    # we only calculate overtones if there is a pitch (= no pause)
    if pitch > 0:
        t = np.linspace(0, duration, int(fs * duration))

        # synthetic sounds
        if sound == 'oct2':
            otfreq = np.arange(1,21)
            weight = 1/2**otfreq
        elif sound == 'oct3':
            otfreq = np.arange(1,21)
            weight = 1/3**otfreq
        elif sound == 'oct4':
            otfreq = np.arange(1,21)
            weight = 1/4**otfreq
        elif sound == 'square':
            otfreq = np.arange(1,41,2)
            weight = 1/otfreq
        # real instruments
        elif sound == 'piano':
            #weight = [0.98, 1, 0.68, 0.58, 0.2, 0.2, 0.08]
            #otfreq = [1, 2, 3, 4, 5, 6, 7]
            weight = [6.2, 2.2, 1, 0.3, 0.6, 0.3, 0.5]
            otfreq = [1, 2, 3, 4, 5, 6, 7]
        elif sound == 'oboe':
            weight = [1, 0.98, 0.58, 0.44]
            otfreq = [1, 2, 3, 4]
        elif sound == 'violin':
            weight = [1, 0.14, 0.12, 0.07]
            otfreq = [1, 2, 3, 4]
        else: # sound == 'sine'
            weight = [1]
            otfreq = [1]

        for ot in range(len(otfreq)):
            otpitch = otfreq[ot] * pitch
            if otpitch > fs/2:
                break
            tone += np.sin(otpitch * 2 * np.pi * t) * weight[ot]

        # normalize
        tone /= max(tone)

    return tone

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

def generateWaveForm(melody,basenote=440,bpm=60,sound='sine',fs=44100):
    wf = createTone(0, 1, bpm, fs)
    for n in range(len(melody)):
        currentNote = melody[n]
        note = createToneOvertones(currentNote[0], currentNote[1]*basenote, bpm, sound, fs)
        wf = np.append(wf,fadeOut(note))

    return wf

def pushMelodyThroughScales(melody, fLow, fCenter, fHigh, bpm, sound='sine', fs=44100):

    assert fLow < fHigh, "fLow must be smaller than fHigh"
    assert fCenter > fLow, "fCenter must be larger than fLow"
    assert fCenter < fHigh, "fCenter must be smaller than fHigh"

    waveComplete = np.zeros(1)

    # go up
    n = 0
    base = fCenter
    while base*np.max(melody,0)[1] < fHigh:
        base = fCenter * 2**(n/12)
        waveStep = generateWaveForm(melody,base,bpm,sound,fs)
        waveComplete = np.append(waveComplete,waveStep)
        n += 1
        
    # go down
    n = 0
    while base > fLow:
        base = fCenter * 2**(n/12)
        waveStep = generateWaveForm(melody,base,bpm,sound,fs)
        waveComplete = np.append(waveComplete,waveStep)
        n -= 1

    return waveComplete

fs = 44100 # sample rate
concertPitch = 440 # a^1

#from melody.melodyOdeToJoy import *
from melody.melodyArpeggio import *
#from melody.melodyAlternate import *


#wave = generateWaveForm(melody,basenote,bpm,'piano',fs)
fLow = concertPitch * 2**(-12/12)
fCenter = concertPitch * 2**(-7/12)
fHigh = concertPitch * 2**(7/12)
wave = pushMelodyThroughScales(melody, fLow, fCenter, fHigh, bpm*5, 'oct2', fs)


wavfile.write('melody.wav', fs, wave)
