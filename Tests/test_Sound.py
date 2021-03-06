from jes4py import *
from random import randint
import simpleaudio as sa
import wave
import os
from jes4py.Sound import Sound

# Supporting functions
def openSound(mediaPath='', filename='myFirstSound.wav'):
    setMediaPath(mediaPath)
    return makeSound(filename)

def openEmptySound(numSamples=3, samplingRate=Sound.SAMPLE_RATE):
    return Sound(numSamples, samplingRate)

# Testing functions

def test_init():
    sound = openSound()

    # create empty Sound
    # s1 = Sound()
    # assert isinstance(s1, Sound)
    # assert s1.getFileName() == ''
    # assert s1.isStereo() == False
    # assert s1.getLengthInFrames() == 3*Sound.SAMPLE_RATE
    # assert s1.getSamplingRate() == Sound.SAMPLE_RATE
    # assert isinstance(s1.getBuffer(), bytearray)

    # create Sound from an Integer
    s2 = Sound(Sound.SAMPLE_RATE * 5)
    assert isinstance(s2, Sound)
    assert s2.getFileName() == ''
    assert s2.isStereo() == False
    assert s2.getLengthInFrames() == 5*Sound.SAMPLE_RATE
    assert s2.getSamplingRate() == Sound.SAMPLE_RATE
    assert isinstance(s2.getBuffer(), bytearray)

    # create Sound from existing Sound
    s3 = Sound(sound)
    assert isinstance(s3, Sound)
    assert s3.getFileName() == sound.getFileName()
    assert s3.isStereo() == sound.isStereo()
    assert s3.getLengthInFrames() == sound.getLengthInFrames()
    assert s3.getSamplingRate() == sound.getSamplingRate()
    assert s3.getBuffer() == sound.getBuffer()

def test_makeSound():
    sound = openSound()
    assert isinstance(sound, Sound)

def test_makeEmptySound():
    sound = openEmptySound()
    assert isinstance(sound, Sound)

def test_setFileName_getFileName():
    newName = "My_new_and_really_long_file_name.jpg"
    sound = openEmptySound()
    sound.setFileName(newName)
    assert newName == sound.getFileName()

def test_setBuffer_getBuffer():
    newBuff = bytearray(70)
    sound = openEmptySound()
    sound.setBuffer(newBuff)
    assert newBuff.__eq__(sound.getBuffer())
    assert newBuff.__eq__(sound.asArray())

def test_setSampleVal_getSampleVal():
    newSampleVal = 5
    pos = 3
    sound = openEmptySound()
    sound.setSampleValueAt(pos, newSampleVal)
    returnVal = sound.getSampleValueAt(3)
    assert returnVal == newSampleVal

def test_setFrame_getFrame():
    newFrameVal = bytearray([1,2])
    print(newFrameVal)
    pos = 3
    sound = Sound(5*Sound.SAMPLE_RATE)
    sound.setFrame(pos, newFrameVal)
    assert newFrameVal == sound.getFrame(3)  

def test_getSamplingRate():
    sound = Sound(1000)
    sampleRate = sound.getSamplingRate()
    assert sampleRate == 22050
    #assert that the sounds sample rate is equal to the base sample rate

def test_toString():
    sound = openSound()
    assumedStringRep = "Sound file: {} number of samples: {}".format(sound.getFileName(), sound.getLengthInFrames())
    assert sound.__str__() == assumedStringRep

def test_play():
   sound = openSound()
   sound.play()

def test_blockingPlay():
    sound = openSound()
    blockingPlay(sound)
    blockingPlay(sound)

def test_write():
    fi1 = "myFirstSound.wav"
    s2 = makeSound(fi1)
    fi = "testFile"
    s2.write(fi)
    s = Sound(5)
    s.loadFromFile(fi)
    assert s.isStereo() == s2.isStereo()
    assert s.getLengthInFrames() == s2.getLengthInFrames()
    assert s.getSamplingRate() == s2.getSamplingRate()
    assert s.getBuffer().__eq__(s2.getBuffer())
    os.remove(fi)

def test_getLeng_getNumSamp_getLenInFrames():
    sound = Sound(1000)
    leng  = sound.getLength()
    numSamples = sound.getNumSamples()
    lenInFrames = sound.getLengthInFrames()
    assert leng == 1000
    assert numSamples == 1000
    assert lenInFrames == 1000

# Can be run as script to create or recreate refimage.jpg if needed
# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1] == "makeref":
#         # makeReferenceImage('refimageA.jpg')
#         print("None")
#     else:
#         print("To (re)create reference image 'refimage.jpg', ", end="")
#         print("run script with command:",)
#         print("    python {} makeref".format(sys.argv[0]))
