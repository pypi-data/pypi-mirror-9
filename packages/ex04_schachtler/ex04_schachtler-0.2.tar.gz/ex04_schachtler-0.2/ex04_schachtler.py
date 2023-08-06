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

def print_lvl(liste, ebene=0):
    '''Diese Funktion erwartet ein positionelles Argument namens
    "liste", das eine beliebige Python-Liste (mit eventuellen
    eingebetteten Listen) ist. Jedes Element der Liste wird (rekursiv)
    auf dem Bildschirm jeweils in einer eigenen Zeile ausgegeben.
    Mit dem zweiten Argument "ebene" können bei eingebetteten Listen
    Tabulatoren eingesetzt werden.
    '''

    for element in liste:
        if isinstance(element, list):
            print_lvl(element, ebene+1)
        else:
            for tab in range(ebene):
                print("\t", end=" ")
            print(element)
