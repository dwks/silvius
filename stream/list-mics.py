import pyaudio

pa = pyaudio.PyAudio()  # prints a lot of junk

print ""
print "LISTING OF ALL INPUT DEVICES SUPPORTED BY PORTAUDIO"
print "(any device numbers not shown are for output only)"
print ""

for i in range(0, pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:  # microphone? or just speakers
        print "DEVICE #%d" % info['index']
        print "    %s" % info['name']
        print "    input channels = %d, output channels = %d" \
            % (info['maxInputChannels'], info['maxOutputChannels'])
