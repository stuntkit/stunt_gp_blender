Hierarchy:

* PMD - whole file
    * Block 0
    * Block 7
    * Metadata
    * Textures
    * LODs
        * Mesh
            * Block 8? uk2 + unk_ind2
            * Transform? - could be level higher as well
                * files use 25 transforms for 75 meshes in 3 lods
                * logically each mesh can have individual transform
            * Vertices
            * UVs
            * Polys
                * Vert IDs (faces)

Not yet known:
    * Block 7/8
    * Blocks 15-23
