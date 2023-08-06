'''
Created on Mar 20, 2015

@author: Marc Lopez (marc.rainier.lopez@gmail.com)
'''

from contextlib import contextmanager
import subprocess
import psutil

subprocess_module = subprocess
process_utility = psutil

@contextmanager
def run_process(command):
    """Runs a command-line program as a context
    
    Parameters
    ----------
    command : string
       Command-line program with necessary arguments and flags to be run.
    """
    process = subprocess_module.Popen(command.split(' '), stdout=subprocess_module.PIPE)
    yield
    _kill_process_tree(process.pid)
    
def _kill_process_tree(pid, including_parent=True):    
    parent = process_utility.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()