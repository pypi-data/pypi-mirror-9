"""Load and play sounds

By default PsychoPy will try to use the following Libs, in this order, for
sound reproduction but you can alter the order in preferences>general>audioLib:
    ['pygame', 'pyo']
If the lib is `pyo` then there is also a choice of the underlying sound driver.
Under OSX this is currently set to use coreaudio (rather than portaudio) and on
windows it will attempt to use an ASIO-based driver if found and fall back to
DirectSound if not. These settings are not currently configurable but let the
team know if you need that.

The sound lib and driver (if lib==pyo) being used will be stored as::
    `psychopy.sound.audioLib`
    `psychopy.sound.audioDriver`

For control of bitrate and buffer size you can call psychopy.sound.init before
creating your first Sound object::

    from psychopy import sound
    sound.init(rate=44100, stereo=True, buffer=128)
    s1 = sound.Sound('ding.wav')

pyo (a wrapper for portaudio and coreaudio):
    pros: powerful, low latency where drivers support it; on Windows you may want to fetch ASIO4ALL
    cons: new in PsychoPy 1.76.00; slower to init and shut down

pygame (must be version 1.8 or above):
    pros: The most robust of the API options so far - it works consistently on all platforms
    cons: needs an additional download, poor latencies

"""
# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import division
import numpy, sys
from os import path
import threading
from sys import platform, exit, stdout
from psychopy import event, core, logging, prefs
from psychopy.constants import *

if platform=='win32':
    mediaLocation="C:\\Windows\Media"
else:
    mediaLocation=""

global audioLib, audioDriver, Sound, init
global pyoSndServer
pyoSndServer=None
Sound = None
audioLib=None
audioDriver=None

for thisLibName in prefs.general['audioLib']:
    try:
        if thisLibName=='pyo':
            import pyo
            havePyo = True
        elif thisLibName=='pygame':
            import pygame
            from pygame import mixer, sndarray
        else:
            raise ValueError("Audio lib options are currently only 'pyo' or 'pygame', not '%s'" %thisLibName)
    except:
        logging.warning('%s audio lib was requested but not loaded: %s' %(thisLibName, sys.exc_info()[1]))
        continue #to try next audio lib
    #if we got this far we were sucessful in loading the lib
    audioLib=thisLibName
    logging.info('sound is using audioLib: %s' % audioLib)
    break

stepsFromA = {
    'C' : -9, 'Csh' : -8,
    'Dfl' : -8, 'D' : -7, 'Dsh' : -6,
    'Efl' : -6, 'E' : -5,
    'F' : -4, 'Fsh' : -3,
    'Gfl' : -3, 'G' : -2, 'Gsh' : -1,
    'Afl': -1, 'A': 0, 'Ash':+1,
    'Bfl': +1, 'B': +2, 'Bsh': +2
    }
knownNoteNames = sorted(stepsFromA.keys())

class _SoundBase(object):
    """Base class for sound object, from one of many ways.
    """
    # Must be provided by class SoundPygame or SoundPyo:
    #def __init__()
    #def play(self, fromStart=True, **kwargs):
    #def stop(self, log=True):
    #def getDuration(self):
    #def getVolume(self):
    #def setVolume(self, newVol, log=True):
    #def _setSndFromFile(self, fileName):
    #def _setSndFromArray(self, thisArray):

    def setSound(self, value, secs=0.5, octave=4, hamming=True, log=True):
        """Set the sound to be played.

        Often this is not needed by the user - it is called implicitly during
        initialisation.

        :parameters:

            value: can be a number, string or an array:
                * If it's a number between 37 and 32767 then a tone will be generated at that frequency in Hz.
                * It could be a string for a note ('A','Bfl','B','C','Csh'...). Then you may want to specify which octave as well
                * Or a string could represent a filename in the current location, or mediaLocation, or a full path combo
                * Or by giving an Nx2 numpy array of floats (-1:1) you can specify the sound yourself as a waveform

            secs: duration (only relevant if the value is a note name or a frequency value)

            octave: is only relevant if the value is a note name.
                Middle octave of a piano is 4. Most computers won't
                output sounds in the bottom octave (1) and the top
                octave (8) is generally painful
        """
        self._snd = None  # Re-init sound to ensure bad values will raise error during setting

        try:#could be '440' meaning 440
            value = float(value)
        except (ValueError, TypeError):
            pass  #this is a string that can't be a number, eg, a file or note
        else:
            # we've been asked for a particular Hz
            if value < 37 or value > 20000:
                raise ValueError('Sound: bad requested frequency %.0f' % value)
            self._setSndFromFreq(value, secs, hamming=hamming)

        if isinstance(value, basestring):
            if value.capitalize() in knownNoteNames:
                self._setSndFromNote(value.capitalize(), secs, octave, hamming=hamming)
            else:
                #try finding a file
                self.fileName=None
                for filePath in ['', mediaLocation]:
                    p = path.join(filePath, value)
                    if path.isfile(p):
                        self.fileName = p
                        break
                    elif path.isfile(p + '.wav'):
                        self.fileName = p + '.wav'
                        break
                if self.fileName is None:
                    raise ValueError, "setSound: could not find a sound file named " + value
                else:
                    self._setSndFromFile(value)
        elif type(value) in [list,numpy.ndarray]:
            #create a sound from the input array/list
            self._setSndFromArray(numpy.array(value))
        #did we succeed?
        if self._snd is None:
            raise ValueError, "Could not make a "+value+" sound"
        else:
            if log and self.autoLog:
                logging.exp("Set %s sound=%s" %(self.name, value), obj=self)
            self.status=NOT_STARTED

    def _setSndFromNote(self, thisNote, secs, octave, hamming=True):
        # note name -> freq -> sound
        freqA = 440.0
        thisOctave = octave-4
        thisFreq = freqA * 2.0**(stepsFromA[thisNote]/12.0) * 2.0 ** thisOctave
        self._setSndFromFreq(thisFreq, secs, hamming=hamming)

    def _setSndFromFreq(self, thisFreq, secs, hamming=True):
        # note freq -> array -> sound
        if secs<0: #if secs=-1 then they want infinite duration - create 1sec and loop it
            secs=10.0
            self.loops = -1
        nSamples = int(secs*self.sampleRate)
        outArr = numpy.arange(0.0,1.0, 1.0/nSamples)
        outArr *= 2*numpy.pi*thisFreq*secs
        outArr = numpy.sin(outArr)
        if hamming and nSamples > 30:
            outArr = apodize(outArr, self.sampleRate)
        self._setSndFromArray(outArr)

class SoundPygame(_SoundBase):
    """Create a sound object, from one of many ways.

    :parameters:
        value: can be a number, string or an array:
            * If it's a number between 37 and 32767 then a tone will be generated at that frequency in Hz.
            * It could be a string for a note ('A','Bfl','B','C','Csh'...). Then you may want to specify which octave as well
            * Or a string could represent a filename in the current location, or mediaLocation, or a full path combo
            * Or by giving an Nx2 numpy array of floats (-1:1) you can specify the sound yourself as a waveform

        secs: duration (only relevant if the value is a note name or a frequency value)

        octave: is only relevant if the value is a note name.
            Middle octave of a piano is 4. Most computers won't
            output sounds in the bottom octave (1) and the top
            octave (8) is generally painful

        sampleRate(=44100): If a sound has already been created or if the

        bits(=16):  Pygame uses the same bit depth for all sounds once initialised
    """
    def __init__(self,value="C",secs=0.5,octave=4, sampleRate=44100, bits=16,
                 name='', autoLog=True, loops=0):
        """
        """
        self.name=name#only needed for autoLogging
        self.autoLog=autoLog
        #check initialisation
        if not mixer.get_init():
            pygame.mixer.init(sampleRate, -16, 2, 3072)

        inits = mixer.get_init()
        if inits is None:
            init()
            inits = mixer.get_init()
        self.sampleRate, self.format, self.isStereo = inits

        #try to create sound
        self._snd=None
        #distinguish the loops requested from loops actual because of infinite tones
        # (which have many loops but none requested)
        self.requestedLoops = self.loops = int(loops) #-1 for infinite or a number of loops
        self.setSound(value=value, secs=secs, octave=octave)

    def play(self, fromStart=True, log=True, loops=None):
        """Starts playing the sound on an available channel.

        Parameters
        ----------
        fromStart : bool
            Not yet implemented.
        log : bool
            Whether or not to log the playback event.
        loops : int
            How many times to repeat the sound after it plays once. If
            `loops` == -1, the sound will repeat indefinitely until stopped.

        Notes
        -----
        If no sound channels are available, it will not play and return None.
        This runs off a separate thread i.e. your code won't wait for the
        sound to finish before continuing. You need to use a
        psychopy.core.wait() command if you want things to pause.
        If you call play() whiles something is already playing the sounds will
        be played over each other.
        """
        if loops is None:
            loops = self.loops
        self._snd.play(loops=loops)
        self.status=STARTED
        if log and self.autoLog:
            logging.exp("Sound %s started" %(self.name), obj=self)
        return self
    def stop(self, log=True):
        """Stops the sound immediately"""
        self._snd.stop()
        self.status=STOPPED
        if log and self.autoLog:
            logging.exp("Sound %s stopped" %(self.name), obj=self)
    def fadeOut(self,mSecs):
        """fades out the sound (when playing) over mSecs.
        Don't know why you would do this in psychophysics but it's easy
        and fun to include as a possibility :)
        """
        self._snd.fadeout(mSecs)
        self.status=STOPPED
    def getDuration(self):
        """Get's the duration of the current sound in secs"""
        return self._snd.get_length()

    def getVolume(self):
        """Returns the current volume of the sound (0.0:1.0)"""
        return self._snd.get_volume()

    def setVolume(self,newVol, log=True):
        """Sets the current volume of the sound (0.0:1.0)"""
        self._snd.set_volume(newVol)
        if log and self.autoLog:
            logging.exp("Set Sound %s volume=%.3f" %(self.name, newVol), obj=self)
        return self.getVolume()

    def _setSndFromFile(self, fileName):
        #load the file
        self.fileName = fileName
        self.loops = self.requestedLoops #in case a tone with inf loops had been used before
        self._snd = mixer.Sound(self.fileName)

    def _setSndFromArray(self, thisArray):
        #get a mixer.Sound object from an array of floats (-1:1)

        #make stereo if mono
        if self.isStereo==2 and \
            (len(thisArray.shape)==1 or thisArray.shape[1]<2):
            tmp = numpy.ones((len(thisArray),2))
            tmp[:,0] = thisArray
            tmp[:,1] = thisArray
            thisArray = tmp
        #get the format right
        if self.format == -16:
            thisArray= (thisArray*2**15).astype(numpy.int16)
        elif self.format == 16:
            thisArray= ((thisArray+1)*2**15).astype(numpy.uint16)
        elif self.format == -8:
            thisArray= (thisArray*2**7).astype(numpy.Int8)
        elif self.format == 8:
            thisArray= ((thisArray+1)*2**7).astype(numpy.uint8)

        self._snd = sndarray.make_sound(thisArray)


class SoundPyo(_SoundBase):
    """Create a sound object, from one of MANY ways.
    """
    def __init__(self, value="C", secs=0.5, octave=4, stereo=True, volume=1.0,
                 loops=0, sampleRate=44100, bits=16, hamming=True, start=0, stop=-1,
                 name='', autoLog=True):
        """
        value: can be a number, string or an array:
            * If it's a number between 37 and 32767 then a tone will be generated at that frequency in Hz.
            * It could be a string for a note ('A','Bfl','B','C','Csh'...). Then you may want to specify which octave as well
            * Or a string could represent a filename in the current location, or mediaLocation, or a full path combo
            * Or by giving an Nx2 numpy array of floats (-1:1) you can specify the sound yourself as a waveform

            By default, a Hamming window (5ms duration) will be applied to a
            generated tone, so that onset and offset are smoother (to avoid
            clicking). To disable the Hamming window, set `hamming=False`.

        secs:
            Duration of a tone. Not used for sounds from a file.

        start : float
            Where to start playing a sound file; default = 0s (start of the file).

        stop : float
            Where to stop playing a sound file; default = end of file.

        octave: is only relevant if the value is a note name.
            Middle octave of a piano is 4. Most computers won't
            output sounds in the bottom octave (1) and the top
            octave (8) is generally painful

        stereo: True (= default, two channels left and right), False (one channel)

        volume: loudness to play the sound, from 0.0 (silent) to 1.0 (max).
            Adjustments are not possible during playback, only before.

        loops : int
            How many times to repeat the sound after it plays once. If
            `loops` == -1, the sound will repeat indefinitely until stopped.

        sampleRate (= 44100): if the psychopy.sound.init() function has been called
            or if another sound has already been created then this argument will be
            ignored and the previous setting will be used

        bits: has no effect for the pyo backend

        hamming: whether to apply a Hamming window (5ms) for generated tones.
            Not applied to sounds from files.
        """
        global pyoSndServer
        if pyoSndServer is None or pyoSndServer.getIsBooted()==0:
            initPyo(rate=sampleRate)

        self.sampleRate=pyoSndServer.getSamplingRate()
        self.format = bits
        self.isStereo = stereo
        self.channels = 1 + int(stereo)
        self.secs=secs
        self.startTime = start
        self.stopTime = stop
        self.autoLog=autoLog
        self.name=name

        #try to create sound; set volume and loop before setSound (else needsUpdate=True)
        self._snd=None
        self.volume = min(1.0, max(0.0, volume))
        #distinguish the loops requested from loops actual because of infinite tones
        # (which have many loops but none requested)
        self.requestedLoops = self.loops = int(loops) #-1 for infinite or a number of loops

        self.setSound(value=value, secs=secs, octave=octave, hamming=hamming)
        self.needsUpdate = False

    def play(self, loops=None, autoStop=True, log=True):
        """Starts playing the sound on an available channel.

        loops : int
            (same as above)

        For playing a sound file, you cannot specify the start and stop times when
        playing the sound, only when creating the sound initially.

        Playing a sound runs in a separate thread i.e. your code won't wait for the
        sound to finish before continuing. To pause while playing, you need to use a
        `psychopy.core.wait(mySound.getDuration())`.
        If you call `play()` while something is already playing the sounds will
        be played over each other.
        """
        if loops is not None and self.loops != loops:
            self.setLoops(loops)
        if self.needsUpdate:
            self._updateSnd()  # ~0.00015s, regardless of the size of self._sndTable
        self._snd.out()
        self.status=STARTED
        if autoStop or self.loops != 0:
            # pyo looping is boolean: loop forever or not at all
            # so track requested loops using time; limitations: not sample-accurate
            if self.loops >= 0:
                duration = self.getDuration() * (self.loops + 1)
            else:
                duration = FOREVER
            self.terminator = threading.Timer(duration, self._onEOS)
            self.terminator.start()
        if log and self.autoLog:
            logging.exp("Sound %s started" %(self.name), obj=self)
        return self

    def _onEOS(self):
        # call _onEOS from a thread based on time, enables loop termination
        if self.loops != 0:  # then its looping forever as a pyo object
            self._snd.stop()
        if self.status != NOT_STARTED:  # in case of multiple successive trials
            self.status = FINISHED
        return True

    def stop(self, log=True):
        """Stops the sound immediately"""
        self._snd.stop()
        try:
            self.terminator.cancel()
        except:  # pragma: no cover
            pass
        self.status=STOPPED
        if log and self.autoLog:
            logging.exp("Sound %s stopped" %(self.name), obj=self)

    def getDuration(self):
        """Return the duration of the sound"""
        return self.duration
    def getVolume(self):
        """Returns the current volume of the sound (0.0 to 1.0, inclusive)"""
        return self.volume
    def getLoops(self):
        """Returns the current requested loops value for the sound (int)"""
        return self.loops

    def setVolume(self, newVol, log=True):
        """Sets the current volume of the sound (0.0 to 1.0, inclusive)"""
        self.volume = min(1.0, max(0.0, newVol))
        self.needsUpdate = True
        if log and self.autoLog:
            logging.exp("Sound %s set volume %.3f" % (self.name, self.volume), obj=self)

    def setLoops(self, newLoops, log=True):
        """Sets the current requested extra loops (int)"""
        self.loops = int(newLoops)
        self.needsUpdate = True
        if log and self.autoLog:
            logging.exp("Sound %s set loops %s" % (self.name, self.loops), obj=self)

    def _updateSnd(self):
        self.needsUpdate = False
        doLoop = bool(self.loops != 0)  # if True, end it via threading.Timer
        self._snd = pyo.TableRead(self._sndTable, freq=self._sndTable.getRate(),
                                  loop=doLoop, mul=self.volume)
    def _setSndFromFile(self, fileName):
        # want mono sound file played to both speakers, not just left / 0
        self.fileName = fileName
        self._sndTable = pyo.SndTable(initchnls=self.channels)
        self.loops = self.requestedLoops #in case a tone with inf loops had been used before
        # mono file loaded to all chnls:
        self._sndTable.setSound(self.fileName,
                                start=self.startTime, stop=self.stopTime)
        self._updateSnd()
        self.duration = self._sndTable.getDur()

    def _setSndFromArray(self, thisArray):
        self._sndTable = pyo.DataTable(size=len(thisArray),
                                       init=thisArray.T.tolist(),
                                       chnls=self.channels)
        self._updateSnd()
        # a DataTable has no .getDur() method, so just store the duration:
        self.duration = float(len(thisArray)) / self.sampleRate

def initPygame(rate=22050, bits=16, stereo=True, buffer=1024):
    """If you need a specific format for sounds you need to run this init
    function. Run this *before creating your visual.Window*.

    The format cannot be changed once initialised or once a Window has been created.

    If a Sound object is created before this function is run it will be
    executed with default format (signed 16bit stereo at 22KHz).

    For more details see pygame help page for the mixer.
    """
    global Sound, audioDriver
    Sound = SoundPygame
    audioDriver='n/a'
    if stereo==True: stereoChans=2
    else:   stereoChans=0
    if bits==16: bits=-16 #for pygame bits are signed for 16bit, signified by the minus
    mixer.init(rate, bits, stereoChans, buffer) #defaults: 22050Hz, 16bit, stereo,
    sndarray.use_arraytype("numpy")
    setRate, setBits, setStereo = mixer.get_init()
    if setRate!=rate:
        logging.warn('Requested sound sample rate was not poossible')
    if setBits!=bits:
        logging.warn('Requested sound depth (bits) was not possible')
    if setStereo!=2 and stereo==True:
        logging.warn('Requested stereo setting was not possible')

def _bestDriver(devNames, devIDs):
    """Find ASIO or Windows sound drivers
    """
    preferredDrivers = prefs.general['audioDriver']
    outputID=None
    audioDriver=None
    osEncoding=sys.getfilesystemencoding()
    for prefDriver in preferredDrivers:
        if prefDriver.lower() == 'directsound':
            prefDriver = u'Primary Sound'
        #look for that driver in available devices
        for devN, devString in enumerate(devNames):
            try:
                if prefDriver.encode('utf-8').lower() in devString.decode(osEncoding).encode('utf-8').lower():
                    audioDriver=devString.decode(osEncoding).encode('utf-8')
                    outputID=devIDs[devN]
                    return audioDriver, outputID #we found a driver don't look for others
            except (UnicodeDecodeError, UnicodeEncodeError):
                logging.warn('find best sound driver - could not interpret unicode in driver name')
    else:
        return None, None

def initPyo(rate=44100, stereo=True, buffer=128):
    """setup the pyo (sound) server
    """
    global pyoSndServer, Sound, audioDriver, duplex, maxChnls
    Sound = SoundPyo
    global pyo
    try:
        assert pyo
    except NameError:  # pragma: no cover
        import pyo  # microphone.switchOn() calls initPyo even if audioLib is something else
    #subclass the pyo.Server so that we can insert a __del__ function that shuts it down
    # skip coverage since the class is never used if we have a recent version of pyo
    class _Server(pyo.Server):  # pragma: no cover
        core=core #make libs class variables so they don't get deleted first
        logging=logging
        def __del__(self):
            self.stop()
            self.core.wait(0.5)#make sure enough time passes for the server to shutdown
            self.shutdown()
            self.core.wait(0.5)#make sure enough time passes for the server to shutdown
            self.logging.debug('pyo sound server shutdown')#this may never get printed
    if '.'.join(map(str, pyo.getVersion())) < '0.6.4':
        Server = _Server
    else:
        Server = pyo.Server

    # if we already have a server, just re-initialize it
    if 'pyoSndServer' in globals() and hasattr(pyoSndServer,'shutdown'):
        pyoSndServer.stop()
        core.wait(0.5)#make sure enough time passes for the server to shutdown
        pyoSndServer.shutdown()
        core.wait(0.5)
        pyoSndServer.reinit(sr=rate, nchnls=maxChnls, buffersize=buffer, audio=audioDriver)
        pyoSndServer.boot()
    else:
        if platform=='win32':
            #check for output device/driver
            devNames, devIDs=pyo.pa_get_output_devices()
            audioDriver,outputID=_bestDriver(devNames, devIDs)
            if outputID is None:
                audioDriver = 'Windows Default Output' #using the default output because we didn't find the one(s) requested
                outputID = pyo.pa_get_default_output()
            if outputID is not None:
                logging.info('Using sound driver: %s (ID=%i)' %(audioDriver, outputID))
                maxOutputChnls = pyo.pa_get_output_max_channels(outputID)
            else:
                logging.warning('No audio outputs found (no speakers connected?')
                return -1
            #check for valid input (mic)
            devNames, devIDs = pyo.pa_get_input_devices() # If no input device is available, devNames and devIDs are empty lists.
            audioInputName, inputID = _bestDriver(devNames, devIDs)
            if len(devIDs)>0 and inputID is None: # Input devices were found, but requested devices were not found
                defaultID = pyo.pa_get_default_input()
                if defaultID is not None and defaultID != -1: # default input is found
                    audioInputName = 'Windows Default Input' #using the default input because we didn't find the one(s) requested
                    inputID = defaultID
                else:
                    inputID = None # default input is not available
            if inputID is not None:
                logging.info('Using sound-input driver: %s (ID=%i)' %(audioInputName, inputID))
                maxInputChnls = pyo.pa_get_input_max_channels(inputID)
                duplex = bool(maxInputChnls > 0)
            else:
                maxInputChnls = 0
                duplex=False
        else:#for other platforms set duplex to True (if microphone is available)
            audioDriver = prefs.general['audioDriver'][0]
            maxInputChnls = pyo.pa_get_input_max_channels(pyo.pa_get_default_input())
            maxOutputChnls = pyo.pa_get_output_max_channels(pyo.pa_get_default_output())
            duplex = bool(maxInputChnls > 0)

        maxChnls = min(maxInputChnls, maxOutputChnls)
        if maxInputChnls < 1:  # pragma: no cover
            logging.warning('%s.initPyo could not find microphone hardware; recording not available' % __name__)
            maxChnls = maxOutputChnls
        if maxOutputChnls < 1:  # pragma: no cover
            logging.error('%s.initPyo could not find speaker hardware; sound not available' % __name__)
            return -1

        # create the instance of the server:
        if platform in ['darwin', 'linux2']:
            #for mac/linux we set the backend using the server audio param
            pyoSndServer = Server(sr=rate, nchnls=maxChnls, buffersize=buffer, audio=audioDriver)
        else:
            #with others we just use portaudio and then set the OutputDevice below
            pyoSndServer = Server(sr=rate, nchnls=maxChnls, buffersize=buffer)

        pyoSndServer.setVerbosity(1)
        if platform=='win32':
            pyoSndServer.setOutputDevice(outputID)
            if inputID is not None:
                pyoSndServer.setInputDevice(inputID)
        #do other config here as needed (setDuplex? setOutputDevice?)
        pyoSndServer.setDuplex(duplex)
        pyoSndServer.boot()
    core.wait(0.5)#wait for server to boot before starting te sound stream
    pyoSndServer.start()
    try:
        Sound()  # test creation, no play
    except pyo.PyoServerStateException:
        msg = "Failed to start pyo sound Server"
        if platform == 'darwin' and audioDriver != 'portaudio':
            msg += "; maybe try prefs.general.audioDriver 'portaudio'?"
        logging.error(msg)
        core.quit()
    logging.debug('pyo sound server started')
    logging.flush()

def setaudioLib(api):
    """DEPRECATED: please use preferences>general>audioLib to determine which audio lib to use"""
    raise DeprecationWarning

def apodize(soundArray, sampleRate):
    """Apply a Hamming window (5ms) to reduce a sound's 'click' onset / offset
    """
    hwSize = int(min(sampleRate // 200, len(soundArray) // 15))
    hammingWindow = numpy.hamming(2 * hwSize + 1)
    soundArray[:hwSize] *= hammingWindow[:hwSize]
    for i in range(2):
        soundArray[-hwSize:] *= hammingWindow[hwSize + 1:]
    return soundArray

#initialise it and keep track
if audioLib is None:
    msg = 'No audio API found. Try installing pyo 0.6.8+, or pygame 1.8+'
    logging.error(msg)
    raise AttributeError(msg)
elif audioLib=='pyo':
    init=initPyo
    Sound=SoundPyo
elif audioLib=='pygame':  # pragma: no cover
    init=initPygame
    Sound=SoundPygame
