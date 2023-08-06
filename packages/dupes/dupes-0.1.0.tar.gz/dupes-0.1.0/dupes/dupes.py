#!/usr/bin/env python

import os
import hashlib

__author__ = "Devin Kelly"


class Dupes(object):

    """Docstring for Dupes. """

    def __init__(self):
        """
        :desc: Initialize, get list of files
        """

        self.pwd = os.getcwd()
        self.files = [f for f in os.listdir(self.pwd) if
                      os.path.isfile(os.path.join(self.pwd, f))]
        self.hashes = {}
        self.duped_hashes = {}
        self.buf_size = int(100e3)

    def get_hashes(self):
        """
        :desc: Makes a dict of file names to file hashes
        :returns: TODO

        """

        for f in self.files:
            m = hashlib.sha1()
            with open(f, 'r') as fd:
                while True:
                    contents = fd.read(self.buf_size)
                    if contents == '':
                        break
                    m.update(contents)
                self.hashes[f] = m.hexdigest()

    def dedupe(self):
        """
        :desc: Find all the common values and group them
        """

        all_hashes = self.hashes.values()
        dupes = set([x for x in all_hashes if all_hashes.count(x) > 1])

        for d in dupes:
            self.duped_hashes[d] = []

        for f in self.files:
            h = self.hashes[f]
            if h in dupes:
                self.duped_hashes[h].append(f)

        return self.duped_hashes
