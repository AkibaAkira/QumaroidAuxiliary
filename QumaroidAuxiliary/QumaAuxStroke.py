import bpy, bmesh

class QumaAuxStroke:

    INVERT_FACE_STROKE_VERTEX_GROUP_NAME = "NoFaceStroke"

    STROKE_MATERIAL_NAME = "Stroke"
    STROKE_OFFSET = 1
    MERGE_THRESHOLD = 0.0
    
    VALID_NAMES = ["Face", "Body"] #Skip "Hair"

    def AddStrokeToObject(meshObject, strokeColor, thickness):
        if not QumaAuxStroke.__IsValidObject(meshObject):
            return
        
        # 1. Create or update stroke material
        stroke_mat = QumaAuxStroke.__GetStrokeMaterial(QumaAuxStroke.STROKE_MATERIAL_NAME, strokeColor)

        # 2. Add Material to object
        if meshObject.data.materials.find(QumaAuxStroke.STROKE_MATERIAL_NAME) < 0:
            meshObject.data.materials.append(stroke_mat)

        materialOffset = meshObject.data.materials.find(QumaAuxStroke.STROKE_MATERIAL_NAME)

        # 3. Add Solidfy Modify to Object
        solidModifier = QumaAuxStroke.__AddSolidfyModifierToObject(meshObject, materialOffset, thickness, QumaAuxStroke.STROKE_OFFSET)
                    
        # 4. Mesh remove doubles
        QumaAuxStroke.__MeshRemoveDoubles(meshObject)
        
        # 5. Face Object (Add Stroke to outline only)
        if "Face" in meshObject.name:            
            verticeGroup = QumaAuxStroke.__CreateInvertFaceStrokeVertexGroup(meshObject)            
            solidModifier.vertex_group = verticeGroup.name
            solidModifier.invert_vertex_group = True

    def __IsValidObject(msehObject)->bool:
        for validName in QumaAuxStroke.VALID_NAMES:
            if validName in msehObject.name:
                return True
            
        return False

    def __GetStrokeMaterial(name, color):
        mat = (bpy.data.materials.get(name) or 
            bpy.data.materials.new(name))

        # Enable 'Use nodes':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        # Add a diffuse shader and set its location:   
        # 1. Clean all nodes
        mat.node_tree.nodes.clear()

        # 2. Create
        emission = mat.node_tree.nodes.new('ShaderNodeEmission')
        emission.inputs['Strength'].default_value = 5.0
        emission.inputs['Color'].default_value = color
        emission.location = (-200, 0)


        material_output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(material_output.inputs[0], emission.outputs[0])

        mat.use_backface_culling = True

        return mat    
        
    def __AddSolidfyModifierToObject(obj, materialOffset, thickness, offset):
        solidfyModifier = (obj.modifiers.get("Solidify") or obj.modifiers.new("Solidify", 'SOLIDIFY'))

        # 1. Set Material Offset
        solidfyModifier.material_offset = materialOffset
        
        # 2. Check Flip
        solidfyModifier.use_flip_normals = True

        # 3. Check High Quality
        solidfyModifier.use_quality_normals = True

        # 4. Set Thickness and Offset
        solidfyModifier.thickness = thickness
        solidfyModifier.offset = offset
        
        return solidfyModifier

    def __MeshRemoveDoubles(meshObject):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = meshObject
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold = QumaAuxStroke.MERGE_THRESHOLD)
        bpy.ops.object.mode_set(mode='OBJECT')
        
    #region Face Stroke functions
    
    def __CreateInvertFaceStrokeVertexGroup(faceObject):
    
        # 1. Create vertex group
        vertexGroupName = QumaAuxStroke.INVERT_FACE_STROKE_VERTEX_GROUP_NAME
        vertexGroup = (faceObject.vertex_groups.get(vertexGroupName) or 
                    faceObject.vertex_groups.new(name = vertexGroupName))
        
        # 2. Get all skin material index
        skinMaterialIndexArr = QumaAuxStroke.__GetSkinMaterialIndex(faceObject)
        
        # 3. Put Vertex to group
        vertList = QumaAuxStroke.__GetVertexIndexListByMaterial(faceObject, skinMaterialIndexArr)
        
        # 4. Add to vertex group
        vertexGroup.add(vertList, 1, 'ADD')
        
        return vertexGroup
    
    def __GetSkinMaterialIndex(bodyObject) -> [int]:

        resultMaterialIndex = []

        for material in bodyObject.material_slots:
            if "SKIN" in material.name:
                resultMaterialIndex.append(bodyObject.data.materials.find(material.name))

        return resultMaterialIndex

    def __GetVertexIndexListByMaterial(meshObject, matIndexArray) -> [int]:
        vertList = []
        bm = bmesh.new()
        bm.from_mesh(meshObject.data)
        # no need to swith into edit mode

        for face in bm.faces:
            if face.material_index not in matIndexArray:
                for v in face.verts:
                    if v.index not in vertList:
                        vertList.append(v.index)
                        
        bm.to_mesh(meshObject.data)
        bm.free()
        
        return vertList

    #endregion
