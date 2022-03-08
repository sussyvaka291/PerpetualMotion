# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from threading import Thread


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
GREY = 144/255, 136/255, 136/255, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 150
RAMP_LENGTH = 725


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1,.1, 1) # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()
s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=2)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    staircaseSpeedText = '0'


    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def toggleGate(self):
        cyprus.set_servo_position(2, 1)
        sleep(1)
        cyprus.set_servo_position(2, 0)
        print("Open gate")

    def toggleStaircase(self):
        cyprus.set_pwm_values(1, period_value=100000, compare_value=10000*self.staircaseSpeed.value, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(5.5)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        print("Turn on and off staircase here")
        
    def toggleRamp(self):
        s0.start_relative_move(28.5)
        while s0.is_busy():
            sleep(1)
        s0.go_until_press(0, self.rampSpeed.value * 6400)
        print("Move ramp up and down here")

    def threadtoggleRamp(self):
        Thread(target=self.toggleRamp, daemon=True).start()

    def auto(self):
        self.ramp.disabled = True
        self.gate.disabled = True
        self.staircase.disabled = True
        self.ids.gate.color = GREY
        self.ids.staircase.color = GREY
        self.ids.ramp.color = GREY
        cyprus.set_pwm_values(1, period_value=100000, compare_value=10000*self.staircaseSpeed.value, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(5.6)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        cyprus.set_servo_position(2, 1)
        sleep(1)
        cyprus.set_servo_position(2, 0)
        sleep(1.1)
        s0.start_relative_move(28.5)
        while s0.is_busy():
            sleep(1)
        s0.go_until_press(0, self.rampSpeed.value * 6400)
        sleep(20)
        print("Run through one cycle of the perpetual motion machine")

    def threadauto(self):
        Thread(target=self.auto, daemon=True).start()
        
    def setrampSpeed(self, speed):
        s0.set_speed(self.rampSpeed.value)
        print("Set the ramp speed and update slider text")
        
    def setstaircaseSpeed(self, speed):
        #cyprus.set_pwm_values(1, period_value=100000, compare_value=10000*self.staircaseSpeed.value, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        print("Set the staircase speed and update slider text")
        
    def initialize(self):
        cyprus.initialize()
        cyprus.setup_servo(2)
        s0.go_until_press(0, 3 * 6400)
        print("Close gate, stop staircase and home ramp here")

    def resetColors(self):
        self.ids.gate.color = GREY
        self.ids.staircase.color = GREY
        self.ids.ramp.color = GREY
    
    def quit(self):
        print("Exit")
        MyApp().stop()

sm.add_widget(MainScreen(name = 'main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
