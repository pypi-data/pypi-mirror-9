#!/usr/bin/env python
# encoding: utf-8
"""
variant_printer.py

Print the variants of a results queue to a file.

Created by Måns Magnusson on 2013-01-17.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function, unicode_literals

import sys
import os

from multiprocessing import Process
from codecs import open
from tempfile import NamedTemporaryFile
from pprint import pprint as pp

from genmod.errors import warning

class VariantPrinter(Process):
    """docstring for VariantPrinter"""
    def __init__(self, task_queue, temp_dir, head, verbosity):
        Process.__init__(self)
        self.task_queue = task_queue
        self.verbosity = verbosity
        self.file_handles = {}
        self.temp_dir = temp_dir
        self.header = head.header
    
    def run(self):
        """Starts the printing"""
        # Print the results to a temporary file:
        number_of_finished = 0
        proc_name = self.name
        if self.verbosity:
            print(('%s: starting!' % proc_name), file=sys.stderr)
        while True:
            
            next_result = self.task_queue.get()
            
            if self.verbosity:
                if self.task_queue.full():
                    warning('Printing queue full')
            
            if next_result is None:
                if self.verbosity:
                    print('All variants printed!', file=sys.stderr)
                for chromosome in self.file_handles:
                    self.file_handles[chromosome].close()
                break
                
            else:
                
                for variant_id in next_result:
                    chrom = next_result[variant_id]['CHROM']
                    
                    if chrom.startswith('chr'):
                        chrom = chrom[3:]
                    print_line = [next_result[variant_id].get(entry, '-') for entry in self.header]
                    if chrom in self.file_handles:
                        self.file_handles[chrom].write('\t'.join(print_line) + '\n')
                    else:
                        temp_file = NamedTemporaryFile(prefix=chrom+'_', dir=self.temp_dir, delete=False)
                        temp_file.close()
                        self.file_handles[chrom] = open(temp_file.name, mode='w', encoding='utf-8', errors='replace')
                        self.file_handles[chrom].write('\t'.join(print_line) + '\n')
        return
    
def main():
    pass

if __name__ == '__main__':
    main()
