#!/usr/bin/env python3

# testUpaxNode.py
import time
import unittest
from rnglib import SimpleRNG
from upax.node import *
from upax.ftlog import LogEntry
from xlattice import Q, checkUsingSHA

rng = SimpleRNG(int(time.time()))


class TestUpaxNode (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # tests both sha1 and sha3 versions of code
    def doTestCheckNodeID(self, usingSHA):
        checkUsingSHA(usingSHA)
        for i in range(15):
            count = i + 18
            nodeID = bytearray(count)
            if usingSHA == Q.USING_SHA1 and count == 20:
                try:
                    checkNodeID(nodeID, usingSHA)
                except ValueError as ve:
                    self.fail('unexpected value error on %s' % nodeID)

            elif (usingSHA != Q.USING_SHA1) and count == 32:
                try:
                    checkNodeID(nodeID, usingSHA)
                except ValueError as ve:
                    self.fail('unexpected value error on %s' % nodeID)
            else:
                try:
                    checkNodeID(nodeID, usingSHA)
                    self.fail('expected value error on %s' % nodeID)
                except ValueError as ve:
                    pass

    def testCheckNodeID(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestCheckNodeID(using)

    # ---------------------------------------------------------------

    def doTestPeer(self, usingSHA):
        """ simple integrity checks on Peer type"""

        checkUsingSHA(usingSHA)
        if usingSHA == Q.USING_SHA1:
            nodeID = bytearray(20)
        else:
            # 32-byte key
            nodeID = bytearray(32)
        rng.nextBytes(nodeID)
        pubKey = bytearray(162)         # number not to be taken seriously
        rng.nextBytes(pubKey)
        peer = Peer(nodeID, pubKey, usingSHA)
        self.assertEqual(nodeID, peer.nodeID)
        self.assertEqual(pubKey, peer.rsaPubKey)
        self.assertIsNone(peer.nodeNdx)
        peer.nodeNdx = 42
        try:
            peer.nodeNdx = 43
            self.fail("changed existing nodeID")
        except:
            pass
        self.assertEqual(42, peer.nodeNdx)

        # expect three empty lists
        self.assertEqual(0, len(peer.cnx))
        self.assertEqual(0, len(peer.ipAddr))
        self.assertEqual(0, len(peer.fqdn))

        # verify that nodeNdx must be non-negative integer
        peer2 = Peer(nodeID, pubKey, usingSHA)          # True = sha1
        try:
            peer2.nodeNdx = 'sugar'
            self.fail('successfully set nodeNdx to string value')
        except:
            pass
        peer3 = Peer(nodeID, pubKey, usingSHA)
        try:
            peer3.nodeNdx = -19
            self.fail('successfully set nodeNdx to negative number')
        except:
            pass

    def testPeer(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestPeer(using)

    # ---------------------------------------------------------------

    def testUpaxNode(self):
        """
        """
        pass

    def testStringSerialization(self):
        pass

    def testEquals(self):
        pass

    def testLHash(self):
        pass

if __name__ == '__main__':
    unittest.main()