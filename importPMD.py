#PMDimporter is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
# any later version.

#PMDimporter is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with PMDimporter.  If not, see <http://www.gnu.org/licenses/>.

# PMD model file path
# in case of tracks files config_lvscript.cfg contains more information ex. about skyboxes to import as well
fpath = "~/SGP/meshdata/car2.PMD"

# Used naming convention: instead of extracting all the files into its subdirectories all the files are in one folder
# filenames or filespath had replaced "\\" with "_" ex. graphics24_cars_car1_b1grid4.png
# materials storage directory, files in png format
mpath = "~/SGP/tools/png/"
# set this for different tracksets, valid range: trackset00-trackset06 
trkset = "trackset01"

from os import path
import sys
import struct
import re
from struct import *
from collections import namedtuple

try:
    import bpy 
    from bpy_extras.io_utils import  _check_axis_conversion
    from bpy.types import Operator 
    from mathutils import Matrix
        
    def createMaterial(name, textureFileName, color = (1,1,1)):
        mat = bpy.data.materials.new(name)
        mat.diffuse_shader = 'LAMBERT' 
        mat.diffuse_color = color
        mat.diffuse_intensity = 0.5
        mat.alpha = 1.0
        mat.use_face_texture=True
        mat.use_shadeless=True
        
        tex = bpy.data.textures.new(name+'.tex', type = 'IMAGE')
        tex.image = bpy.data.images.load(textureFileName)
        # Add texture slot for bump texture
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_color_diffuse = True 
        mtex.use_map_color_emission = True 
        mtex.emission_color_factor = 0.5
        
        return (mat, mtex) #0material 1texture
        
    def addMaterialsFromFiles(materialFilenames):
        materials  = []
        for name in materialFilenames:
            name = name.replace('\\\\','\\').replace('\\','_')+".png"
            if "_trk_" in name:
                name = name[name.find("_trk_"):]
                name = trkset+name

            fname = path.join(mpath,"graphics24_"+name)
            materials.append(createMaterial(path.basename(name), fname))
        return materials
        
    def addMesh(name, verts, faces, uvs, materialIndexes, materials, transform):    
        mesh = bpy.data.meshes.new(name+".mesh")
        ob = bpy.data.objects.new(name, mesh)
        mesh.from_pydata(verts, [], faces)
        mesh.uv_textures.new()
        
        for material in materials:
            mesh.materials.append(material[0])
        for i in range(len(mesh.polygons)):
            mesh.uv_textures.active.data[i].image =  materials[materialIndexes[i]][1].texture.image
        
        # set UV
        for poly, polyDef, mIndex in zip(mesh.polygons, uvs, materialIndexes):
            for vertex, uv in zip(list(poly.loop_indices), polyDef):
                for uv_layer in mesh.uv_layers:
                    uv_layer.data[vertex].uv = uv
            poly.material_index = mIndex
            
        #ob.location = transform[3][0:3]
        #ob.rotation_euler = 
        
        matrix = ob.matrix_local.to_4x4()
        matrix.translation = (transform[3][0],transform[3][2],transform[3][1])
        
        #rotation
        matrix[1][1] = transform[1][2]
        matrix[2][2] = transform[0][1]
           
        matrix[1][2] = transform[1][1]
        matrix[2][1] = -transform[0][2]
        matrix[1][0] = transform[0][0]
        matrix[2][0] = transform[1][0]

        #matrix = Matrix(transform)
        #matrix.transpose()
        ob.matrix_local = matrix 

        #mesh.calc_normals()
        bpy.context.scene.objects.link(ob) 
        return ob
except:
    def addMesh(name, vs, faces, uvs, materialIndexes, materials, transform):
        pass
    def addMaterialsFromFiles(materialFilenames):
        for name in materialFilenames:
            print(path.join(mpath,"graphics24_"+name.replace('\\\\','\\').replace('\\','_')+".png"))
        
def loadPMD(fpath, mpath, trkset, location = None):
    sizesTableOffset = 0xb0
    dataStartOffset = 480
    buffptr = 0

    fdir = path.dirname(fpath)
    f = open(fpath, "rb")
    buffer = f.read()

    def padding():
        nonlocal buffptr
        paddingLen = 32 - buffptr % 32
        if (paddingLen < 32):
            buffptr += paddingLen

    # read header
    hdr = Struct('<10s').unpack_from(buffer[: 10])[0].decode()
    if "PMD" not in hdr:
        print("Unsupported file format")
        #return
        
    ver = int(hdr[7:9])
    if ver != 82 and ver != 83: 
        print("Unsupported file version: 1.%d" % ver)
        #return

    #read sizes table, sizes are in bytes
    sizes = struct = Struct('<34i').unpack_from(buffer[sizesTableOffset:])
    fcnt = int(sizes[5]/2)
    vcnt = int(sizes[4]/(4*4))
    uvcnt = int(sizes[3]/16)
    pcnt = int(sizes[2]/(2*4))
    if ver == 83:
        tcnt = int(sizes[10]/80)
    else:
        tcnt = int(sizes[10]/72)
    if ver == 83:
        scnt = int(sizes[11]/64)
    else:
        scnt = int(sizes[11]/60)

    #print(fcnt, vcnt, uvcnt, pcnt)
    
    # read faces table
    buffptr = dataStartOffset
    facesTable = []
    for i in range(fcnt):
        struct = Struct('<h').unpack_from(buffer[buffptr:])
        buffptr += 2
        facesTable.append(struct[0])
    padding()

    # read verts
    verts = []
    for i in range(vcnt):
        struct = Struct('<ffff').unpack_from(buffer[buffptr:])
        buffptr += 4*4
        # flip coordinates for blender top Z axis
        verts.append((struct[0], struct[2],struct[1]))
    padding()

    #skip verts 2
    buffptr += sizes[1]
    padding()

    # read uvs
    uvs = []
    for i in range(uvcnt):
        struct = Struct('<ffhhi').unpack_from(buffer[buffptr:])
        buffptr += 4*4
        # U, V, vertexTableIndex, unknownIndex, some float 1.0
        # flip U for blender different coordinates system
        uv = list(struct[0:4])
        uv[1] = -uv[1]
        uvs.append(uv)
        #print(struct[2], struct[3])
    padding()

    # read polygons definition list
    polys = []
    for i in range(pcnt):
        struct = Struct('<bbhhh').unpack_from(buffer[buffptr:])
        buffptr += 2*4
        # 0size, 1start index and 2material index
        polys.append((struct[0], struct[4], struct[1]))
    padding()

    # read surfaces transforms
    transforms = []

    for i in range(tcnt):
        struct = Struct('<16f').unpack_from(buffer[buffptr:])
        if ver == 83:
            buffptr += 80
        else:
            buffptr += 72
        transforms.append((struct[12:16],struct[8:12], struct[4:8], struct[0:4]))
    padding()
        
    # read surfaces definitions
    surfaces = []
    for i in range(scnt):
        if ver == 83:
            struct = Struct('<8h3ifhhhhiiii').unpack_from(buffer[buffptr:])
            buffptr += 64
            # 0polysCnt, 1uvsCnt, 2vtCnt, 3uvsStart, 4vtStart, 5polysStart, 6transformPtr
            srfc = list(struct[14:21])
            srfc.append(struct[4])
            surfaces.append(srfc)
        else:
            struct = Struct('<2h2i2h4if6h3i').unpack_from(buffer[buffptr:])
            buffptr += 60
            # 0polysCnt, 1uvsCnt, 2vtCnt, 3uvsStart, 4vtStart, 5polysStart, 6transformPtr
            srfc = (struct[13],struct[14],struct[15],struct[17],struct[18],struct[19],struct[3])
            surfaces.append(srfc)
            #print("polysCnt %d, 1uvsCnt %d, vtCnt %d, uvsStart %d, vtStart %d, polysStart %d, transformPtr %d" % srfc)
       
    # skip unknown coordinates
    buffptr += sizes[8]
    padding()
    buffptr += sizes[9]
    padding()

    # read texture filenames references
    textures = Struct('<%ds' % sizes[6]).unpack_from(buffer[buffptr:])[0]
    textures = textures.decode().split('\0')
    textures = [name.lower() for name in textures if len(name) > 0]

    #GOGO
    mname = path.basename(fpath)
    materials = addMaterialsFromFiles(textures)
    loaded = 0
    for surface in surfaces:
        # nothing to draw
        if surface[0] < 1 or surface[1] < 1 or surface[2] < 1:
            continue
        print("Loading surface %d" % loaded)
        vs = verts[surface[4]:surface[4]+surface[2]] #vertexIndexPtr starts from 0 again
        uvss = uvs[surface[3]:surface[3]+surface[1]]
        ps = polys[surface[5]:surface[5]+surface[0]]
        transform = transforms[surface[6]]
        # polygons 
        faces = []
        us = []
        materialIndexes = []
        
        #getVertIndx = lambda x: uvs[x][2]
        getVertIndx  = lambda x: uvss[x][2]
        getUV        = lambda x: uvss[x][0:2]
        for num, p in enumerate(ps):
            tab = facesTable[p[1]:p[1]+p[0]]
            us.append([ getUV(i) for i in tab])
            tab = [ getVertIndx(i) for i in tab]
            faces.append(tab)
            materialIndexes.append(p[2])
        
        
        
        ob = addMesh(mname+str(loaded), vs, faces, us, materialIndexes, materials, transform)
        if location:
            ob.location.x += location
            
        loaded += 1
        # this limits the number of surfaces to import, higher values are low poly models
        if loaded > 100:
            break

    #print (verts)
    #print (uvs)
    #print (facesTable)
    #print (polys)
    #print (surfaces)
    #print (transforms)

loadPMD(fpath, mpath, trkset)
