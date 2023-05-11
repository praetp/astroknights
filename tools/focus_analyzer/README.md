# Introduction

Focus shift during a long, nightly astrophotography session is an annoying fact of life.
As temperature drops during the night. The optical train gets out of focus and your pictures degrade till they become useless.

Using an electronic autofocuser (such as the ZWO EAF) is an essential piece of equipment to address this situation.

Periodic refocusing with one of the of the EKOS algorithms is a reasonable approach but unfortunately the algorithm is not that reliable.
Alas, it does not always yield the optimal result for various reasons. Also, a periodic refocus is not optimal:
either you refocus a lot (but then you lose valuable imaging time) or you do not focus enough (but then the images before your refocus are probably worthless already).

It would be better to continuously keep the OTA in focus as the temperature drops. For this to work we need to know the right coefficient: how many steps do we need to move for every delta in in ambient temperature.

This project intends to discover this coefficient.

# Main goal

With Siril we can learn the FWHM of every image. For every image we also know the temperature and focus position.
We want to know the optimal focus position for a given temperature so that `P = aT + b`. `a` is here the coefficent and `b` the offset we need to learn.
We can use linear regression to learn these values.

However, not all of our images are equally good. Some have a good focus, some mediocre, some outright bad.
We have two possible ways to handle the problem

## Basic linear regresion

Only consider those samples with FWHM < 4 and drop the rest.

## Weighted linear regression

Consider all data but assign a weight to each datapoint which we derive from the FWHM: `weight = 1/(FWHM-2)^2`.
Example: an FWHM of 3 (which is very good), will yield a weight of 1, while a FWHM of 5 (poor) will yield a weight of 1/9.

We can then apply a weighted linear regression.

## One step or two steps ?

It is still unclear if we can combine the data of observations (different targets, moon phases etc) into one model.
Or maybe we should build different models and just average them out somehow ?
At least the following parameters we should keep constant:

- telescope (obviously)
- camera
- offset/gain settings
- exposure time
- siril version ?

# Data sanitization

Some of the data samples are simply not good. (e.g. when the mount got jammed for some reason or where there were many clouds etc).
We first sanitize the data by looking at:

- star roundness: all samples with a star roundness less than 0.85 are discarded
- number of stars: all samples with fewer than 80% of the maximum number of stars (for the dataset)
