bl_info = {
    'name': 'Qumaroid Auxiliary Plugin',
    'category': '3D View',
    'author': 'Akiba Akira',
    'description': 'Qumaroid Auxiliary Functions',
    'version': (0, 19, 0),  
    'blender': (2, 80, 0),
    'warning': '',
}

import array
from email.policy import default
import sys,os,bpy,bmesh
sys.path.append(os.getcwd())

from .QumaAuxStroke import QumaAuxStroke
from .QumaShaderModifier import QumaShaderModifier
from .QumaClothCollision import QumaClothCollsion

class QumaApplyStroke(bpy.types.Operator):
    bl_label = "Add Stroke"
    bl_idname = "object.quma_aux_apply_stroke"
    bl_description = "Add Stroke to Hair and Face"

    def execute(self, context):
        childrenObject = GetAllChildrenObject(context)
        
        CreateClothsObject(context, childrenObject)

        for child in childrenObject:
            # Apply On Mesh Object only
            if child.type == "MESH":
                QumaAuxStroke.AddStrokeToObject(child, context.scene.qumaroidAuxStrokeColor, context.scene.qumaroidAuxStrokeThickness)

        return {'FINISHED'}

class QumaApplyShader(bpy.types.Operator):
    bl_label = "Add Shader"
    bl_idname = "object.quma_aux_apply_shader"
    bl_description = "Add Shader which reacts to light"

    def execute(self, context):
        childrenObject = GetAllChildrenObject(context)

        for child in childrenObject:
            # Apply On Mesh Object only
            if child.type == "MESH":
                QumaShaderModifier.AddLightShaderToObject(child, context.scene.qumaroidAuxMaterialSaturation, context.scene.qumaroidAuxMaterialValue)
                
        return {'FINISHED'}

class QumaApplyClothCollision(bpy.types.Operator):
    bl_label = "Cloth Collisions"
    bl_idname = "object.quma_aux_apply_cloth_collisions"
    bl_description = "Add Cloth Collisions"

    def execute(self, context):
        childrenObject = GetAllChildrenObject(context)

        for child in childrenObject:
            # Apply On Mesh Object only
            if child.type == "MESH":
                QumaClothCollsion.AddBodyAndClothCollision(child)

        return {'FINISHED'}

class QumaAuxiliaryPanel(bpy.types.Panel):
    
    bl_label = "Qumaroid Auxiliary"
    bl_idname = "SCENE_PT_qumarion_auxiliary_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Item"

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        
        if scene.qumaroidArmatureObject is not None:
            row = layout.row()
            row.prop(scene, "qumaroidAuxStrokeThickness")

            row = layout.row()
            row.prop(scene, "qumaroidAuxStrokeColor")
            
            row = layout.row()
            row.operator("object.quma_aux_apply_stroke")

            row = layout.row()
            row.operator("object.quma_aux_apply_shader")

            row = layout.row()
            row.prop(scene, "qumaroidAuxMaterialSaturation")

            row = layout.row()
            row.prop(scene, "qumaroidAuxMaterialValue")

            row = layout.row()
            row.operator("object.quma_aux_apply_cloth_collisions")

def __OnUpdateStroke(self, context):
    childrenObject = GetAllChildrenObject(context)

    for child in childrenObject:
        # Apply On Mesh Object only
        if child.type == "MESH":
            QumaAuxStroke.AddStrokeToObject(child, context.scene.qumaroidAuxStrokeColor, context.scene.qumaroidAuxStrokeThickness)

def __OnUpdateSaturation(self, context):
    childrenObject = GetAllChildrenObject(context)

    for child in childrenObject:
        # Apply On Mesh Object only
        if child.type == "MESH":
            QumaShaderModifier.SetSaturation(child, context.scene.qumaroidAuxMaterialSaturation)

def __OnUpdateValue(self, context):
    childrenObject = GetAllChildrenObject(context)

    for child in childrenObject:
        # Apply On Mesh Object only
        if child.type == "MESH":
            QumaShaderModifier.SetValue(child, context.scene.qumaroidAuxMaterialValue)

def __GetSkinAndHairMaterialIndex(bodyObject) -> array:

    resultMaterialIndex = []

    for material in bodyObject.material_slots:
        if any(s in material.name for s in ("SKIN", "HAIR")):
            resultMaterialIndex.append(bodyObject.data.materials.find(material.name))

    return resultMaterialIndex

def CreateClothsObject(context, childrenObject):
    for child in childrenObject:
        # Apply On Mesh Object only
        if child.type == "MESH" and "Body" in child.name:
            body = child

            # 1. Make A copy as "clothes"
            clothes = body.copy()
            clothes.data = body.data.copy() # linked = False
            clothes.name = 'Clothes'
            bpy.context.scene.collection.objects.link(clothes)

            # 2. Get Skin Material Index
            skinMaterialIndexArr = __GetSkinAndHairMaterialIndex(body)

            # 4. Delete All Mesh with skin index
            deleteMeshWithMat(body, skinMaterialIndexArr, reverse=True)
            deleteMeshWithMat(clothes, skinMaterialIndexArr)

def GetAllChildrenObject(context):
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == context.scene.qumaroidArmatureObject: 
            children.append(ob) 
    return children 


def deleteMeshWithMat(meshObject, matIndexArray, reverse = False):
    # ref
    # https://blender.stackexchange.com/questions/237163/how-can-i-get-a-list-of-all-the-mesh-objects-names-in-a-scene
    faces_mat_c1 = []
    bm = bmesh.new()
    bm.from_mesh(meshObject.data)
    # no need to swith into edit mode

    for face in bm.faces:
        if reverse:
            if face.material_index not in matIndexArray:
                # face has mat_c1 assigned
                faces_mat_c1.append(face)
        else:
            if face.material_index in matIndexArray:
                # face has mat_c1 assigned
                faces_mat_c1.append(face)

    # delete faces with mat_c1
    bmesh.ops.delete(bm, geom=faces_mat_c1, context="FACES")
    bm.to_mesh(meshObject.data)
    bm.free()

def register():
    bpy.utils.register_class(QumaAuxiliaryPanel)   
    bpy.utils.register_class(QumaApplyStroke)
    bpy.utils.register_class(QumaApplyShader)
    bpy.utils.register_class(QumaApplyClothCollision)
    
    Scene = bpy.types.Scene

    Scene.qumaroidAuxStrokeThickness = bpy.props.FloatProperty(
        name = "Stroke Thickness",
        default = 0.001,
        update = __OnUpdateStroke
        )
    Scene.qumaroidAuxStrokeColor = bpy.props.FloatVectorProperty(
        name = "Stroke Color",
        subtype = "COLOR",
        default = (0,0,0,1),
        size = 4,
        min = 0.0,
        max = 1.0,
        update = __OnUpdateStroke
        )
    Scene.qumaroidAuxMaterialSaturation = bpy.props.FloatProperty(
        name = "Saturation",
        default = 2.0,
        min = 0,
        max = 2,
        update = __OnUpdateSaturation
        )
    Scene.qumaroidAuxMaterialValue = bpy.props.FloatProperty(
        name = "Value",
        default = 2.0,
        min = 0,
        max = 2,
        update = __OnUpdateValue
        )
      
def unregister():
    bpy.utils.unregister_class(QumaAuxiliaryPanel)
    bpy.utils.unregister_class(QumaApplyStroke)
    bpy.utils.unregister_class(QumaApplyShader)
    bpy.utils.unregister_class(QumaApplyClothCollision)

    del bpy.types.Scene.qumaroidAuxStrokeThickness
    del bpy.types.Scene.qumaroidAuxStrokeColor
    del bpy.types.Scene.qumaroidAuxMaterialSaturation
    del bpy.types.Scene.qumaroidAuxMaterialValue