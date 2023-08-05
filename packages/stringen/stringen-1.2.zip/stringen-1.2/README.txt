

Prog:	Stringen 1.2 (Python 3.3.2)
Type:	Dictionary/wordlist/password generator.	
---------------------------------------------------------------------------------------------------------------------------
Author:	Nicolai Lessel 
E-mail:	nicklessel@gmail.com
Date:	Oct 2, 2013 - Aug 23, 2014

Feedback is welcome at the e-mail address provided.

Sections:
I.	Background
II.	Instructions
III.	Examples
IV.	Wish List
V.	Version history
VI.	License agreement


I.	Background
---------------------------------------------------------------------------------------------------------------------------
It all began, when one day, I went to open a RAR file that I had created some time ago, only to realize that I had forgotten the password. 

Things I knew about the RAR password:
1.	the password was long (more than 12 characters), so brute force was out of the question.
2.	the password was created from several words and numbers (my guess was 3-4).
3.	the words (at least some of them), used in making the password are most likely NOT to be found in a dictionary.

So, with this knowledge, brute force and regular dictionary attack was a no go. 
What I was able to do, was to put together a list of around 15-20 words and numbers, which I believed could be part of the password. 
Although this was great, I quickly became aware, that I had no idea of how many of these words and numbers were combined, to form the password.
I quickly did the math on how many possible passwords could be created when using a list of just 15-20 words, stringing anything from 2 to 5 of them together at a time, to make the password. It was way more than I cared to do by hand..lol.
I looked around on the net in an attempt to find a program that would do this for me, but no luck. Some were very close, but not what I really needed.
So, the only solution left was to write the program myself. 

The input (in.txt) would consist of a list of words and numbers, the ones I remember having used in the past to create passwords. 
The output (out.txt) would be a list of generated passwords (all possible combinations of the items in the in.txt file), which could then be used in a dictionary attack.

I have limited programming experience using Pascal and C++, but recently discovered Python and thought I'd give it a go. So after digging into Python, I started writing this program. 

To make a long story short, the program works! I got my list created, used it in a dictionary attack and was able to recover the contents of my RAR file.

I decided to make this program available to everyone, because there is nothing more frustrating, than having that file in front of you and 'almost' remembering the password. 


II.	Instructions
---------------------------------------------------------------------------------------------------------------------------
I used Python 3.3.2. I tested this program with Python 2.7.5 and received errors. 
I now know that I probably should have written it for Python 2.7 for better compatibility. Sorry for that oversight, I'm a neewb ;-)

*	The program expects a file 'in.txt' to be located in same folder as the program itself. 
*	This 'in.txt' file contains the words and/or numbers that you want to use. 
*	Use one word/number/item per line, starting with the first line.
*	Use Notepad or similar to edit the 'in.txt' file. 
*	Make sure that there are no spaces or other formatting after the last item/line. One way to ensure this is to press DEL 	key at the end of the last item, thereby deleting anything below or after this point.
*	If spaces are needed in the passwords, then a space can be added as an item on one of the lines. So, instead of 	writing your word/number on one of the lines, just press the spacebar and then ENTER for the next line.
*	Output file will be 'out.txt' in same folder as program.


III.	Examples
---------------------------------------------------------------------------------------------------------------------------
The time it takes the program to generate the passwords varies greatly. A setting of 4 items (concatenation), with 22 items in the 'in.txt' file takes my computer around 6 seconds. Going from 4 items to 5, will increase the time quite a bit and even longer going to 6 items.

Times, number of passwords generated and resulting file size using the included 'in.txt' file:

22 items/lines, setting 3: ca. 1 second, passwords 11,154, output file size 192KB
22 items/lines, setting 4: ca. 6 seconds, passwords 245,410, output file size 5.26MB
22 items/lines, setting 5: 1min 56sec, passwords 5,399,042, output file size 142MB
22 items/lines, setting 6: 43min 20sec, passwords 118,778,946, output file size 3.63GB

As can be seen from the numbers, start with a low setting.

When generating 5.4M passwords, I get an average of 52000 passwords per second.


IV.	Wish List
---------------------------------------------------------------------------------------------------------------------------
1.	Multi-core CPU and GPU support
2.	Stat: time spent generating passwords and passwords per second. Added in ver. 1.2
3.	Estimated output file size
4.	Progress indicator. Added in ver. 1.2
5.	Stat: length of longest password generated. Added in ver. 1.2


V.	Version history
---------------------------------------------------------------------------------------------------------------------------
See included "CHANGES.txt"


VI.	License agreement
---------------------------------------------------------------------------------------------------------------------------
Copyright (C) 2013-2014  Nicolai Lessel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.