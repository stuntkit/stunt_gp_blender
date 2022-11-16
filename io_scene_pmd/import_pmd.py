"""This module manages Blender import for Stunt GP 3D files"""

import bpy
from os.path import exists
from bpy_extras.io_utils import ImportHelper  # , orientation_helper
from bpy.props import StringProperty, FloatProperty, BoolProperty
from bpy.types import Operator

from pathlib import Path

from .stunt_gp_model import PMD


# @orientation_helper(axis_forward="Z", axis_up="Y")
class ImportPMD(Operator, ImportHelper):
    """Load a Stunt GP model file"""

    bl_idname = "import_scene.pmd"
    bl_label = "Import Stunt GP model"
    bl_options = {"UNDO", "PRESET"}

    # ImportHelper mixin class uses this
    filename_ext = ".pmd"

    filter_glob = StringProperty(
        default="*.pmd",
        options={"HIDDEN"},
        maxlen=255,
    )

    # TODO make it work on multiple files at once?
    # files: CollectionProperty(
    #     name="File Path",
    #     type=bpy.types.OperatorFileListElement,
    # )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    load_track_settings: BoolProperty(  # type: ignore
        name="Load track .cfg file",  # noqa: F722
        description="Load LevelBox data for track files",  # noqa: F722
        default=True,
    )

    # vertices have values in range (-225000, 225000)
    # Blender will crash withour rescaling
    scale: FloatProperty(  # type: ignore
        name="Model scale",  # noqa: F722
        description="rescales the model, which is too big for Blender",  # noqa: F722
        default=2**-8,
    )

    # TODO add track/car texture selector?

    # TODO support for multi-file import?
    # skipcq: PYL-W0613
    def execute(self, context):
        pmd = PMD.from_file(self.filepath)
        print("PMD has been loaded")

        print("convert it to something Blender understands")
        name = Path(self.filepath).stem
        result = self.to_blender_basic(pmd, self.filepath, name, self.scale)

        print("done, result:", result)
        return result

    @staticmethod
    def to_blender_basic(pmd: PMD, filename: str, name: str, scale=1.0):
        # blender_textures = []
        # load textures and create material for each
        blender_materials = ImportPMD.create_materials(filename, pmd.textures)

        print("meshes in LOD: ", pmd.block_11.meshes_per_lod)
        model_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(model_collection)

        for lod in range(len(pmd.block_11.lods)):
            lod_collection = bpy.data.collections.new("lod_" + str(lod))
            model_collection.children.link(lod_collection)
            if lod != 0:
                # by default how only the best LOD
                model_collection.children["lod_" + str(lod)].hide_render = True
                model_collection.children["lod_" + str(lod)].hide_select = True

            for i in range(pmd.block_11.meshes_per_lod):
                # meshbpy.data.collections.new("My Sub Collection")
                # model_collection.children.link()
                mesh_definition = pmd.block_10[i + (lod * pmd.block_11.meshes_per_lod)]
                if (
                    (mesh_definition.uvs_count == 0)
                    or (mesh_definition.polys_count == 0)
                    or (mesh_definition.verts_count == 0)
                ):
                    print("empty mesh:", i, "in LOD", lod)
                    continue

                mesh = bpy.data.meshes.new("meshdata_" + str(lod) + "_" + str(i))

                transform = pmd.block_9[mesh_definition.transform_index]

                # load vetices
                vertices = pmd.block_3[
                    mesh_definition.verts_start_index : mesh_definition.verts_start_index
                    + mesh_definition.verts_count
                ]
                verts = [v.get_coords_blender(scale) for v in vertices]
                # TODO check
                uvs = pmd.block_2[
                    mesh_definition.uvs_start_index : mesh_definition.uvs_start_index
                    + mesh_definition.uvs_count
                ]

                faces = []
                uv_table = []

                # for each poly in mesh
                faces_extracted = []
                for poly_index in range(
                    mesh_definition.polys_start_index,
                    mesh_definition.polys_start_index + mesh_definition.polys_count,
                ):
                    # for each poly
                    curr_poly = pmd.block_1[poly_index]
                    faces_extracted = pmd.block_4[
                        curr_poly.face_index : curr_poly.face_index
                        + curr_poly.vertices_count
                    ]

                    print(
                        "try",
                        len(faces_extracted),
                        len(uvs),
                        "poly",
                        poly_index,
                        "mesh",
                        i,
                        "lod",
                        lod,
                    )
                    tab = [uvs[k].vertex_id for k in faces_extracted]
                    faces.append(tab)

                # create mesh
                mesh.from_pydata(verts, [], faces)
                mesh.update()

                # add all materials
                # TODO don't add unused ones
                for material in blender_materials:
                    mesh.materials.append(material)

                # TODO assign proper material
                for id, poly in enumerate(mesh.polygons):
                    poly.material_index = 0

                # add UV data
                uv_layer = mesh.uv_layers.new()
                mesh.uv_layers.active = uv_layer
                for uv in uvs:
                    uv_layer.data[uv.vertex_id].uv = (uv.u, -uv.v)
                # TODO asaa

                # add a new object using the mesh
                mesh_obj = bpy.data.objects.new("mesh_" + str(lod) + "_" + str(i), mesh)

                object_transform = mesh_obj.matrix_local.to_4x4()

                object_transform.translation = (
                    transform.matrix[0][0] * scale,
                    transform.matrix[0][2] * scale,
                    transform.matrix[0][1] * scale,
                )
                # rotation
                object_transform[1][1] = transform.matrix[2][2]
                object_transform[2][2] = transform.matrix[3][1]

                object_transform[1][2] = transform.matrix[2][1]
                object_transform[2][1] = -transform.matrix[3][2]
                object_transform[1][0] = transform.matrix[3][0]
                object_transform[2][0] = transform.matrix[2][0]
                mesh_obj.matrix_local = object_transform

                lod_collection.objects.link(mesh_obj)

        # meta_collection = bpy.data.collections.new("meta")
        # model_collection.children.link(meta_collection)
        # mesh0 = bpy.data.meshes.new("mesh_zero")
        # verts0 = [v.get_coords_blender(scale) for v in pmd.block_0]
        # mesh0.from_pydata(verts0, [], [])
        # mesh0.update()
        # mesh0_obj = bpy.data.objects.new("mesh_zero_o", mesh0)
        # meta_collection.objects.link(mesh0_obj)

        # mesh7 = bpy.data.meshes.new("mesh_seven")
        # verts7 = [v.get_coords_blender(scale) for v in pmd.block_7]
        # mesh7.from_pydata(verts7, [], [])
        # mesh7.update()
        # mesh7_obj = bpy.data.objects.new("mesh_seven_o", mesh7)
        # meta_collection.objects.link(mesh7_obj)

        return {"FINISHED"}

    @staticmethod
    def create_materials(file_path: str, texture_names: list[str]) -> list[str]:
        materials: list["bpy.types.Material"] = []
        for m in texture_names:
            # TODO check if .tga exists, then .png, then .pc (optional if you have time and importer)
            img_ext = "png"
            img_path = (
                str(Path(file_path).parents[0])
                + "/graphics24/"
                + m.replace("\\\\", "/").replace("\\", "/").lower()
                + "."
                + img_ext
            )
            if "/trk_" in img_path:
                first = img_path[: img_path.find("/trk_") - 6]  # levelX
                second = img_path[img_path.find("/trk_") + 1 :]
                img_path = first + "/trackset00/" + second
            # TODO check if texture exists, if not replace levelX with tracksetX
            # TODO add trackset, skin option to importer (number?)

            # tex = bpy.ops.texture.new()
            # blender_textures.append(tex)

            # create material
            # TODO easier name
            material = bpy.data.materials.new(name=img_path)
            material.use_nodes = True
            # TODO does this make sense???
            node_tree = material.node_tree
            bsdf = node_tree.nodes.get("Principled BSDF")

            texture_node = node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.select = True
            node_tree.nodes.active = texture_node

            img = None
            if exists(img_path):
                print("loading", img_path)
                img = bpy.data.images.load(img_path)
                texture_node.image = img
            else:
                print("couldn't load", img_path)

            node_tree.links.new(texture_node.outputs[0], bsdf.inputs[0])
            materials.append(material)
        return materials
