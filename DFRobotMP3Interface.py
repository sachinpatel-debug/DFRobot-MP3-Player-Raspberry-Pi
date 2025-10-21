#you can control the DFRobot mp3 player to different things (such as change which song to play or change volume) 

#you can do this through UART

#you can send 10 byte strings of 1s and 0s using UART protocol

#this class provides a nice interface for different commands 
#complete documentation found here
#https://wiki.dfrobot.com/dfplayer_mini_sku_dfr0299

import serial
from time import sleep
class MP3Player:
    start_byte = 0x7E #something like this
    version = 0xFF #you can query the software version with cmd 0x46
    length = 0x06 
    end_byte = 0xEF

    def __init__(self, playback_source = 1, EQ = 0):
        #playback source: U is 0, TF (TF is mini SD card) is 1, /AUX is 2, /SLEEP is 3, /FLASH is 4
        #EQ specifies the style of music (it does this by controlling the volume of specific frequencies 0 is normal, 1 is pop, 2 is Rock, 3 is Jazz, 4 is classic, and 5 is base)
        self.media_type = playback_source
        self.EQ = EQ
        self.param_high = 0x00
        self.param_low = 0x00
        self.cmd = 0x00
        self.feedback = 0x00
        self.resetModule()
        self.specifyEqualizer()
        self.specifyPlaybackSource()

    def playNext(self, feedback=0):
        self.feedback = hex(feedback)
        self.cmd = 0x01
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack()
        
    def playPrevious(self, feedback=0):
        self.feedback = hex(feedback)
        self.cmd = 0x02
        self.param_low = 0x00
        self.param_high = 0x00
        self.sendStack(self)

    def playTrackNumber(self, trackNumber, feedback = 0): #changes the volume to the specified number. volume can be from 0-30
        if trackNumber < 0:
            desiredVolume = 0
        elif desiredVolume > 2999:
            desiredVolume = 2999
        self.param_high = (trackNumber >> 8) & 0xFF
        self.param_low = trackNumber & 0xFF
        self.cmd = 0x03 #command to play track number
        self.feedback = hex(feedback)
        self.sendStack(self)    

    def increaseVolume(self, feedback = 0):
        self.feedback = hex(feedback)
        self.cmd = 0x04
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)

    def decreaseVolume(self, feedback = 0):
        self.feedback = hex(feedback)
        self.cmd = 0x05
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)

    def changeVolumeTo(self, desiredVolume, feedback = 0): #changes the volume to the specified number. volume can be from 0-30
        if desiredVolume < 0:
            desiredVolume = 0
        elif desiredVolume > 30:
            desiredVolume = 30
        self.param_low = hex(desiredVolume)
        self.cmd = 0x06 #cmd to change volume to a specific number (number is determined by parameters)
        self.feedback = hex(feedback)
        self.sendStack(self)

    def specifyEqualizer(self, feedback = 0):
        self.feedback = hex(feedback)
        self.cmd = 0x07
        if 0 <= self.EQ <= 5:
            self.param_low = hex(self.EQ)
        else: 
            raise IndexError("Please enter a value between 0 and 5 (inclusive)") #EQ specifies the style of music (it does this by controlling the volume of specific frequencies 0 is normal, 1 is pop, 2 is Rock, 3 is Jazz, 4 is classic, and 5 is base)

        self.param_high = 0x00
        self.sendStack()

    def specifyPlaybackMode(self, mode=0, feedback=0):
        self.feedback = hex(feedback)
        self.cmd = 0x08
        if 0 <= mode <= 3:
            self.param_low = hex(mode)
        else:
            raise IndexError("Please enter a value between 0 and 3 (inclusive)") #0=repeat, 1=folder repeat, 2=single repeat, 3=random
        self.param_high = 0x00
        self.sendStack(self)
    
    def specifyPlaybackSource(self, feedback = 0):
        self.feedback = hex(feedback)
        self.cmd = 0x09
        if 0 <= self.media_type <= 4:
            self.param_low = hex(self.media_type)
        else:
            raise IndexError("Please enter a value between 0 and 4 (inclusive)") #0=U, 1= TF(tf is mini sd card which is what we use), 2=Aux, 3=sleep,4=flash
        self.param_high = 0x00
        self.sendStack()
    
    def standbyMode(self, feedback = 0): #command to go into low power mode
        self.feedback = hex(feedback)
        self.cmd = 0x0A
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)
    
    def normalWorkingMode(self): #put the module back into normal mode from low power mode? idk, use this at our peril
        self.cmd = 0x0B
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)

    def resetModule(self):
        self.cmd = 0x0C
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack()
    
    def play(self):
        self.cmd = 0x0D
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)
    
    def pause(self):
        self.cmd = 0x0E
        self.param_high = 0x00
        self.param_low = 0x00
        self.sendStack(self)
    
    def specifyFolderPlayback(self, folder = 1): #specify the folder to playback
        self.cmd = 0x0F
        self.param_high = 0x00
        if 1 <= folder <= 10:
            self.param_low = hex(folder)
        else:
            raise IndexError("Please enter a folder number btwn 1 and 10")


    def repeatPlay(self, start = 1): #start input parameter must equal 1 or 0
        self.cmd = 0x11
        self.param_high = 0x00
        if 0 <= start <= 1:
            self.param_low = hex(start)
        else:
            raise IndexError("Please enter either 0 or 1 (0 to stop play and 1 to start repeating play)")

    
        
    def sendStack(self): #this sends the chain of UART signals
        checksum = 0xFFFF - (self.version + self.length + self.cmd + self.feedback + self.param_high + self.param_low) + 1
        self.checksum_high = (checksum >> 8) & 0xFF
        self.checksum_low = checksum & 0xFF
        self.feedback = 0x00
        frame = serial.to_bytes(bytes([self.start_byte,self.version,self.length,self.cmd,self.feedback,self.param_high,self.param_low,self.checksum_high,self.checksum_low, self.end_byte]))
        # frame = bytes([self.start_byte,self.version,self.length,self.cmd,self.feedback,self.param_high,self.param_low,self.checksum_high,self.checksum_low, self.end_byte])

        print(frame)
        #ser.write(frame)       

    

    
#ser = serial.Serial('\dev\serial0', 9600, timeout = 1)
dfrobot = MP3Player()
dfrobot.changeVolumeTo(25)
        


