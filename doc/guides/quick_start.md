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
- Start image acquisition

## To keep in mind
### iOptron SkyGuider Pro
- Pushing the right button, decreases RA (and HA): if looking east, the object goes down in the frame.
- Pushing the left button, increases RA (and HA): if looking east, the object goes up in the frame.

### Focus
Tightening the left knob, makes the central line in the bahtinov mask go up. The ring moves to the right.
Tightening the right knob, makes the central line in the bahtinov mask go down. The ring moves to the left.

### Polar alignment
When the Ekos polar alignment indicates an error in azimuth with a positive angle, you should move the base
westwards by turning the right knob. 
When the Ekos polar alignment indicates an error in azimuth with a negative angle, you should move the base
eastwards by turning the left knob. 

When the Ekos polar alignment indicates an error in altitude with a positive angle, you should move the base
down by turning the altitude knob counter clockwise. This moves the base downwards (decreases altitude). 
When the Ekos polar alignment indicates an error in altitude with a negative angle, you should move the base
up by turning the altitude knob clockwise. This moves the base upwards (increases altitude).


