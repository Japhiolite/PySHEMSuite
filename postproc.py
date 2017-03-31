"""
This post_processing module contains classes to analyse and visualise simulation data from SHEMAT-Suite Models.
The module contains methods for visualising HDF5 files and monitoring files. Support for VTK Files is planned.

This module is part of PySHEMSuite package and published under the MIT License as published by the Open Source
Initiative. Copyright 2017 (c)
"""
# import matplotlib as m
import matplotlib.pyplot as plt
import h5py
import seaborn as sb

class postprocess(object):
    def __init__(self,datafile):
        if datafile[-3:] == ".h5":
            print("Loading HDF5 file of simulation {}".format(datafile[:-3]))
            self.data = self.load_hdf(datafile)

   # def __repr__(self):
   #     print("The simulation has following fields:")
   #     print(list(self.data.keys()))
   #     print("nx = {}, ny = {}, nz = {}. ".format(*self.data['uindex'].shape))

    def print_fields(self):
        """
        Method to display all variables available in the loaded HDF file
        """
        print('The simulation has following fields: \n')
        print(list(self.data.keys()))


    def _set_plot_style(self):
        plt.style.use(['seaborn-white', 'seaborn-paper'])

    def load_hdf(self,file):
        return h5py.File(file,'r')

    def calc_ent_prod(sc, dim):
        """calculate entropy production in a model.
        **Arguments**:
         """

        if dim == '3D':
            x = np.linspace(min(f['x'][0, 0, :]), max(f['x'][0, 0, :]), f['delx'].shape[2])
            y = np.linspace(min(f['y'][0, :, 0]), max(f['y'][0, :, 0]), f['dely'].shape[1])
            z = np.linspace(min(f['z'][:, 0, 0]) + 25, max(f['z'][:, 0, 0]) + 25, f['delz'].shape[0])
            # z1 = np.linspace(-3000.,0,fid['delz'].shape[0])
            (X, Y) = np.meshgrid(x, y)
            Z = f['z'][:, 0, 0]

            delx = f['delx'][0, 0, 0]
            dely = f['dely'][0, 0, 0]
            delz = f['delz'][0, 0, 0]

            TC = f['lz'][:, :, :]
            temp = f['temp'][:, :, :]
            uind = f['uindex'][:, :, :]

            grTx, grTy, grTz = np.gradient(temp)
            grTx = grTx / delx
            grTy = grTy / dely
            grTz = grTz / delz

            ds = (TC / temp ** 2) * (grTx ** 2 + grTy ** 2 + grTz ** 2)
            cubeds = ds ** (1. / 3.)
            return ds, X, Y, Z, cubeds, temp, uind

        # if 2D, check if xz or yz
        if dim == '2D':
            dimcheck = f['temp'].shape
            # print "Shape is:", dimcheck
            if dimcheck[0] == 1 and dimcheck[1] != 1 and dimcheck[2] != 1:
                print
                "section is yz"
                # dimenstions
                delx = f['delx'][0, 0, 0]
                dely = f['dely'][0, 0, 0]
                delz = f['delz'][0, 0, 0]

                # Parameters: TC = Thermal conductivity, temp = temperature

                TC = f['lz'][0, :, :]
                temp = f['temp'][0, :, :]

                grTx, grTz = np.gradient(temp)

                grTx = grTx / delx
                grTz = grTz / delz

                ds = (TC / (temp * temp)) * (grTx ** 2 + grTz ** 2)
                cubeds = ds ** (1. / 3.)
                return ds, cubeds
            elif dimcheck[1] == 1 and dimcheck[0] != 1 and dimcheck[2] != 1:
                # print "section is xz"
                # dimenstions
                delx = f['delx'][0, 0, 0]
                dely = f['dely'][0, 0, 0]
                delz = f['delz'][0, 0, 0]

                # Parameters: TC = Thermal conductivity, temp = temperature

                TC = f['lz'][:, 0, :]
                temp = f['temp'][:, 0, :]
                # np.shape(temp[:,0,:])
                grTx, grTz = np.gradient(temp)

                grTx = grTx / delx
                grTz = grTz / delz

                ds = (TC / (temp * temp)) * (grTx ** 2 + grTz ** 2)
                cubeds = ds ** (1. / 3.)
            return cubeds
        elif dimcheck[2] == 1 and dimcheck[0] != 1 and dimcheck[1] != 1:
            print
            "section is xy"
            # dimenstions
            delx = f['delx'][0, 0, 0]
            dely = f['dely'][0, 0, 0]
            delz = f['delz'][0, 0, 0]

            # Parameters: TC = Thermal conductivity, temp = temperature

            TC = f['lz'][:, :, 0]
            temp = f['temp'][:, :, 0]

            grTx, grTz = np.gradient(temp)

            grTx = grTx / delx
            grTz = grTz / delz

            ds = (TC / (temp * temp)) * (grTx ** 2 + grTz ** 2)
            cubeds = ds ** (1. / 3.)
            return ds, cubeds


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

