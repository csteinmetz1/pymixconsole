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
import glob
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

## Processor API

### Gain

| Parameter     |  Min. | Max. | Default | Units | Type  | Options | 
| ------------- | ----- | ---- | ------- | ----- | ----- | ------- |
| gain          | -80.0 | 24.0 |  0.0    | dB    | float |         |

### Panner

| Parameter    |  Min. | Max. | Default  | Units   | Type   | Values | 
| ------------ | ----- | ---- | -------- | ------- | ------ | ------ |
|  pan         |  0.0  | 1.0  |  0.5     |         | float  |        | 
|  outputs     |    2  |   2  |   2      | outputs | int    |        | 
|  pan_law     |       |      | "-4.5dB" |         | string | "linear", "constant_power", "-4.5dB" | 

### Equalizer

| Parameter        |  Min.     | Max.     | Default  | Units   | Type   | Values | 
| ---------------- | --------- | -------- | -------- | ------- | ------ | ------ |
| low_shelf_gain   |     -24.0 |     24.0 |      0.0 | dB      | float  |        |
| low_shelf_freq   |      20.0 |   1000.0 |     80.0 | Hz      | float  |        |
| first_band_gain  |     -24.0 |     24.0 |      0.0 | dB      | float  |        |
| first_band_freq  |     200.0 |   5000.0 |    400.0 | Hz      | float  |        |
| first_band_q     |       0.1 |     10.0 |      0.7 |         | float  |        |
| second_band_gain |     -24.0 |     24.0 |      0.0 | dB      | float  |        |
| second_band_freq |     500.0 |   6000.0 |   1000.0 | Hz      | float  |        |
| second_band_q    |       0.1 |     10.0 |      0.7 |         | float  |        |
| third_band_gain  |     -24.0 |     24.0 |      0.0 | dB      | float  |        |
| third_band_freq  |    2000.0 |  10000.0 |   5000.0 | Hz      | float  |        |
| third_band_q     |       0.1 |     10.0 |      0.7 |         | float  |        |
| high_shelf_gain  |     -24.0 |     24.0 |      0.0 | dB      | float  |        |
| high_shelf_freq  |    8000.0 |  20000.0 |  10000.0 | Hz      | float  |        |

### Delay

| Parameter        |  Min.     | Max.     | Default  | Units   | Type   | Values | 
| ---------------- | --------- | -------- | -------- | ------- | ------ | ------ |
| delay            |         0 |    65536 |     5000 | samples | int    |        |
| feedback         |       0.0 |      1.0 |      0.3 |         | float  |        |
| dry_mix          |       0.0 |      1.0 |      0.9 |         | float  |        |
| wet_mix          |       0.0 |      1.0 |      0.0 |         | float  |        |

### Compressor

| Parameter        |  Min.     | Max.     | Default  | Units   | Type   | Values | 
| ---------------- | --------- | -------- | -------- | ------- | ------ | ------ |
| threshold        |     -80.0 |      0.0 |      0.0 |      dB | float  |        |
| attack_time      |     0.001 |    500.0 |     10.0 |      ms | float  |        |
| release_time     |       0.0 |      1.0 |    100.0 |      ms | float  |        |
| ratio            |       1.0 |    100.0 |      2.0 |         | float  |        |
| makeup_gain      |     -12.0 |     24.0 |      0.0 |      dB | float  |        |

### Algorithmic reverb

| Parameter        |  Min.     | Max.     | Default  | Units   | Type   | Values | 
| ---------------- | --------- | -------- | -------- | ------- | ------ | ------ |
| room_size        |       0.1 |      1.0 |      0.5 |         | float  |        |
| damping          |       0.0 |      1.0 |      1.0 |         | float  |        |
| dry_mix          |       0.0 |      1.0 |      0.9 |         | float  |        |
| wet_mix          |       0.0 |      1.0 |      0.1 |         | float  |        |
| stereo_spread    |         0 |      100 |       23 |         | int    |        |

## Dependancies
- SciPy (https://www.scipy.org/)
- NumPy (http://www.numpy.org/)
- SoundFile (https://github.com/bastibe/SoundFile)

## References

[Pan-laws](http://www.cs.cmu.edu/~music/icm-online/readings/panlaws/)