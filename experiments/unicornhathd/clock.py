#!/usr/bin/env python3
# based on  https://github.com/jonathanmeaney/unicorn-hat-hd-clock

import time
import datetime

try:
    import unicornhathd as unicorn
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd as unicorn

unicorn.rotation(90) #usb and ethernet on right-hand side
unicorn.brightness(0.45) # put brightness low to save power and reduce impact on night vision
(red, green, blue) = (255, 0, 0)
displayedHourParts = [0, 0]
displayedMinuteParts = [0, 0]

#at 128x speed, this means sleeping approx 0.5s per day_minute 
SIMULATED_SPEED=60.0/128


# There are 4 different types of patterns used when generating
# a number that is to be placed in a rectangle 3X5 pixels. Combinations of these
# are used to create a number pattern such as:
#   * * *
#   *
#   * * *
#   *   *
#   * * *

# 1) * * * Full Row
# 2) *   * Both Sides
# 3)     * Right Side
# 4) *     Left Side

# Composition methods
def fullLine(start, row):
  for x in range(start, start+3):
    unicorn.set_pixel(x, row, red, green, blue)

def bothSides(start, row):
  unicorn.set_pixel(start, row, red, green, blue)
  unicorn.set_pixel(start+2, row, red, green, blue)

def leftSide(start, row):
  unicorn.set_pixel(start, row, red, green, blue)

def rightSide(start, row):
  unicorn.set_pixel(start+2, row, red, green, blue)

# Numbers
def displayZero(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  bothSides(x, y-1)
  bothSides(x, y-2)
  bothSides(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displayOne(x, y):
  clearNumberPixels(x, y)
  rightSide(x, y)
  rightSide(x, y-1)
  rightSide(x, y-2)
  rightSide(x, y-3)
  rightSide(x, y-4)
  unicorn.show()

def displayTwo(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  rightSide(x, y-1)
  fullLine(x, y-2)
  leftSide(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displayThree(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  rightSide(x, y-1)
  fullLine(x, y-2)
  rightSide(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displayFour(x, y):
  clearNumberPixels(x, y)
  bothSides(x, y)
  bothSides(x, y-1)
  fullLine(x, y-2)
  rightSide(x, y-3)
  rightSide(x, y-4)
  unicorn.show()

def displayFive(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  leftSide(x, y-1)
  fullLine(x, y-2)
  rightSide(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displaySix(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  leftSide(x, y-1)
  fullLine(x, y-2)
  bothSides(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displaySeven(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  rightSide(x, y-1)
  rightSide(x, y-2)
  rightSide(x, y-3)
  rightSide(x, y-4)
  unicorn.show()

def displayEight(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  bothSides(x, y-1)
  fullLine(x, y-2)
  bothSides(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displayNine(x, y):
  clearNumberPixels(x, y)
  fullLine(x, y)
  bothSides(x, y-1)
  fullLine(x, y-2)
  rightSide(x, y-3)
  fullLine(x, y-4)
  unicorn.show()

def displayNumber(x,y, number):
  if number == 0:
    displayZero(x,y)
  elif number == 1:
    displayOne(x,y)
  elif number == 2:
    displayTwo(x,y)
  elif number == 3:
    displayThree(x,y)
  elif number == 4:
    displayFour(x,y)
  elif number == 5:
    displayFive(x,y)
  elif number == 6:
    displaySix(x,y)
  elif number == 7:
    displaySeven(x,y)
  elif number == 8:
    displayEight(x,y)
  elif number == 9:
    displayNine(x,y)

# Clears the pixels in a rectangle. x,y is the top left corner of the rectangle
# and its dimensions are 3X5
def clearNumberPixels(x, y):
  for y1 in range(y, y-5, -1):
    for x1 in range(x, x+3):
      # print("x1 = "+str(x1)+" y1 = "+str(y1))
      unicorn.set_pixel(x1, y1, 0, 0, 0)
  unicorn.show()

def displayTimeDots(x, y):
  unicorn.set_pixel(x, y-1, red, green, blue)
  unicorn.set_pixel(x, y-3, red, green, blue)
  unicorn.show()

def show_current(hours, minutes):
    displayTimeDots(7,15)
    hourParts = [ hours // 10, hours % 10 ]
    minuteParts = [ minutes // 10, minutes % 10 ]

    # TIME Details
    # Only update first hour number if it is different to what is currently displayed
    if hourParts[0] != displayedHourParts[0]:
      displayedHourParts[0] = hourParts[0]
      displayNumber(0,15, hourParts[0])

    # Only update second hour number if it is different to what is currently displayed
    if hourParts[1] != displayedHourParts[1]:
      displayedHourParts[1] = hourParts[1]
      displayNumber(4,15, hourParts[1])

    # Only update first minute number if it is different to what is currently displayed
    if minuteParts[0] != displayedMinuteParts[0]:
      displayedMinuteParts[0] = minuteParts[0]
      displayNumber(9,15, minuteParts[0])

    # Only update second minute number if it is different to what is currently displayed
    if minuteParts[1] != displayedMinuteParts[1]:
      displayedMinuteParts[1] = minuteParts[1]
      displayNumber(13,15, minuteParts[1])

    unicorn.show()

def show_target(hours, minutes):
    displayTimeDots(7,5)
    hourParts = [ hours // 10, hours % 10 ]
    minuteParts = [ minutes // 10, minutes % 10 ]

    displayNumber(0,5, hourParts[0])
    displayNumber(4,5, hourParts[1])
    displayNumber(9,5, minuteParts[0])
    displayNumber(13,5, minuteParts[1])

    unicorn.show()


if __name__ == "__main__":
    day_minute = 0
    direction = -1 # 1 or -1
    try:
        while True:
            show_target(9, 56) #M81 Bode
            show_current(day_minute // 60, day_minute % 60)
            day_minute = (day_minute + direction) % (60 * 24)
            time.sleep(SIMULATED_SPEED)

    except KeyboardInterrupt:
        unicorn.off()
