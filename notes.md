PMD -  raw 1:1 file implementation, physical structure
StuntGPModel - high level structure, logical structure

Converter - converts PMD -> StuntGPModel





====
addMaterialsFromFiles


thing
    dependent on PMD/files

texture
    image
material
    texture

mesh
    name
    verts
    faces
    uvs
    materials
    tranform

addMesh(mname+str(loaded), vs, faces, us, materialIndexes, materials, transform)
    mesh.from_pydata(verts, [], faces)
    bind material to polygon
    set uvs per vert????
    matrix translation
    bpy.context.scene.objects.link(object) 

<trackname>.fan
This file contains the AI nodes.


Ideas for later

* join ALL vertex data in one class - DUMB?
    * cause one vertex can have more than one material, it would have to have list of UVs inside

TODO add generic PMD class (type 0/2) and additional one for track that build upon that with thrack specific things

ANALYSE:
* is point w always 1.0?
* is UV normal always 1.0?
* Poly unknown /  unknown2
* Tranform unknow[4]
