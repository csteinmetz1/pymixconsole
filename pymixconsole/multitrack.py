import warnings
import numpy as np

class Multitrack():
    """ Multitrack audio object 
    
    Load audio either directly as a numpy array with shape [samples, channels].

    All channels must have the same number of samples.
    
    """
    def __init__(self, data=None, files=None, num_channels=1, rate=44100, block_size=512, current_index=0):
        self.data          = data
        self.files         = files
        self.num_channels  = num_channels
        self.block_size    = block_size
        self.current_index = current_index

        self.rate = rate # deal with this later

        # if files are given load them
        #if self.files is not None:
        #    self._load_tracks_from_file()
        #else:
        #    self._load_tracks_from_array()

        self._load_tracks_from_array()

        # calculate number of full blocks
        self.num_blocks = int(np.floor(self.num_samples / self.block_size))

        if self.data is None and self.files is None:
            warnings.warn("No multitrack data was loaded.")

    def __iter__(self):
        return self

    def __next__(self):
        next_index = self.current_index + self.block_size

        if next_index <= self.num_samples:
            self.current_index += self.block_size
        else:
            raise StopIteration

        return self.data[self.current_index-self.block_size:self.current_index,:]
    
    def __repr__(self):
        pass

    def _determine_array_size_from_file(self, files):

        max_num_samples    = 0
        total_num_channels = 0

        for track_file in files:
            track_data, track_rate = sf.read(track_file) # load audio (with shape (samples, channels))

            max_num_samples     = np.max([max_num_samples, track_data.shape[0]])
            total_num_channels  += track_data.shape[1] if len(track_data.shape) > 1 else 1
        
        return [max_num_samples, total_num_channels]

    #def _load_tracks_from_file(self):
    #
    #    self.num_samples, self.num_channels = self._determine_array_size_from_file(self.files)
    #
    #    self.data = np.empty([self.num_samples, self.num_channels])
    #
    #    self.loaded_channels = 0
    #    
    #    for track_file in self.files:
    #        track_data, track_rate = sf.read(track_file) # load audio (with shape (samples, channels))
    #
    #        pad_size = self.num_samples - track_data.shape[0]
    #        
    #        if track_rate != self.rate:
    #            raise RuntimeError(f"Track has fs={track_rate}, but project has fs={self.rate}.")
    #
    #        if len(track_data.shape) > 1:
    #            for ch in range(track_data.shape[1]):
    #
    #                self.data[:,self.loaded_channels] = np.pad(track_data[:,ch], (0,pad_size), 'constant')
    #                self.loaded_channels += 1
    #        else:
    #            self.data[:,self.loaded_channels] = np.pad(track_data, (0,pad_size), 'constant')
    #            self.loaded_channels += 1

    def _load_tracks_from_array(self):
        self.num_channels = self.data.shape[1]
        self.num_samples  = self.data.shape[0]
