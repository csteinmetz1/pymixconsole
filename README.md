# <img alt="pymixconsole" src="img/icons8-adjust-60.png" height="30"> pymixconsole
Headless multitrack mixing console in Python

## Installation
```
pip install git+https://github.com/csteinmetz1/pymixconsole
```

## Usage
Setup a mixing `console` with a set of tracks from a multitrack project and apply processing per block.
By default, a `console` will contain n channels and each channel will have a series of default processors:

``` gain -> polarity inverter -> parametric EQ -> compressor -> gain (fader) -> stereo panner ```

These are setup in such a way that if you do not modify their settings the signal should pass largely unprocessed. 
Additionally a `console` is initialized with two effect busses, one for reverb and one for delay. 
Finally there is a master bus which sums the output of all the busses and channels and then applies a simple
processing chain:

``` parametric EQ -> compressor ```

In the example below you can see how to initialize a `console` and then pass multitrack data into the console
and process it block by block to get the output.

## Basic processing

One way to apply processing is to create a multidimensional array of shape [samples, tracks/channels],
where each channel is a mono stream of audio, which will be processed by the associated channel in the console.

In this example we create an array with 8 channels of audio and then instantiate a default console with 8 channels.
Then we iterate over the input data by the `block_size` and we pass each block to the console's `process_block()` 
function, which takes this array, applies each channel processor, and return a stereo mix. We then store this output
in our pre-allocated array. We finally save this data to a `.wav` file with pySoundFile as the end. 

``` python
import numpy as np
import soundfile as sf
import pymixconsole as pymc

data = np.random.rand(44100,8)   # one second of audio for 8 mono tracks
rate = 44100                     # 44.1 kHz sampling rate
block_size = 512                 # processor block size

# create a mix console with settings that match our audio data
console = pymc.Console(block_size=block_size, sample_rate=rate, num_channels=8)

# array to hold the output of the console (stereo)
out = np.empty(shape=(data.shape[0], 2))

# iterate over each block of data
for i in range(data.shape[0]//block_size):

    start = i * block_size 
    stop  = start + block_size

    out[start:stop,:] = console.process_block(data[start:stop,:])

# save out the processed audio
sf.write("output.wav", out, rate)
```

## Console control

pymixconsole provides a high level of control over how the mix console is set up.
By default, a console will include the supplied number of channels, as well as two
busses (one for reverb, one for delay) and a master bus which features a compressor 
and equalizer. By default each channel is created with a pre-gain, polarity inverter, 
equaliser, compressor, post-gain, and a panner. 

There are three levels of processors for each channel: pre-processors, core-processors, 
and post-processors. The distinction is useful since we want to impose some constraints
on how these processors may be randomized in our `randomize()` method. The simple explanation
is that the order of pre and post processors is never shuffled, while core-processors can be.

The defaults were chosen to be a good starting place for basic processing, but the 
user can customize this completely. For example, we can at any time add an extra processor
to a channel as follows. Here we add a second compressor to the third channel's core-processors 
(zero-indexed), and then change the threshold parameter.

```python
console.channels[2].processors.add(pymc.processors.Compressor(name="second-comp"))
console.channels[2].processor.get("second-comp").parameters.threshold.value = -22.0
```

## Processor API

A number of basic processor units are included which can be included
on a channel, bus, or the master bus. 

- Gain
- Polarity inverter
- Converter
- Panner 
- Equaliser 
- Compressor 
- Delay
- Distortion
- Reverb

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

## Cite
If you use this in your work please consider citing: 
```
  @article{steinmetz2020mixing,
            title={Automatic multitrack mixing with a differentiable mixing console of neural audio effects},
            author={Steinmetz, Christian J. and Pons, Jordi and Pascual, Santiago and Serrà, Joan},
            journal={arXiv:2010.10291},
            year={2020}}
```