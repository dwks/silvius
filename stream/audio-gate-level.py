# Silvius microphone audio gate tool 
__author__ = 'dwk'

import argparse
import sys

class MikeLevels:

    def __init__(self, mic):
        self.mic = mic
        self.chunk = 0
        self.byterate = 16000

    def run_test(self):
        import pyaudio
        import audioop
        pa = pyaudio.PyAudio()
        sample_rate = self.byterate
        stream = None 
        
        while stream is None:
            try:
                # try adjusting this if you want fewer network packets
                self.chunk = 2048 * 2 * sample_rate / self.byterate

                mic = self.mic
                if mic == -1:
                    mic = pa.get_default_input_device_info()['index']
                    print >> sys.stderr, "Selecting default mic"
                print >> sys.stderr, "Using mic #", mic
                stream = pa.open(
                    rate = sample_rate,
                    format = pyaudio.paInt16,
                    channels = 1,
                    input = True,
                    input_device_index = mic,
                    frames_per_buffer = self.chunk)
            except IOError, e:
                if(e.errno == -9997 or e.errno == 'Invalid sample rate'):
                    new_sample_rate = int(pa.get_device_info_by_index(mic)['defaultSampleRate'])
                    if(sample_rate != new_sample_rate):
                        sample_rate = new_sample_rate
                        continue
                print >> sys.stderr, "\n", e
                print >> sys.stderr, "\nCould not open microphone. Please try a different device."
                global fatal_error
                fatal_error = True
                sys.exit(0)
     
        print >> sys.stderr, "\nLISTENING TO MICROPHONE"
        last_state = None
        while True:
            data = stream.read(self.chunk)
            rms = audioop.rms(data, 2)

            print rms


def setup():
    parser = argparse.ArgumentParser(description='Microphone client for silvius')
    parser.add_argument('-d', '--device', default="-1", dest="device", type=int, help="Select a different microphone (give device ID)")
    args = parser.parse_args()

    run(args)

def run(args):
    a = MikeLevels(args.device)    
    a.run_test()

def main():
    try:
        setup()
    except KeyboardInterrupt:
        print >> sys.stderr, "\nexiting..."

if __name__ == "__main__":
    main()

