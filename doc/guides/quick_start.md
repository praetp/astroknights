# Astrophotography field guide - quick start
These are the steps you have to do every evening:
- Deploy your gear (if possible in the daytime)
- Determine target and note down its coordinates
- Set focal length to intended (typically maximum).
- Get declination right for target
- Get balance right in two axes based on eventual focal length and declination (see steps before)
- Acquire focus using a bright target such as Vega or Deneb. Don't modify anymore after this point. 
- Polar alignment with Ekos
- Target finding using target solving with ZWO (did you remove lenscap ?). 
	Alternative star hopping : (you may want to use shorter focal length - don't touch the focus ring !): prefer to use target solving in fact..
- Update position in EKOS (through Kstars)
- Set focal length right again if you changed it
- Start Guiding calibration
- Check focus again !
- Start image acquisition

## To keep in mind
### iOptron SkyGuider Pro
- Pushing the right button, decreases RA (and HA): if looking east, the object goes down in the frame.
- Pushing the left button, increases RA (and HA): if looking east, the object goes up in the frame.

### Focus
Tightening the left knob, makes the central line in the bahtinov mask go up. The ring moves to the right.
Tightening the right knob, makes the central line in the bahtinov mask go down. The ring moves to the left.

### Polar alignment
#### Polar scope polar alignment
Steps:
- Bring Polaris in frame with the recticle illuminated.
- Put polaris in the center. When moving altitude up (or down) all the way the outermost circle, Polaris should be exactly at 12h (or 6h).
  If this is not the case, press the RA buttons to correct for this.
- Look at the Polar alignment app where to put Polaris. Adjust the knobs to get Polaris in the right place. Some indication about the error: 
  The polar scope has 6 ticks per 'hour' so this means in total 72 ticks. One tick is then equal to: 
```
2*40*pi=72*x
      x=3.5'
```
  In other words, if you make a mistake of one tick, your error is at least 3.5', which is already a lot.

#### Ekos Polar alignment assistent
When the Ekos polar alignment indicates an error in azimuth with a positive angle, you should move the base
westwards by turning the right knob. 
When the Ekos polar alignment indicates an error in azimuth with a negative angle, you should move the base
eastwards by turning the left knob. 

When the Ekos polar alignment indicates an error in altitude with a positive angle, you should move the base
down by turning the altitude knob counter clockwise. This moves the base downwards (decreases altitude). 
When the Ekos polar alignment indicates an error in altitude with a negative angle, you should move the base
up by turning the altitude knob clockwise. This moves the base upwards (increases altitude).


