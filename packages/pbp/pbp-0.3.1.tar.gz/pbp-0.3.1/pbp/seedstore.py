#!/usr/bin/env python2
#
# invoke with
# ./seeder.py alice bob 23235
# as alice, and as bob:
# ./seeder.py bob alice 23235 127.0.0.1

class SeedStore():
    # TODO implement locking
    hashlen = 4
    hash_salt = 'pbp hash salt nonce'
    nonce_salt = 'pbp nonce salt nonce'
    seedsize = 48 #(nonce+seed)
    entrysize = 32 #(hashlen+4(len(int))+nonce)

    def __init__(self, key, basedir = '.'):
        self.key = publickey.Identity(key, basedir=basedir)
        self.basedir = basedir

    def save(self, id, seeds):
        indexfn, seedsfn= self.get_filenames(id)
        offset = self.verifyindex(indexfn)
        with open(seedsfn, 'ab+') as sfd, open(indexfn,'ab+') as ifd:
            for i, seed in enumerate(seeds):
                h = nacl.crypto_generichash(seed, self.hash_salt, outlen=self.hashlen)
                n = nacl.crypto_generichash(seed, self.nonce_salt, outlen=nacl.crypto_secretbox_NONCEBYTES)
                sfd.write(nacl.crypto_box(seed, n, self.key.cp, self.key.cs))
                ifd.write(h+pack('<i', offset+i)+n)
                # todo clear sensitive vars
        self.signindex(indexfn)

    def get(self, peer, keyid = None):
        indexfn, seedsfn= self.get_filenames(peer)
        if not os.path.exists(indexfn) and not os.path.exists(seedsfn):
            print 'not found', indexfn, seedsfn
            return None
        if not os.path.exists(indexfn) and os.path.exists(seedsfn):
            raise ValueError("missing seedfile")
        if os.path.exists(indexfn) and not os.path.exists(seedsfn):
            raise ValueError("missing file")
        # verify index file
        seedslen = self.verifyindex(indexfn)
        if seedslen != os.path.getsize(indexfn)/float(self.entrysize):
            raise ValueError('corrupt seed file')

        if keyid:
            return [self.getseed(seedsfn, i, n) for idx, i, n in self.getentries(indexfn, keyid)]
        else:
            # get random seed
            seedsize = (seedslen >> 8) or 1
            part = ((1 << (seedsize<<3)) / seedslen)
            rnd = byte2int(nacl.randombytes(seedsize))
            i = int(rnd / part)
            offset = 0; dir = -1; alt = True
            with open(indexfn,'rbw+') as fd:
                while True:
                    fd.seek(i*self.entrysize)
                    block = fd.read(self.entrysize)
                    if not block:
                        return
                    if block==('\0' * self.entrysize):
                        if alt:
                            if 0<= i+(offset+1)*dir*-1<seedslen:
                                # alternating
                                offset+=1
                                dir*=-1
                            else:
                                # only one direction
                                offset=1
                                alt = False
                        if not(0<=i+offset*dir<seedslen):
                            break
                        i+=offset*dir
                        continue
                    ix = unpack('<i', block[self.hashlen:self.hashlen+4])[0]
                    if ix != i :
                        raise ValueError('invalid index entry')
                    h = block[:self.hashlen]
                    n = block[self.hashlen+4:self.hashlen+4+nacl.crypto_secretbox_NONCEBYTES]
                    return (self.getseed(seedsfn, i, n), h)

    def deletekey(self, peer, key):
        indexfn, seedsfn= self.get_filenames(peer)
        keyid = nacl.crypto_generichash(key, self.hash_salt, outlen=self.hashlen)
        for idx, i, n in self.getentries(indexfn, keyid):
            if key == self.getseed(seedsfn, i, n):
                # purge key
                with open(indexfn,'rbw+') as fd:
                    fd.seek(idx*self.entrysize)
                    fd.write('\0' * self.entrysize)
                with open(seedsfn, 'rbw+') as fd:
                    fd.seek(i*self.seedsize)
                    fd.write('\0' * self.seedsize)
                self.signindex(indexfn)
                return True
        return False

    def count(self, peer):
        indexfn, seedsfn= self.get_filenames(peer)
        idx = 0
        with open(indexfn,'rbw+') as ifd:
            block=ifd.read(4096)
            while block:
                for i in xrange(0, len(block),self.entrysize):
                    if block[i:i+self.entrysize]==('\0' * self.entrysize):
                        # skip deleted blocks
                        continue
                    idx += 1
                block=ifd.read(4096)
        return idx

    def getentries(self, indexfn, keyid):
        idx = 0
        with open(indexfn,'rbw+') as ifd:
            block=ifd.read(4096)
            while block:
                for i in xrange(0, len(block),self.entrysize):
                    if block[i:i+self.hashlen]==keyid:
                        if block[i:i+self.entrysize]==('\0' * self.entrysize):
                            # skip deleted blocks
                            continue
                        yield (idx,
                               unpack('<i', block[i+self.hashlen:i+self.hashlen+4])[0],
                               block[i+self.hashlen+4:i+self.hashlen+4+nacl.crypto_secretbox_NONCEBYTES])
                    idx += 1
                block=ifd.read(4096)

    def verifyindex(self, indexfn):
        if not os.path.exists(indexfn):
            return 0
        if not os.path.exists(indexfn+'.sig'):
            raise ValueError('unsigned seed index')
        # check if index is untampered
        with open(indexfn,'rb') as ifd:
            try:
                publickey.buffered_verify(ifd, None, self.basedir, self = self.key)
            except ValueError:
                raise ValueError('corrupt seed index')
        return int(os.path.getsize(indexfn)/float(self.entrysize))

    def signindex(self,indexfn):
        # resign index file
        state = nacl.crypto_generichash_init()
        with open(indexfn,'rb') as ifd:
            block=ifd.read(4096)
            while block:
                state = nacl.crypto_generichash_update(state, block)
                block=ifd.read(4096)
        self.sign_index_hash(nacl.crypto_generichash_final(state), indexfn)

    def sign_index_hash(self, hashsum, indexfn):
        # sign hashsum
        sig = self.key.sign(hashsum)[:nacl.crypto_sign_BYTES]
        #me.clear()
        with open(indexfn+".sig",'wb') as fd:
            fd.write(sig)

    def getseed(self, seedsfn, i, n):
        with open(seedsfn, 'rwb+') as fd:
            fd.seek(i*self.seedsize)
            seed = nacl.crypto_box_open(fd.read(self.seedsize), n, self.key.cp, self.key.cs)
        return seed

    def get_filenames(self, id):
        ifn="%s/dh/%s/%s.i" % (self.basedir,self.key.name, id)
        sfn="%s/dh/%s/%s.s" % (self.basedir,self.key.name, id)
        return (ifn, sfn)

def byte2int(str):
    res = 0
    for c in str:
        res = (res << 8) + ord(c)
    return res

def test1():
    store = SeedStore('alice', 'test-pbp')
    test_vec=['4'*32,'5'*32,'6'*32,'c'*32,'a'*32,'b'*32, 'de'*16, 'ef'*16, 'gh'*16, 'i'*32, 'j'*32]
    for f in store.get_filenames('asdf'):
        try: os.unlink(f);
        except: pass
    store.save('asdf', test_vec)
    print store.count('asdf')
    test_vec2=['x'*32,'z'*32]
    store.save('asdf', test_vec2)
    print store.count('asdf')

    key = store.get('asdf', '\xeeK\x04\xa4')[0]
    print 'get 4444', repr(key)
    store.deletekey('asdf',key)
    print store.count('asdf')
    print 'reget 4444', repr(store.get('asdf', '\xeeK\x04\xa4'))
    for _ in xrange(14):
        key = (store.get('asdf') or (None,None))[0]
        print 'key', repr(key)
        if key:
            store.deletekey('asdf',key)
            print store.count('asdf')

    store.save('asdf', test_vec2)
    print store.count('asdf')
    for _ in xrange(3):
        key = (store.get('asdf') or (None,None))[0]
        print 'key', repr(key)
        if key:
            store.deletekey('asdf',key)
            print store.count('asdf')

def test2():
    import scrypt, pbp

    test_vec = [nacl.randombytes(32) for _ in xrange(3)]
    # alice and bob share the seeds - see dh or seeder
    astore = SeedStore('alice', 'test-pbp')

    # clear seedstore - only for running clean tests
    for f in astore.get_filenames('bob'):
        try: os.unlink(f);
        except: pass

    astore.save('bob', test_vec)
    print astore.count('bob')

    bstore = SeedStore('bob', 'test-pbp')

    # clear seedstore - only for running clean tests
    for f in bstore.get_filenames('alice'):
        try: os.unlink(f);
        except: pass
    bstore.save('alice', test_vec)
    print bstore.count('alice')

    # alice wants to send a message
    seed, h = astore.get('bob')
    key = scrypt.hash(seed,'pbp crypto seed', buflen=nacl.crypto_secretbox_KEYBYTES)
    (n, c) = pbp.encrypt('hello bob!', k=key)
    astore.deletekey('bob', seed)
    print astore.count('bob')

    # bob receives c, n, h
    for seed in bstore.get('alice', h):
        key = scrypt.hash(seed,'pbp crypto seed', buflen=nacl.crypto_secretbox_KEYBYTES)
        try:
            print pbp.decrypt((n, c), k=key)
            bstore.deletekey('alice', seed)
            print bstore.count('alice')
        except:
            pass

import pysodium as nacl
import publickey
from struct import pack, unpack
import os

if __name__ == '__main__':
    #test1()
    #test2()
    astore = SeedStore('alice', 'test-pbp')
    bstore = SeedStore('bob', 'test-pbp')
    print astore.count('bob')
    print bstore.count('alice')
