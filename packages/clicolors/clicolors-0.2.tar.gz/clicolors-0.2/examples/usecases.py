#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clicolors import colors, COLORS, ATTRIBUTES

if __name__=='__main__':

# clicolors Demo
    print colors('clicolors : Lightweight Python script for styling strings in your Linux terminal',fg='black',bg='white',attr='underline')
    print ('Foreground: '+' '.join([colors(color, fg=color) for color in COLORS]))
    print ('Background: '+' '.join([colors(color, bg=color) for color in COLORS]))
    print ('Attributes: '+' '.join([colors(attributes, attr=attributes) for attributes in ATTRIBUTES]))

# example 1
    print colors('Example text 1', fg='blue',bg='red',attr='bold')

# example 2
    print colors('Example text 2', 'blue','red','bold')

# example 3
    print colors('Example text 3', fg='yellow')

# example 4
    print colors('Example text 4', 'yellow')

# example 5
    print colors('Example text 5', bg='green')

# example 6
    print colors('Example text 6',attr='underline')

# example 7
    print colors('Example text 7',bg='cyan',attr='underline',fg='black')


