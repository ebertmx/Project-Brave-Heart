#Code for alarm clock
#Connor Wiebe, Matt Ebert
#July 19 2022

#libraries to import
from machine import Pin, SPI, Timer
import utime as time
from encoder_library import RotaryIRQ
from Clock_code import Clock,Alarm
import Clock_code
from bh_fm_radio import Radio
import math
#end of libraries to import 

#button/motor setup
snooze_button1 = machine.Pin(7,machine.Pin.IN,machine.Pin.PULL_UP)
snooze_button2 = machine.Pin(8,machine.Pin.IN,machine.Pin.PULL_UP)
vol_up_button = machine.Pin(3,machine.Pin.IN,machine.Pin.PULL_UP)
vol_down_button = machine.Pin(4,machine.Pin.IN,machine.Pin.PULL_UP)
seek_button = machine.Pin(6,machine.Pin.IN,machine.Pin.PULL_UP)
mute_toggle_button = machine.Pin(5,machine.Pin.IN,machine.Pin.PULL_UP)
motor = machine.Pin(21,machine.Pin.OUT)
motor.value(0)
audio_out =machine.Pin(22,machine.Pin.OUT)
#radio_on_off = machine.Pin(8,machine.Pin.OUT)
#radio_on_off.value(0)

#end of button setup

#radio setup
fm_radio = Radio( 100.3, 2, True,9)
#end of radio setup

#encoder setup
encoder_button = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)

encoder = RotaryIRQ(pin_num_clk=0,pin_num_dt=1,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
#end of encoder setup

#Stuff for the oled screen

from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display. 
SCREEN_WIDTH = 128 #number of columns
SCREEN_HEIGHT = 64 #number of rows
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(16) # res stands for reset; always be connected to SPI RX pin of the Pico; this is the MISO
spi_dc  = Pin(17) # dc stands for data/commonda; always be connected to SPI CSn pin of the Pico
spi_cs  = Pin(20) # can be connected to any free GPIO pin of the Pico
SPI_DEVICE = 0 
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )
#End of OLED setup stuff

#Setting up varibales and classes for later
count = 0
page = 0
hour = 8
minute = 45
end_change_flag =False
am_pm = True
time_type=False
Clock = Clock(hour,minute,am_pm,time_type,False)
Alarm = Alarm(hour,minute,am_pm,time_type,set_flag=False)
#end of varibale and class setup

def motor_off(x):
    motor.value(0)
    
def vol_up(x):
    check = debounce(x)
    if check == True:
        return
    else:
        fm_radio.increase_volume()
        check_page(page)
def vol_down(x):
    check = debounce(x)
    if check == True:
        return
    else:
        fm_radio.decrease_volume()
        check_page(page)
def snooze(x):
    check = debounce(x)
    if check == True:
        return
    else:
        #motor.value(1)
        #time.sleep(2)
        motor.value(0)
        print("snoozed")
        Alarm.snooze(Clock,fm_radio)
def mute_toggle(x):
    check = debounce(x)
    if check == True:
        return
    else:
        fm_radio.toggle_mute()
        check_page(page)            
def seek(x):
    #print(fm_radio.get_Frequency())
    check = debounce(x)
    if check == True:
        return
    else:
        fm_radio.Seek()
        check_page(page)

def update_time(x):#function for updating and displaying clock time 
    if page == 0 or page==1:
        oled.text("%02d:%02d %s" %(Clock.get_hour(),Clock.get_minute(),Clock.get_am_pm()),25,0,0)
        Clock.update()
        Alarm.pop_off(Clock,fm_radio)
        oled.text("%02d:%02d %s" %(Clock.get_hour(),Clock.get_minute(),Clock.get_am_pm()),25,0,1)
        oled.show()
    else:
        Clock.update()
        Alarm.pop_off(Clock,fm_radio)
    if fm_radio.get_mute()==False:
            oled.text("Mute",0,55,0)
    if Alarm.goin_off==True:
          #print("motor 1")
          time.sleep(0.01)
          motor.value(1)
          #print("motor 2")
          #time.sleep(2)
          #motor.value(0)
          #print("motor 3")
        #check_page(page)
def update_radio(x):
    if page ==0:
        oled.fill_rect(0,35,300,10,0)
        oled.text(fm_radio.GetInfo(),15,35)
        oled.show()
        
        
def debounce(x):#function for debouncing the button
   state =0xff
   i=0
   while i<16:
       i=i+1
      # print(x.value()|0x00)
       state = ((state<<1) | (x.value() | 0x00)) & 0xFF 
       #print(hex(state))
   if (state == 0x00):
       return False
   else:
       return True
    
def work(x):#main encoder press function
    #debounce check
    check = debounce(x)
    if check == True:
        return
    #end of debounce check
    else:#main bulk of the function
        global page
        global count
        if page==0 or page==1:
            print("press")
            if page == 0:
                if encoder.value() == 0:#set alarm
                    page = 3
                #print("notyet")
                elif encoder.value() == 1:#set radio 
                    page =4
                if encoder.value() == 2:#radio info button
                    #print("radio not done yet")
                    page =5
                if encoder.value() ==3:#next button
                    page = 1
                    encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
            elif page == 1:
                if encoder.value() == 0:#set clock
                    #print("here")
                    page =2
                elif encoder.value() == 1:#toggle 12/24hr time
                   Clock.time_type_change(not Clock.get_time_type())
                   Alarm.time_type_change(Clock.get_time_type())
                elif encoder.value() ==2:#toggle alarm
                    Alarm.update_set_flag()
                elif encoder.value() == 3:#prev button
                    page = 0
                    encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
        if page==2 or page==3:
            #print("clock change press")
            count = count+1 #incrementing the varible to indicate which step we are on
            if Clock.get_time_type() == False:
                if count>3:#set the encoder back to values for main pages
                    #page=0
                    encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
            elif Clock.get_time_type() == True:
                if count>2:#set the encoder back to values for main pages
                    #page=0
                    encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
        if page ==4:
            count+=1#incrementing the varible to indicate which step we are on
            if count>2:#set the encoder back to values for main pages
                encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
        if page==5:#set encoder back to values for main pages
            if encoder.value()==0:
                page=0
                encoder.set(value = 0,min_val=0,max_val=3,range_mode=RotaryIRQ.RANGE_WRAP)
            
                
            
        check_page(page)                
        
def check_page(page):#function to display correct stuff for page on screen and update encoder values
    mute_stat,vol_stat,freq_stat,sterio_stat=fm_radio.GetSettings()
    if page ==0:#this is to display page 0
        oled.fill(0)
        oled.text("%02d"%vol_stat,0,0)
        oled.text("%02d:%02d %s" %(Clock.get_hour(),Clock.get_minute(),Clock.get_am_pm()),25,0)
        oled.text("Set Alarm",15,15)
        oled.text("Set Radio",15,25)
        #oled.text("Radio Info",15,35)
        oled.text("Next ->",15,45)
        if fm_radio.get_mute()==True:
            oled.text("Mute",0,55,1)
        elif fm_radio.get_mute()==False:
            oled.text("Mute",0,55,0)
        if Alarm.get_set_flag()==True:
            oled.text("Armd",98,0)
        oled.text("%.2f FM"%freq_stat,35,55)
        oled.show()
    elif page==1:#this is to display page 1
        oled.fill(0)
        oled.text("%02d"%vol_stat,0,0)
        oled.text("%02d:%02d %s" %(Clock.get_hour(),Clock.get_minute(),Clock.get_am_pm()),25,0)
        oled.text("Set Clock",15,15)
        oled.text("12/24 hour",15,25)
        oled.text("Alarm On/Off",15,35)
        oled.text("<- Prev",15,45)
        if fm_radio.get_mute()==True:
            oled.text("Mute",0,55,1)
        elif fm_radio.get_mute()==False:
            oled.text("Mute",0,55,0)            
        if Alarm.get_set_flag()==True:
            oled.text("Armd",98,0)
        oled.text("%.2f FM"%freq_stat,35,55)
        oled.show()
    elif page==2 or page==3: #this is to change the encoder to have valid values for the clock
        oled.fill(0)
        if Clock.time_type == False: #12hr time
            if count ==1:
                #oled.text("Change Minute:",25,25,1)
                encoder.set(value = 0,min_val=0,max_val=59,range_mode=RotaryIRQ.RANGE_WRAP)
            if count ==2:
                encoder.set(value = 1,min_val=1,max_val=12,range_mode=RotaryIRQ.RANGE_WRAP)
                #oled.text("Change Minute:",25,25,0)
                #oled.text("Change Hour:",25,25,1)
            if count ==3:
                encoder.set(value = 0,min_val=0,max_val=1,range_mode=RotaryIRQ.RANGE_WRAP)
                #oled.text("Change Hour:",25,25,0)
                #oled.text("Am or Pm?",25,25,1)
            #if count>3:
               # page=0
        else:
            if count ==1:
                encoder.set(value = 0,min_val=0,max_val=59,range_mode=RotaryIRQ.RANGE_WRAP)
                #oled.text("Change Minute",25,25,1)
            if count ==2:
                encoder.set(value = 0,min_val=0,max_val=23,range_mode=RotaryIRQ.RANGE_WRAP)
                #oled.text("Change Minute",25,25,0)
                #oled.text("Change Hour",25,25,1)
           # if count>2:
             #   page=0
    elif page ==4:#set encoder values for the radio
        oled.fill(0)
        if count ==1:
            encoder.set(value = 0,min_val=0,max_val=9,range_mode=RotaryIRQ.RANGE_WRAP)
        if count ==2:
            encoder.set(value = 88,min_val=88,max_val=108,range_mode=RotaryIRQ.RANGE_WRAP)
    elif page==5:#essentially make the encoder a back button
        encoder.set(value = 0,min_val=0,max_val=0,range_mode=RotaryIRQ.RANGE_WRAP)
        oled.fill(0)
        
        
oled.fill(0)
oled.text("%02d"%fm_radio.get_volume(),0,0)
oled.text("%02d:%02d %s" %(Clock.get_hour(),Clock.get_minute(),Clock.get_am_pm()),25,0)
oled.text("Set Alarm",15,15)
oled.text("Set Radio",15,25)
#oled.text("Radio Info",15,35)
oled.text("Next ->",15,45)
oled.text("%.2f FM"%fm_radio.get_Frequency(),35,55)
if fm_radio.get_mute()==True:
            oled.text("Mute",0,55,1)
elif fm_radio.get_mute()==False:
            oled.text("Mute",0,55,0) 
oled.show()
clk_update = Timer(-1)
clk_update.init(period=600,callback=update_time)
radio_update = Timer(-1)
radio_update.init(period=300,callback=update_radio)

#interrupt handler setup
encoder_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=work)
seek_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=seek)
snooze_button1.irq(trigger=machine.Pin.IRQ_FALLING, handler=snooze)
snooze_button2.irq(trigger=machine.Pin.IRQ_FALLING, handler=snooze)
vol_up_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=vol_up)
vol_down_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=vol_down)
mute_toggle_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=mute_toggle)
#end of interuppt handler setup
#radio bug stoppage
mute_stat,vol_stat,freq_stat,sterio_stat=fm_radio.GetSettings()
if freq_stat>108:
    print("called")
    fm_radio.DefaultSettings()
#end of radio bug stoppage
while (True):
    #print(fm_radio.GetInfo())
    #print(encoder.value())
    if page==1 or page ==0:#this is for using the 2 main pages
        #update_radio()
        if encoder.value() == 0:
            #oled.fill(0)
            oled.text(">",0,25,0)
            oled.text(">",0,35,0)
            oled.text(">",0,15,1)
            oled.text(">",0,45,0)
            #oled.show()
        elif encoder.value() == 1:
            #oled.fill(0)
            oled.text(">",0,25,1)
            oled.text(">",0,35,0)
            oled.text(">",0,15,0)
            #oled.show()
        elif encoder.value() == 2:
            #oled.fill(0)
            oled.text(">",0,25,0)
            oled.text(">",0,35,1)
            oled.text(">",0,15,0)
            oled.text(">",0,45,0)
        elif encoder.value() == 3:
            #oled.fill(0)
            oled.text(">",0,15,0)
            oled.text(">",0,25,0)
            oled.text(">",0,35,0)
            oled.text(">",0,45,1)
            #oled.show()
        oled.show()
    if page==4:#page for setting radio frequency
        init_freq = fm_radio.get_Frequency()
        radio_freq_dec, radio_freq_main = math.modf(init_freq)
        radio_freq_dec = radio_freq_dec*100
        radio_freq_dec = int(radio_freq_dec)
        radio_freq_main = int(radio_freq_main)
        while (True):
            #print("oops")
            if count>2:#statement to end the loop an revert to main operation
                count =0
                page =1
                final_freq = float(radio_freq_main)+float(radio_freq_dec)/10
                fm_radio.SetFrequency(final_freq)
                fm_radio.SetMute(False)
                end_change_flag = True
                fm_radio.ProgramRadio()
                break
            oled.fill(0)
            oled.text("Set Radio Frequency:",15,0)
            if count ==1:
                oled.text("%2d.%02d"%(radio_freq_main,encoder.value()),25,45)
                radio_freq_dec=encoder.value()
            if count ==2:
                oled.text("%2d.%02d"%(encoder.value(),radio_freq_dec),25,45)
                radio_freq_main=encoder.value()
            oled.show()
    if page ==5: #this page displays the radio information
        mute_stat,vol_stat,freq_stat,sterio_stat=fm_radio.GetSettings()
        #next 2 if statements are to print if mute is true or false
        if mute_stat ==1:
            mute_stat_string = "True"
        elif mute_stat==0:
            mute_stat_string = "False"
        oled.fill(0)
        oled.text("Radio Freq:",0,0)
        oled.text("           %2f FM"%freq_stat,0,0)
        oled.text("Mute: %s"%mute_stat_string,0,25)
        oled.text("Volume: %d"%vol_stat,0,35)
        oled.text("Station Info: %s"%sterio_stat,0,15)
        oled.text("<- Back",0,45)
        oled.show()
        
                
            
    if page ==2 or page==3:#this if statement is for setting the clock
        while (True):
            if page==3: #this page is for setting the alarm
                if Alarm.time_type == False: #12hr time
                    if count>3:#statement to end the loop an revert to main operation
                        count=0
                        page=0
                        Alarm.set_flag=True
                        end_change_flag = True
                        print("broken")
                        break
                    oled.fill(0)
                    oled.text("Set Alarm:",25,0)
                    if count ==1:
                        oled.text("Change Minute:",25,25,1)
                        oled.text("%02d:    %s" %(Alarm.get_hour(),Alarm.get_am_pm()),25,45)
                        oled.text("    %02d"%encoder.value(),25,45,1)
                        #oled.text("    %2d"%encoder.value(),25,45,0)
                        Alarm.minute_set(encoder.value())
                        #print(page)
                    if count ==2:
                        oled.text("   :%02d %s" %(Alarm.get_minute(),Alarm.get_am_pm()),25,45)
                        oled.text("%02d"%encoder.value(),25,45,1)
                        #oled.text("%2d"%encoder.value(),25,45,0)
                        oled.text("Change Minute:",25,25,0)
                        oled.text("Change Hour:",25,25,1)
                        Alarm.hour_set(encoder.value())
                    if count ==3:
                        oled.text("%02d:%02d " %(Alarm.get_hour(),Alarm.get_minute()),25,45)
                        oled.text("        %s"%Alarm.get_am_pm(),25,45,1)
                        #oled.text("        %s"%Clock.get_am_pm(),25,45,0)
                        oled.text("Change Hour:",25,25,0)
                        oled.text("Am or Pm?",25,25,1)
                        Alarm.am_pm_set(encoder.value())
                    oled.show()
                else: #24 hr time
                    if count>2:#statement to end the loop an revert to main operation
                        count=0
                        page=0
                        Alarm.set_flag=True
                        end_change_flag = True
                        break
                    oled.fill(0)
                    oled.text("Change Time:",25,0)
                    if count ==1:
                        oled.text("%02d:%02d" %(Alarm.get_hour(),encoder.value()),25,45)
                        oled.text("Change Minute:",25,25,1)
                        Alarm.minute_set(encoder.value())
                    if count ==2:
                        oled.text("%02d:%02d" %(encoder.value(),Alarm.get_minute()),25,45)
                        oled.text("Change Minute:",25,25,0)
                        oled.text("Change Hour:",25,25,1)
                        Alarm.hour_set(encoder.value())
                    oled.show()
                    
                
                oled.show()
            if page ==2: #this page is for setting the clock
                if Clock.time_type == False: #12hr time
                    if count>3:#statement to end the loop an revert to main operation
                        count=0
                        page=0
                        end_change_flag = True
                        print("broken")
                        break
                    oled.fill(0)
                    oled.text("Change Time:",25,0)
                    if count ==1:
                        oled.text("Change Minute:",25,25,1)
                        oled.text("%2d:    %s" %(Clock.get_hour(),Clock.get_am_pm()),25,45)
                        oled.text("    %2d"%encoder.value(),25,45,1)
                        #oled.text("    %2d"%encoder.value(),25,45,0)
                        Clock.minute_set(encoder.value())
                        #print(page)
                    if count ==2:
                        oled.text("   :%2d %s" %(Clock.get_minute(),Clock.get_am_pm()),25,45)
                        oled.text("%2d"%encoder.value(),25,45,1)
                        #oled.text("%2d"%encoder.value(),25,45,0)
                        oled.text("Change Minute:",25,25,0)
                        oled.text("Change Hour:",25,25,1)
                        Clock.hour_set(encoder.value())
                    if count ==3:
                        oled.text("%2d:%2d " %(Clock.get_hour(),Clock.get_minute()),25,45)
                        oled.text("        %s"%Clock.get_am_pm(),25,45,1)
                        #oled.text("        %s"%Clock.get_am_pm(),25,45,0)
                        oled.text("Change Hour:",25,25,0)
                        oled.text("Am or Pm?",25,25,1)
                        Clock.am_pm_set(encoder.value())
                    oled.show()
                else:
                    if count>2:#statement to end the loop an revert to main operation
                        count=0
                        page=0
                        end_change_flag = True
                        break
                    oled.fill(0)
                    oled.text("Change Time:",25,0)
                    if count ==1:
                        oled.text("%2d:%2d" %(Clock.get_hour(),encoder.value()),25,45)
                        oled.text("Change Minute:",25,25,1)
                        Clock.minute_set(encoder.value())
                    if count ==2:
                        oled.text("%2d:%2d" %(encoder.value(),Clock.get_minute()),25,45)
                        oled.text("Change Minute:",25,25,0)
                        oled.text("Change Hour:",25,25,1)
                        Clock.hour_set(encoder.value())
                    oled.show()
                    
                
                oled.show()
    if end_change_flag ==True:
        end_change_flag =False
        check_page(page)
        
    

    




