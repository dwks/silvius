__author__ = 'tanel'

import argparse
from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib
import Queue
import json
import time
import os

debug_partial = True

def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class MyClient(WebSocketClient):

    def __init__(self, filename, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.fn = filename
        self.byterate = byterate
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened0(self):
        #print "Socket opened!"
        def send_data_to_ws():
            f = open(self.fn, "rb")
            if self.send_adaptation_state_filename is not None:
                print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print >> sys.stderr, "Failed to send adaptation state: ",  e
            for block in iter(lambda: f.read(self.byterate/4), ""):
                #print >> sys.stderr, "Sending", len(block), "bytes"
                self.send_data(block)
            print >> sys.stderr, "Audio sent, now sending EOS"
            self.send("EOS")
        t = threading.Thread(target=send_data_to_ws)
        t.start()
    def opened(self):
        Q = Queue.Queue()

        def mic_to_ws():
            import pyaudio
            pa = pyaudio.PyAudio()
            stream = pa.open(
                rate = 16000,
                format = pyaudio.paInt16,
                channels = 1,
                input = True,
                input_device_index = 2)
            try:
                while True:
                    #print >> sys.stderr, "read..."
                    data = stream.read(2048*2)
                    #print >> sys.stderr, "sending", len(data), "bytes... ",
                    #print >> sys.stderr, data
                    #self.send_data(data)
                    Q.put(data)
                    #print >> sys.stderr, "done"
            except IOError, e:
                print e
                pass
            self.send_data("")
            self.send("EOS")

        #t = threading.Thread(target=send_data_to_ws)
        t = threading.Thread(target=mic_to_ws)
        t.start()

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
                    #print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    if debug_partial:
                        print >> sys.stderr, '\r%s' % trans.replace("\n", "\\n")
                    print '%s' % trans.replace("\n", "\\n")
                    sys.stdout.flush()
                elif debug_partial:
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

    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri", help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int, help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='', help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    parser.add_argument('audiofile', help="Audio file to be sent to the server")
    args = parser.parse_args()

    content_type = args.content_type
    if content_type == '': #and args.audiofile.endswith(".raw"):
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(args.rate/2)
        content_type = "audio/x-raw, layout=(string)non-interleaved, coding=linear, rate=(int)8000, format=(string)S16LE, channels=(int)1"
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)8000, format=(string)S16LE, channels=(int)2"
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)8000, format=(string)S16LE, channels=(int)1"
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)32000, format=(string)S16LE, channels=(int)1"
        content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)16000, format=(string)S16LE, channels=(int)1"
        #content_type = "audio/x-wav"
    print >> sys.stderr, "Content-Type:", content_type


    ws = MyClient(args.audiofile, args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])), byterate=args.rate,
                  save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)
    ws.connect()
    #result = ws.get_full_hyp()
    #print result.encode('utf-8')
    ws.run_forever()

if __name__ == "__main__":
    main()

