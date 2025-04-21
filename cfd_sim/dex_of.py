# DexOF - DEXter openfoam interface.
# Originally,
# Stevens Institute of Technology
# Pitz & Pochiraju
# December 13 - 2021
# Release 0.1
#
# Modified by S.Siwakorn


import numpy as np
import stl
from stl import mesh
import math
import sys
import os
import json
import kajiki
import logging

def parse_args_any(args):
    pos = []
    named = {}
    key = None
    for arg in args:
        if key:
            if arg.startswith('--'):
                named[key] = True
                key = arg[2:]
            else:
                named[key] = arg
                key = None
        elif arg.startswith('--'):
            key = arg[2:]
        else:
            pos.append(arg)
    if key:
        named[key] = True
    return (pos, named)

def kajiki_it(templfile,outfile,problemdict):
    with open(templfile) as templ:
        data=templ.read()
    Template = kajiki.TextTemplate(data)
    outlines = Template(problemdict).render()
    with open(outfile,'w') as outfile:
        outfile.write(outlines)
    return outlines

def dex2dict(filename):
    # lame version of dex parser to extract what's needed
    with open(filename) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
    dexdict = {}
    for line in lines:
        if not line.startswith('*'):
            words = line.split(',')
            dexdict[words[0]]=words[-1]
    return dexdict

def find_mins_maxs(obj):
    minx = obj.x.min()
    maxx = obj.x.max()
    miny = obj.y.min()
    maxy = obj.y.max()
    minz = obj.z.min()
    maxz = obj.z.max()
    return minx, maxx, miny, maxy, minz, maxz

def computational_domain(problemdict):
    bb = problemdict['boundingbox']
    xlength = bb[1]-bb[0]
    ylength = bb[3]-bb[2]
    zlength = bb[5]-bb[4]
    #
    DomainSizeXFront = float(problemdict['DomainSizeXFront'])
    DomainSizeXBack = float(problemdict['DomainSizeXBack'])
    xmin = round(-xlength*DomainSizeXBack, 3)
    # xmax = round(xlength*DomainSizeXFront, 3)
    xmax = round(xlength, 3)
    x_tpd5 = xmax + 0.25
    #
    DomainSizeYLeft= float(problemdict['DomainSizeYLeft'])
    DomainSizeYRight = float(problemdict['DomainSizeYRight'])
    ymin = round(-ylength*DomainSizeYRight, 3)
    # ymax = ylength*DomainSizeYLeft
    ymax = 0.0
    #
    DomainSizeZTop = float(problemdict['DomainSizeZTop'])
    DomainSizeZBot = float(problemdict['DomainSizeZBottom'])
    zmin = round(-zlength*DomainSizeZBot * 1.0, 3)
    zmax = round(zlength*DomainSizeZTop, 3)
    zmid3 = round(float(problemdict['Draft']), 3)
    zmid2 = round(zmid3 - (zmid3 / 4), 3)
    zmid4 = round(zmid3 + (zmid3 / 4), 3)
    # zmid3 = round(zmax / 10.0, 3)
    # zmid2 = round(zmid3 - 0.05, 3)
    # zmid2 = round(zmid3 - 0.056, 3)
    zmid1 = round(-1.0, 3)
    
    # zmid2 = 0.188
    # zmid3 = 0.244
    # zmid4 = 0.3
    zmid5 = zmax


    # set up domain grid
    nxgrid = int((xmax-xmin)/float(problemdict['cellSizeX']))
    # nygrid = int((ymax-ymin)/float(problemdict['cellSizeY']))
    nygrid =  int(abs(ymin))
    nzgrid = int((zmax-zmin)/float(problemdict['cellSizeZ']))
    # nzgrid1 = int(nzgrid * 0.2)
    # nzgrid2 = int(nzgrid / 5.0)
    nzgrid1 = nzgrid
    nzgrid2 = nzgrid
    # nzgrid3 = int(nzgrid/1.2)
    nzgrid3 = int(nzgrid * 0.8 * 0.1)
    # nzgrid4 = nzgrid
    nzgrid4 = nzgrid3
    # nzgrid5 = nzgrid
    nzgrid5 = int(nzgrid * 0.8)
    # nzgrid6 = int(nzgrid / 5.0)
    nzgrid6 = int(nzgrid * 0.4)
    #
    #note siwakorn (xmin-0.7 0 0)
    # xlocinside = xmax - 0.01*(xmax-xmin)
    # ylocinside = ymax - 0.01*(ymax-ymin)
    # zlocinside = zmax - 0.01*(zmax-zmin)
    # xlocinside = xmin-0.7
    xlocinside = -0.7
    ylocinside = 0
    zlocinside = 0

    return {'xmin':xmin, 'xmax':xmax, 'x_tpd5':x_tpd5,
            'ymin':ymin,'ymax':ymax,'zmin':zmin,'zmax':zmax,
            'zmid1':zmid1, 'zmid2':zmid2, 'zmid3':zmid3, 'zmid4':zmid4, 'zmid5':zmid5,
            'nxgrid':nxgrid,'nygrid':nygrid,'nzgrid':nzgrid,
            'nzgrid1':nzgrid1, 'nzgrid2':nzgrid2, 'nzgrid3':nzgrid3, 'nzgrid4':nzgrid4, 'nzgrid5':nzgrid5, 'nzgrid6':nzgrid6,
            'xlocinside':xlocinside,'ylocinside':ylocinside,'zlocinside':zlocinside}

def stlPrep(configdict):
    outdict = {}
#    print("usage python stlPrep.py orig.stl aoa_degrees final.stl ")
    infile = configdict['infile']
    # aoa = float(configdict['aoa'])
    outfile = 'stl_cfd/ship.stl'

    your_mesh = mesh.Mesh.from_file(infile)
    # decrease loglevel
    your_mesh.logger.setLevel(logging.ERROR)

    volume, cog, inertia = your_mesh.get_mass_properties()
    # print("Volume                                  = {0}".format(volume))
    # print("Position of the center of gravity (COG) = {0}".format(cog))
    # print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
    # print("                                          {0}".format(inertia[1,:]))
    # print("                                          {0}".format(inertia[2,:]))
    # print("Bounding Box")
    # print (find_mins_maxs(your_mesh))

    # cogx = cog[0]
    # cogy = cog[1]
    # cogz = cog[2]

    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(your_mesh)
    bbox = [minx,maxx,miny,maxy,minz,maxz]
    # cog = [cog[0], cog[1], cog[2]]

    # unbracket 
    cog = ' '.join(map(str, cog))

    # save the mesh
    # your_mesh.save(outfile, mode=stl.Mode.ASCII)
    
    meshcpycmd = 'cp -r ' + 'stl_cfd/ship_gen.stl ' + 'stl_cfd/ship.stl'
    
    os.system(meshcpycmd)

    outdict.update({'outfile':outfile,'volume':volume,
        'cog':cog,'inertia':inertia,'boundingbox':bbox})
    return outdict

# Run stl2ascii on this.
def setup_of(problemdict):
    # check if casefolder exists if not create it.
    casefolder = problemdict['current_dir']+"/OF_default_casefolder"
    if 'casefoldername' in problemdict:
        casefolder = problemdict['current_dir']+"/"+problemdict['casefoldername']
    if not os.path.exists(casefolder):
        os.makedirs(casefolder)
    else:
        print("Warning: Casefolder already exists, files will be overwritten")

    # create files that need to be templated
    ofcopycmd  = 'cp -r ' + problemdict['dexof_path']+"/ofTemplate/* " + casefolder
    print("Copying::",ofcopycmd)
    #os.system('cp -r ofTemplate/* '+ casefolder)
    os.system(ofcopycmd)
    # move stl file into the casefolder
    outfile = problemdict['current_dir']+"/"+problemdict['outfile']
    stlmovecmd = 'cp '+outfile+' ' + casefolder+'/constant/triSurface/ship.stl'
    os.system(stlmovecmd)
    # First copy the STL File in the right place
    templatesdict={'system/blockMeshDict_templ.txt': 'system/blockMeshDict','system/decomposeParDict_templ.txt': 'system/decomposeParDict',
    'system/snappyHexMeshDict_templ.txt':'system/snappyHexMeshDict', 'system/setFieldsDict_templ.txt':'system/setFieldsDict',
    'system/controlDict_templ.txt':'system/controlDict', 'system/topoSetDict.1_templ.txt':'system/topoSetDict.1', 'system/topoSetDict.2_templ.txt':'system/topoSetDict.2',
    'system/topoSetDict.3_templ.txt':'system/topoSetDict.3', 'system/topoSetDict.4_templ.txt':'system/topoSetDict.4', 'system/topoSetDict.5_templ.txt':'system/topoSetDict.5',
    'system/topoSetDict.6_templ.txt':'system/topoSetDict.6', 'constant/hRef_templ.txt':'constant/hRef'}
    for key in templatesdict:
        kajiki_it(casefolder+"/"+key,casefolder+"/"+templatesdict[key],problemdict)
    # write input definition json into the casefolder
    with open(casefolder+"/problem_def.json", "w") as outfile:
        keys_values = problemdict.items()
        new_d = {str(key): str(value) for key, value in keys_values}
        json.dump(new_d, outfile,indent=4)
    print("Case folder (%s) has been created " % casefolder)
    print("Problem definition %s/problem_def.json is written into the case folder"%casefolder)

# main run 
pos,named = parse_args_any(sys.argv)

# print(len(pos))
if (len(pos) != 2 ):
    print("Usage: python dex_of <config.dex> --infile foo.stl")
    exit()
print ("Dex_of called with arguments:")
print(f" Positional Arguments: {pos}")
print(f" Named Arguments: {named}")

dexof_path = os.path.dirname(os.path.realpath(__file__))
print("Path: ",dexof_path)
current_dir = os.path.abspath(os.getcwd())

# dex file is postional 0
configdict = dex2dict(pos[1])
configdict['dexof_path'] = dexof_path
configdict['current_dir']= current_dir
# overwrite named named arguments from dict -ignore new arguments
if (len(pos) != 2):
    print("First positional argument is needed.\n Program looks for a .dex file")
    exit()

if len(named) != 0 :
    for key in named:
        if key in configdict:
            configdict[key]=named[key]
            print("Updated the value for %s given in dex file with  that from the command line" % key)

problemdict = stlPrep(configdict)
problemdict.update(configdict)
problemdict.update(computational_domain(problemdict))

print(problemdict)

setup_of(problemdict)
print("**** ALL DONE ****")
# print(problemdict)
