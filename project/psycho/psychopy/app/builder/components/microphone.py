# Part of the PsychoPy library
# Copyright (C) 2014 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: Jeremy R. Gray, 2012

from _base import *
from os import path
from psychopy.app.builder import components #for getInitVals()

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'microphone.png')
tooltip = _('Microphone: basic sound capture (fixed onset & duration), okay for spoken words')

_localized = {'stereo': _('Stereo')}

class MicrophoneComponent(BaseComponent):
    """An event class for capturing short sound stimuli"""
    categories = ['Responses']
    def __init__(self, exp, parentName, name='mic_1',
                 startType='time (s)', startVal=0.0,
                 stopType='duration (s)', stopVal=2.0, startEstim='', durationEstim='',
                 stereo=False
                ):
        super(MicrophoneComponent, self).__init__(exp, parentName, name=name,
                    startType=startType, startVal=startVal,
                    stopType=stopType, stopVal=stopVal,
                    startEstim=startEstim, durationEstim=durationEstim)
        self.type='Microphone'
        self.url="http://www.psychopy.org/builder/components/microphone.html"
        self.exp.requirePsychopyLibs(['microphone'])
        #params
        self.params['stereo']=Param(stereo, valType='bool',
            hint=_("Record two channels (stereo) or one (mono, smaller file)"),
            label=_localized['stereo'])
        self.params['stopType'].allowedVals = ['duration (s)']
        self.params['stopType'].hint = _('The duration of the recording in seconds; blank = 0 sec')
    def writeStartCode(self,buff):
        # filename should have date_time, so filename_wav should be unique
        buff.writeIndented("wavDirName = filename + '_wav'\n")
        buff.writeIndented("if not os.path.isdir(wavDirName):\n" +
                           "    os.makedirs(wavDirName)  # to hold .wav files\n")
    def writeRoutineStartCode(self,buff):
        inits = components.getInitVals(self.params)
        buff.writeIndented("%s = microphone.AdvAudioCapture(name='%s', saveDir=wavDirName, stereo=%s)\n" %(
            inits['name'], inits['name'], inits['stereo']))
    def writeFrameCode(self,buff):
        """Write the code that will be called every frame"""
        duration = "%s" % self.params['stopVal']  # type is code
        if not len(duration):
            duration = "0"
        # starting condition:
        buff.writeIndented("\n")
        buff.writeIndented("# *%s* updates\n" %(self.params['name']))
        self.writeStartTestCode(buff)  # writes an if statement
        buff.writeIndented("%(name)s.status = STARTED\n" %(self.params))
        buff.writeIndented("%s.record(sec=%s, block=False)  # start the recording thread\n" %
                            (self.params['name'], duration))
        buff.setIndentLevel(-1, relative=True)  # ends the if statement
        buff.writeIndented("\n")
        # these lines handle both normal end of rec thread, and user .stop():
        buff.writeIndented("if %(name)s.status == STARTED and not %(name)s.recorder.running:\n" % self.params)
        buff.writeIndented("    %s.status = FINISHED\n" % self.params['name'])
    def writeRoutineEndCode(self,buff):
        #some shortcuts
        name = self.params['name']
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1] #last (outer-most) loop
        else:
            currLoop = self.exp._expHandler

        #write the actual code
        buff.writeIndented("# check responses\n" %self.params)
        buff.writeIndented("if not %(name)s.savedFile:\n"%self.params)
        buff.writeIndented("    %(name)s.savedFile = None\n" %(self.params))
        buff.writeIndented("# store data for %s (%s)\n" %(currLoop.params['name'], currLoop.type))

        #always add saved file name
        buff.writeIndented("%s.addData('%s.filename', %s.savedFile)\n" % (currLoop.params['name'],name,name))
        if currLoop.params['name'].val == self.exp._expHandler.name:
            buff.writeIndented("%s.nextEntry()\n" % self.exp._expHandler.name)
        # best not to do loudness / rms or other processing here
