# -*- coding:utf-8 -*-
__author__ = 'nathan'

import threading
import logging
import time
import codecs

class BaseSync():

    def __init__(self):

        pass

    def run(self):
        pass


class Dumper(threading.Thread):
    def __init__(self, dst_file, sq):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger("dbsync.syncs")
        self.dst_file = dst_file
        self.sq = sq

    def run(self):
        start = time.clock()
        count = 0
        self._logger.info("run start")
        with codecs.open(self.dst_file, 'w', 'utf-8') as w :
            for item in self.sq.naive().iterator():
                w.write(item.unicode_dumps() + "\n")
                count += 1

        self._logger.info("write count : %d" % count)

        end = time.clock()
        self._logger.info("%s file count %d, run time : %.03f seconds" % (self.dst_file, count, end - start))

    def stop(self):
            self.thread_stop = True