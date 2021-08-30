import usbrelay_py
import time
import atexit
import sys

count = usbrelay_py.board_count()
boards = usbrelay_py.board_details()

def end():
    usbrelay_py.board_control("BITFT", 1, 0)
    usbrelay_py.board_control("BITFT", 2, 0)

atexit.register(end)

def help():
    print("ERROR")
    print()
    print(sys.argv[0] + " [r|l] <msec>")
    exit(-1)

bit=1
sec=0

if (len(sys.argv) < 3):
    help()
if (sys.argv[1]=='r'):
    bit=1
elif (sys.argv[1]=='l'):
    bit=2
else:
    help()

if (sys.argv[2].isnumeric()):
    sec=int(sys.argv[2])/1000
else:
    help()

print("Bit " + str(bit) + " for " + str(sec) + " seconds")

usbrelay_py.board_control("BITFT", bit, 1)
time.sleep(sec)
usbrelay_py.board_control("BITFT", bit, 0)
