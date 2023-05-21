#!/usr/bin/python3

from astropy.io import fits
import sys, getopt, os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="fits_focus_extractor")
    parser.add_argument('-o', '--outputfile', required=True)
    parser.add_argument('-i', '--inputdir', required=True)
    args = parser.parse_args()
    inputdir = args.inputdir
    outputfile = args.outputfile

    print ('Input directory is ', inputdir)
    print ('Output file is ', outputfile)

    fits_files = []
    for path in os.listdir(inputdir):
        fullpath = os.path.join(inputdir, path)
        if os.path.isfile(fullpath) and fullpath.endswith("fits"):
            fits_files.append(fullpath)
    fits_files = sorted(fits_files)
    index = 1
    with open(outputfile, 'w') as f:
        f.write("filename,index,temperature,position\n")
        for fits_file in fits_files:
            hdulist = fits.open(fits_file)
            temp = hdulist[0].header['FOCUSTEM']
            position = hdulist[0].header['FOCUSPOS']
            f.write("%s,%d,%2.2lf,%d\n" % (fits_file, index, temp, position))
            index = index + 1
