from machine import Pin, I2C
import machine
import utime


RDA_RDSR = 0b1000000000000000
RDA_BLERB = 0b0000000000000011


class Radio:
    
    def __init__( self, NewFrequency, NewVolume, NewMute, NewMutePin):
        
        
#
# set the initial values of the radio
#
        self.Volume = 2
        self.Frequency = 88
        self.Mute = False
 
#
# Update the values with the ones passed in the initialization code
#
        self.SetVolume( NewVolume )
        self.SetFrequency( NewFrequency )
        self.SetMutePin(NewMutePin)
        self.SetMute( NewMute )

      
# Initialize I/O pins associated with the radio's I2C interface

        self.i2c_sda = Pin(14)
        self.i2c_scl = Pin(15)

#
# I2C Device ID can be 0 or 1. It must match the wiring. 
#
# The radio is connected to device number 1 of the I2C device
#
        self.i2c_device = 1
        self.i2c_device_address = 0x10

#
# Array used to configure the radio
#
        self.Settings = bytearray( 8 )
        self.Reg_info = bytearray( 12 )
        self.stationName = "------------"
        self.stationName_tmp1 = ['-'] * 12
        self.stationName_tmp2 = ['-'] * 12

        self.radio_i2c = I2C( self.i2c_device, scl=self.i2c_scl, sda=self.i2c_sda, freq=200000)
        self.DefaultSettings()
        self.ProgramRadio()
    

        
    def increase_volume (self):
        self.SetVolume(self.Volume+1)
        #print(self.Volume)
        self.ProgramRadio()
        
    def decrease_volume(self):
        self.SetVolume(self.Volume-1)
        self.ProgramRadio()
    def get_volume(self):
        return self.Volume
        
    def get_mute(self):
        return self.Mute
    
    def toggle_mute(self):
        self.Mute = not self.Mute
        self.MutePin.value(not self.Mute)
    def Seek(self):
        self.Settings[3] = self.Settings[3] | 0x00
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )
        self.Settings[0] = self.Settings[0] | 0x03
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )
        self.UpdateSettings()
        
        
    def SetMutePin(self, NewMutePin):
        self.MutePin = machine.Pin(NewMutePin,machine.Pin.OUT)
        self.MutePin.value(0)
 
    def SetVolume( self, NewVolume ):
        #print("sel vol")
#
# Conver t the string into a integer
#
        try:
            
                
            NewVolume = int( NewVolume )
            
        except:
            return( False )
        
#
# Validate the type and range check the volume
#
        if ( not isinstance( NewVolume, int )):
            return( False )
        
        if (( NewVolume < 0 ) or ( NewVolume >= 16 )):
            return( False )

        self.Volume = NewVolume
        return( True )



    def SetFrequency( self, NewFrequency ):
#
# Convert the string into a floating point value
#
        try:
            NewFrequency = float( NewFrequency )
            
        except:
            return( False )
        
#
# validate the type and range check the frequency
#
        if ( not ( isinstance( NewFrequency, float ))):
            return( False )
 
        if (( NewFrequency < 88.0 ) or ( NewFrequency > 108.0 )):
            return( False )

        self.Frequency = NewFrequency
        return( True )
    
    def get_Frequency(self):
        return self.Frequency
    
    def SetMute( self, NewMute ):
        #print("set mute")
        
        try:
            self.Mute = bool( int( NewMute ))
            self.MutePin.value(not self.Mute)
            
        except:
            return( False )
        
        return( True )

#
# convert the frequency to 10 bit value for the radio chip
#
    def ComputeChannelSetting( self, Frequency ):
        Frequency = int( Frequency * 10 ) - 870
        
        ByteCode = bytearray( 2 )
#
# split the 10 bits into 2 bytes
#
        ByteCode[0] = ( Frequency >> 2 ) & 0xFF
        ByteCode[1] = (( Frequency & 0x03 ) << 6 ) & 0xC0
        return( ByteCode )

#
# Configure the settings array with the mute, frequency and volume settings
        
#
    def UpdateSettings( self ):
        self.Settings[0] = 0xC0
        self.Settings[1] = 0x09 | 0x00
        print(len(self.Settings))
        cs = self.ComputeChannelSetting( self.Frequency )
        self.Settings[2] = cs[0]
        self.Settings[3] = cs[1]
        self.Settings[3] = self.Settings[3] | 0x10#change to 0x10 if it stops working
        self.Settings[4] = 0x00
        self.Settings[5] = 0x00
        self.Settings[6] = 0x84
        self.Settings[7] = (0x80 + self.Volume)

    def DefaultSettings( self ):
        self.Settings[0] = 0xC0
        self.Settings[1] = 0x09 | 0x04
        cs = self.ComputeChannelSetting( self.Frequency )
        self.Settings[2] = cs[0]
        self.Settings[3] = cs[1]
        self.Settings[3] = self.Settings[3] | 0x10#change to 0x10 if it stops working
        self.Settings[4] = 0x04
        self.Settings[5] = 0x00
        self.Settings[6] = 0x84
        self.Settings[7] = (0x80 + self.Volume)
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )
  
# Update the settings array and transmitt it to the radio
#
    def ProgramRadio( self ):
        #utime.sleep(5)
        print("programming")
        self.UpdateSettings()
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )

#
# Extract the settings from the radio registers
#
    def GetSettings( self ):
#        
# Need to read the entire register space. This is allow access to the mute and volume settings
# After and address of 255 the 
#
        self.RadioStatus = self.radio_i2c.readfrom( self.i2c_device_address, 256 )

        if (( self.RadioStatus[0xF0] & 0x40 ) != 0x00 ):
            MuteStatus = False
        else:
            MuteStatus = True
            
        VolumeStatus = self.RadioStatus[0xF7] & 0x0F
 
 #
 # Convert the frequency 10 bit count into actual frequency in Mhz
 #
        FrequencyStatus = (( self.RadioStatus[0x00] & 0x03 ) << 8 ) | ( self.RadioStatus[0x01] & 0xFF )
        FrequencyStatus = ( FrequencyStatus * 0.1 ) + 87.0
        
        if (( self.RadioStatus[0x00] & 0x04 ) != 0x00 ):
            StereoStatus = True
        else:
            StereoStatus = False
        
        return( MuteStatus, VolumeStatus, FrequencyStatus, StereoStatus )


    def GetInfo(self):
        self.Reg_info = self.radio_i2c.readfrom( self.i2c_device_address, 12 )
        a = self.Reg_info
        b = a[4]& 0x03
        if(b != 0x4):     
            reg_a = (a[0] << 8) | a[1]
            reg_b = (a[2] << 8) | a[3]
            #if reg_b & RDA_BLERB != 0:
            if reg_a & RDA_RDSR == 0 or reg_b & RDA_BLERB != 0:
                # no new rds group ready
                #print('continue')
                return self.stationName
                
            
            block_b = (a[6] << 8) | a[7]
            block_c = (a[8] << 8) | a[9]
            block_d = (a[10] << 8) | a[11]
            group_type = 0x0a + ((block_b & 0xf000) >> 8) | ((block_b & 0x0800) >> 11)        
            if group_type in [0x0a, 0x0b]:
                # PS name
                idx = (block_b & 3) * 2
                c1 = chr(block_d >> 8)
                c2 = chr(block_d & 0xff)
                if (c1.isalpha() or c1 == ' ' ) and (c2.isalpha() or c2 ==' '):
                    #print("c1 = " + c1 + "  c2 = " + c2)
                    if self.stationName_tmp1[idx:idx + 2] == [c1, c2]:
                            self.stationName_tmp2[idx:idx + 2] = [c1, c2]
                            if  self.stationName_tmp1 ==  self.stationName_tmp2:
                                 self.stationName = ''.join( self.stationName_tmp1)
                                 #savedName = savedName + str(stationName_tmp1)
                    if  self.stationName_tmp1[idx:idx + 2] != [c1, c2]:
                            self.stationName_tmp1[idx:idx + 2] = [c1, c2]
        return self.stationName
        
    #print(str(savedName))
        
        
      
