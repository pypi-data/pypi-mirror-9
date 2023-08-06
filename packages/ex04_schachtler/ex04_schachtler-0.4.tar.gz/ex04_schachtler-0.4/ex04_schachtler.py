#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Aufgabe Seite 35 & 37 "Python von Kopf bis Fuß"
Der auf Seite 29 entwickelte Code soll nun in eine Python modul
geschrieben werden, damit er immer wieder verwendet werden kann.

Dies ist das Modul "ex04_schachtler.py". Es stellt eine Funktion names
print_lvl() bereit, die eine Liste mit beliebig vielen eingebetteten
Listen ausgibt
'''
import sys

def print_lvl(liste, einzug=False, ebene=0, dat=sys.stdout):
    '''Diese Funktion erwartet ein positionelles Argument namens
    "liste", das eine beliebige Python-Liste (mit eventuellen
    eingebetteten Listen) ist. Jedes Element der Liste wird (rekursiv)
    auf dem Bildschirm jeweils in einer eigenen Zeile ausgegeben.
    Das Argument "einzug" kann bestimmt werden, ob die Listen eingerückt
    werden oder nicht der Standardwert ist False.
    Mit dem driten Argument "ebene" können bei eingebetteten Listen
    Tabulatoren eingesetzt werden.
    Mittels dat kann der Ort der Ausgabe bestimmt werden, Standard ist
    sys.stdout
    '''

    for element in liste:
        if isinstance(element, list):
            print_lvl(element, einzug, ebene+1, dat)
        else:
            if einzug:
                print("\t"*ebene, end='',file=dat)
            print(element, file=dat)
