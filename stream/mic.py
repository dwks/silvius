# Silvius microphone client based on Tanel's client.py
__author__ = 'dwk'

import argparse
from ws4py.client.threadedclient import WebSocketClient
import threading
import sys
import urllib
import Queue
import json

class MyClient(WebSocketClient):

    def __init__(self, url, mic=1, protocols=None, extensions=None, heartbeat_freq=None, byterate=16000,
                 show_hypotheses=True,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.mic = mic
        self.show_hypotheses = show_hypotheses
        self.byterate = byterate
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        # set up a queue so data can be grabbed from pyaudio and put here 
        # right away without blocking (we must poll pyaudio quickly)
        Q = Queue.Queue()

        def mic_to_ws():
            import pyaudio
            pa = pyaudio.PyAudio()
            try:
                if self.mic == -1:
                    print >> sys.stderr, "Using default mic"
                    stream = pa.open(
                        rate = self.byterate,
                        format = pyaudio.paInt16,
                        channels = 1,
                        input = True)
                else:
                    print >> sys.stderr, "Using mic #", self.mic
                    stream = pa.open(
                        rate = self.byterate,
                        format = pyaudio.paInt16,
                        channels = 1,
                        input = True,
                        input_device_index = self.mic)
            except IOError, e:
                if(e.errno == 'Invalid sample rate'):
                    print >> sys.stderr, "\n", e
                    print >> sys.stderr, "\nCould not open microphone. 16K sampling not directly supported."
                    print >> sys.stderr, "Instead of using this device directly, please configure it from"
                    print >> sys.stderr, "within alsa or pulseaudio (run pavucontrol), which can do resampling."
                else:
                    print >> sys.stderr, "\n", e
                    print >> sys.stderr, "\nCould not open microphone. Please try a different device."
                return

            try:
                print >> sys.stderr, "\nLISTENING TO MICROPHONE"
                while True:
                    data = stream.read(2048*2)
                    #print >> sys.stderr, "sending", len(data), "bytes... ",
                    #self.send_data(data)
                    Q.put(data)
            except IOError, e:
                print e
            self.send_data("")
            self.send("EOS")

        threading.Thread(target=mic_to_ws).start()

        def send_on():
            while True:
                #print >> sys.stderr, "send"
                q = Q.get()
                self.send_data(q)
        threading.Thread(target=send_on).start()


    def received_message(self, m):
        response = json.loads(str(m))
        #print >> sys.stderr, "RESPONSE:", response
        #print >> sys.stderr, "JSON was:", m
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    if self.show_hypotheses:
                        print >> sys.stderr, '\r%s' % trans.replace("\n", "\\n")
                    print '%s' % trans.replace("\n", "\\n")  # final result!
                    sys.stdout.flush()
                elif self.show_hypotheses:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    print >> sys.stderr, '\r%s' % print_trans,
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print >> sys.stderr, "Received error from server (status %d)" % response['status']
            if 'message' in response:
                print >> sys.stderr, "Error message:",  response['message']


    def closed(self, code, reason=None):
        #print "Websocket closed() called"
        #print >> sys.stderr
        pass


def main():
    content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)16000, format=(string)S16LE, channels=(int)1"
    path = 'client/ws/speech'

    parser = argparse.ArgumentParser(description='Microphone client for silvius')
    parser.add_argument('-s', '--server', default="localhost", dest="server", help="Speech-recognition server")
    parser.add_argument('-p', '--port', default="8019", dest="port", help="Server port")
    parser.add_argument('-r', '--rate', default=16000, dest="rate", type=int, help="Rate in bytes/sec at which audio should be sent to the server.")
    parser.add_argument('-d', '--device', default="-1", dest="device", type=int, help="Select a different microphone (give device ID)")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default=content_type, help="Use the specified content type (default is " + content_type + ")")
    parser.add_argument('--hypotheses', default=True, type=int, help="Show partial recognition hypotheses (default: 1)")
    args = parser.parse_args()

    content_type = args.content_type
    print >> sys.stderr, "Content-Type:", content_type

    uri = "ws://%s:%s/%s?%s" % (args.server, args.port, path, urllib.urlencode([("content-type", content_type)]))
    print >> sys.stderr, "Connecting to", uri

    ws = MyClient(uri, byterate=args.rate, mic=args.device, show_hypotheses=args.hypotheses,
                  save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)
    ws.connect()
    #result = ws.get_full_hyp()
    #print result.encode('utf-8')
    ws.run_forever()

if __name__ == "__main__":
    main()

