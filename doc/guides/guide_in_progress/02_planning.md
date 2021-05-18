# Planning
## Identify a target
Use Telescopius to find an interesting target, based on your location and date. 
Be realistic and don't attempt to shoot very faint or small targets if your environment and/or equipment does not allow for it. 
You can apply some basic filters:
- visible over 30 degrees for at least 30 minutes (less atmospheric interference, less light pollution)
- apparent magnitude no more than 10 (depends on the light gathering capabilities of your lens, light sensitivity of your sensor etc)
- apparent size at least 10 arcminutes (example on a 300mm crop sensor)

Use [Clear Outside](https://clearoutside.com) to know when the weather in your location is suitable. Note down when it becomes dark and the what phase of the moon is.

The (apparent) magnitude should be compared with the size of target. 
[E.g. Andromeda has a low magnitude value but appears less bright than you expect because the object is big (magnitude dispersed over a large object)](https://www.cloudynights.com/topic/139079-andromeda-vs-orion/).

## Is the target visible ?
Use Telescopius' telescope simulator or Stellarium. Look at the coordinates for your location and date/time.
Low above the sky (e.g. altitude < 30 degrees) means more light pollution and atmopsheric distortion and slightly shorter exposure times. Also, are you sure there are no physical obstructions (buildings, trees,..) ?
High above the sky means less light pollution and atmospheric distortion and slightly longer exposure times. However, it may be harder to frame a target high in the sky, you may need to push your tripod to the limits :).

## Camera settings
Minimum focal length (FL) to have a decent picture. e.g. at least 500 pixels ? Note that higher FL makes everything else harder, especially if untracked.
Determine aperture (focal ratio). It's recommended to step down one stop (a full stop ? or less?) from the highest aperture to have less lens distortion. E.g. step down from f/5.6 to f/6.3.

### Untracked
Don't be too ambitious on focal length.
Use [NPF formula](https://sahavre.fr/wp/regle-npf-rule/) to determine max exposure time per subexposure.
You can go all the way up to ISO 6400 if needed.

Determine length of each session. Every session means reframing the target because it drifts too far away: higher focal lengths mean shorter sessions.

### Tracked
Long at your camera specs (e.g. at [https://www.photonstophotos.net](https://www.photonstophotos.net) to see what is the optimal ISO setting for your camera.
Subexposure time will be determined by histogram at location and will be constrained by:
- light pollution (it's impossible to have 5' exposures in a Bortle 9 zone)
- ISO setting
- focal ratio
- tracking accuracy


### Untracked and tracked
Determine total integrated exposure time (IET) you will do. Longer is better, however your time may be constrained by:
- storage
- battery life
- weather: no point in continuing when the clouds arrive
- moonlight: you may want to abort when the moon rises
- local curfews :(

## Configure intervalometer in advance.
There are multiple ways to configure your intervalometer. 
Always use a delay (e.g. 10")

What I recommend:

### Short exposures 
By short, I mean, the maximum your camera natively supports (e.g. 30").
- Set camera exposure time to desired exposure time
- Set camera shooting mode to 'continuous' shooting
- On intervalometer: put LONG equal to IET, put INVL to 1s (minimum value) and COUNT to 1s

Example: if you want 1 hour of IET with 5" exposures, you put exposure time to 5", INVL to 1 hour.

Note that very short exposure times (<1s) will be capped by your sensor read speed and storage write speed.

### Long exposures
In this case you have to use the intervalometer as it is intended:
- Set camera exposure time to BULB
- Set camera shooting mode to 'single shot'
- On intervalometer, put LONG and INVL to exposure time plus 1 second and COUNT to the number of subs for the session. 
Don't ask me why you need to add one second.. that is why I saw on my intervalometer.
Also note the intervalometer may not be not superaccurate (especially when it's cold).

Example: if you want 1 hour of IET with 1' exposures, you put exposure time to BULB, LONG and INVL to 1'1" and COUNT to 60.

## Make 40 bias frames
Put lenscap on lens, minimal exposure (e.g. 1/4000). ISO as above. 
FL and aperture does not matter. 
Can be reused if taken previously, even with different lens.
Of course, shoot in RAW format.

## Print out the 'plan'
The plan should at least contain:
- Name of the target
- Equatorial coordinates
- Constellation
- Azimuthal coordinates approx at start time
- Camera settings 
- Intervalometer settings
- (Nautical Dark time)
- (Astro dark time)

Print it out (or memorize it) so you have it available without looking at your phone 
(which is bad for your nightvision).

## Prepare the camera
- Red-eye reduction off
- Image review off
- Lens auto-focus off
- Lens stabilization off
- RAW format, highest resolution
- In camera noise reduction off
- Long exposure noise reduction off (you can leave it on but it will reduce your IET by 50%, no need to make dark frames then)
