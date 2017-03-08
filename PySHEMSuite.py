"""
PySHEMAT-Suite is an open-source collection of Python modules to easily create
and process SHEMAT-Suite Input files.

********************************************************************************

PySHEMAT-Suite can be redistributed and/or modified under the terms of the GNU
General Public License as published by the Free Software Foundation, either
version 3 of the License, or any later version.

PySHEMAT-Suite is distributed WITHOUT ANY WARRANTY; without the implied WARRANTY
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
http://www.gnu.org/licenses/
********************************************************************************

For module, update and documentation of PySHEMAT-Suite, see the Git-repository.
"""

import os, sys
import matplotlib as m
import numpy as np
import h5py
import scipy.constants
import itertools
import collections
import pandas
import fileinput
import re


class SHEMATSuiteFile:
    """
    Class for SHEMAT-Suite simulation input files
    Object methods enable a direct access of all variables and parameters
    defined in the input file.
    Further methods enable 1D, 2D and 3D plots of HDF5 files and creation of
    publication-ready images.
    """
    def __init__(self, filename='', **kwds):
        """
        Initialization of the SHEMAT-Suite Object

        **Arguments**:
            -*new_filename* = string: filename in cas an empty file is created
            -*filename* = string: filename of SHEMAT-Suite Input file to load

        **Optional keywords**:
            -*offscreen* = boolean: set variables for offscreen rendering, e.g.
            for creating plots on a remote machine via ssh
        """
        if filename == '':
            print("creating empty file")
            if kwds.has_key('new_filename'):
                self.filename = kwds['new_filename']
        else:
            self.filelines = self.read_file(filename)
            self.filename = filename
            self.idim = int(self.get("grid").split()[0])
            self.jdim = int(self.get("grid").split()[1])
            self.kdim = int(self.get("grid").split()[2])
        if kwds.has_key('offscreen') and kwds['offscreen']:
            m.use('Agg')

    def __repr__(self,**kwargs):
        """
        Information display of the SHEMAT-Suite Object
        """
        # basic information
        if hasattr(self, '_nx') and hasattr(self, '_ny'):
            info_string = "Model object with 2D grid data \n"
            # info on grid cells, spacing, extent
            info_string += "Number of cells \t = (%d, %d)\n" % (self._nx, self._ny)
            info_string += "Cell dimensions \t = (%.1f, %.1f)\n" % (self._dx, self._dy)
            info_string += "Grid extent \t = (%.1f, %.1f)\n" % (self._extent_x, self._extent_y)
        else:
            info_string = "There is no model info yet!"

        return info_string

    def read_file(self, filename):
        """
        Open and read a SHEMAT-Suite input file
        **Arguments**:
            -*filename* = string: filename

        **Returns**:
            -List of lines in the file #better Dict??
        """
        try:
            file = open(filename, 'r')
        except IOError, (nr, string_err):
            print("Cannot open file {} : {} Err# {}.".format(filename, string_err, nr))
            print("Please check if the file name and directory are correct.")
            raise IOError
        # check if number of entries is correct
        filelines = file.readlines()
        file.close()
        # set local vairables
        return filelines

    def write_file(self, filename):
        """
        Write SHEMAT object to file
        """
        try:
            file = open(filename, 'w')
        except IOError, (nr, string_err):
            print("Cannot open file {} : {} Err# {}.".format(filename, string_err, nr))
            print("Please check if the file name and directory are correct.")
            raise IOError
            exit(0)
        print("Write new SHEMAT-Suite Input file: {}".format(filename))
        file.writelines(self.filelines)
        file.close()


    def get(self, var_name, line=1):
        """
        Get the value of a scalar variable.
        Determines the value of a variable or parameter in the SHEMAT-Suite Input
        file.

        **Arguments**:
            - *var_name* = string: Name of the scalar variable

        **Optional keywords**:
            - *line* = Number of lines for multiline variables

        **Returns**
            String with variable
        """
        for (i,j) in enumerate(self.filelines):
            if var_name in j:
                if line == 1:
                    return self.filelines[i+1]
                    break
                else:
                    lines = []
                    for k in range(line):
                        lines.append(self.filelines[i+1+k])
                    return lines
                    break

    def get_array(self, var_name):
        """
        Get the values of an array variable
        Array variables (e.g. temperature, pressure, etc.) in SHEMAT-Suite are
        stored in 1-D arrays in a compressed format. With this method, the variables
        are decompressed and returned as a 1-D list. The method also adjusts
        special boundary condition settings which are partly implemented as
        negative values of pressure, porosity and permeability.

        Decide if necessary!!! Use HDF for output...so rewrite
        """

    def set(self, var_name, value, line=1):
        """
        Set a SHEMAT-Suite variable to a specific value

        **Arguments**:
            - *var_name* = string: name of SHEMAT-Suite variable
            - *value* = string or number: variable value
        """
        for (i,j) in enumerate(self.filelines):
            if var_name in j:
                self.filelines[i+line] = str(value) + "\n"

    def set_array(self, var_name, value_list, **kwargs):
        value = ""
        for (i, l) in enumerate(self.filelines):
            # construct variable in correct format with multiplier "*"
            if var_name in l:
                n = 1
                for (j, val) in enumerate(value_list):
                    try:
                        if val == value_list[j+1]:
                            n += 1
                            continue
                    except IndexError:
                        pass
                    if n == 1:
                        if var_name == 'grid':
                            nx = value_list[0]
                            ny = value_list[1]
                            nz = value_list[2]
                            value += "%d " % val
                            nxyz = nx*ny*nz
                            if hasattr(self, 'temp init'):
                                tinit = self.get('temp init').rsplit()[0]
                            if hasattr(self, 'head init'):
                                hinit = self.get('head init').rsplit()[0]
                            if hasattr(self, 'pres init'):
                                pinit = self.get('pres init').rsplit()[0]
                        else:
                            value += "%.2f " % val
                    else:
                        value += "%d*%.2f " % (n, val)
                    n = 1
                self.filelines[i+1] = value + '\n'
                if var_name == 'grid':
                    if hasattr(self, 'temp init'):
                        self.set('temp init', '%d*%s' % (nxyz,tinit.split('*')[1]))
                    if hasattr(self, 'temp init'):
                        self.set('head init', '%d*%s' % (nxyz,hinit.split('*')[1]))
                    if hasattr(self, 'temp init'):
                        self.set('pres init', '%d*%s' % (nxyz,pinit.split('*')[1]))




    def set_grid(self, grid_data):
        new_nx, new_ny = grid_data.shape
        if new_nx != self._nx:
            print("nx is not the right dimension!")
            raise AttributeError
        if new_ny != self._ny:
            print("nx is not the right dimension!")
            raise AttributeError
        self._grid_data = grid_data

    def get_grid(self):
        return self._grid_data

    def update_extent(self):
        # first: check if both number of cells and cell widths are already defined
        if hasattr(self, '_dx') and hasattr(self, '_nx'):
            self._extent_x = self._nx * self._dx
            self._extent_y = self._ny * self._dy
            self._extent_z = self._nz * self._dz

    def get_extent(self):
        return (self._extent_x, self._extent_y, self._extent_z)

    def set_nxny(self, nx, ny):
        self._nx = nx
        self._ny = ny
        self.update_extent()

    def get_nxny(self):
        return (self._nx, self._ny)

    def set_dxdy(self, dx, dy):
        self._dx = dx
        self._dy = dy
        self.update_extent()

    def get_dxdy(self):
        return (self._dx, self._dy)

    def get_cell_boundaries(self):
        """
        calculate cell boundaries from delx, dely, delz, and save
        to self.boundaries_x, self.boundaries_y, self.boundaries_z
        """
        delx = self.get_array("delx")
        dely = self.get_array("dely")
        delz = self.get_array("delz")
        # x
        b = []
        laststep = 0
        b.append(laststep)
        for step in delx:
            b.append(laststep+step)
            laststep += step
        self.boundaries_x = b
        # y
        b = []
        laststep = 0
        b.append(laststep)
        for step in dely:
            b.append(laststep+step)
            laststep += step
        self.boundaries_y = b
        # z
        b = []
        laststep = 0
        b.append(laststep)
        for step in delz:
            b.append(laststep+step)
            laststep += step
        self.boundaries_z = b

            
    def get_cell_centres(self):
        """
        Calculate centre of cells in absolute values
        Cell centres are stored in object variables
        self.centre_x, self.centre_y, self.centre_z
        """
        # reload cell boundaries
        self.get_cell_boundaries()
        # calculate cell centres for each dimension
        self.centre_x = []
        for i in range(len(self.boundaries_x[:-1])):
            self.centre_x.append((self.boundaries_x[i+1]-self.boundaries_x[i])/2.+self.boundaries_x[i])
        self.centre_y = []
        for i in range(len(self.boundaries_y[:-1])):
            self.centre_y.append((self.boundaries_y[i+1]-self.boundaries_y[i])/2.+self.boundaries_y[i])
        self.centre_z = []
        for i in range(len(self.boundaries_z[:-1])):
            self.centre_z.append((self.boundaries_z[i+1]-self.boundaries_z[i])/2.+self.boundaries_z[i])



    def create_structure_from_voxel(self, filename):
        """
        Create a uindex structure field from a voxel file exported from GeoModeller.
        **Arguments**
        *filename*: string: name of .vox file

        **Returns**
        *info*:dictionary of model info, delxyz, nxyz, x0y0z0 etc
        *s*: string with uindex-field
        *TOP_BC_XX*:files with optional top bcs for surface topography
        """
        if filename[-4:] != ".vox":
            print("Not a valid voxel file (no .vox ending).")
            print("Please check file name and if it is a .vox export from GeoModeller.")
            raise IOError("Invalid file type.")
        else:
            with open(filename) as f:
                data = [line.split() for line in f]
                info = dict((var.strip(), float(num.strip())) for var, num in data[0:9])

                if data[9] == ['nodata_value','out']:
                    print("Warning: nodata_value in line 9.")
                    print("There are cells above the surface.")
                    print("See TOP_BC_{} for boundary conditions.".format(f.name[:-4]))
                    units = list(itertools.chain(*data[10:]))
                else:
                    units = list(itertools.chain(*data[9:]))

            try:
                fT = open("TOP_BC_{}.temp".format(f.name[:-4]), 'w')
                fh = open("TOP_BC_{}.head".format(f.name[:-4]), 'w')
                fp = open("TOP_BC_{}.pres".format(f.name[:-4]), 'w')
            except IOError:
                print("Can not open file TOP_BC_{}.temp for writing".format(f.name[:-4]))
                print("Can not open file TOP_BC_{}.head for writing".format(f.name[:-4]))
                print("Can not open file TOP_BC_{}.pres for writing".format(f.name[:-4]))

            nxyz = int(info['nx'] * info['ny'] * info['nz'])
            unui = {}
            uindex = 1
            count = 1
            form = units[0]
            uindex_field = []
            s = ""
            ix = 1
            iy = 1
            iz = 1
            p0 = 0.101325
            lapserate = -0.0065
            t_surf = 286.15

            for i in range(1, nxyz):
                if units[i] not in unui:  # if the unit is not in the dictionary, add it
                    unui.update({units[i]: uindex})
                    uname = units[i]
                    uindex += 1  # increase the uindex for shemat

                if units[i] == units[i - 1]:  # count up the units found in the voxel file
                    count += 1
                else:
                    # print("{}*{}".format(count,unui[units[i-1]]))
                    # append the units and write it in the format x*y until a new
                    # unit is reached
                    uindex_field.append("{}*{}".format(count, unui[units[i - 1]]))
                    s += "{}*{} ".format(count, unui[units[i - 1]])
                    count = 1
                if i == (nxyz - 1):
                    # print("{}*{}".format(count,unui[units[i]]))
                    # don't forget to include the last unit
                    uindex_field.append("{}*{}".format(count, unui[units[i]]))
                    s += "{}*{}".format(count, unui[units[i]])

                if ix < info['nx']:
                    ix += 1
                elif iy < info['ny']:
                    ix = 1
                    iy += 1
                else:
                    ix = 1
                    iy = 1
                    iz += 1

                if (units[i] == 'out' and iz < info['nz']) or iz == info['nz']:
                    fT.write("{} {} {} {} 0 \n".format(ix, iy, iz,
                                                       ((iz * info['dz'] + info['z0']) * lapserate + t_surf - 273.15)))
                    fh.write("{} {} {} {} 0 \n".format(ix, iy, iz, head))
                    fp.write("{} {} {} {} 0 \n".format(ix, iy, iz, 0.101325))
                else:
                    head = iz * info['dz']
                    # pres = p0 * (1 + lapserate/t_surf * (iz*info['dz'] + info['z0']))**((-scipy.constants.g*0.0289644)/(lapserate*scipy.constants.R))

            #un_counts = collections.Counter(units)
            fT.close()
            fh.close()
            fp.close()
            return info, s


    def read_monitor_as_dataframe(self, filename):
        """
        Routine to read the monitoring points of a transient SHEMAT-Suite simulation, returning an array of recorded
        values
        param filename: string: name of monitoring file
               varname: string or list of strings: name of variables to be loaded
        return: monitoring file: dataframe containing all information of the monitoring file
        """
        # replace any % comments with
        if sys.version_info.major == 2:
            print("Seems you still work with Python 2.7.")
            print("You should consider moving to Version 3.x")
            fid = fileinput.FileInput(filename, inplace=True, backup='.bak')
            for line in fid:
                print(line.replace('%', ''))
        elif sys.version_info.major == 3:
            with fileinput.FileInput(filename, inplace=True, backup='.bak') as fid:
                for line in fid:
                    print(line.replace('%', ''))


        # load dataframe
        datframe = pandas.read_csv(filename, delim_whitespace=True)
        return datframe

def create_empty_model(**kwargs):
    """
    Create a new SHEMAT-Suite model based on given grid and boundary conditions given.

    This method can be used to create a simple empty standard model with predefined grid spacing
    in each direction (delx, dely, delz) and simple boundary conditions.
    The standard base model without any kwargs is a conductive heat transport model with h5 and vtk
    output files. The simulation is steady-state and consists of a single unit. All default settings
    can be changed with optional kwargs.

    **Optional kwargs**:
        -*title* = string: title of the model
        -*delx* = []: list of spacing in x-direction
        -*dely* = []: list of spacing in y-direction
        -*delz* = []: list of spacing in z-direction
        -*extent_x* = (float, float): range of geomodel in x-direction (def= model range)
        -*extent_y* = (float, float): range of geomodel in y-direction (def= model range)
        -*extent_z* = (float, float): range of geomodel in z-direction (def= model range)
        -*transient* = boolean: if TRUE, set to transient simulation

    **Additional kwargs for boundary and initial conditions**:
        -*filename* = string: name of input file
        -*verbose* = boolean: show output of model on screen (def=False)
        -*vtk* = boolean: toggle output of a .vtk file (def=True)
        -*bc_temperature_top* = 'bcd', 'bcn': top boundary condition type for temp
        -*bc_temperature_base* = 'bcd', 'bcn': bottom boundary condition type for temp
        -*value_temperature_top* = float: fixed value (temperature for bcd, spec. heat flow for bcn)
        -*value_temperature_base* = float: fixed value (temperature for bcd, spec. heat flow for bcn)
        -*bc_head_top* = 'bcd', 'bcn': top boundary condition type for head
        -*bc_head_base* = 'bcd', 'bcn': base boundary condition type for head
        -*value_head_top* = float: fixed value (head for bcd, volumetric flow rate for bcn)
        -*value_head_base* = float: fixed value (head for bcd, volumetric flow rate for bcn)

    **Additional Keywords for geometry functionalities**:
        -*update_from_voxel_file* = boolean: update geology and grid properties from .vox file
        -*update_property_from_csv* = csv_file: csv file containing petrophysical properties (# units)
    """
    verbose = kwargs.get("verbose", False)
    S1 = SHEMATSuiteFile()
    S1.filelines = []
    lines = """!==========>>>>> MODEL INFO
# title
default_model
# linfo
1 1 1 1
# runmode
0
# USER=none
# PROPS=bas
# active temp head

!==========>>>>> I/O
# file output hdf vtk

!==========>>>>> MESH in meters
# grid
10 10 10
# delx
10*10
# dely
10*10
# delz
10*10

!==========>>>>> TIME STEP
# timestep control
0
1.0 1.0 1.0 0.0
# tunit
1
# time periods records=1
0.0	150000	100 lin
# output times records=1
31557600

!==========>>>>> NONLINEAR SOLVER
# nlsolve
100 0

!==========>>>>> FLOW
# lsolvef (linear solver control)
1.d-12 64 300
# nliterf (nonlinear iteration control)
1.0d-9 1.
# grad nliterf (nonlinear iterations control)
1.0d-7

!==========>>>>> TEMPERATURE
# lsolvet (linear solver control)
1.d-12 64 300
# nlitert (nonlinear iteration control)
1.0d-9 1.
#grad nlitert (nonlinear iteration control)
1.0d-7

!==========>>>>> BOUNDARY CONDITIONS

# head bcd	simple=top error=ignore
100*100.d0

# temp bcd simple=top error=ignore
100*11
# temp bcn simple=base error=ignore
100*0.03

!==========>>>>> INITIAL VALUES
# head init
1000*100.0d0
# temp init
1000*50.0d0

!==========>>>>> UNIT DESCRIPTION
# units
0.06 1.d0 1.d0 1.0d-15 1.0d-10 1.d0 1.d0 2.d0 0.d0 2.0d6 10.d0 0.d0 0.d0 2.d0 1.0d3 0.05d0 0.2d0
# uindex
1000*1
"""
    if kwargs.has_key('filename'):
        filename = kwargs['filename']
    else:
        filename = "default_SHEMAT_Model"

    for line in lines.split('\n'):
        if verbose:
            print line
        S1.filelines.append(line + '\n')

    if kwargs.has_key('transient') and kwargs['transient'] == True:
        S1.set("timestep control",1)
    if kwargs.has_key('title'):
        title = kwargs['title']
    else:
        title = "default SHEMAT-Suite model"
    S1.set('title', title)

    S1.write_file(filename)
    return S1
