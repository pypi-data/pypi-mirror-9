import os, sys, time

def printCharByChar(text, millisecounds):
    for line in text:
        print(line,end='')
        sys.stdout.flush()
        time.sleep(millisecounds)




