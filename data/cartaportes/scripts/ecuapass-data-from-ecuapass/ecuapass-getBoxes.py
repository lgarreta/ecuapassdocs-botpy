#!/usr/bin/env python3

import sys, time
import pyautogui as py
from pyperclip import copy as pyperclip_copy
from pyperclip import paste as pyperclip_paste

def main ():
    outFile = sys.argv [1]
    cboxType = sys.argv [2]

    print ("Locate mouse pointer on field...")
    time.sleep (5)

    if cboxType == "1":
        dataList = iterateComboBox_01 ()
    elif cboxType == "2":
        dataList = iterateComboBox_02 ()

    with open (outFile, "w", encoding="utf-16") as fp:
        for item in dataList:
            fp.write (item + "\n")


def iterateComboBox_01 ():
    print (">>> CBox 01...")
    dataList = []

    lastText = "XXXYYYZZZ"
    while True:
        py.hotkey ("ctrl", "a");py.hotkey ("ctrl","c"); 
        text = pyperclip_paste()
        if (text == lastText):
            break

        dataList.append (text)
        py.press ("down");
        lastText = text 

    return (dataList)


def iterateComboBox_02 ():
    print (">>> CBox 02...")
    #py.PAUSE = 0.1
    dataList = []

    py.hotkey ("ctrl","c"); py.hotkey ("ctrl","v"); py.hotkey ("ctrl","a");
    py.press ("backspace");
    py.press ("down");

    lastText = "XXXYYYZZZ"
    while True:
        py.hotkey ("ctrl","c"); py.hotkey ("ctrl","v")
        text = pyperclip_paste()
        if (text == lastText):
            print (f">>> Fin de los datos")
            break

        dataList.append (text)
        py.hotkey ("ctrl","a"); py.press ("backspace"); 
        py.press ("down");
        lastText = text 

    return (dataList)

main ()
