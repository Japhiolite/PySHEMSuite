"""
PyASCII is a module of PySHEMAT, a free set of Python modules to create and process input
files for fluid and heat flow simulation with SHEMAT (http://137.226.107.10/aw/cms/website/zielgruppen/gge/research_gge/~uuv/Shemat/?lang=de)

******************************************************************************************
PySHEMAT is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

PySHEMAT is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with PyTOUGH.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************************

For module, update and documentation of PySHEMAT please see:
https://github.com/flohorovicic/PySHEMAT

If you use PySHEMAT for a scientific study, please cite our publication in Computers and Geoscience


PyASCII provides methods to handle of ASCII-Gridfiles:

    - load as Object
    - define Object Overload:
        - __add__: add two ASCII Gridobjects (and save as new one)
        - other calculations possible (multiply __mul__, __sub__, ...)
        - __repr__: print with header
        - __len__: ASCII Grid dimensions and discretisation (makes comparison easier?)
        - __cmp__: Comparison: header and data!
    - grid trim to given Values, if compatible with header data
        (be careful not to change absolute data positioning!)
    - methods to analyse
    - methods to plot??
    - methods to write to file (incl. conversion/ formatting for FracSYS)
    - methods to write as xyz
    - methods to cut to given parameters (x, y, but also z- Values?)
    - methods to perform calculations?
    
    - cross-check data_array_3D data to exported XYZ grid with VerticalMappper!!
"""


from sys import exit
import string
import numpy as np

class ASCII_File:
    def __init__(self, *args):
        # read ASCII_File directly with object instantiation
        if len(args) != 0:
            file_name = args[0]
            self.file_name_str = file_name
            self.f_ascii = self.load_grid(file_name)
            self.header = self.read_header(self.f_ascii)
            # store data in list to avoid problems of pointer in file...
            self.data = self.f_ascii.readlines()
        else:
            # create default Attributes
            self.header = {}
            self.data = []
            self.file_name_str = "__no_Filename_given__"

    def __repr__(self):
        """define Object representation: header and data in string, can be
        used to output Object"""
        # ToDo: output format as FracSYS input format -> make conversion easier
        # print header
        header_str = ''
        header_str += "ncols %d\n" % self.header['ncol']
        header_str += "nrows %d\n" % self.header['nrow']
        header_str += "xllcorner %d\n" % self.header['xllcorner']
        header_str += "yllcorner %d\n" % self.header['yllcorner']
        header_str += "cellsize %d\n" % self.header['cellsize']
        header_str += "NODATA_value %f\n" % self.header['NODATA_value']
        # print data out of data_array row per row
        data_str = ''
        for row in self.data_array:
            line_str = ''
            for val in row:
                line_str += "%f " % val
            line_str += "\n"
            data_str += line_str
        return header_str + data_str

    def __sub__(self, other_AFO):
        """overload - function: substract values of two ASCII File objects
        if header data are equal
        returns new AFO with substracted values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 - data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out
    
    def __add__(self, other_AFO):
        """overload - function: substract values of two ASCII File objects
        if header data are equal
        returns new AFO with substracted values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 + data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out

    def __mul__(self, other_AFO):
        """overload - function: multiply values of two ASCII File objects
        if header data are equal
        returns new AFO with multiplied values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 * data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out
    
    
    def __div__(self, other_AFO):
        """overload - function: divide values of two ASCII File objects
        if header data are equal
        returns new AFO with divided values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 / data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out


        
    def size(self):
        """Calculate grid extend
        returns (x_min, x_max, y_min, y_max)
        flo, 04/2008"""
        x_min = self.header['xllcorner']
        x_max = x_min + self.header['ncol'] * self.header['cellsize']
        y_min = self.header['yllcorner']
        y_max = y_min + self.header['nrow'] * self.header['cellsize']
        return((x_min, x_max, y_min, y_max))

    def resize_grid(self, extend):
        """Trim grid to given extend; only performed, if in accordance with header data
        and absolute positioning is not changed:
            remainder of (x_min - xllcorner) % 500 should be 0 (other points equivalent)
        if new grid extends old grid: fill with NODATA_values (does not work yet!!!)

        extend is tuple with (x_min, x_max, y_min, y_max) as produced with ASCII_File.size()
        x_min: will be new xllcorner
        y_min: will be new yllcorner
        x_max: not included (check if senseful!!!)
        y_max: not included
        
        Caution: AFO itself is changed!
        flo, 04/2008"""
        x_min = extend[0]
        x_max = extend[1]
        y_min = extend[2]
        y_max = extend[3]
        # check, if given values are in accordance to grid metadata
        if not (
            ((x_min - self.header['xllcorner']) % self.header['cellsize'] == 0) &
            ((x_max - self.header['xllcorner']) % self.header['cellsize'] == 0) &
            ((y_min - self.header['yllcorner']) % self.header['cellsize'] == 0) &
            ((y_max - self.header['yllcorner']) % self.header['cellsize'] == 0)):
            print "Grid resizing not possible, given values not in accordance to header data"
        # calculate offset of x and y values
        x_min_offset = (x_min - self.header['xllcorner']) // self.header['cellsize']
        x_max_offset = (x_max - self.header['xllcorner']) // self.header['cellsize']
        y_min_offset = (y_min - self.header['yllcorner']) // self.header['cellsize']
        y_max_offset = (y_max - self.header['yllcorner']) // self.header['cellsize']
        # check, if values are in current grid extend
        if not ((0 < x_min_offset < self.header['ncol']) &
            (0 < x_max_offset < self.header['ncol']) &
            (0 < y_min_offset < self.header['nrow']) &
            (0 < y_max_offset < self.header['nrow'])):
                print "Grid resizing not possible, given values extend grid"
                return
        # calculate new grid
        self.check_data_array()
        # process every row separately: is there a more elegant way to perform the slicing?
        data_array_temp = []
        # Caution! Data rows are in reverse order, as llcorner as reference!
        self.data_array.reverse()
        for i in range(int(y_min_offset), int(y_max_offset)):
            row = self.data_array[i]
            data_array_temp.append(row[int(x_min_offset):int(x_max_offset)])
            
        data_array_temp.reverse()
        self.data_array = data_array_temp
        # adjust header data
        self.header['xllcorner'] = x_min
        self.header['yllcorner'] = y_min
        self.header['ncol'] = (x_max_offset - x_min_offset)
        self.header['nrow'] = (y_max_offset - y_min_offset)
        return
        
    def header_equal_to(self, other_AFO):
        """Check if header data of ASCII File object instance are equal to other
        AFO instance
        returns boolean
        flo 04/2008"""
        # test, if other_AFO is really an ASCII File Object
        if not isinstance(other_AFO, ASCII_File):
            print "Not an ASCII File object!"
            return False
        if self.header == other_AFO.header:
            return True
        else:
            return False
    
    def load_grid(self, file_name):
        # print "load File " + file_name
        try:
            f_ascii = open(file_name)
        except IOError, (nr, string_err):
            print "\n\tNot able to open file:", string_err
            print "\tPlease check file name and run program again\n"
            exit(0)

        return(f_ascii)
    
    def read_header(self, f_ascii):
        """ returns the 6 line header as a dict"""
        # print "read Header of file " + self.file_name_str
        header = {}
        line = f_ascii.readline().split()
        header['ncol'] = int(line[1])
        line = f_ascii.readline().split()
        header['nrow'] = int(line[1])
        line = f_ascii.readline().split()
        header['xllcorner'] = float(line[1])
        line = f_ascii.readline().split()
        header['yllcorner'] = float(line[1])
        line = f_ascii.readline().split()
        header['cellsize'] = float(line[1])
        line = f_ascii.readline().split()
        header['NODATA_value'] = int(line[1])
        return(header)
   
    def import_SHEMAT_2D_array(self, S1, property_xy, **kwds):
        """Import a 2D array, created from a PySHEMAT object
        
        This method can be used to import a 2D array created from a PySHEMAT object,
        for example mean temperatures of a specific formation, created with:
        temperature_xy = S1.calculate_mean_form_temp(formation_id);
        
        The header of the PyASCII object is adapted according to the dimensions
        of the PySHEMAT object.
        
        ..Attention..: ASCII grid object are per definition regular grid objects!
        Therefore, the conversion only works when the original SHEMAT grid is completely regular (dx = dy).

        **Arguments**:
            - *S1* = PySHEMAT.Shemat_file : original SHEMAT object (for dimensions, etc.)
            - *property_xy* = 2D property array, created with PySHEMAT
            
        **Optional Keywords**:
            - *set_nodata_value* = True/ False : set Nodata value for a defined range
            - *nodata_range_min* = float : minimum for nodata range
            - *nodata_range_max* = float : maximum for nodata range
            - filename = string : filename of ASCII grid file
        
        **Returns**: None
        """
        # this has to be defined:
        self.header = {'ncol' : int(S1.get("IDIM")),
                       'nrow' : int(S1.get("JDIM")),
                       'xllcorner' : float(S1.get("I0")),
                       'yllcorner' : float(S1.get("J0")),
                       'cellsize' : float(S1.get_array("DELX")[0]),
                       'NODATA_value' : -9999
                        }

        # set nodata value, if required
        if kwds.has_key('set_nodata_value') and kwds['set_nodata_value']:
            for i,t in enumerate(property_xy):
                if t < kwds['nodata_range_max'] and t > kwds['nodata_range_min']:
                    property_xy[i] = self.header['NODATA_value']

        # data organisation in ASCII grid: one row per list entry
        n = 0
        rows_tmp = []
        for row in range(self.header['nrow']):
            data_row = []
            for col in range(self.header['ncol']):
                data_row.append(property_xy[n])
                n += 1
            rows_tmp.append(data_row)
        # reverse rows_temp because of strange orientation of lines in ASCII
        # grid file (first line corresponds to most Northern line)
        rows_tmp.reverse()
        self.data_array = rows_tmp
        if kwds.has_key('filename'):
            self.file_name_str = kwds['filename']
        else:
            self.file_name_str = "imported_from_PySHEMAT"
        
    def write_file(self, **kwds):
        """Write ASCII grid to file
        
        Write the ASCII grid object to a .txt file. This file should be usable
        for both MapInfo and ArcGIS. Per default, the filename defined in
        self.file_name_str is used, but another filename can be defined with
        an optional keyword.
        
        **Optional Keywords**:
            - *filename* = string : filename (with or without extension); default: self.file_name_str
            - *path* = string : path where file is saved, default: cwd
        """
        from os import path, chdir, getcwd
        if kwds.has_key('filename'):
            if path.splitext(kwds['filename'])[1] == "":
                filename = kwds['filename']+".txt"
            else:
                filename = kwds['filename']
        else:
            if path.splitext(self.file_name_str)[1] == "":
                filename = self.file_name_str+".txt"
            else:
                filename = self.file_name_str
        if kwds.has_key('path'):
            ori_dir = getcwd()
            chdir(path)
        
        f = open(filename, 'w')
        f.write(repr(self))
        f.close()
            
        if kwds.has_key('path'):
            # return to original working directory
            chdir(ori_dir)
            
        
   
    def convert_SHEMAT_results_to_header(self, S1, property_xy):
        """convert a calulcated SHEMAT property array to an ASCII grid
        using the original SHEMAT object to set the header properties
        !!! ATTENTION: ASCII grid only for regular space grids with dx = dy! 
        S1 : Shemat Object
        property_xy : property array (1D) with 2.5 D grid info as written by various
        Shemat_file methods, e.g. mean properties
        """        
        # this has to be defined:
        self.header = {'ncol' : int(S1.get("IDIM")),
                       'nrow' : int(S1.get("JDIM")),
                       'xllcorner' : float(S1.get("I0")),
                       'yllcorner' : float(S1.get("J0")),
                       'cellsize' : float(S1.get_array("DELX")[0]),
                       'NODATA_value' : -9999
                        }
        # data organisation in ASCII grid: one row per list entry
        n = 0
        rows_tmp = []
        for row in range(self.header['nrow']):
            data_row = []
            for col in range(self.header['ncol']):
                data_row.append(property_xy[n])
                n += 1
            rows_tmp.append(data_row)
        # reverse rows_temp because of strange orientation of lines in ASCII
        # grid file (first line corresponds to most Northern line)
        rows_tmp.reverse()
        self.data_array = rows_tmp
        self.file_name_str = "__no_Filename_given__"        
        
    def save(self, filename, **kwds):
        """save ASCII grid to file;
        filename = string : filename of grid file
        optional keywords:
        dir = directory path : path where file is saved"""
        if kwds.has_key('dir'):
            from os import getcwd, chdir
            ori_dir = getcwd()
            chdir(kwds['dir'])
            
        # write ASCII grid to new file
        myfile = open(filename, 'w')
        # use repr to derive a string representation of the Object, as defined in __repr__
        myfile.write(repr(self))
        myfile.close()
        

        
        
        # go back to original directory
        if kwds.has_key('dir'):
            chdir(ori_dir)

    def print_detailed_header_data(self):
        # print header data to output (flo, 04/2008)
        
        # print "Number of Columns:\t%d" % self.header['ncol']
        # print "Number of Rows:\t\t%d" % self.header['nrow']
        print "%s is a %d x %d grid (columns x rows)" % (self.file_name_str, self.header['ncol'], self.header['nrow'])
        print "with "
        print "\tlower-left corner at \t(%d, %d)" % (self.header['xllcorner'], self.header['yllcorner'])
        print "\tupper-right corner at \t(%d, %d)" % (self.header['xllcorner']+self.header['ncol']*self.header['cellsize'],
                                                        self.header['yllcorner']+self.header['nrow']*self.header['cellsize'])
        print "and a cellsize of %d" % self.header['cellsize']


# what for???
    def float2str(self, number):
        """ strips off trailing zeros from coordinates """
        s = "%f" % number
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s

##    def process_z_values_to_array(self):
##        x_list = self.xcoords(self.header)
##        y_list = self.ycoords(self.header)
##        return self.grid_z_values_to_array(self.data, self.header, x_list, y_list)

    def xcoords(self, header):
        """ calculates x coordinates of a grid"""
        x = []
        for col in range(header['ncol']):
            x.append(ASCII_File.float2str(self,header['xllcorner'] + (0.5 * header['cellsize']) + (col * header['cellsize'])))
        return(x)

    def ycoords(self, header):
        """ calculates y coordinates of a grid"""
        y = []
        for (j, row) in enumerate(range(header['nrow'])):
            y.append(ASCII_File.float2str(self,header['yllcorner'] -
                               (0.5 * header['cellsize']) + (header['nrow'] - row) * header['cellsize']))
        return(y)

    def process_z_values_to_array(self):
        """ Read data in list and write to array 
        
        ..Note: This function returns a list of the data lines, i.e. one list entry
        per y-value (2-D), and not a 1-D list of the data itself.
        """
        # if talk: print "\tread data file line by line"
        self.data_array = []
        # L_col = []
        for row in range(self.header['nrow']):
            for col in range(self.header['ncol']):
                # Get new data if necessary
                if col == 0:
                    L_col = []
                    line = self.data[row].split()

                # Write output to array
                L_col.append(string.atof(line[col]))

            self.data_array.append(L_col)
        return self.data_array
    
    def export_to_meshgrid(self):
        """Export ASCII grid into a format than can be used with meshgrid in Matlab/ Pylab
        
        This method can be used to export the mesh structure and the data to create
        a plot with the meshgrid functions, used in Matlab and Pylab. The method exports
        the x- and y-coordinates of the grid in a 1-D array and the z-data in a x-dominant
        1-D array.
        
        **Returns:
            *(x_coords, y_coords, z_values)
        """
        # determine x and y corrds, can be done with predefined functions
        xcoords = [float(x) for x in self.xcoords(self.header)]
        ycoords = [float(y) for y in self.ycoords(self.header)]
        # get z-values
        self.get_z_values()
        return (xcoords, ycoords, self.z_values)
    
    
    def check_data_array(self):
        """ Check if data_array already exists, if not -> create """
        try:
            self.data_array
        except AttributeError:
            # print "Create z-Value Data array"
            self.process_z_values_to_array()

    def check_mask(self):
        """Check, if data_array_masks exisist, if not -> create """
        try:
            self.data_array_mask
        except AttributeError:
            print "Create Mask for Data with values:"
            print "0: if NODATA_value, 1: else"
            self.create_z_value_mask()
    
    def check_hist(self):
        """Check, if hist_data exists, if not -> create """
        try:
            self.hist_data
        except AttributeError:
            # print "Calculate histogram data"
            self.calculate_histogram()

    
    def set_NODATA_values(self, data_mask, NODATA_value = -9999):
        """write NODATA_value (defined in header) to all positions, where
        data_mask == 0
        flo, 04/2008"""
        # Maybe all this mask-thing too complicated?? Advantage: can be handled
        # with Matrix functionality implemented in numpy...
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        data_mask = array(data_mask)
        data_mask_inv = 1 - data_mask
        self.check_data_array()
        data_array = array(self.data_array)
        data_array = data_array * data_mask + data_mask_inv * NODATA_value
        self.data_array = list(data_array)
        
    
    def create_z_value_mask(self):
        """ Create grid mask out of data_array (0 for 'NODATA_value', 1 else) """

        # Check if data_array already exists, if not -> create
##        try:
##            self.data_array
##        except AttributeError:
##            print "Create z-Value Data array"
##            self.process_z_values_to_array
        self.check_data_array()
        self.data_array_mask = [] # = self.data_array[:][:]
        # TO DO: simplify with "list comprehensives"???
        # self.data_array_mask = [0 for val in self.data_array if val=='-9999']
        for row in self.data_array:
            data_row = []
            for val in row:
                if val == self.header['NODATA_value']:
                    data_row.append(0)
                else:
                    data_row.append(1)

            self.data_array_mask.append(data_row)

                    

##
##
##        for val in self.data_array:
##            if j==2:
##                print val
##

        
    
    def process_xyz_values_to_3D_array(self):
        """Read data and store X,Y,Z values in 3D array, flo 03/2008 """
        self.data_array_3D = []
        # read self.x_data and self.y_data if they do not already exist...
        # to save computation time??
        try:
            (self.x_data, self.y_data)
        except AttributeError:
            # print "Create x- and y- coordinates"
            self.x_data = self.xcoords(self.header)
            self.y_data = self.ycoords(self.header)
            
        for row in range(self.header['nrow']):
            for col in range(self.header['ncol']):
                # Get new data if necessary
                if col == 0:
                    L_col = []
                    line = self.data[row].split()
                    
                L_col.append([self.x_data[col], self.y_data[row], line[col]])

            self.data_array_3D.append(L_col)

        return self.data_array_3D
    
    def calculate_histogram(self):
        """Read Data from data_array and create histogram over z-values
        uses matplotlib/
        """
        # test, if data_array exists, if not -> create
        try:
            self.data_array
        except AttributeError:
            # print "Create z-Value Data array"
            self.process_z_values_to_array()
        self.hist_data = []
        for row in self.data_array:
            for val in row:
                if val != self.header['NODATA_value']:
                    self.hist_data.append(val)
        # convert to numpy array
        self.hist_data = np.array(self.hist_data)

    def get_z_values(self, **kwds):
        """Get z-values from grid and write to 1-D x-dominant data array
        
        **Optional Keywords**:
            - *nodata_value* = float : set nodata entries to specific value
        """
        try:
            self.data_array
        except AttributeError:
            # print "Create z-Value Data array"
            self.process_z_values_to_array()
        self.z_values = []
        for row in self.data_array:
            for val in row:
                if val == self.header['NODATA_value'] and kwds.has_key('nodata_value'):
                    self.z_values.append(kwds['nodata_value'])
                else:
                    self.z_values.append(val)

    def plot_ASCII_grid_histogram(self, n=100, **kwds):
        """Plot histogram created with self.calculate_histogram()
        
        **Arguments**:
            - *n* = int : number of bins (default=100)
        
        **Optional Keywords**:
            - *smooth* = bool : create a smoothed version (default: False)
            - *add_stats* = bool : add percentile lines in plot (default: False)
              .. note:: Statistics are calculated for original (not scaled) dataset!
            - *return_stats* = bool : return statistics as dictionary
            - *exclude_zero* = bool : exclude zero values (default: False)
            - *figsize* = (x,y) : matplotlib figsize
            - *savefig* = bool : save figure to file (default: False)
            - *fig_filename* = string : filename (default: "Histogram fname")
            - *vmin* = float : lower limit
            - *vmax* = float : limit to maximum value
            - *title* = string : title of plot
        """
        # test, if self.hist_data exists, if not -> create
        try:
            self.hist_data
        except AttributeError:
            self.calculate_histogram()
        # Import matplotlib modules, test, if matplotlib installed
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Sorry, Module matplotlib is not installed."
            print "Histogram can not be plotted."
            print "Install Matplotlib and try again ;-) "
            return
        
        # set flags 
        exclude_zero = kwds.get("exclude_zero", False)
        smooth = kwds.get("smooth", False)
        add_stats = kwds.get("add_stats", False)
        savefig = kwds.get("savefig", False)
        figsize = kwds.get("figsize", (6,4))
        fig_filename = kwds.get("fig_filename", "histogram_%s.png" % self.file_name_str)
        return_stats = kwds.get("return_stats", False)
        title = kwds.get("title", "")
         
        if exclude_zero:
            h_data = self.hist_data[self.hist_data > 0]
        
        if kwds.has_key("vmax"):
            h_data = h_data[h_data < kwds['vmax']]
        
        if kwds.has_key("vmin"):
            h_data = h_data[h_data > kwds['vmin']]
        
        # generate figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        if smooth:
            # first: get histogram data
            h1 = np.histogram(h_data, bins = n)
            x = h1[1][:-1] # note: should use centroids, but too lazy
            y = h1[0]
            from scipy.interpolate import interp1d
            f2 = interp1d(x, y, kind='cubic')
            x_new = np.linspace(1.01*min(h_data),0.99*max(h_data),len(x)/2.)
            ax.fill_between(x_new,f2(x_new), color='0.1')
            ax.set_xlim((min(h_data), max(h_data)))
            _, ymax = ax.get_ylim()
            ax.set_ylim((0,ymax))
            ax.set_title(title)
        
        else: 
            # plot normal histogram        
            ax.hist(h_data,n, color = '0.1', lw=0, fc = '0.1')
            ax.set_xlim((min(h_data), max(h_data)))
            ax.set_title(title)
            
        if add_stats:
            # calculate statistics and add on plot:
            # compute statistics
            # define light color
            col = '1.0'
            med = np.median(self.hist_data)
            p5 = np.percentile(self.hist_data,5)
            p25 = np.percentile(self.hist_data,25)
            p75 = np.percentile(self.hist_data,75)
            p95 = np.percentile(self.hist_data,95)
            ax.axvline(med, c='#CC0000', lw=2)
            ax.axvline(p25, c=col, lw=2)
            ax.axvline(p75, c=col, lw=2)
            ax.set_xlabel("Thickness")
            ax.set_ylabel("Counts")

        
        if savefig:
            plt.savefig(fig_filename)
        else:
            plt.show()
            
        if return_stats:
            return {'p5' : p5, 
                    'p25' : p25, 
                    'median' : med,
                    'p75' : p75,
                    'p95' : p95}
          
    def plot_ASCII_grid_2D(self, **kwds):
        """Create 2D plot of ASCII grid
        
        **Optional keywords**:
            - *filename* = string : filename (and, implicitly, the format) of plot file
            - *cmap* = maptlotlib colormap: colormap for plot (default: gray)
            - *figsize* = (float, float) : figure size in x,y (default: 8,6)
            - *colorbar* = bool : plot colorbar (default: True)
            - *title* = string : plot title (default: filename)
            - *vmin* = float : minimum valule to plot (default: min of data)
            - *vmax* = float : maximum value to plot (default: max of data)
            - *ax* = matplotlib.axis : axis object to append plot (axis is returned!)
            - *interpolation* = 'spline36', 'nearest', etc. : matplotlib interpolation types
                    (default: spline36)
            - *fraction* = float [0-1] : fraction of width for colorbar (default: 0.15)
            - *colorbar_title* = string: title of colorbar
            - *rotate_labels* = bool : rotate y-axis labels (default: False)
            - *max_labels_x* = int : maximum number of labels on x-axis
            - *max_labels_y* = int : maximum number of labels on y-axis
            - *adjust_coords* = bool : adjust axes coordinates to grid (default: cell number)
            - 
        """
        # check all keywords and assign default values
        cmap = kwds.get("cmap", 'gray')
        figsize = kwds.get("figsize", (8,6))
        colorbar = kwds.get("colorbar", True)
        title = kwds.get("title", self.file_name_str)
        interpolation = kwds.get("interpolation", "spline36")
        fraction = kwds.get("fraction", 0.15)
        colorbar_title = kwds.get("colorbar_title", "")
        rotate_labels = kwds.get("rotate_labels", False)
        
        self.check_hist()
        vmin = kwds.get("vmin", min(self.hist_data))
        vmax = kwds.get("vmax", max(self.hist_data))
        
        # hack to adjust labels
        from matplotlib.ticker import MultipleLocator, FormatStrFormatter
        from matplotlib import rcParams
        
        majorLocator   = MultipleLocator(50)
        majorFormatter = FormatStrFormatter('%d')
        minorLocator   = MultipleLocator(25)
        rcParams.update({'font.size': 15})

        
        # read self.x_data and self.y_data if they do not already exist...
        # to save computation time??
        try:
            (self.x_data, self.y_data)
        except AttributeError:
            # print "Create x- and y- coordinates"
            self.x_data = self.xcoords(self.header)
            self.y_data = self.ycoords(self.header)
        # check, if data_array with z values is already created
        try:
            self.data_array
        except AttributeError:
            # print "Create z-Value Data array"
            self.process_z_values_to_array
        # Import matplotlib modules, test, if matplotlib installed
        # export test to separate function?
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Sorry, Module matplotlib is not installed."
            print "Histogram can not be plotted."
            print "Install Matplotlib and try again ;-) "
            return
        
        # if axes is not passed as keyword, create stand alone figure
        if kwds.has_key('ax'):
            ax = kwds['ax']
        else:
            fig = plt.figure(figsize = figsize)
            ax = fig.add_subplot(111)
        
        # [X,Y] = meshgrid(self.xcoords, self.ycoords)
        #
        # self.check_data_array()
        
        im = ax.imshow(self.data_array, vmin=vmin, vmax=vmax,
                       cmap=cmap, interpolation=interpolation)
        
        if kwds.has_key("adjust_coords") and kwds['adjust_coords']:
            # setting to real coordinates
            im.set_extent([self.header['xllcorner'],
                    self.header['xllcorner'] + self.header['ncol'] * self.header['cellsize'],
                    self.header['yllcorner'],
                    self.header['yllcorner'] + self.header['nrow'] * self.header['cellsize']])
        
        from matplotlib.ticker import MaxNLocator
        if kwds.has_key("max_labels_x"):
            im.axes.xaxis.set_major_locator(MaxNLocator(kwds['max_labels_x']))
       
        if kwds.has_key("max_labels_y"):
            im.axes.yaxis.set_major_locator(MaxNLocator(kwds['max_labels_y']))
        
        
        # rotate labels on y-acis:
        if rotate_labels:
            for label in im.axes.yaxis.get_ticklabels():
                label.set_rotation(-90)
        
#        def mjrFormatter(x, pos):
##            x = x - self.header['yllcorner']
#            return "{0}".format(x)
#            # return "$2^{{{0}}}$".format(x)
#        
#        import matplotlib as mpl
#        im.axes.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(mjrFormatter))
#        
            # im = imshow(self.data_array)
        if colorbar:
            cbar = plt.colorbar(im, fraction=fraction) # , location="bottom")
            cbar.set_label(colorbar_title)
                         
        # plot contour lines on top? -> TEST!!

        # axis('off')
        ax.set_title(title)
        if kwds.has_key('filename'):
            plt.savefig(kwds['filename'])
        else:
            plt.savefig('ascii_grid.png')
        if kwds.has_key("ax"):
            return ax
        
    def plot_grid_and_hist(self, **kwds):
        """Create a 2-D plot of the grid in space and a histogram of values
        
        The histogram contains median and percentiles
        
        **Optional Keywords**:
            - *filename* = string : filename (and, implicitly, the format) of plot file
            - *cmap* = maptlotlib colormap: colormap for plot (default: gray)
            - *figsize* = (float, float) : figure size in x,y (default: 8,6)
            - *colorbar* = bool : plot colorbar (default: True)
            - *title* = string : plot title (default: filename)
            - *vmin* = float : minimum valule to plot (default: min of data)
            - *vmax* = float : maximum value to plot (default: max of data)
            - *n* = int : number of bins for histogram (default: 100)
         """
        cmap = kwds.get("cmap", "gray")
        figsize = kwds.get("figsize", (8,6))
        colorbar = kwds.get("colorbar", True)
        title = kwds.get("title", self.file_name_str)
        n = kwds.get("n", 100)
        
        self.check_hist()
        vmin = kwds.get("vmin", min(self.hist_data))
        vmax = kwds.get("vmax", max(self.hist_data))
        
        
        # read self.x_data and self.y_data if they do not already exist...
        # to save computation time??
        try:
            (self.x_data, self.y_data)
        except AttributeError:
            # print "Create x- and y- coordinates"
            self.x_data = self.xcoords(self.header)
            self.y_data = self.ycoords(self.header)
        # check, if data_array with z values is already created
        try:
            self.data_array
        except AttributeError:
            # print "Create z-Value Data array"
            self.process_z_values_to_array
        # Import matplotlib modules, test, if matplotlib installed
        # export test to separate function?
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Sorry, Module matplotlib is not installed."
            print "Histogram can not be plotted."
            print "Install Matplotlib and try again ;-) "
            return
        
        fig = plt.figure(figsize = figsize)
#        ax1 = fig.add_subplot(121)
        ax1 = fig.add_axes([0.02, 0.05, 0.35, 0.9])
        
        # [X,Y] = meshgrid(self.xcoords, self.ycoords)
        #
        # self.check_data_array()
        
        im = ax1.imshow(self.data_array, vmin=vmin, vmax=vmax,
                       cmap=cmap)
        # im = imshow(self.data_array)
        if colorbar:
            plt.colorbar(im, aspect=50) 
        # plot contour lines on top? -> TEST!!

        # axis('off')
        ax1.set_title(title)
        
        #=======================================================================
        # Plot Histogram 
        #=======================================================================
        
#        ax2 = fig.add_subplot(122)
        ax2 = fig.add_axes([0.4, 0.05, 0.48, 0.9])
        
                
        import numpy as np
        # extract values > 0
        d1 = np.array(self.hist_data)
        d2 = d1[d1>0]
        # compute statistics
        med = np.median(d2)
        p5 = np.percentile(d2,5)
        p25 = np.percentile(d2,25)
        p75 = np.percentile(d2,75)
        p95 = np.percentile(d2,95)
        
        ax2.hist(d2, bins=n, lw = 0, color='DarkGray')
        ax2.axvline(med, c='k', lw=2)
        ax2.axvline(p25, c='k', lw=1)
        ax2.axvline(p75, c='k', lw=1)
        ax2.set_xlabel("Thickness")
        ax2.set_ylabel("Counts")
        ax2.set_xlim([0,vmax])
        
#        ax2.hist(self.hist_data,n)
        
        
        if kwds.has_key('filename'):
            plt.savefig(kwds['filename'])
        else:
            plt.savefig('ascii_grid.png')

        
        
    def get_gmt_range(self):
        """Determine the (x,y) range of the grid in the format used by GMT
        
        The typical GMT format is: -Rmin_x/max_x/min_y/max_y
        """
        min_x = self.header['xllcorner']
        min_y = self.header['yllcorner']
        max_x = min_x + self.header['nrow'] * self.header['cellsize']
        max_y = min_y + self.header['ncol'] * self.header['cellsize']
        return "-R%05.2f/%05.2f/%05.2f/%05.2f" % (min_x, max_x, min_y, max_y)
        
    def create_netcdf_file(self, **kwds):
        """Create a netcdf gridfile from ASCII grid, using GMT
        
        ..Note..: This function is only working if GMT is installed and in the search path!
        
        **Optional Keywords**:
            - *
        """
        # In a first step, the ASCII grid file has to be saved to a temporary file; this file is
        # later deleted in the gmt-script
        self.write_file(filename = "tmpgrid.txt") 
        
        if kwds.has_key("netcdf_filename"):
            netcdf_filename = kwds['netcdf_filename']
        else:
            netcdf_filename = "tmp.grd"
        
        gmt_range = self.get_gmt_range() 
         
        gmtscript = "#!/bin/bash\n"
        gmtscript += "xyz2grd tmpgrid.txt -G" + netcdf_filename + " -E -V " + gmt_range + "\n"
        
        gmt_file = open("create_netcdf_file.gmt", "w")
        gmt_file.write(gmtscript)
        # run conversion script if keyword is defined
        if kwds.has_key("run_conversion") and kwds['run_conversion']:
            import subprocess
            my_proc=subprocess.Popen('bash ./create_netcdf_file.gmt',shell=True)
            my_proc.wait()
        
    def create_gmt_plot_script(self, **kwds):
        """Create a GMT script to create a high-quality eps figure
        
        This function creates a script file that can be executed on the command line
        if GMT is installed. The file is a bash script file per default. A DOS file can
        be created with the keyword DOS=True
        """
        # In a first step, the ASCII grid file has to be saved to a temporary file; this file is
        # later deleted in the gmt-script
        print("\n\tNote: a lot of hardcoded stuff in this GMT script!\n")
        print("\tFor better scales: try multiplying by 1000\n\n")
        self.write_file(filename = "tmpgrid.txt") 
 
        if kwds.has_key("netcdf_filename"):
            netcdf_filename = kwds['netcdf_filename']
        else:
            netcdf_filename = "tmp.grd"
        
        gmt_range = self.get_gmt_range() 
         
        self.script = []
        self.script.append("#!/bin/bash")
        
        # set some fancy GMT default values
        self.script.append( 'gmtset PAPER_MEDIA                Custom_5mx30m')
        self.script.append('gmtset ANNOT_MIN_SPACING           0p')
        self.script.append('gmtset ANNOT_FONT_SIZE_PRIMARY    10p')
        self.script.append('gmtset ANNOT_FONT_SIZE_SECONDARY  10p')
        self.script.append('gmtset HEADER_FONT_SIZE           10p')
        self.script.append('gmtset LABEL_FONT_SIZE            12p')
        self.script.append('gmtset TICK_LENGTH              0.1c')
        self.script.append('# End of header \n')
        
        # convert ascii grid file to netcdf format
        self.script.append("xyz2grd tmpgrid.txt -G" + netcdf_filename + " -E -V " + gmt_range)
        
        # create color palette table matching to grid file
        self.script.append("grd2cpt " + netcdf_filename + " -Cjet > mygrid.cpt\n")
        
        # now create grid file 
        self.script.append('grdimage ' + netcdf_filename + ' ' + gmt_range + ' -JX3i -B500:."Temperature Gradient:" -Cmygrid.cpt -P -K > out.ps\n')
        
        # append scalebar
        self.script.append('psscale -Cmygrid.cpt -D3.7i/1.55i/2.88i/0.4i -O -I0.3 -Ac -Ba0.005f0.001:Gradient:/:C/km: >> out.ps')
        
        # for a better output (i.e. cropped bounding box, etc.):
        self.script.append("ps2epsi out.ps\nmv out.epsi gridfile.eps") 
        fh=open('gmt_script.sh','w')
        for line in self.script:
            fh.write(line + "\n")
        fh.close()
        
        
        

        

           

### End of Class definition for ASCII grid object

def calculate_Ra_number(ASCII_grid_object):
    """Simple 1D Ra-Number Analysis based on
    - formation thickness values stored in ASCII Gridfile
    - simple 1set order estimations of phyiscal parameters
    Output:
    new ASCII Grid-Object with Ra-Values in Grid
    flo, 04/2008"""
    pass



# test object/ module
if __name__ == '__main__':
    import string
    from os import chdir
    from PySHEMAT import Shemat_file

#    chdir("C:\GeoModels\Evaluation_Models\Eval_Model_2_Graben_2d")
#    A1 = ASCII_File("test2_Isobaths_Formation3.txt")
    chdir(r'C:\GeoModels\WAGCoE\North_Perth_Basin\nml_run_14')
    S1 = Shemat_file("PB_N_nml14_updated.nlo")
    form_id = 6
    temperature_xy = S1.calc_mean_formation_value(form_id, "TEMP")
    A2 = ASCII_File()
    A2.import_SHEMAT_2D_array(S1, temperature_xy,
                              set_nodata_value = True,
                              nodata_range_min = -0.0001,
                              nodata_range_max = 0.0001,
                              filename = 'mean_temp_formation_%d_a' % form_id)
    print("write ASCII grid file")
    A2.write_file()
#    write_str = repr(A2)
#    myfile = open('Grad_grid_out1.txt', 'w')
#    # use repr to derive a string representation of the Object, as defined in __repr__
#    myfile.write(repr(A2))
#    myfile.close()
    exit()
    # A1 = ASCII_File("iso_080326_Isopachs_Leseur.txt")
    # A1.print_detailed_header_data()
    # f_ascii = A1.load_grid("bla.txt")
    # head = A1.read_header(A1.f_ascii)
    # A1.process_grid_to_array()
#    A1.process_xyz_values_to_3D_array()

 #   from pylab import *
    # test fpconst module (has to be downloaded separately!!!) for NaN
##    import fpconst
##    i=0
##    for data in A1.data_array:
##        if data == A1.header['NODATA_value']:
##            A1.data_array[i] = 17
##            print A1.data_array[i]
##            # print A1.data_array[i]
##
##        i = i+1
##
##    hist(A1.data_array,100)
##    show()
#    print A1.data_array[2][4]
#    print A1.data_array_3D[2][4]
#    print A1.header['NODATA_value']
#    A1.create_z_value_mask()
#    print
#    print A1.data_array[2][4]
#    print A1.data_array_3D[2][4]
#    A1.calculate_histogram()
#    print A1.hist_data
#    # A1.plot_ASCII_grid_2D()
#    print "Calculate min/max values"
#    print min(A1.hist_data)
#    print max(A1.hist_data)
#
##    chdir(r'C:\GeoModels\Geothermal_Resource_Base\Talk_AGEC\Model_2\export\shemat_lowres\nml_run_2')
##    S1 = Shemat_file('agec2_2_lowres_model.nml')
#    A1.plot_ASCII_grid_2D()
    form_id = 6
    temperature_xy = S1.calc_mean_formation_value(form_id, "TEMP")
    print temperature_xy
    A2 = ASCII_File()
    A2.convert_SHEMAT_results_to_header(S1, temperature_xy)
    # write ASCII grid to new file
    write_str = repr(A2)
    myfile = open('Grad_grid_out1.txt', 'w')
    # use repr to derive a string representation of the Object, as defined in __repr__
    myfile.write(repr(A2))
    myfile.close()
    # A1.plot_ASCII_grid_2D()
    

#    print A1.data_array_mask
    
    # xstr = A1.xcoords(head)
    # ystr = A1.ycoords(head)

    # ascii_array = A1.grid_xyz_to_array(f_ascii, head, xstr, ystr)

    # print(ascii_array[0][1])
