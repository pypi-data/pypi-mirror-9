import os, sys, time

def printCharByChar(text, milliseconds):
    for line in text:
        print(line,end='')
        sys.stdout.flush()
        time.sleep(milliseconds)




