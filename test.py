import os, sys
import re
import matplotlib as mp
import numpy as np

class SHEMAT_suite_file:

    def __init__(self,filename='', **kwds):
        """
        Initialization of a SHEMAT_Suite object
        **Arguments**:
            -*new_filename*: string: filename in case an empty file is created
            -*filename*: string: filename of SHEMAT-Suite file to load
        **Optional keywords**:
            -*offscreen*: boolean: set variables for offscreen rendering, e.g.
                          to create plots on a remote machine via ssh
        """
        if filename == '':
            print("creating empty SHEMAT-Suite input file")
            if kwds.has_key('new_filename'):
                self.filename = kwds['new_filename']
            else:
                self.filelines = self.read_file(filename)
                self.filename = filename
            if kwds.has_key('offscreen') and kwds['offscreen']:
                mp.use('Agg')

    def read_file(filename):
        """
        Open and read a SHEMAT Suite Input File
        **Arguments**:
            - *filename* = string with filename
        **Returns**:
            - List with lines in the file
        """
        try:
            file = open(filename,'r')
        except IOError (nr, string_error):
            print("Cannot open file {}: {} Err# {}".format(filename, string_error, nr))
            print("Please check file name and directory and try again.")
            raise IOError
        # check if number of entries is correct
        filelines = file.readlines()
        file.close()
        return filelines
      
      
      
      
    def sel(self, var_name, value, line=1):
        """
        Set a SHEMAT-Suite variable to a specific value
        **Arguments**:
            -*var_name* = string: name of variable
            -*value* = string or number: value of variable
        """
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                print(var_name)
                self.filelines[i+line] = str(value) + " \n"
    
    
    def get(self, var_name, line=1):
        """
        Get the value of a scalar variable
        Determines the value of a scalar variable in the SHEMAT-Suite object
        **Arguments**:
            -*var_name*: string: name of scalar variable
        **Optional kwrds**:
            -*line*: int: Number of lines for multiline variables
        **Returns**:
            String with variable
        """
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                if line == 1:
                    return self.filelines[i+1]
                    break
                else:
                    lines = []
                    for j in range(line):
                        lines.append(self.filelines[i+1])
                    return lines
                    break
