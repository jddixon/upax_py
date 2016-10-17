#!/usr/bin/env python3

# testBoundLog.py

import os
import time
import unittest
from xlattice import Q, checkUsingSHA

from upax.ftlog import BoundLog, FileReader, Log, LogEntry, Reader, StringReader


class TestBoundLog (unittest.TestCase):

    def setUp(self):
        self.uDir = "dev0/U"
        self.pathToLog = "%s/L" % self.uDir
        if os.path.exists(self.pathToLog):
            os.remove(self.pathToLog)

    def tearDown(self):
        pass

    def getGood(self, usingSHA):
        if usingSHA == Q.USING_SHA1:
            GOODKEY_1 = '0123456789012345678901234567890123456789'
            GOODKEY_2 = 'fedcba9876543210fedcba9876543210fedcba98'
            GOODKEY_3 = '1234567890123456789012345678901234567890'
            GOODKEY_4 = 'edcba9876543210fedcba9876543210fedcba98f'
            GOODKEY_5 = '2345678901234567890123456789012345678901'
            GOODKEY_6 = 'dcba9876543210fedcba9876543210fedcba98fe'
            GOODKEY_7 = '3456789012345678901234567890123456789012'
            GOODKEY_8 = 'cba9876543210fedcba9876543210fedcba98fed'
        else:
            # meaningless values, OK for sha2 or sha3
            GOODKEY_1 = '0123456789012345678901234567890123456789abcdef3330123456789abcde'
            GOODKEY_2 = 'fedcba9876543210fedcba9876543210fedcba98012345678901234567890123'
            GOODKEY_3 = '1234567890123456789012345678901234567890abcdef697698768696969696'
            GOODKEY_4 = 'edcba9876543210fedcba9876543210fedcba98f012345678901234567890123'
            GOODKEY_5 = '2345678901234567890123456789012345678901654654647645647654754757'
            GOODKEY_6 = 'dcba9876543210fedcba9876543210fedcba98fe453254323243253274754777'
            GOODKEY_7 = '3456789012345678901234567890123456789012abcdef696878687686999987'
            GOODKEY_8 = 'cba9876543210fedcba9876543210fedcba98fedfedcab698687669676999988'
        return (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
                GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,)

    def doTestLogWithoutEntries(self, usingSHA):

        checkUsingSHA(usingSHA)
        (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
         GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,) = self.getGood(usingSHA)

        t0 = 1000 * (int(time.time()) - 10000)
        # the first line of an otherwise empty log file
        EMPTY_LOG = "%013u %s %s\n" % (t0, GOODKEY_1, GOODKEY_2)
        reader = StringReader(EMPTY_LOG, usingSHA)
        log = BoundLog(
            reader,
            usingSHA,
            self.uDir,
            'L')  # will default to 'L'

        assert log is not None
        self.assertEqual(t0, log.timestamp)
        self.assertEqual(GOODKEY_1, log.prevHash)
        self.assertEqual(GOODKEY_2, log.prevMaster)

        # only first line should appear, because there are no entries
        expected = EMPTY_LOG
        actual = log.__str__()
        self.assertEqual(expected, actual)
        self.assertEqual(0, len(log))

        # disk file must exist and must contain just the one line
        pathToLog = "%s/L" % "dev0/U/"
        assert os.path.exists(pathToLog)
        contents = ''
        with open(pathToLog, "r") as f:
            contents = f.read()
        self.assertEqual(EMPTY_LOG, contents)
        log.close()

    def testLogWithoutEntries(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestLogWithoutEntries(using)

    def setUpTheThree(self, usingSHA):

        (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
         GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,) = self.getGood(usingSHA)

        t0 = int(time.time()) - 10000
        t1 = t0 + 100
        t2 = t1 + 100
        t3 = t2 + 100
        entry1 = LogEntry(t1, GOODKEY_3, GOODKEY_4, 'jdd', 'e@document1')
        entry2 = LogEntry(t2, GOODKEY_5, GOODKEY_6, 'jdd', 'e@document2')
        entry3 = LogEntry(t3, GOODKEY_7, GOODKEY_8, 'jdd', 'e@document3')
        EMPTY_LOG = "%013u %s %s\n" % (t0, GOODKEY_1, GOODKEY_2)
        LOG_W_THREE = EMPTY_LOG + str(entry1) + str(entry2) + str(entry3)
        return (t0, t1, t2, t3, entry1, entry2, entry3, EMPTY_LOG, LOG_W_THREE)

    def doTestMultiEntryLog(self, usingSHA):
        checkUsingSHA(usingSHA)

        (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
         GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,) = self.getGood(usingSHA)

        (t0, t1, t2, t3, entry1, entry2, entry3, EMPTY_LOG, LOG_W_THREE) = \
            self.setUpTheThree(usingSHA)
        reader = StringReader(LOG_W_THREE, usingSHA)
        log = BoundLog(reader, usingSHA, self.uDir, 'L')   # XXX FAILS
        assert log is not None
        self.assertEqual(t0, log.timestamp)
        self.assertEqual(GOODKEY_1, log.prevHash)
        self.assertEqual(GOODKEY_2, log.prevMaster)
        self.assertEqual(3, len(log))

        self.assertTrue(GOODKEY_3 in log)
        entry = log.getEntry(GOODKEY_3)
        self.assertTrue(entry1.equals(entry))

        self.assertTrue(GOODKEY_5 in log)
        entry = log.getEntry(GOODKEY_5)
        self.assertTrue(entry2.equals(entry))

        self.assertTrue(GOODKEY_7 in log)
        entry = log.getEntry(GOODKEY_7)
        self.assertTrue(entry3.equals(entry))

        with open(self.pathToLog, 'r') as f:
            logContents = f.read()
        self.assertEqual(LOG_W_THREE, logContents)
        log.close()

    def testMultiEntryLog(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestMultiEntryLog(using)

    def doTestAddEntry(self, usingSHA):

        checkUsingSHA(usingSHA)
        (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
         GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,) = self.getGood(usingSHA)

        (t0, t1, t2, t3, entry1, entry2, entry3, EMPTY_LOG, LOG_W_THREE) = \
            self.setUpTheThree(usingSHA)
        reader = StringReader(EMPTY_LOG, usingSHA)
        log = BoundLog(reader, usingSHA, self.uDir, 'L')
        assert log is not None
        self.assertEqual(t0, log.timestamp)
        self.assertEqual(GOODKEY_1, log.prevHash)
        self.assertEqual(GOODKEY_2, log.prevMaster)
        self.assertEqual(0, len(log))

        #                   key     srcNodeID
        log.addEntry(t1, GOODKEY_3, GOODKEY_4, 'jdd', 'e@document1')
        self.assertEqual(1, len(log))
        entry = log.getEntry(GOODKEY_3)
        self.assertTrue(entry1.equals(entry))
        self.assertTrue(GOODKEY_3 in log)
        self.assertFalse(GOODKEY_5 in log)

        log.addEntry(t2, GOODKEY_5, GOODKEY_6, 'jdd', 'e@document2')
        self.assertEqual(2, len(log))
        entry = log.getEntry(GOODKEY_5)
        self.assertTrue(entry2.equals(entry))
        self.assertTrue(GOODKEY_5 in log)

        log.addEntry(t3, GOODKEY_7, GOODKEY_8, 'jdd', 'e@document3')
        self.assertEqual(3, len(log))
        entry = log.getEntry(GOODKEY_7)
        self.assertTrue(entry3.equals(entry))
        self.assertTrue(GOODKEY_7 in log)

        log.close()                     # without this next test fails
        with open(self.pathToLog, 'r') as f:
            logContents = f.read()
        self.assertEqual(LOG_W_THREE, logContents)

    def testAddEntry(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestAddEntry(using)

    def doTestWithOpensAndCloses(self, usingSHA):

        checkUsingSHA(usingSHA)

        (GOODKEY_1, GOODKEY_2, GOODKEY_3, GOODKEY_4,
         GOODKEY_5, GOODKEY_6, GOODKEY_7, GOODKEY_8,) = self.getGood(usingSHA)

        (t0, t1, t2, t3, entry1, entry2, entry3, EMPTY_LOG, LOG_W_THREE) = \
            self.setUpTheThree(usingSHA)
        reader = StringReader(EMPTY_LOG, usingSHA)
        log = BoundLog(reader, usingSHA, self.uDir)
        assert log is not None
        self.assertEqual(t0, log.timestamp)
        self.assertEqual(GOODKEY_1, log.prevHash)
        self.assertEqual(GOODKEY_2, log.prevMaster)
        self.assertEqual(0, len(log))
        log.close()

        reader = FileReader(self.uDir, usingSHA)
        log = BoundLog(reader, usingSHA)
        log.addEntry(t1, GOODKEY_3, GOODKEY_4, 'jdd', 'e@document1')
        self.assertEqual(1, len(log))
        entry = log.getEntry(GOODKEY_3)
        self.assertTrue(entry1.equals(entry))
        self.assertTrue(GOODKEY_3 in log)
        self.assertFalse(GOODKEY_5 in log)
        log.close()

        reader = FileReader(self.uDir, usingSHA)
        log = BoundLog(reader, usingSHA)
        log.addEntry(t2, GOODKEY_5, GOODKEY_6, 'jdd', 'e@document2')
        self.assertEqual(2, len(log))
        entry = log.getEntry(GOODKEY_5)
        self.assertTrue(entry2.equals(entry))
        self.assertTrue(GOODKEY_5 in log)
        log.close()

        reader = FileReader(self.uDir, usingSHA)
        log = BoundLog(reader, usingSHA)
        log.addEntry(t3, GOODKEY_7, GOODKEY_8, 'jdd', 'e@document3')
        self.assertEqual(3, len(log))
        entry = log.getEntry(GOODKEY_7)
        self.assertTrue(entry3.equals(entry))
        self.assertTrue(GOODKEY_7 in log)
        log.close()

        with open(self.pathToLog, 'r') as f:
            logContents = f.read()
        self.assertEqual(LOG_W_THREE, logContents)

    def testWithOpensAndCloses(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestWithOpensAndCloses(using)

if __name__ == '__main__':
    unittest.main()