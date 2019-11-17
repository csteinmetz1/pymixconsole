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

## Processor API

### Gain

| Parameter     |  Min. | Max. | Default | Units | Type  | Values | 
| ------------- | ----- | ---- | ------- | ----- | ----- | ------ |
| `gain_val`    |  -120 | 12.0 |  0.0    | dB    | float |        |

### Panner

| Parameter    |  Min. | Max. | Default  | Units   | Type   | Values | 
| ------------ | ----- | ---- | -------- | ------- | ------ | ------ |
| `pan_val`    |  0.0  | 1.0  |  0.5     |         | float  |        | 
| `n_outputs`  |    2  |   2  |   2      | outputs | int    |        | 
| `pan_law`    |       |      | "-4.5dB" |         | string | "linear", "constant_power", "-4.5dB" | 

### Equalizer

| Parameter     |  Min. | Max. | Default  | Units   | Type   | Values | 
| ------------- | ----- | ---- | -------- | ------- | ------ | ------ |
| `in_gain`     |  -120 | 12.0 |  0.5     |  dB     | float  |        | 
| `out_gain`    |  -120 | 12.0 |  0.5     |  dB     | float  |        | 
| `bands`       |       |      |          |         |        |        | 

| Band          | Parameter     |  Min. | Max.    | Default      | Units   | Type   | Values |
| ------------- | ------------- | ----- | ------- | ------------ | ------- | ------ | ------ |
| `low_shelf`   |               |       |         |              |         |        |        |
|               | `filter_type` |       |         | "low_shelf"  |         | string |        |
|               | `gain`        | -12.0 | 12.0    |  0.0         |  dB     | float  |        |
|               | `Fc`          |  22.0 | 1000.0  | 80.0         |  Hz     | float  |        |
|               | `Q`           |   0.1 |   10.0  |  0.707       |         | float  |        |
| `first_band`  |               |       |         |              |         |        |        |
|               | `filter_type` |       |         | "peaking"    |         | string |        |
|               | `gain`        | -12.0 | 12.0    |   0.0        |  dB     | float  |        |
|               | `Fc`          |  82.0 | 3900.0  | 200.0        |  Hz     | float  |        |
|               | `Q`           |   0.1 |   10.0  |   0.707      |         | float  |        |
| `second_band` |               |       |         |              |         |        |        |
|               | `filter_type` |       |         | "peaking"    |         | string |        |
|               | `gain`        | -12.0 | 12.0    |   0.0        |  dB     | float  |        |
|               | `Fc`          | 180.0 | 4700.0  | 1000.0       |  Hz     | float  |        |
|               | `Q`           |   0.1 |   10.0  |   0.707      |         | float  |        |
| `third_band`  |               |       |         |              |         |        |        |
|               | `filter_type` |       |         | "peaking"    |         | string |        |
|               | `gain`        | -12.0 | 12.0    |   0.0        |  dB     | float  |        |
|               | `Fc`          | 220.0 | 10000.0 | 5000.0       |  Hz     | float  |        |
|               | `Q`           |   0.1 |   10.0  |   0.707      |         | float  |        |
| `high_shelf`  |               |       |         |              |         |        |        |
|               | `filter_type` |       |         | "high_shelf" |         | string |        |
|               | `gain`        | -12.0 | 12.0    |  0.0         |  dB     | float  |        |
|               | `Fc`          | 580.0 | 20000.0 | 10000.0      |  Hz     | float  |        |
|               | `Q`           |   0.1 |   10.0  |  0.707       |         | float  |        |

```python
import numpy as np
import pymixconsole as pymc

# crate an EQ processor with default params
eq = pymc.processors.Equaliser()

# decrease the input gain
eq.parameters["in_gain"] = -3.0

# change the low-shelf gain
eq.parameters["bands"]["low_shelf"]["gain"] = 6.0

# and increase the cutoff frequency
eq.parameters["bands"]["low_shelf"]["Fc"] = 200.0

# process a block of audio samples
output = eq.process(np.random.rand(512))
```

### Delay

### Compressor

### Algorithmic reverb

## Dependancies
- SciPy (https://www.scipy.org/)
- NumPy (http://www.numpy.org/)
- SoundFile (https://github.com/bastibe/SoundFile)

## References

[Pan-laws](http://www.cs.cmu.edu/~music/icm-online/readings/panlaws/)