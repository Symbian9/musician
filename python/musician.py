# SYMBIAN_UID = 0x100002B6#
# Musician, created by Steve Litchfield, now open source.
# to do: add tap-tempo function
# add louder/quieter metronome (diff samples)
# setting for different piano note lengths (within reason)??
# 2008 01 14 - 2.4 fixed for Nokia E70 - William F. Dudley Jr.
# 2008 01 22 - 3.0 fixed stack overflow problem(s), cleaned up some
#            code, improved response time of piano(). - William F. Dudley Jr.
# 2008 01 22 - 3.1 piano tweak, slight speed increase - SL


import appuifw
from graphics import *
import e32
from key_codes import *
import os
import audio
import time
import random
import sysinfo

timer = e32.Ao_timer()
app_lock = e32.Ao_lock()

class Keyboard(object):
    def __init__(self,onevent=lambda:None):
        self._keyboard_state={}
        self._downs={}
        self._onevent=onevent
	self.last_key = None
    def handle_event(self,event):
        if event['type'] == appuifw.EEventKeyDown:
            code=event['scancode']
	    self.last_key = code
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code,0)+1
            self._keyboard_state[code]=1
        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']]=0
        self._onevent()
    def is_down(self,scancode):
        return self._keyboard_state.get(scancode,0)
    def pressed(self,scancode):
        if self._downs.get(scancode,0):
            self._downs[scancode]-=1
            return True
        return False
    def get_last_key(self):
	return self.last_key
    def clear_last_key(self):
	self.last_key = None
keyboard=Keyboard()

version=u'3.1'
soundflag=1
tuninglength=0
registered=0
dummy1=0 # dummy variable, for later extension to the settings file
dummy2=0
volume=-1

appuifw.app.screen='full'
img=None
def handle_redraw(rect):
    if img:
        canvas.blit(img)
appuifw.app.body=canvas=appuifw.Canvas(
    event_callback=keyboard.handle_event,
    redraw_callback=handle_redraw)

img=Image.new(canvas.size) # (a 2 element tuple)
[width,height]=img.size

# sound files put in a list for elegance sake 
soundfiles = [ \
    "metronome.wav", \
    "a.mid", \
    "b.mid", \
    "d.mid", \
    "e.mid", \
    "g.mid", \
    "pc.mid", \
    "pcsharp.mid", \
    "pd.mid", \
    "pdsharp.mid", \
    "pe.mid", \
    "pf.mid", \
    "pfsharp.mid", \
    "pg.mid", \
    "pgsharp.mid", \
    "pa.mid", \
    "pbflat.mid", \
    "pb.mid", \
    "ptopc.mid", \
    ]


def cache_files():
# put all sound files in RAM drive for better performance, if not already there

    if os.path.exists("D:\\ptopc.mid"):
        dummy1=0
    else:
	for filename in soundfiles:
	    fromfile = "E:\\musician\\%s" % filename
	    tofile = "D:\\%s" % filename
	    e32.file_copy(tofile, fromfile)


keycode2filename = { \
    EScancodeStar : "D:\\pc.mid", \
    EScancode7 : "D:\\pcsharp.mid", \
    EScancode4 : "D:\\pd.mid", \
    EScancode1 : "D:\\pdsharp.mid", \
    EScancode0 : "D:\\pe.mid", \
    EScancode8 : "D:\\pf.mid", \
    EScancode5 : "D:\\pfsharp.mid", \
    EScancode2 : "D:\\pg.mid", \
    EScancodeHash : "D:\\pgsharp.mid", \
    EScancode9 : "D:\\pa.mid", \
    EScancode6 : "D:\\pbflat.mid", \
    EScancode3 : "D:\\pb.mid", \
    EScancodeBackspace : "D:\\ptopc.mid", \
    }

def set_volume(S, adj):
    global volume
    S.set_volume(S.current_volume() + adj)
    volume = S.current_volume()
    appuifw.note(u"Volume is now: %s" % volume, "info")

def piano():
    global volume
    filename = "E:\\Musician\\keyboard%3d.raw" % width
    img.load(filename ,callback=handle_redraw)

    appuifw.note(u"You can use up-down to change the volume", "info")
    handle_redraw(())

    delay=0.1 # delay means that loop doesn't burn round so fast that nothing works
    timer.after(delay)
    S = None
    lastfilename = None

    def open_midi(filename):
        if filename != lastfilename:
            if S:
                S.close()
            new_S = audio.Sound.open(filename)
            if (volume != -1):
                new_S.set_volume(volume)
            return new_S
        return S


    # Load an arbitrary midi file to load the volume global value
    S = open_midi(keycode2filename.values()[0])
    volume = S.current_volume()

    while 1:
	if(keyboard.get_last_key() and keycode2filename.has_key(keyboard.get_last_key())):
	    filename = keycode2filename[keyboard.get_last_key()]
	    keyboard.clear_last_key()
	    S.stop()
	    S = open_midi(filename)
            lastfilename = filename
	    S.play(1,0)
        elif keyboard.pressed(EScancodeLeftSoftkey):  #want to exit piano
            S.stop()
            break
        elif keyboard.pressed(EScancodeDownArrow) : # Decrease volume
            set_volume(S, -1)
        elif keyboard.pressed(EScancodeUpArrow):  # Increase volume
            set_volume(S, 1)
        e32.ao_yield()
        timer.after(delay)

def calcdelay(tempo):
    return float(60)/float(tempo) # in seconds


def writetempo(tempo):

    # appuifw.note(u'Tempo: '+str(tempo), "info")

    img.rectangle((0, height/2.0-25, width, height/2.0),0x0000ff, fill=0x0000ff) #blank previous value
    img.text((20,height/2.0-10), u'Tempo (bpm): '+str(tempo) , font='title')


def metronome():
    global soundflag

    tempo=49
    while (tempo<50 or tempo>220): # got to make sure the number's sensible!
        tempo = appuifw.query(u"Tempo (bpm):", "number")
        if (tempo<50 or tempo>220):
            appuifw.note(u"Tempo out of range (50 to 220)", "error")

    delay=calcdelay(tempo)

    if soundflag == 1:
        S = audio.Sound.open("D:\\metronome.wav")

    img.clear(0x0000ff)
    handle_redraw(())
    writetempo(tempo)

    appuifw.note(u"You can use left-right or up-down to nudge this tempo...", "info")
    metroheight = height/3.0


    for n in range(1, 9000): # will eventually return, just in case!

        if soundflag == 1:
            S.play()

        img.rectangle((0,0,width,metroheight),0xff0000, fill=0xff0000)
        handle_redraw(())
        if keyboard.pressed(EScancodeLeftSoftkey):  #want to exit metronome
            if soundflag == 1:
                S.stop()
            break
        elif (keyboard.pressed(EScancodeLeftArrow) or keyboard.pressed(EScancodeDownArrow)) :  #reduce tempo
            tempo=tempo-1
            delay=calcdelay(tempo)
            writetempo(tempo)
        elif (keyboard.pressed(EScancodeRightArrow) or keyboard.pressed(EScancodeUpArrow)):  #increase tempo
            tempo=tempo+1
            delay=calcdelay(tempo)
            writetempo(tempo)

        timer.after(delay)

        if soundflag == 1:
            S.play()

        img.rectangle((0,0,width,metroheight),0x0000ff, fill=0x0000ff)
        img.rectangle((0,height-metroheight-40, width, height-40),0xff0000, fill=0xff0000)
        handle_redraw(())
        if keyboard.pressed(EScancodeLeftSoftkey):  #want to exit metronome
            if soundflag == 1:
                S.stop()
            break
        elif (keyboard.pressed(EScancodeLeftArrow) or keyboard.pressed(EScancodeDownArrow)) :  #reduce tempo
            tempo=tempo-1
            delay=calcdelay(tempo)
            writetempo(tempo)
        elif (keyboard.pressed(EScancodeRightArrow) or keyboard.pressed(EScancodeUpArrow)):  #increase tempo
            tempo=tempo+1
            delay=calcdelay(tempo)
            writetempo(tempo)

        timer.after(delay)

        img.rectangle((0,height-metroheight-40, width, height-40),0x0000ff, fill=0x0000ff)
        handle_redraw(())

def settings():
    global soundflag
    global tuninglength

    state = [u'Off', u'On']
    svalue = [u'1 bar',u'2 bars', u'3 bars']

    data = [(u"Audible metronome",'combo',(state, soundflag)), (u'Tuning length','combo', (svalue, tuninglength))]

    flags = appuifw.FFormEditModeOnly+appuifw.FFormDoubleSpaced
    f = appuifw.Form(data, flags)

    # make the form visible on the UI
    f.execute()
    soundflag = int(f[0][2][1])
    tuninglength = int(f[1][2][1])

def write_settings():
    global registered
    global soundflag
    global tuninglength
    global dummy1
    global dummy2

    CONFIG_DIR='E:\\musician'
    CONFIG_FILE=os.path.join(CONFIG_DIR,'musician.set')
    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        CONFIG_FILE=os.path.join(CONFIG_DIR,'musician.set')
    config={}
    config['registered']= registered
    config['sound']= soundflag
    config['volume']= volume
    config['tuninglength']= tuninglength
    config['param1']= dummy1
    config['param2']= dummy2
    f=open(CONFIG_FILE,'wt')
    f.write(repr(config))
    f.close()


def read_settings():
    global registered
    global soundflag
    global tuninglength
    global volume
    global dummy1
    global dummy2
    CONFIG_FILE='E:\\musician\\musician.set'
    try:
        f=open(CONFIG_FILE,'rt')
        try:
            content = f.read()
            config=eval(content)
            f.close()
            registered=config.get('registered','')
            soundflag=config.get('sound','')
            tuninglength=config.get('tuninglength','')
            volume=config.get('volume',-1)
            dummy1=config.get('param1','')
            dummy2=config.get('param2','')
        except:
            appuifw.note(u"Cannot read settings file", "error")
    except:
        appuifw.note(u"Creating settings file", "info")

def exit_key_handler():
    write_settings()
    appuifw.app.set_exit()

L = [u"Piano", u"Metronome", u"Tune to E", u"Tune to B", u"Tune to G", u"Tune to D", u"Tune to A", u"Settings", u"About", u"exit"]

menu2note = { 2 : "e", 3 : "b", 4 : "g", 5 : "d", 6 : "a" }

def menu():
    S = None
    lastfilename = "silence"
    while(1):
	index = appuifw.popup_menu(L)
	if index == 0:
	    piano()
	elif index == 1:
	    metronome()
	elif(index >= 2 and index <= 6):
	    # playtuning(menu2note[index])
	    filename = "D:\\"+ menu2note[index] +".mid"
	    if S is not None:
		S.stop()
	    if(filename != lastfilename):
		if S is not None:
		    S.close()
		S = audio.Sound.open(filename)
	    S.play((tuninglength+1),0)
	elif index == 7:
	    settings()
	elif index == 8:
	    about()
	elif index == 9:
	    exit_key_handler()
	    return

def about():
    appuifw.note(u"Musician v"+version+"\n(C) 2006-2008 Steve Litchfield\nhttp://3lib.ukonline.co.uk/", "info")

appuifw.app.title = u"Musician"

appuifw.app.exit_key_handler = exit_key_handler
appuifw.app.screen='normal'

read_settings()

cache_files()
menu()
