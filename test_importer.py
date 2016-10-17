#!/usr/bin/env python3

# testImporter.py

import os
import time
import unittest
import rnglib
from xlattice import Q, checkUsingSHA
from xlattice.u import UDir, fileSHA1Hex, fileSHA2Hex, fileSHA3Hex
from upax import *

rng = rnglib.SimpleRNG(time.time())

DATA_PATH = 'myData'


class TestImporter (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def makeSomeFiles(self, usingSHA):
        """ return a map: hash=>path """

        # create a random number of unique data files of random length
        #   in myData/; take hash of each as it is created, using
        #   this to verify uniqueness; add hash to list (or use hash
        #   as key to map

        checkUsingSHA(usingSHA)
        fileCount = 17 + rng.nextInt16(128)
        files = {}             # a map hash->path
        for n in range(fileCount):
            dKey = None
            # create a random file name                  maxLen   minLen
            (dLen, dPath) = rng.nextDataFile(DATA_PATH, 16 * 1024, 1)
            # perhaps more restrictions needed
            while '.' in dPath:
                (dLen, dPath) = rng.nextDataFile(DATA_PATH, 16 * 1024, 1)
            if usingSHA == Q.USING_SHA1:
                dKey = fileSHA1Hex(dPath)
            elif usingSHA == Q.USING_SHA2:
                dKey = fileSHA2Hex(dPath)
            elif usingSHA == Q.USING_SHA3:
                dKey = fileSHA3Hex(dPath)
            files[dKey] = dPath

        self.assertEqual(fileCount, len(files))
        return files

    def constructEmptyUDir(self, uPath, usingSHA):

        # we are guaranteed that uPath does NOT exist
        self.assertFalse(os.path.exists(uPath))

        s = BlockingServer(uPath, usingSHA)
        self.assertIsNotNone(s)
        self.assertTrue(os.path.exists(s.uPath))
        self.assertEqual(s.usingSHA, usingSHA)

        # subdirectories
        self.assertTrue(os.path.exists(os.path.join(uPath, 'in')))
        self.assertTrue(os.path.exists(os.path.join(uPath, 'tmp')))

        # nodeID
        idPath = os.path.join(uPath, 'nodeID')
        self.assertTrue(os.path.exists(idPath))
        with open(idPath, 'r') as f:
            nodeID = f.read()
        if usingSHA == Q.USING_SHA1:
            self.assertEqual(41, len(nodeID))
            self.assertEqual('\n', nodeID[40])
        else:
            self.assertEqual(65, len(nodeID))
            self.assertEqual('\n', nodeID[64])
        nodeID = nodeID[:-1]                    # drop terminating newline

        self.assertTrue(os.path.exists(os.path.join(uPath, 'L')))   # GEEP
        return s

    def populateEmpty(self, s, fileMap, usingSHA):
        uPath = s.uPath
        fileCount = len(fileMap)

        for key in list(fileMap.keys()):
            s.put(fileMap[key], key, 'testPutToEmpty')
            self.assertTrue(s.exists(key))                  # FAILS
            with open(fileMap[key], 'rb') as f:
                dataInFile = f.read()
            dataInU = s.get(key)
            self.assertEqual(dataInFile, dataInU)

        log = s.log
        self.assertEqual(fileCount, len(log))

        for key in list(fileMap.keys()):
            s.exists(key)
            entry = log.getEntry(key)
            self.assertIsNotNone(entry)
            # STUB: shold examine properties of log entry
        self.assertTrue(os.path.exists(os.path.join(uPath, 'L')))   # GEEP

    def doTestImport(self, usingSHA):
        checkUsingSHA(usingSHA)

        srcPath = os.path.join(DATA_PATH, rng.nextFileName(16))
        while os.path.exists(srcPath):
            srcPath = os.path.join(DATA_PATH, rng.nextFileName(16))

        destPath = os.path.join(DATA_PATH, rng.nextFileName(16))
        while os.path.exists(destPath):
            destPath = os.path.join(DATA_PATH, rng.nextFileName(16))

        # create a collection of data files
        fileMap = self.makeSomeFiles(usingSHA)
        fileCount = len(fileMap)

        # create an empty source directory, populate it, shut down the server
        try:
            s0 = self.constructEmptyUDir(srcPath, usingSHA)
            self.populateEmpty(s0, fileMap, usingSHA)
        finally:
            s0.close()

        # create an empty destination dir
        s1 = self.constructEmptyUDir(destPath, usingSHA)
        s1.close()

        # create and invoke the importer
        importer = Importer(srcPath, destPath,
                            'testImport ' + __version__, usingSHA)
        importer.doImportUDir()

        # verify that the files got there
        s2 = BlockingServer(destPath, usingSHA)
        self.assertIsNotNone(s2)
        self.assertTrue(os.path.exists(s2.uPath))
        self.assertEqual(s2.usingSHA, usingSHA)
        log = s2.log

        for key in list(fileMap.keys()):
            s2.exists(key)
            entry = log.getEntry(key)
            self.assertIsNotNone(entry)

        s2.close()
        self.assertTrue(os.path.exists(os.path.join(destPath, 'L')))

    def testImport(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestImport(using)

if __name__ == '__main__':
    unittest.main()