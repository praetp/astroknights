# Guide for easy targeting

Small guide for easily finding your target when using the iOptron SkyGuider Pro

## Prerequisites

Make sure the ballhead mounted to the declination bracket is in a straigt line with the rest
of the declination bracket.
Set the declination marker to zero.

## Find out the max speed of your ra

According to the manual, when pressing the left/right buttons, your ra will move at 144x the speed.
However, testing has shown these results can vary.
To find the rate for your device, do the following:
(with camera attached and balanced):
Align declination bracket vertically (not really needed, but i do it)
Switch of skyguider pro.
Get a stopwatch ready.
Press middle button (cirkel) and power on skyguider. At the same time start the timer.
The skyguider will start rotating a full circle on the ra-axis and stop when its complete.
Note down the time. (left rotation)
If your press the circle again, it will rotate in the other direction.
Note down the time. (right rotation)
Convert both number to seconds and apply the following formula:

24 * 60 * 60 / seconds

In my case, a full rotation was 00:11:18 minutes, resulting in 127.

This value represents how many seconds the ra moves for every second of pressing the button.
Will call this RLR (left rotation) and RRR (right rotation)


## Step 1: Polar Alignment

Ensure the declination bracket is straight.
Easiest way to do this is to put the polar star in the center, then move the adust the latitude up and down
while ensuring the polaris remains on the vertical line.
Once its straight, align the polar star correctly (eg. use PolarFinder)

## Step 2: Align camera on polaris

Open live viewer on the camera, and ensure polaris is aligned in the center (more or less).
DO NOT change the declination marker for this. This should remain at 0.
Instead use the DEC camera mounting block for moving the camera.
If polaris is to low/high, you need to use the ballhead to position it correctly.
Getting it perfectly centered is not needed. How perfect you need this depends on
your focal length.

## Step 3: Find the position of your target.

Open stellarium, select your target and find the following values:

Hour angle (HA):  example 2:30h = 150minutes
Declination (dec): example 69 degrees

!! Ensure your have stellarium in realtime mode !!

## Note:

Every target can be found by turning the declination bracket either right or left.
Start by calculating the one for turning left. If it's over 120 seconds, change it to the right.
Also be aware:
Turning RA Left, means pushing the button right.
Turning RA Right, means pushing button left.

## Step 4: Change RA

Use the following formulat to determine how many seconds you need to press to turn:
Note: HA should be converted to minutes
Note: Need to use 6hour(360 min) offset because declination is left/right iso up down
Note: Not going to explain the above note. Either you get it or you need to think about it more.

RA Right: (360 - HA) / RLR
RA Left: (360 + HA) / LRL

Example with HA: 2:30h = 150min

RA Right: (360 - 150) * 60 / 127 = 99 seconds
RA Left: (360 + 150) * 60 / 127 = 240 seconds

In this case, the best choice is RA Right, so press RA Left (yes, the opposite) for 90 seconds

## Step 5: Adust declination of your camera

Use the following formula to change your declination:

If previous step was RA Right:
90 degrees - <dec>

example: 
90 - 69 = 21 degrees

If previous step was RA Left:
360 degrees - <dec>

example: 
360 - 69 = 291 degrees

## Step 6: Finetune

If you follow the steps and I made no mistakes while typing this guide, you should be more or less on target.
Finetune if needed

