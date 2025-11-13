# Overview

Using the OpenEXR core API, this sample demonstrates:
* the use of lossy HTJ2K compression in OpenEXR; and
* the use of HTJ2K resolution scalability to extract lower resolution images.

The lossy HTJ2K images are compatible with the current OpenEXR HTJ2K decoder.

The sample is not intended for performance testing.

# Quickstart

```
git clone --recurse-submodules https://github.com/sandflow/lossy-j2k-exr.git
cd lossy-j2k-exr
mkdir build
cd build
cmake ..

# transcode an OpenEXR scanline file to an HTJ2K lossy file
# the q parameter (QStep) controls the compression level and should be larger than 1/2^(sample depth)
./bin/exrj2klossy_enc SPARKS_ACES_01000.exr SPARKS_ACES_01000.q.exr -q 0.001

# transcode the HTJ2K lossy file back to baseband EXR file
./bin/exrmetrics SPARKS_ACES_01000.q.exr -o SPARKS_ACES_01000.q.none.exr --convert -z none

# generate a 4x lower resolution image using the HTJ2K resolution scalability features
# the s parameter controls the number of resolution levels skipped when decoding
./bin/exrj2klossy_dec SPARKS_ACES_01000.q.exr SPARKS_ACES_01000.2.exr -s 2

```