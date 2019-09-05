# <img alt="pymixconsole" src="img/icons8-adjust-60.png" height="30"> pymixconsole
Headless multitrack mixing console in Python

## Installation
```
pip install git+https://github.com/csteinmetz1/pymixconsole
```

## Usage
Setup a mixing console with a set of tracks from a multitrack project and apply processing per block.

## Basic processing
``` python
import soundfile as sf
import pymixconsole as pymc

# find all tracks in a directory
multitrack_files = glob.glob("multitrack/*.wav")

# construct Multitrack with list of files
multitrack = pymc.Multitrack(files=multitrack_files)

# construct Console with multitrack object
console = pymc.MixConsole(multitrack)

# iterate over blocks and apply mixing console processing
for block_idx in range(multitrack.num_blocks):
    console.process_block()
```

You can also directly load a multidimensional numpy array to create the `Multitrack` object.
The array must have dimensions of [samples, tracks/channels]

``` python
import numpy as np
import pymixconsole as pymc

data = np.zeros(44100,8)    # one second of audio for 8 mono tracks
rate = 44100                # 44.1 kHz sampling rate

# create the Multitrack object
multitrack = pymc.Multitrack(data=data, rate=rate)
```

## Dependancies
- SciPy (https://www.scipy.org/)
- NumPy (http://www.numpy.org/)
- SoundFile (https://github.com/bastibe/SoundFile)

## References
