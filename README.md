# ISpy
Induced seismicity library

## Scripts:
ISmonitor.py
created 06/07/21, A Butcher

Trigger script which continuously scans a waveform directory and processes new files using the workflow:

1. New waveform files imported into an obspy stream, detrended and bandpass filtered (utils.data_in).
2. A plot of the data is created and displayed.
3. A coincidence function is applied to the stream (trigger.iscoincidence).
4. If events are identified, data are sliced into 5 second parts with P- and S-wave picks added.
5. These are saved as .sac files and .png images.
6. The .sac files are opened in SAC to allow the waveforms to be more accurately picked.
7. User asked if they want a .obs exported. If yes, dir moved to 'Local' dir, if no, dir moved to 'Noise' dir.
8. If .obs file requested, file exported.

Requires SAC to be install. (https://members.elsi.jp/~george/sac-download.html)

## Functions:

### utils.py
file_scanner - Checks and records which waveform files have been processed.
data_in - Seismic data reader with preprocessing and plotting functions.
tr_write - Removes the instrument response, and exports data to a SAC format.

### trigger.py
trigger_check - Function to check the stalta trigger levels using zdetect.
iscoincidence - Coincidence function based on obspy's zdetect function. Identifies triggers and saves sac files with pick times.
sac_picker - SAC wrapper. Opens pick file created from iscoincidence in SAC.
sac_to_nnloc - Exports sac header into an .obs file for NNLOC.

# Installation

Once downloaded the library is installed using
'python setup.py develop'

ISpy uses Obspy, SAC and NNLoc.