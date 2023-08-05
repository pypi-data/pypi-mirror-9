#!/usr/bin/env python2
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import reactor, stdio, threads
import binascii, sys, time
import pysodium as nacl
from merkle import MerkleHashTree
from seedstore import SeedStore
from utils import split_by_n
import fcntl, os

PORT = 23235
stack = None

# commands
START_CMD = '0'
REPLY_CMD = '1'
FINAL_CMD = '2'
CLOSE_CMD = '3'
VALID_CMD = '4'

class ECDHFactory(Factory):
    def buildProtocol(self, addr):
        return ECDH()

class ECDH(Protocol):
    def __init__(self):
        self.e = None
        self.active = True
        self.seeds = []
        self.mht = None
        self.mychain = ChainingContext(sys.argv[1],sys.argv[2], 'test-pbp')
        self.mychain.load()

    def send(self, cmd, *data):
        if cmd == VALID_CMD:
            pkt = cmd+'#'.join(data)
        else:
            pkt = cmd+data[0]

        self.transport.write(''.join(self.mychain.send(pkt)))

    def parse(self, data):
        n = data[:nacl.crypto_secretbox_NONCEBYTES]
        self.mychain.receive(n,c)

    def dataReceived(self, data):
        # respond to initial packet
        cmd = data[0]
        if cmd == REPLY_CMD:
            self.answerECDH(data[1:1+nacl.crypto_scalarmult_curve25519_BYTES])
        elif cmd == FINAL_CMD:
            self.endECDH(data[1:1+nacl.crypto_scalarmult_curve25519_BYTES])
        elif cmd == CLOSE_CMD:
            self.validator(data[1:])
        elif cmd == VALID_CMD:
            size, dsize, data = data[1:].split('#',2)
            dump = list(split_by_n(data,nacl.crypto_generichash_BYTES))
            dump.extend([''] * (int(dsize)-len(dump)))
            self.validate(int(size), dump)

    def startECDH(self):
        self.e = nacl.randombytes(nacl.crypto_scalarmult_curve25519_BYTES)
        pub = nacl.crypto_scalarmult_curve25519_base(self.e)
        self.send(REPLY_CMD,pub)

    def answerECDH(self, peer_pub):
        if not self.active: return
        e = nacl.randombytes(nacl.crypto_scalarmult_curve25519_BYTES)
        seed = nacl.crypto_generichash(sys.argv[1]+sys.argv[2]+nacl.crypto_scalarmult_curve25519(e, peer_pub), outlen=32)
        pub = nacl.crypto_scalarmult_curve25519_base(e)
        self.send(FINAL_CMD,pub)
        self.seeds.append(seed)
        print "\r%s" % len(self.seeds),
        sys.stdout.flush()

    def endECDH(self, peer_pub):
        seed = nacl.crypto_generichash(sys.argv[2]+sys.argv[1]+nacl.crypto_scalarmult_curve25519(self.e, peer_pub), outlen=32)
        self.seeds.append(seed)
        print "\r%s" % len(self.seeds),
        sys.stdout.flush()
        # start over
        if self.active == True:
            self.startECDH()

    def validator(self,size):
        self.active = False
        size = min(int(size),len(self.seeds))
        print '\ncreating validator', size
        self.mht = MerkleHashTree(self.seeds[:size])
        dmp = self.mht.dump()
        self.send(VALID_CMD,str(size),str(len(dmp)),''.join(dmp))

    def validate(self, size, dump):
        print '\rvalidating...', size if size else ''
        def verify():
            self.mht.verify(dump)
            print 'saved', len(self.mht.saved)
            # todo fix argparsing!
            store = SeedStore(sys.argv[2], 'test-pbp')
            store.save(sys.argv[1],self.mht.saved)
            reactor.callFromThread(reactor.stop)

        if not self.mht:
            self.mht = MerkleHashTree(self.seeds[:size])
            dmp = self.mht.dump()
            self.transport.write(VALID_CMD+'0#'+str(len(dmp))+"#"+(''.join(dmp)))
            self.send(VALID_CMD,str(len(self.seeds[:size])),str(len(dmp)),''.join(dmp))
        reactor.callInThread(verify)

    #def connectionLost(self, reason):
    #    print '\rconnection lost, aborting...', reason
    #    reactor.stop()

    def connectionMade(self):
        global stack
        print "connection from", self.transport.getPeer().host
        stack = self
        #self.startECDH()

    def close(self):
        self.active = False
        self.send(CLOSE_CMD, str(len(self.seeds)))
        #self.transport.write(CLOSE_CMD+str(len(self.seeds)))

class KeyHandler(Protocol):
    def dataReceived(self, data):
        if data == '\n':
            stack.close()

def clientStart(p):
    p.startECDH()

if len(sys.argv) > 4:
    endpoint = TCP4ClientEndpoint(reactor, sys.argv[4], int(sys.argv[3])).connect(ECDHFactory())
    endpoint.addCallback(clientStart)
else:
    endpoint = TCP4ServerEndpoint(reactor, int(sys.argv[3])).listen(ECDHFactory())

stdio.StandardIO(KeyHandler())
reactor.run()
