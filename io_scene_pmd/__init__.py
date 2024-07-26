"""This module allows Blender to import/export Stunt GP 3D files"""

# pylint: disable=import-error
import bpy  # type: ignore

from .import_pmd import ImportPMD

# TODO expand to textures import?
# pylint: disable=unused-variable
bl_info = {
    "name": "Stunt GP model format",
    "author": 'Piotr "Halamix2" Halama',
    "version": (0, 0, 3),
    # might work with 2.80, I haven't checked
    "blender": (4, 0, 0),
    "location": "File > Import",  # 'Import-Export',
    "description": "Import as Stunt GP 3D files",
    "warning": "Early prototype, can only import",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}
classes = (ImportPMD,)


# skipcq: PYL-W0613
def menu_func_import(self, context) -> None:
    # pylint: disable=unused-argument
    """register function registers the addon in import menu"""
    self.layout.operator(ImportPMD.bl_idname, text="Stunt GP model (.pmd)")


def register() -> None:
    """register function registers classes and menus for use in Blender"""
    for single_class in classes:
        bpy.utils.register_class(single_class)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


# pylint: disable=unused-variable
def unregister() -> None:
    """register function unregisters classes and menus for use in Blender"""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    for single_class in classes:
        bpy.utils.unregister_class(single_class)


if __name__ == "__main__":
    register()
