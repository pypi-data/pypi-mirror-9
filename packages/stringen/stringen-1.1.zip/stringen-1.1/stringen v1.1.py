__author__ = 'Nicolai Lessel, 2012-2013'

# Copyright (C) 2013  Nicolai Lessel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

print('-' * 45, sep='')
print('Stringen - By Nicolai Lessel 2012-2013')
print('-' * 45, sep='')
print('')

fout = open('out.txt','w')                      # output file - establish new file to write output to

infile = open('in.txt','r')                     # opens file for reading
wordlist = ['\n'] + list(infile)                # reads the words from your text file, in.txt, and creates a list called 'wordlist'
infile.close()                                  # closes file after reading


# print('The words in your list are: ', wordlist)     # debug info - prints the words read from the list to the screen


# the following initializes the various counters
a = 1
b = 0
c = 0
d = 0
e = 0
f = 0
g = 0
h = 0

numwordsgenerated = 0                                # counter of word combinations generated
n = 0                                                # initialize loop counter



listlength = len(wordlist)-1                         # displays number of words in the feed list

print('Warning! If you enter more than 5 below, the output file size can become very large. \n')
print('There are', len(wordlist)-1, 'line(s) in the list. \n')

maxstr = int(input('Enter the max number of words to use per new word generated (1-7): '))           # input number of strings to use when generating wordlist


# calculations - number of combinations
if maxstr == 1:
    theoretical = pow(listlength, maxstr)

if maxstr == 2:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)

if maxstr == 3:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)

if maxstr == 4:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)

if maxstr == 5:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)

if maxstr == 6:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)+pow(listlength, maxstr-5)

if maxstr == 7:
    theoretical = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)+pow(listlength, maxstr-5)+pow(listlength, maxstr-6)


# print('There are', len(wordlist)-1, 'lines in the list.')
print('Number of words to be generated in new list:', theoretical)                                     # info on how many new words will be generated
print('A new wordlist will now be generated, using',len(wordlist)-1,'lines, going from 1 up to', maxstr, 'line(s) at a time.')
sure = (input('Are you sure? y/n: '))

if sure == 'n':
    print('Exiting...')
    exit()



print('-' * 45, sep='')

print('Working....... ', end='')


while numwordsgenerated < theoretical:

    # print(a,b,c,d,e)                                                                                                   # debug info
    # print(wordlist[a],wordlist[b],wordlist[c],wordlist[d],wordlist[e],wordlist[f],wordlist[g],sep='')                  # debug info - prints output to screen

    fout.write(wordlist[a].strip('\n')),                            # strip command removes the automatic new line, () strips both sides of the string of spaces
    fout.write(wordlist[b].strip('\n')),
    fout.write(wordlist[c].strip('\n')),
    fout.write(wordlist[d].strip('\n')),
    fout.write(wordlist[e].strip('\n')),
    fout.write(wordlist[f].strip('\n')),
    fout.write(wordlist[g].strip('\n')),                                                              # + \n adds new line, + \b adds backspace ---> wordlist[g] + \n
    fout.write(wordlist[h]),

    numwordsgenerated = numwordsgenerated + 1                                             # counts the number of passwords generated


    #if numwordsgenerated % 100000 == 0:
    #    print('*', end='')


    n = n + 1                                                                             # add one to the loop

    a = a + 1

    if a > listlength and 1 < maxstr:
        a = 1
        b = b + 1
        n = 0
    if b > listlength and 2 < maxstr:
        a = 1
        b = 1
        c = c + 1
        n = 0
    if c > listlength and 3 < maxstr:
        a = 1
        b = 1
        c = 1
        d = d + 1
        n = 0
    if d > listlength and 4 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e = e + 1
        n = 0
    if e > listlength and 5 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e = 1
        f = f + 1
        n = 0
    if f > listlength and 6 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e = 1
        f = 1
        g = g + 1
        n = 0

fout.close()                        # closes output file being written to

print('\n''Done! Output file is: out.txt ')
print('Number of words generated:', numwordsgenerated)
print('-' * 45, sep='')

