import bpy

box_collection = bpy.data.collections.new("boxes")
bpy.context.scene.collection.children.link(box_collection)


class Tri:
    def __init__(self, x: float, y: float, z: float, flipped=True, scale=2**-10):
        self.x = x * scale
        self.y = y * scale
        self.z = z * scale
        if flipped:
            self.y = z * scale
            self.z = y * scale


class LevelBox:
    def __init__(self, position, scale, v, n):
        self.position = position
        self.scale = scale
        self.v = v
        self.n = n


def createBox(box: LevelBox, name: str):
    vertices = [
        (box.position.x, box.position.y, box.position.z),
        (box.position.x + box.scale.x, box.position.y, box.position.z),
        (box.position.x, box.position.y + box.scale.y, box.position.z),
        (box.position.x + box.scale.x, box.position.y + box.scale.y, box.position.z),
        (box.position.x, box.position.y, box.position.z + box.scale.z),
        (box.position.x + box.scale.x, box.position.y, box.position.z + box.scale.z),
        (box.position.x, box.position.y + box.scale.y, box.position.z + box.scale.z),
        (
            box.position.x + box.scale.x,
            box.position.y + box.scale.y,
            box.position.z + box.scale.z,
        ),
    ]
    faces = [
        (0, 2, 3, 1),
        (0, 4, 5, 1),
        (0, 2, 6, 4),
        (7, 3, 1, 5),
        (7, 6, 2, 3),
        (7, 5, 4, 6),
    ]

    mesh = bpy.data.meshes.new(name + ".mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh_obj = bpy.data.objects.new(name, mesh)

    # object_transform = mesh_obj.matrix_local.to_4x4()

    # mesh_obj.rotation_euler[0] = box.n.x
    # mesh_obj.rotation_euler[1] = box.n.y
    # mesh_obj.rotation_euler[2] = box.n.z
    # mesh_obj.matrix_local = object_transform
    box_collection.objects.link(mesh_obj)


box_0 = LevelBox(
    Tri(0.0, 0.0, 0.0),
    Tri(1000.0, 1000.0, 1000.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(0.0, 0.0, 1.0, scale=1.0),
)
createBox(box_0, "box_0_2")

box_1 = LevelBox(
    Tri(12700.0, 600.0, 11700.0),
    Tri(4300.0, 1500.0, 5000.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(-0.484870, 0.0, 0.874587, scale=1.0),
)
createBox(box_1, "box_1_6")

box_2 = LevelBox(
    Tri(-3300.0, 700.0, 20700.0),
    Tri(5300.0, 1800.0, 6000.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(0.258572, 0.0, 0.965992, scale=1.0),
)
createBox(box_2, "box_2_6")

box_3 = LevelBox(
    Tri(5400.0, 500.0, 8600.0),
    Tri(6300.0, 1000.0, 4700.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(-0.191328, 0.0, 0.981526, scale=1.0),
)
createBox(box_3, "box_3_6")

box_4 = LevelBox(
    Tri(200.0, 2700.0, 16400.0),
    Tri(3300.0, 2000.0, 17600.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(-0.484870, 0.0, 0.874587, scale=1.0),
)
createBox(box_4, "box_4_4")

box_5 = LevelBox(
    Tri(-8600.0, 1200.0, 36200.0),
    Tri(17000.0, 2400.0, 9300.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(-0.374876, 0.0, 0.927075, scale=1.0),
)
createBox(box_5, "box_5_6")


box_default = LevelBox(
    Tri(1000.0, 1000.0, 1000.0),
    Tri(1.0, 1.0, 1.0),
    Tri(0.0, 1.0, 0.0, scale=1.0),
    Tri(0.0, 0.0, 1.0, scale=1.0),
)
