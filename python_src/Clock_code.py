from bh_fm_radio import Radio
import machine
import utime as time
def motor_off(x):
    motor = machine.Pin(21, machine.Pin.OUT)
    motor.value(0)

class Clock:
    def __init__ (self,hour,minute,am_pm,time_type,set_flag):
        self.hour = hour
        self.minute = minute
        self.am_pm = am_pm
        self.time_type=time_type
        self.set_flag=False
        
    def get_hour(self):
        return self.hour
        
    def get_minute(self):
        return self.minute
        
    def get_am_pm(self):
        if self.time_type == False:
            if self.am_pm == False:
                return "am"
            else:
                return "pm"
        else:
            return ""
    def get_time_type(self):
        return self.time_type
    
    def hour_set(self, hour):
        self.hour = hour
        
    def minute_set(self,minute):
        self.minute = minute
        
    def am_pm_set(self,am_pm):
        if am_pm == 1:
            self.am_pm = True
        else:
            self.am_pm = False
    
    def time_type_change(self,time_type):
        if self.time_type == False:
            if self.am_pm ==True and self.hour !=12:
                self.hour = self.hour+12
                self.time_type=time_type
            else:
                self.time_type = time_type
                
        elif self.time_type ==True:
            if self.hour>12 and (self.hour !=12 or self.am_pm != False):
                self.hour = self.hour-12
                self.time_type=time_type
            else:
                self.time_type = time_type
        
    
    def update(self):
        if self.time_type == False:
            if self.minute>=0 and self.minute<59:
               self.minute = self.minute+1
               
            elif self.hour<12 and self.hour>0:
                self.hour = self.hour+1
                self.minute =0
                edge_flag=False
                
            if self.hour==12 and self.minute ==0:
                self.am_pm = not self.am_pm
                
            elif self.hour==12 and self.minute==59:
                self.hour=1
                self.minute=0
                
        if self.time_type == True:
            if self.minute>=0 and self.minute<59:
               self.minute = self.minute+1
               
            elif self.hour<23 and self.hour>=0:
                self.hour = self.hour+1
                self.minute =0
            elif self.hour==23 and self.minute==59:
                self.hour=0
                self.minute=0
        
class Alarm(Clock):
    def __init__ (self,hour=1,minute=1,am_pm=False,time_type=False,set_flag=False):
        self.motor = machine.Pin(21, machine.Pin.OUT)
        self.goin_off =False
        super().__init__(hour,minute,am_pm,time_type,set_flag)
    def get_set_flag(self):
        return self.set_flag
    def update_set_flag(self):
        self.set_flag = not self.set_flag
    def pop_off(self,Clock,Radio):
        if self.set_flag == True:
            #print("here")
            if Clock.get_time_type()==False:
                #print(self.am_pm)
                if self.hour==Clock.get_hour() and self.minute == Clock.get_minute() and self.am_pm==Clock.am_pm:
                    print("start runnin 12hr")
                    Radio.SetMute(False)
                    Radio.SetVolume(15)
                    Radio.ProgramRadio()
                    self.goin_off = True
                    #self.motor.value(1)
                    #time.sleep(2)
                    #self.motor.value(0)
                    #print(self.goin_off)
                    
            if Clock.get_time_type() ==True:
                if self.hour==Clock.get_hour() and self.minute == Clock.get_minute():
                    print ("start runnin 24hr")
                    Radio.SetMute(False)
                    Radio.SetVolume(15)
                    Radio.ProgramRadio()
                    self.goin_off = True
                    #self.motor.value(1)
                    #time.sleep(2)
                    #self.motor.value(0)
            else:
                return
    
        
        
    def snooze(self,Clock,Radio):
        if self.goin_off == True:
            self.motor.value(0)
            Radio.SetMute(True)
            Radio.ProgramRadio()
            if Clock.get_time_type() == False:
                if Clock.get_minute()<55:
                    self.minute = Clock.get_minute()+5
                    #goin_off = False
                elif Clock.get_minute()>=55 and Clock.get_hour()==11:
                    self.minute = Clock.get_minute()-55
                    self.hour = 12
                    self.am_pm = not self.am_pm
                
                elif Clock.get_minute()>=55 and Clock.get_hour()==12:
                    self.minute = Clock.get_minute()-55
                    self.hour = 1
                    #goin_off = False
                elif Clock.get_minute()>=55 and Clock.get_hour()<11:
                    self.minute = Clock.get_minute()-55
                    self.hour = Clock.get_hour()+1
                    #goin_off = False
            elif Clock.get_time_type()==True:
                if Clock.get_minute()<55:
                    self.minute = Clock.get_minute()+5
                    #goin_off = False
                elif Clock.get_minute()>=55 and Clock.get_hour()<23:
                    self.minute = Clock.get_minute()-55
                    self.hour = Clock.get_hour()+1
                    #goin_off = False
                elif Clock.get_minute()>=55 and Clock.get_hour()==23:
                    self.minute = Clock.get_minute()-55
                    self.hour = 0
                    #goin_off = False
            self.goin_off =False
        else:
            return
                

    
                
                
            
                    
                    
        
    
    
    
    
    
    
    
        