__author__ = 'Nicolai Lessel, 2012-2014'

print('-' * 45, sep='')
print('Stringen - By N Lessel 2012-2014')
print('nicklessel@gmail.com')
print('-' * 45, sep='')
print('')

import time
import os

infile = open('in.txt', 'r')         # opens file for reading
wordlist = ['\n'] + list(infile)     # reads the words from your text file, in.txt, and creates a list called 'wordlist'
infile.close()                       # closes file after reading

start_time = time.time()             # set start time for time elapsed and pwd per second

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
theoreticalnum = 0
n = 0                                                # initialize loop counter
maxlengthcand = 0
maxlength = 0
minlengthcand = 0
minlength = 10000
progress = 0.0

listlength = len(wordlist)-1                         # number of words in the feed list (in.txt)

maxstr = int(input('Enter the max number of words to use per new word generated (1-7), Warning! If you enter more than 5, the output file size can become very large:  ' ))           # input number of strings to use when generating wordlist

# calculations - number of combinations
if maxstr == 1:
    theoreticalnum = pow(listlength, maxstr)

if maxstr == 2:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)

if maxstr == 3:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)

if maxstr == 4:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)

if maxstr == 5:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)

if maxstr == 6:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)+pow(listlength, maxstr-5)

if maxstr == 7:
    theoreticalnum = pow(listlength, maxstr)+pow(listlength, maxstr-1)+pow(listlength, maxstr-2)+pow(listlength, maxstr-3)+pow(listlength, maxstr-4)+pow(listlength, maxstr-5)+pow(listlength, maxstr-6)


print('There are', len(wordlist)-1, 'lines in the list.')
print('Number of words to be generated in new list:', theoreticalnum)     # info on how many new words will be generated
print('Will now generate a new word list using', len(wordlist)-1, 'lines, going from 1 up to', maxstr, 'line(s) at a time.')
sure = (input('Are you sure? y/n  '))

if sure == 'n':
    print('Exiting...')
    exit()

print('-' * 45)     #print('-' * 45, sep='')
print('Working.......')

fout = open('out.txt', 'w')                      # output file - establish new file to write output to

while numwordsgenerated < theoreticalnum:

    # print(a,b,c,d,e)                                                                                                   # debug info
    # print(wordlist[a],wordlist[b],wordlist[c],wordlist[d],wordlist[e],wordlist[f],wordlist[g],sep='')                  # debug info - prints output to screen

    fout.write(wordlist[a].strip('\n')),        # strip command removes the automatic new line, () strips both sides of the string of spaces
    fout.write(wordlist[b].strip('\n')),
    fout.write(wordlist[c].strip('\n')),
    fout.write(wordlist[d].strip('\n')),
    fout.write(wordlist[e].strip('\n')),
    fout.write(wordlist[f].strip('\n')),
    fout.write(wordlist[g].strip('\n')),        # + \n adds new line, + \b adds backspace ---> wordlist[g] + \n
    fout.write(wordlist[h]),

    numwordsgenerated += 1                                             # counts the number of passwords generated

    # ------------------ progress display -----------------------------------------------------------
    progress = numwordsgenerated / theoreticalnum * 100         # calculate progress percentage

    if numwordsgenerated % 1000 == 0:                          # print progress
        print('\r', 'Percent complete: ', round(progress, 2), end='')
    # -----------------------------------------------------------------------------------------------

    #if quit == 'q':
     #   print('Exiting...')
      #  exit()

    n += 1       # add one to the loop (n = n + 1)
    a += 1

    if a > listlength and 1 < maxstr:
        a = 1
        b += 1
        n = 0
    if b > listlength and 2 < maxstr:
        a = 1
        b = 1
        c += 1
        n = 0
    if c > listlength and 3 < maxstr:
        a = 1
        b = 1
        c = 1
        d += 1
        n = 0
    if d > listlength and 4 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e += 1
        n = 0
    if e > listlength and 5 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e = 1
        f += 1
        n = 0
    if f > listlength and 6 < maxstr:
        a = 1
        b = 1
        c = 1
        d = 1
        e = 1
        f = 1
        g += 1
        n = 0

fout.close()                        # closes output file being written to (out.txt)

elapsed_time = time.time() - start_time
print('\n', 'Searching for the longest password generated...')


#open out.txt file - Code to find the longest password generated, comes here...
fout = open('out.txt', 'r')          # open out.txt file
for line in open('out.txt'):
    maxlengthcand = len(line) - 1
    minlengthcand = len(line) - 1
    if maxlengthcand > maxlength:
        maxlength = maxlengthcand
        theword = line
    if minlengthcand < minlength:
        minlength = minlengthcand
fout.close()                        # close out.txt file


print('\n''Done! Output file is: out.txt ')
print('Number of words generated:', numwordsgenerated)
print('Length of the longest word generated was: ', maxlength)
print('Length of the shortest word generated was: ', minlength)
#print('One of the longest words:  ', theword)

print('Time elapsed, seconds: ', round(elapsed_time, 2))
print('Time elapsed, minutes: ', round(elapsed_time / 60, 2))
print('Words generated per second: ', round(numwordsgenerated / elapsed_time, 2))
print('Output file (out.txt) location:')
print(os.getcwd())
#def getSize(out.txt);
   # st = os.stat(out.txt)
   #return st.st_size

print('-' * 45, sep='')
exit()
