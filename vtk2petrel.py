# -*- coding: utf-8 -*-
"""
Created on Fri May 19 14:45:12 2017

@author: ath
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:53:42 2017

@author: ath
"""
#-----------------------------------READ ME-----------------------------------#
# AUTHOR: Ariel T. Thomas  (athomas@eonercrwth-aachen.de)
#
# This code was created for facilitating the transfer of model simulation data
# from a VTK file to a Gslib file format which can be read by PETREL into the 
# existing 3D grid. The code functions as follows:
# User must define:
# 1--> name of text file in VTK format. e.g Model1.txt 
# 
# The followings tasks are performed:
# 
# 1> Reads the user defined input file, stores the names and number of scalar 
#    parameters. The main input file is then split with each paramter stored in
#    a separate file named by the paramter. The output files are named according
#    to the following structure: e.g <filename>_<propertyname>.txt
#
# N.B. Vector parameters are stored in a seperate file and NOT included in
# final output. <filename>_vectors.txt
#
# 2> Writes the file header to a text file for reference.
# 
# 3> Writes the data for each parameter in files named according to the paramater
#    

# OUTPUTS:
# +> File containing all scalar properties in Gslib format
# +> File containing only header information from original VTK
# +> 1 file for every scalar parmater with a list of values
# +> 1 file containing vector parameters

# N.B. The data is listed in the same order as assumed by SHEMAT from the front
# bottom corner of the model traversing along i first then j from the base of 
# the model upward. This data can then be imported into a Petrel model which must
# be simply defined as a box with the same dimensions.
# 
# --------------------------------------------------------------------------------------------
import os
# USER INPUTS----------------------------------------------------------
# Full name of text file with VTK format
filename = 'Dip_layer_mod_finalvtk.txt'      # <<<<<<<<<<<< USER INPUT
# number of cells in i, j & k directions
filebase = os.path.splitext(filename)[0]  #stores the name of the file to append to the output files           

#%%--------------------------------------------------------------------
# Splitting the scalars and vectors into separate files
pat ='VECTORS'
i=0
j=0
with open(filename) as myFile:
    for line in myFile:
        i+=1
        if pat in line:
            break
myFile = open(filename, 'r')
part2 = open('%s_vectors.txt' % filebase, 'w')
with open('%s_scalars.txt' % filebase, 'w') as part1:
    for line in myFile:
        j+=1
        if j<i:
            part1.write(line)
        else :
            part2.write(line)
part1.close()
part2.close()
myFile.close()

            

#%% Splitting the scalars into individual parts 
pat = 'SCALARS'
outfile = open('%s_Header.txt' % filebase, 'w')
list_props = []  #empty list created to store the names of properties found in file

with open('%s_scalars.txt' % filebase) as infile:      
    for line in infile:
        if pat not in line:
            outfile.write(line)
        else:
            items = line.split(pat)
            prop = line.split()
            list_props.append(prop[1])   #property names stored in list
            outfile.write(items[0])
            fp = open('%s.txt' % prop[1],'w')        
            for item in items[1:]:
                outfile = fp 
                outfile.write(pat + item)
outfile.close()
infile.close()
num_props = len(list_props)  #no. of properties counted and stored
print (' The properties in this file are listed: %s' %list_props)
pat = 'DIMENSIONS'
with open('%s_Header.txt' % filebase, 'r') as infile:
    for line in infile:
        if pat in line:
            n_i = line.split()[1]
            n_j = line.split()[2]
            n_k = line.split()[3]
infile.close()
print n_i,n_j,n_k                    
        

#%%  Rearranging the files into column form
cnt=0
ind=0
i=0
for i in range(num_props):
    with open('%s.txt' % list_props[i], 'r') as infile:
        val = infile.readlines()
        del val[:2]  #deleting heading lines
        tempfile = open('temp.txt','w+')
        for item in val:
            tempfile.write('%s' % item.replace('\n',''))
        tempfile.seek(0,0)
        val2 = tempfile.readline().replace('\n','')
        values = val2.split()
        tempfile.close()
        os.remove('temp.txt')
        with open('col_%s.txt' % list_props[i], 'w') as outfile:
            for item in values:
                outfile.write('%s\n' % item)
              
outfile.close()       

#%% Writing the properties to the gslib format
n_i=int(n_i)
n_j=int(n_j)
n_k=int(n_k)
length = n_i*n_j*n_k # 
prop_vals = []
# This loop creates a seperate file for each of the properties
for cnt in range(num_props):
    with open('col_%s.txt' % list_props[cnt], 'r') as temp: #opens the file containing the property values
        prop_vals = temp.readlines() #read all the values into a list
        outfile = open('%s_%s.txt' %(filebase,list_props[cnt]),'w') #opens file to write out
        outfile.write('PETREL: Properties \n'  #creates header for Petrel file
            '4 \n'                  #no. of property columns included in file
            'i_index unit1 scale1\n'
            'j_index unit1 scale1\n'
            'k_index unit1 scale1\n'
            '%s unit1 scale1\n' % list_props[cnt])
        i=j=k=n=0
        vert = n_k+1 
        for k in range(n_k):
            vert= vert - 1
            for j in range (n_j):
                for i in range (n_i):
                    outfile.write('%d   %d   %d %s ' %((i+1),(j+1),vert,prop_vals[n]))
                    n+=1
                    #print i,j,vert,n
        outfile.close()
outfile.close()
print 'DONE'




