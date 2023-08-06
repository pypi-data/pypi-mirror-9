#!/usr/bin/env python3
#==================================================================================
#  Copyright:
#            
#      Copyright (C) 2012 - 2015 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#  
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 2 as
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

__version__ = "0.9.5b7"

__doc__ =   """Converts numbers to greek words.
    
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

__all__ = ["numtogreek"]
