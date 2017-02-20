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
        print "    input channels = %d, output channels = %d, defaultSampleRate = %d" \
            % (info['maxInputChannels'], info['maxOutputChannels'], info['defaultSampleRate'])
        print info
#       try:
#           supports16k = pa.is_format_supported(16000,  # sample rate
#               input_device = info['index'],
#               input_channels = info['maxInputChannels'],
#               input_format = pyaudio.paInt16)
#       except ValueError:
#           print "    NOTE: 16k sampling not supported, configure pulseaudio to use this device"
