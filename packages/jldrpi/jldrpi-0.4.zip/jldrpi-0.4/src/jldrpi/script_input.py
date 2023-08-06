"""
    Created on 2015-02-28
    @author: jldupont
"""
import logging
import os
import time

from defs import Pin
        
import RPi.GPIO as gp


def parse_pin_definition(input_list):
    """
    Format:
    
      25:UF ==> pin 25, pull-up,   falling edge
      1:DR  ==> pin 1,  pull-down, rising edge

    """
    result = []
    
    for pindef in input_list:
        try:
            pindef = pindef.lower()
            pin_number_str, props = pindef.split(":")
            
            pin_number = int(pin_number_str)
        except:
            raise Exception("wrong format for entry: %s" % pindef)
            
        pin_number, pull, edge = Pin.parse_and_validate(pin_number, props)
        result.append(Pin(pin_number, pull, edge))

    return result


def event(pin_number):
    
    print "{pin: %s}" % pin_number
    

def set_pins(pins, bounce):
    
    for pin in pins:
        
        pull = gp.PUD_DOWN if pin.pull == Pin.PULL_DOWN else gp.PUD_UP
        edge = gp.FALLING  if pin.edge == Pin.EDGE_FALLING else gp.RISING
        
        pin_number = pin.pin_number
        
        gp.setup(pin_number, gp.IN, pull_up_down = pull)
        
        gp.add_event_detect(pin_number, edge, callback = event, bouncetime = bounce)

        
        

def run(pins=None, debug=False, bounce = 200):
    """
    Entry Point
    """
    
    start_ppid = os.getppid()
    
    if debug:
        logging.info("Process pid: %s" % os.getpid())
        logging.info("Parent pid : %s" % start_ppid)
        logging.info("Starting loop...")

    
    try:
        lpins = parse_pin_definition(pins)
        
    except Exception, e:
        logging.warn(e.message)
        return
    
    try:
        gp.setmode(gp.BCM)
    except:
        logging.warn("Can't set GPIO mode to BCM")
        return
    
    try:
        set_pins(lpins, bounce)
        
    except Exception, e:
        logging.warn("Problem with initialization: %s" % repr(e))
        return


    while True:
        
        current_ppid = os.getppid()
        if current_ppid!=start_ppid:
            logging.warning("Parent exited...")
            break
        
        time.sleep(5)
        
    
#
#