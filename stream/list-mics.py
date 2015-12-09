import pyaudio

pa = pyaudio.PyAudio()
for i in range(0, pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    print "DEVICE #%d" % info['index']
    print "    %s" % info['name']
    print "    input channels = %d, output channels = %d" \
        % (info['maxInputChannels'], info['maxOutputChannels'])
