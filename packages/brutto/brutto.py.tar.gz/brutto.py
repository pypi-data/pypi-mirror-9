#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       
#          Copyright 2015 @jofpin  <jofpin@gmail.com>
#
#######################################
from random import sample             #
from itertools import chain, product  #
try:                                  #
    from string import (              #
        digits as numb,               #
        letters as lett,              #
        whitespace as spac,           #
        punctuation as symb,          #
    )                                 ###############################
except:                                                             #
    print "\t\nError: Something bad has happened in the import!\n"  #
                                                                    #
#####################################################################
#
# Brutto
#
#############################################################
# Generate characters for gross , very easy strength.       #
#############################################################
#    These are the options , which must customize.          #         
#    letters:> add letters  by default is True.             #
#    numbers:> add numbers. by default is True.             #
#    symbols:> add symbols  by default is False.            #
#    scope:>  add scope. customize value                    #
#############################################################

def brutto(letters=True, numbers=True, symbols=False, space=False, scope=4):

    # Seting of imports
    rang = 1
    base = ""
    base += spac if space else base
    base += lett if letters else base
    base += numb if numbers else base
    base += symb if symbols else base
    base = ''.join(sample(base, len(base)))

    # Return relations
    return ("".join(conex) for conex in chain.from_iterable(product(base, repeat = rel,) for rel in range(rang, scope + rang),))

#for example in brutto(scope=8, letters=True, numbers=True, symbols=False):
    #print example