"""
PySHEMAT-Suite is an open-source collection of Python modules to easily create
and process SHEMAT-Suite Input files.

********************************************************************************

PySHEMAT-Suite can be redistributed and/or modified under the terms of the MIT
License as published by the Open Source Initiative.
(https://opensource.org/licenses/MIT)
Copyright 2017(c) Jan Niederau

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
********************************************************************************

For module, update and documentation of PySHEMAT-Suite, see the Git-repository.
"""

import os, sys
import matplotlib as m
import numpy as np
# import h5py
# import scipy.constants
import itertools
# import collections
import pandas as p
# import fileinput
# import re


class SHEMATSuiteFile:
    """
    Class for SHEMAT-Suite simulation input files
    Object methods enable a direct access of all variables and parameters
    defined in the input file.
    Further methods enable 1D, 2D and 3D plots of HDF5 files and creation of
    publication-ready images.
    """

    def __init__(self, filename='', **kwargs):
        """
        Args:
        :param filename: string, filename of SHEMAT-Suite Input file to load.
                         If no filename is provided, an empty file object is created.
        :param kwargs: Optional arguments.
                        offscreen: boolean, set variables for offscreen rendering, e.g. for creating plots
                        on a remote machine via ssh

        """
        if filename == '':
            print("creating new Input file")
            self.filelines = ['!===>>Empty model input created with PySHEMSuite \n',
                              '# title \n',
                              'Empty_input_file \n']
            if 'new_filename' in kwargs:
                self.filename = kwargs['new_filename']
        else:
            self.filelines = self.read_file(filename)
            self.filename = filename
            self._nx, self._ny, self._nz = self.get('grid').split()
        if 'offscreen' in kwargs and kwargs['offscreen']:
            m.use('Agg')
        if sys.version_info.major == 2:
            print("You are using Python version 2.x")
            print("This software is programmed for Python 3.x.")
            print("Full functionalities are not guaranteed with Python 2.x")
        elif sys.version_info.major == 3:
            print("Python 3, good to go!")

    def __str__(self, **kwargs):
        """
        Print function of the Basic Input File components if an existing SHEMAT-Suite file is loaded
            :param kwargs:

        :return: info_string: string, containing information about model dimensions, active variables, etc
        """
        # basic information
        info_string = "SHEMAT-Suite object"
        try:
            info_string = "Model object with these parameters: \n"
            # info on grid cells, spacing, extent
            #try:
            #    info_string += "Number of cells \t = nx:{}, ny:{}, nz:{}\n".format(self._nx, self._ny, self._nz)
            #    info_string += "Cell dimensions \t = dx:{} m, dy:{} m, dz:{} m\n".format(self._dx, self._dy, self._dz)
            #    info_string += "Grid extent \t = x:{} m, y:{} m, z:{} m\n".format(self._nx*self._dx, self._ny*self._dy, self._nz*self._dz)
            #except:
            self._nx, self._ny, self._nz = [int(it) for it in self.get('grid').split()]
            info_string += "Number of cells \t = nx:{}, ny:{}, nz:{}\n".format(self._nx, self._ny, self._nz)
            self._dx = int(self.get('delx').split('*')[1].rstrip())
            self._dy = int(self.get('dely').split('*')[1].rstrip())
            self._dz = int(self.get('delz').split('*')[1].rstrip())
            info_string += "Cell dimensions \t = dx:{} m, dy:{} m, dz:{}\n".format(self._dx, self._dy, self._dz)
            info_string += "Grid extent \t \t = x:{} m, y:{} m, z:{} m\n \n".format(self._nx*self._dx,self._ny*self._dy,self._nz*self._dz)
            info_string += "Property module \t = {} \n".format(self.get('PROPS').rstrip())
            info_string += "User \t \t \t = {} \n".format(self.get('USER').rstrip())
            info_string += "active equations \t = {}, {}".format(*self.get('active'))
        except:
            info_string = 'Not all model grid information yet!'

        return info_string

    def read_file(self, filename):
        """
        Read an existing SHEMAT-Suite Input file

        Arguments:
            :param filename:    string, name of the Input file to load.
            :return:    filelines, list of filelines in the Input file.

        Example:
        (n is a SHEMATSuiteFile object)
        n.read_file('SHEMAT-Suite_inp_file')
        """
        try:
            file = open(filename, 'r')
        except IOError:
            print("Cannot open file {}.".format(filename))
            print("Please check if the file name and directory are correct.")
            raise IOError
        # check if number of entries is correct
        filelines = file.readlines()
        file.close()
        # set local vairables
        return filelines

    def write_file(self, filename):
        """
        Write a PySHEMSuite object to a file

        Arguments:
            :param filename:    string, name of the SHEMAT-Suite Input file to write

        Example:
        (n is a SHEMATSuiteFile object)
        n.write('Test_file')
        """
        try:
            file = open(filename, 'w')
        except IOError:
            print("Cannot open file {}.")
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

        Arguments:
            :param var_name:    string Name of the scalar variable

        Optional Argument:
            :param line:        integer, number of lines to read after the var_name


        :return:            string, containing variables to get
        """
        for (i, j) in enumerate(self.filelines):
            if var_name in j:
                if var_name == 'PROPS':
                    return self.filelines[i].split('=')[1]
                if var_name == 'USER':
                    return self.filelines[i].split('=')[1]
                if var_name == 'active':
                    return self.filelines[i].split()[1:]
                if line == 1:
                    return self.filelines[i + 1]
                    break
                else:
                    lines = []
                    for k in range(line):
                        if self.filelines[i + 1 + k].startswith(("#","!","\n")):
                            return lines
                            break
                        lines.append(self.filelines[i + 1 + k])
                    return lines
                    break

    def get_array(self, var_name):
        """
        Get the values of an array variable
        Array variables (e.g. temperature, pressure, etc.) in SHEMAT-Suite are
        stored in 1-D arrays in a compressed format. With this method, the variables
        are decompressed and returned as a 1-D list.
        """
        #for (i,l) in enumerate(self.filelines):
        #    if var_name in l:
        pass


    def set(self, var_name, value, line=1):
        """
        Set a SHEMAT-Suite variable to a specific value

        Arguments:
            :param var_name:    string, name of SHEMAT-Suite variable
            :param value:       string or number, variable value

        :param line:        *optional* integer, for multiline variables
        """
        for (i, j) in enumerate(self.filelines):
            if var_name in j:
                self.filelines[i + line] = str(value) + " \n"
        if not any(var_name in l for l in self.filelines):
            self.filelines.append("# " + str(var_name) + " \n")
            self.filelines.append(str(value) + " \n")


    def set_array(self, var_name, value_list, **kwargs):
        """
        Set a value array
        :param var_name:  string, variable name
        :param value_list:
        :param kwargs:
        :return:
        """
        value = ""
        for (i, l) in enumerate(self.filelines):
            # construct variable in correct format with multiplier "*"
            if var_name in l:
                n = 1
                for (j, val) in enumerate(value_list):
                    try:
                        if val == value_list[j + 1]:
                            if var_name != 'grid':
                                n += 1
                                continue
                    except IndexError:
                        pass
                    if n == 1:
                        if var_name == 'grid':
                            nx = value_list[0]
                            ny = value_list[1]
                            nz = value_list[2]
                            value += "{} ".format(val)
                            nxyz = nx * ny * nz
                            try:
                                tinit = self.get('temp init').rsplit()[0]
                            except AttributeError:
                                pass
                                print("temp init not found")
                            try:
                                hinit = self.get('head init').rsplit()[0]
                            except AttributeError:
                                pass
                                print("head init not found")
                            try:
                                pinit = self.get('pres init').rsplit()[0]
                            except AttributeError:
                                pass
                                #print("pres init not found")
                            try:
                                delx = self.get('delx').rsplit()[0]
                                dely = self.get('dely').rsplit()[0]
                                delz = self.get('delz').rsplit()[0]
                            except AttributeError:
                                pass
                        else:
                            value += "{} ".format(val)
                    else:
                        value += "{}*{} ".format(n, val)
                    n = 1
                self.filelines[i + 1] = value + '\n'
                if var_name == 'grid':
                    try:
                        self.set('temp init', '{}*{}'.format(nxyz, tinit.split('*')[1]))
                    except:
                        pass
                    try:
                        self.set('head init', '{}*{}'.format(nxyz, hinit.split('*')[1]))
                    except:
                        pass
                    try:
                        self.set('pres init', '{}*{}'.format(nxyz, pinit.split('*')[1]))
                    except:
                        pass
                    try:
                        self.set('delx', '{}*{}'.format(nx, delx.split('*')[1]))
                        self.set('dely', '{}*{}'.format(ny, dely.split('*')[1]))
                        self.set('delz', '{}*{}'.format(nz, delz.split('*')[1]))
                    except:
                        raise AttributeError

        if not any(var_name in l for l in self.filelines):
            self.filelines.append("# " + str(var_name) + " \n")
            s = (' '.join(str(e) for e in value_list) + " \n")
            self.filelines.append(s)

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
            b.append(laststep + step)
            laststep += step
        self.boundaries_x = b
        # y
        b = []
        laststep = 0
        b.append(laststep)
        for step in dely:
            b.append(laststep + step)
            laststep += step
        self.boundaries_y = b
        # z
        b = []
        laststep = 0
        b.append(laststep)
        for step in delz:
            b.append(laststep + step)
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
            self.centre_x.append((self.boundaries_x[i + 1] - self.boundaries_x[i]) / 2. + self.boundaries_x[i])
        self.centre_y = []
        for i in range(len(self.boundaries_y[:-1])):
            self.centre_y.append((self.boundaries_y[i + 1] - self.boundaries_y[i]) / 2. + self.boundaries_y[i])
        self.centre_z = []
        for i in range(len(self.boundaries_z[:-1])):
            self.centre_z.append((self.boundaries_z[i + 1] - self.boundaries_z[i]) / 2. + self.boundaries_z[i])

    def create_structure_from_voxel(self, filepath, ret=False):
        """
        Create a uindex structure field from a voxel file exported from GeoModeller.
        Also creates three files with boundary conditions for the top of the model (dirichlet) for
        temperature, head, and pressure.

        Arguments
            :param filename: string, name of .vox file
            :param ret:         boolean, if true, method gives return

        **Returns**
        :return:
            info:           dictionary of model info, delxyz, nxyz, x0y0z0 etc
            uindex_str:     string with uindex-field
            unui:           dictionary with Unit-name <-> Uindex connection
            TOP_BC_XX:      external files automatically created with optional top bcs for surface topograpy
        """
        if "\\" in filepath:
            filepath = filepath.replace('\\','/')
        filename = filepath.split('/')[-1]
        print(type(filename),filename)
        if filename[-4:] != ".vox":
            print("Not a valid voxel file (no .vox ending).")
            print("Please check file name and if it is a .vox export from GeoModeller.")
            raise IOError("Invalid file type.")
        else:
            with open(os.path.join(filepath)) as f:
                self.data = [line.split() for line in f]
                self.info = dict((var.strip(), float(num.strip())) for var, num in self.data[0:9])
                try:
                    self.info['nx'] = int(self.info['nx'])
                    self.info['ny'] = int(self.info['ny'])
                    self.info['nz'] = int(self.info['nz'])
                except TypeError:
                    print("Error generating integer nx, ny, nz.")


                if self.data[9] == ['nodata_value', 'out']:
                    print("Warning: nodata_value in line 9.")
                    print("There are cells above the surface.")
                    print("See TOP_BC_{} for boundary conditions.".format(filename[:-4]))
                    self.units = list(itertools.chain(*self.data[10:]))
                else:
                    self.units = list(itertools.chain(*self.data[9:]))

            try:
                fT = open("TOP_BC_{}.temp".format(filename[:-4]), 'w')
                fh = open("TOP_BC_{}.head".format(filename[:-4]), 'w')
                fp = open("TOP_BC_{}.pres".format(filename[:-4]), 'w')
            except IOError:
                print("Can not open file TOP_BC_{}.temp for writing".format(filename[:-4]))
                print("Can not open file TOP_BC_{}.head for writing".format(filename[:-4]))
                print("Can not open file TOP_BC_{}.pres for writing".format(filename[:-4]))

            self.nxyz = int(self.info['nx'] * self.info['ny'] * self.info['nz'])
            self.unui = {}
            uindex = 1
            count = 1
            form = self.units[0]
            uindex_field = []
            self.uindex_str = ""
            ix = 1
            iy = 1
            iz = 1
            p0 = 0.101325
            lapserate = -0.0065
            t_surf = 286.15

            for i in range(1, self.nxyz):
                if self.units[i] not in self.unui:  # if the unit is not in the dictionary, add it
                    self.unui.update({self.units[i]: uindex})
                    self.uname = self.units[i]
                    uindex += 1  # increase the uindex for shemat

                if self.units[i] == self.units[i - 1]:  # count up the units found in the voxel file
                    count += 1
                else:
                    # print("{}*{}".format(count,unui[units[i-1]]))
                    # append the units and write it in the format x*y until a new
                    # unit is reached
                    uindex_field.append("{}*{}".format(count, self.unui[self.units[i - 1]]))
                    self.uindex_str += "{}*{} ".format(count, self.unui[self.units[i - 1]])
                    count = 1
                if i == (self.nxyz - 1):
                    # print("{}*{}".format(count,unui[units[i]]))
                    # don't forget to include the last unit
                    uindex_field.append("{}*{}".format(count, self.unui[self.units[i]]))
                    self.uindex_str += "{}*{}".format(count, self.unui[self.units[i]])

                if ix < self.info['nx']:
                    ix += 1
                elif iy < self.info['ny']:
                    ix = 1
                    iy += 1
                else:
                    ix = 1
                    iy = 1
                    iz += 1

                if (self.units[i] == 'out' and iz < self.info['nz']) or iz == self.info['nz']:
                    fT.write("{} {} {} {:.5f} 0 \n".format(ix, iy, iz,
                                                       ((iz * self.info['dz'] + self.info['z0']) * lapserate + t_surf - 273.15)))
                    fh.write("{} {} {} {:.5f} 0 \n".format(ix, iy, iz, head))
                    fp.write("{} {} {} {:.5f} 0 \n".format(ix, iy, iz, 0.101325))
                else:
                    head = iz * self.info['dz']
                    # pres = p0 * (1 + lapserate/t_surf * (iz*info['dz'] + info['z0']))**((-scipy.constants.g*0.0289644)/(lapserate*scipy.constants.R))

            # un_counts = collections.Counter(units)
            fT.close()
            fh.close()
            fp.close()
            if ret == True:
                return self.info, self.uindex_str, self.unui

    def place_shape(self, filename, unitname, ret=False):
        """
        Modifies an existing (uniform) uindex-field with shape data extracted from
        GeoModeller.

            Arguments
                :param filename: string, name of .wrl file
                :param unitname: string, name of new unit
                :param ret:      boolean, if true, method gives return

            **Returns**
            :return:
                uindex_str:     string with modified uindex-field
        """
        if unitname in self.unui:
            print("The chosen unitname '{}' is already taken - Placement aborted.".format(unitname))
            return
        with open(filename, 'r') as f:
            shape = f.read()

        # read-in-comprehension-voodoo
        shape = shape[shape.find("point [") + 8:shape.find("]")]
        shape = [line.rstrip(", ").split() for line in shape.splitlines()]

        # plug coordinates in respective lists
        x_shape, y_shape, z_shape = zip(*shape)

        # to arrays
        x_shape = np.array(x_shape, dtype=float)
        y_shape = np.array(y_shape, dtype=float)
        z_shape = np.array(z_shape, dtype=float)

        # correct offset of model, divide by dxyz
        x_shape = (x_shape - self.info['x0'] + self.info['dx']/2) / self.info['dx']
        y_shape = (y_shape - self.info['y0'] + self.info['dy']/2) / self.info['dy']
        z_shape = (z_shape - self.info['z0'] + self.info['dz']/2) / self.info['dz']

        # floor to nearest int
        x_shape = np.floor(x_shape)
        y_shape = np.floor(y_shape)
        z_shape = np.floor(z_shape)

        # clip maximum value
        np.place(x_shape, x_shape >= self.info['nx'], self.info['nx'] - 1)
        np.place(y_shape, y_shape >= self.info['ny'], self.info['ny'] - 1)
        np.place(z_shape, z_shape >= self.info['nz'], self.info['nz'] - 1)

        # copy and unpack uindex
        model = self.unpack(self.uindex_str.split())
        model = np.reshape(np.array(model), (self.info['nx'], self.info['ny'], self.info['nz']), order='F')
        for x, y, z in zip(x_shape, y_shape, z_shape):
            model[int(x), int(y), int(z)] = len(self.unui) + 1

        # flatten and re-write in *-notation
        model = " ".join(self.collapse(model))
        self.uindex_str = model
        self.set("uindex",self.uindex_str)

        # unit list handling
        self.unui[unitname] = len(self.unui) + 1
        self.filelines.insert(
            self.filelines.index("# units\n") + len(self.unui),
            '0.06 1.d0 1.d0 1.0d-15 1.0d-10 1.d0 1.d0 2.d0 0.d0 2.0d6 10.d0 0.d0 0.d0 2.d0 1.0d3 0.05d0 0.2d0\n')

        if ret==True:
            return self.uindex_str

    def unpack(self, raw_list):
        """
        Takes a list in SHEMAT notation and splits it into its constituents.

        Parameters
        ----------
        raw_list : list
               A list of strings in the format 'X*Y' and/or 'Y' corresponding to SHEMAT short notation.

        Returns
        -------
        array
                An array of grid-matching (uncollapsed) ints. Can easily be manipulated afterwards.

        """
        splitlist = []
        for element in raw_list:
            if "*" in element:
                splitlist.append(element.split("*"))
            else:
                splitlist.append(['1', element])

        unpacked_temp = [[int(X)] * int(Y) for Y, X in splitlist]
        self.unpacked_list = [item for pairs in unpacked_temp for item in pairs]

        return np.array(self.unpacked_list)


    def collapse(self, array3d):
        """
        Takes a 3-d field, flattens and re-writes it to SHEMAT short notation.

        Parameters
        ----------
        array3d : numpy-array
                   a 3-d array containing a (uindex) field mapped to the grid.

        Returns
        -------
        list
            A list of strings in SHEMAT short notation representing the unit information.

        """
        a = array3d.flatten('F')
        sequence = [len(list(group)) for key, group in itertools.groupby(a)]
        unit_id = [key for key, group in itertools.groupby(a)]
        self.combined = ["%s*%s" % (pair) for pair in zip(sequence, unit_id)]
        return self.combined



def create_layercake(num_layers,dp=True,**kwargs):
    """
    Method to create an example layercake model with n horizontal units
    :param num_layers: integer, number of units
    :param dp: Boolean, if string should be transformed to Fortran double precision "d0"
    :return: string, Input File
    """

    verbose = kwargs.get("verbose", False)
    lcake = SHEMATSuiteFile(new_filename='layer_cake_model')
    lcake.filelines = []
    lines = """!==========>>>>> MODEL INFO
# title
layercake_model
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
50 50 20
# delx
50*50
# dely
50*50
# delz
20*50

!==========>>>>> TIME STEP
# timestep control
0
1.0 1.0 1.0 0.0

!==========>>>>> NONLINEAR SOLVER
# nlsolve
100 0

!==========>>>>> FLOW
# lsolvef (linear solver control)
1.d-10 64 300
# nliterf (nonlinear iteration control)
1.0d-8 1.

!==========>>>>> TEMPERATURE
# lsolvet (linear solver control)
1.d-9 64 300
# nlitert (nonlinear iteration control)
1.0d-7 1.

!==========>>>>> BOUNDARY CONDITIONS

# head bcd	simple=top error=ignore
2500*1000.d0

# temp bcd simple=top error=ignore
2500*11
# temp bcn simple=base error=ignore
2500*0.06

!==========>>>>> INITIAL VALUES
# head init
50000*1000.0d0
# temp init
50000*50.0d0

!==========>>>>> UNIT DESCRIPTION
# units
0.1 1.0 1.0 1.0e-15 1.0e-10 1.0 1.0 2.1 0.4e-6 2.0e6 10.0 0.0 0.0 2.0 1.0e3 0.05 0.2
# uindex
1000*1
"""

    if 'filename' in kwargs:
        filename = kwargs['filename']
    else:
        filename = "layer_cake_model"

    for line in lines.split(('\n')):
        if verbose:
            print(line)
        lcake.filelines.append(line + '\n')


    if num_layers == 1:
        pass
    else:
        units = {'!Porosity': 0.1,
                 'kxz': 1.0,
                 'kyz': 1.0,
                 'kz': 1.0e-15,
                 'Compressibility': 1.0e-10,
                 'lxz': 1.0,
                 'lyz': 1.0,
                 'lz': 2.1,
                 'Heat Prod rate': 0.4e-6,
                 'thermal capacity': 2.0e6,
                 'dispersivity': 10.0,
                 'Electric cond': 0.0,
                 'coupling coeff': 0.0,
                 'BC-parameter': 2.0,
                 'Capillary pressure': 1.0e3,
                 'res saturation non-wet': 0.05,
                 'res saturation wet': 0.2}

        df = p.DataFrame([units], columns=list(units.keys()))
        add_unit = []
        for i in range(num_layers-1):
            add_unit.append([np.random.normal(loc=0.1,scale=0.05),
                             1.0,
                             1.0,
                             np.random.lognormal(mean=1.0,sigma=3)*10**-15,
                             np.random.normal(loc=1.0e-10,scale=5.0e-11),
                             1.0,
                             1.0,
                             np.random.normal(loc=2.2,scale=0.6),
                             np.random.normal(loc=1.0e-7,scale=2.0e-8),
                             np.random.normal(loc=2.0e6, scale=1.0e5),
                             np.random.normal(loc=10., scale=3.),
                             0.0,
                             0.0,
                             2.0,
                             np.random.normal(loc=1.0e3,scale=2.0e2),
                             0.0,
                             0.0])
        df2 = p.DataFrame(add_unit,columns=list(units.keys()))
        df = df.append(df2, ignore_index=True)
        df_string = df.to_string(index=False,justify='left',header=False)

        if dp == True:
            df_string = df_string.replace('e-','d-')
            df_string = df_string.replace('e+','d+')

        lcake.set('units',df_string)

        i,j,k = lcake.get('grid').split()
        i = int(i)
        j = int(j)
        k = int(k)
        layer_thickness = np.round(k/num_layers,0)
        cum_thickness = 0
        uindex = ''

        if k % num_layers == 0:
            for num in range(1,num_layers+1):
                uindex += str(int(layer_thickness*i*j))+'*'+str(num)+' '
        else:
            count = 0
            for num in range(1,num_layers):
                uindex += str(int(layer_thickness*i*j))+'*'+str(num)+' '
                count += layer_thickness
            uindex += str(int((k-count)*i*j))+'*'+str(num_layers)

        lcake.set('uindex',uindex)

        return lcake





def create_standard_model(**kwargs):
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
    if 'filename' in kwargs:
        filename = kwargs['filename']
    else:
        filename = "default_SHEMAT_Model"

    for line in lines.split('\n'):
        if verbose:
            print(line)
        S1.filelines.append(line + '\n')

    if 'transient' in kwargs and kwargs['transient'] == True:
        S1.set("timestep control", 1)
    if 'title' in kwargs:
        title = kwargs['title']
    else:
        title = "default SHEMAT-Suite model"
    S1.set('title', title)

    S1.write_file(filename)
    return S1


