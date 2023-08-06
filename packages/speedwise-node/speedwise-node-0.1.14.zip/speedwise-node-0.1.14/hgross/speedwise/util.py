import fnmatch
import threading
import time
import os
import ntpath

__author__ = 'Henning Gross'

def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def ensure_dir(dirname):
    """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
    try:
        os.makedirs(dirname)
    except OSError, e:
        return

class ProcessTerminationNotifier(threading.Thread):
    '''
        Simply calls onTerminationCallback if a popen process (process) terminates.
    '''
    def __init__(self, process, onTerminationCallback, log_hint=None):
        threading.Thread.__init__(self)
        self.process = process
        self.onTerminationCallback = onTerminationCallback
        self.log_hint = log_hint if log_hint else str(process) + " PID: " + str(process.pid)
    def run(self):
        while True:
            #self.process.wait() # interferes with the piping we use for mplayer on the raspberry pi cam
            if self.process.poll() != None:
                break
            time.sleep(0.5)
        print ("[ProcessTerminationNotifier] " + "Process terminated -> %s" % (self.log_hint))
        self.onTerminationCallback()