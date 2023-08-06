import sys
import textwrap
from colorama import init, Fore, Back

init() # windows compatibility

def podsay(str, length=40):
    return stitch(default_message, build_bubble(str, length))

def stitch(str1, str2):
    l1 = str1.split("\n")
    l2 = str2.split("\n")

    width1 = 100 #max([len(l) for l in l1])

    stitched = ''

    for i in range(max(len(l1), len(l2))):
        try:
            line1 = l1[i]
        except IndexError:
            line1 = ''

        try: 
            line2 = l2[i]
        except IndexError:
            line2 = ''

        stitched += line1 + line2 + "\n"

    return stitched

default_message = '      ' + Fore.GREEN + '..~~~~~~~~....' + Fore.RESET + '          ' + \
  '\n   ' + Fore.GREEN + ',-\'              ``_       ' + Fore.RESET + \
  '\n  ' + Fore.GREEN + '/' + '       ' + Fore.WHITE + 'd@b   d@b' + '    ' + Fore.GREEN + '`\\     ' + Fore.RESET + \
  '\n ' + Fore.GREEN + '|' + '       ' + Fore.WHITE + ':' + Back.BLACK + '* ' + Back.RESET + Fore.WHITE + '@l :' + Back.BLACK + '* ' + Back.RESET + Fore.WHITE + '@l' + Fore.GREEN + '     `\\   ' + Fore.RESET + \
  '\n ' + Fore.GREEN + '/        ' + Fore.WHITE + '`PP   `PP' + Fore.GREEN + '        |  ' + Fore.RESET + \
  '\n' + Fore.GREEN + '<._____     ' + Fore.MAGENTA + '\\____/' + Fore.GREEN + '          \\>' + Fore.RESET + \
  '\n' + Fore.GREEN + '       ````-----------``````  ' + Fore.RESET

def build_bubble(str, length=40):
    bubble = []

    lines = normalize_text(str, length)

    bordersize = len(lines[0])

    bubble.append("  " + "_" * bordersize)

    for i, line in enumerate(lines):
       
        border = get_border(lines, i)

        bubble.append("%s %s %s" % (border[0], line, border[1]))

    bubble.append("  " + "-" * bordersize)

    return "\n".join(bubble)

def normalize_text(str, length):
    lines  = textwrap.wrap(str, length)
    maxlen = len(max(lines, key=len))
    return [ line.ljust(maxlen) for line in lines ]

def get_border(lines, index):
    if len(lines) < 2:
        return [ "<", ">" ]

    elif index == 0:
        return [ "/", "\\" ]
    
    elif index == len(lines) - 1:
        return [ "\\", "/" ]
    
    else:
        return [ "|", "|" ]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: '%s string'" % sys.argv[0]
        sys.exit(0)

    print podsay(sys.argv[1])
