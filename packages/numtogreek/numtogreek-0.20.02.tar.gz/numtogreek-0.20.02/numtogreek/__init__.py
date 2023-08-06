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

__version__ = "00.20.02"

__doc__ =   """Converts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, currency) or
           n2g(thenumber, currency, case) or
           n2g(thenumber, currency=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           currency:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower', 'capfirst' or 'upper'. Displays the string as Title Case, lower case, Upper the first letter or UPPER CASE.
                      Default 'title'.
onverts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, currency) or
           n2g(thenumber, currency, case) or
           n2g(thenumber, currency=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           currency:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower', 'capfirst' or 'upper'. Displays the string as Title Case, lower case, Capitalized first letter or UPPER CASE.
                      Default 'title'.
"""

__all__ = ["numtogreek"]
