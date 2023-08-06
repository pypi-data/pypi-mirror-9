#!/usr/bin/env python3
#-*-coding:utf-8-*-

#==================================================================================
#  Copyright:
#            
#      Copyright (C) 2012 - 2015 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#  
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 3 as
#      published by the Free Software Foundation.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this package; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#================================================================================== 

import sys


__enimerothike__ = '30-03-2015'

def metatropi_psifion(psifio):
    """
     Converts digits to greek words
    """
    psifia = {1: "Ένα",
              2: "Δύο",
              3: "Τρία",
              4: "Τέσσερα",
              5: "Πέντε",
              6: "Έξι",
              7: "Επτά",
              8: "Οκτώ",
              9: "Εννέα"}

    try:
        psifio = int(psifio)
        if psifio in psifia.keys():
            return psifia[psifio]
        else:
            return ""
    except ValueError as err:
        print("Πρέπει να δώσετε ψηφίο 0-9.\nΣφάλμα: {0}".format(err))


def metatropi_dekadon(dekad):
    """Converts tens to greek words
    """
    
    apotelesma =''

    dekades = {10: "Δέκα",
              11: "Έντεκα",
              12: "Δώδεκα",
              13: "Δεκατρία",
              14: "Δεκατέσσερα",
              15: "Δεκαπέντε",
              16: "Δεκαέξι",
              17: "Δεκαεπτά",
              18: "Δεκαοκτώ",
              19: "Δεκαεννέα"}

    eikosieneninta ={2: "Είκοσι ",
                     3: "Τριάντα ",
                     4: "Σαράντα ",
                     5: "Πενήντα ",
                     6: "Εξήντα ",
                     7: "Εβδομήντα ",
                     8: "Ογδόντα ",
                     9: "Ενενήντα "}
    
    if int(dekad) in dekades.keys():
        apotelesma = dekades[int(dekad)]
        return apotelesma
    elif int(str(dekad)[0]) in eikosieneninta.keys():
        apotelesma = eikosieneninta[int(str(dekad)[0])]

    return apotelesma + metatropi_psifion(int(str(dekad)[1]))


def metatropi_ekatontadon(arithmos):
    """Converts hundrets to greek words
    """
    apotelesma = ''
    
    ekatontades = {1: "Εκατό ",
              2: "Διακόσια ",
              3: "Τριακόσια ",
              4: "Τετρακόσια ",
              5: "Πεντακόσια ",
              6: "Έξακόσια ",
              7: "Επτακόσια ",
              8: "Οκτακόσια ",
              9: "Εννιακόσια "}
    try:
        if int(arithmos) == 0:
            exit
    except ValueError as err:
            print('\n\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            exit
        
    arithmos = "000"+ str(arithmos)
    arithmos = arithmos[-3:]

    if arithmos[0] != "0":
        try:
            if int(arithmos[0]) in ekatontades.keys():
                apotelesma = ekatontades[int(arithmos[0])]
        except ValueError as err:
            print('\n\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            exit
##            raise ValueError('Ο αριθμός που δώσατε είναι πολύ μεγάλος ή δεν είναι αριθμός.')
        
    if arithmos[1] != "0":
        apotelesma = apotelesma + metatropi_dekadon(arithmos[1:])
    
    else:
        apotelesma = apotelesma + metatropi_psifion(arithmos[2])

    return apotelesma


def n2g(thenumber, nomisma=False, case='title' ):
    """Converts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, nomisma) or
           n2g(thenumber, nomisma, case) or
           n2g(thenumber, nomisma=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           nomisma:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower' or 'upper'. Displays the string as Title Case, lower case or UPPER CASE.
                      Default 'title'.
    """
    version = '0.7.9beta'
    
    if case not in ('lower', 'upper', 'title'):
        return
        
    place = {0: " ",
            1: " Χιλιάδες ",
            2: " Εκατομμύρια ",
            3: " Δισεκατομμύρια ",
            4: " Τρισεκατομμύρια ",
            5: " Τετράκις Εκατομμύρια ",
            6: " Πεντάκις Εκατομμύρια ",
            7: " Εξάκις Εκατομμυρια ",
            8: " Έπτάκις Εκατομμύρια "}
    
    replacements = {"Ένα": "Μία",
                  "Τρία": "Τρείς",
                  "Τέσσερα": "Τέσσερις",
                  "Δεκατρία": "Δεκατρείς",
                  "Δεκατέσσερα": "Δεκατέσσερις",
                   "Διακόσια": "Διακόσιες",
                  "Τριακόσια": "Τριακόσιες",
                  "Τετρακόσια": "Τετρακόσιες",
                  "Πεντακόσια": "Πεντακόσιες",
                  "Έξακόσια": "Έξακόσιες",
                  "Επτακόσια": "Επτακόσιες",
                  "Οκτακόσια": "Οκτακόσιες",
                  "Εννιακόσια": "Εννιακόσιες"
                    }
    
    thenumber = str(thenumber).strip()
    dekadika = ''
    dol = ''
    decplace = thenumber.find(".")
    count = 0
    
    if decplace >= 0:
        temp = thenumber[decplace + 1:]
        if len(temp) > 2:
            temp = temp[:2]
        if len(temp) == 1: # If the number is .6 make it .60
            temp = temp + '0'
        
        if int(temp[:2]) == 0:
            dekadika = ''
        else:
            dekadika = metatropi_dekadon(temp[:2])
        thenumber = thenumber[:decplace]

    while thenumber != "":
        temp = metatropi_ekatontadon(thenumber[-3:])
        if temp != "":
            if count == 1:
                for k, v in replacements.items():
                    if k in temp:
                        temp = temp.replace(k, v)
                        
            dol = temp + place[count] + dol
            
        if len(thenumber) > 3:
            thenumber = thenumber[:-3]
        else:
            thenumber = ""
        count += 1
    
    if dol == "":
        dol = "Μηδέν"
    elif dol == "Ένα Χιλιάδες ":
        dol = "Χίλια"

    else:
        if dol.startswith("Ένα Χιλιάδες "):
            dol = dol.replace("Ένα Χιλιάδες ", "Χίλια ")
        if dol.find("Ένα Εκατομμύρια") != -1:
            dol = dol.replace( "Ένα Εκατομμύρια", "Ένα εκατομμύριο")
        if dol.find("Ένα Δισεκατομμύρια") != -1:
            dol = dol.replace("Ένα Δισεκατομμύρια", "Ένα Δισεκατομμύριο")
        if dol.find("Ένα Τρισεκατομμύρια") != -1:
            dol = dol.replace("Ένα Τρισεκατομμύρια", "Ένα Τρισεκατομμύριo")
        if dol.find("Ένα Τετράκις Εκατομμύρια") != -1:
            dol = dol.replace("Ένα Τετράκις Εκατομμύρια", "Ένα Τετράκις Εκατομμύριο")
        if dol.find("Ένα Πεντάκις Εκατομμύρια") != -1:
            dol = dol.replace("Ένα Πεντάκις Εκατομμύρια", "Ένα Πεντάκις Εκατομμύριο")
                
    if dekadika == '':
        dekadika = ' '
    else:
        if dekadika == "Ένα":
            dekadika = " και Ένα"
        else:
            dekadika = " και {0}".format(dekadika)  
    if nomisma:
        if dekadika == '' or dekadika == ' ' or dekadika == None:
            greekword = "{0} Ευρώ".format(dol.strip())
        else:
            greekword = "{0} Ευρώ {1} λεπτά".format(dol.strip(), dekadika)
    else:
        greekword = dol.strip() + dekadika
        
    if case == 'lower':
        return greekword.lower().strip()
    elif case == 'upper':
        return greekword.upper().strip()
    else:
        return greekword.strip()
    
    
if __name__ == '__main__':
##    print(n2g(1524.00, True))
##    print(n2g(1524.12, True, 'lower'))
##    print(n2g(1524.12, True, 'upper'))
##    for i in (1000000, 3000000, 4000000):
##        print(n2g(i))
    print(n2g(4154524.621, False))
    print(n2g(4000000.99))
    print(n2g(4154524.6, False))
    print(n2g(99999999999999.98))
    print(n2g(9999999999990999999999))
                  
##    print(n2g(1524.12, False, 'lower'))
##    print(n2g(111524.12, False, 'upper'))
##
#     for i in range(0, 50000, 1000):
#         print("{0:>8}:{1}".format(i, n2g(i)))
    
#     print(n2g.__doc__)
    print(n2g(999999999999999999999.09))
