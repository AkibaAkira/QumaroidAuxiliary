import bpy, bmesh

class QumaClothCollsion:
    
    COLLISION_BODY_OUTER_THICKNESS = 0.003
    CLOTH_OBJECT_COLLISION_MIN_DISTANCE = 0.005
    CLOTH_SELF_COLLISION_MIN_DISTANCE = 0.003

    MERGE_THRESHOLD = 0.0
    NO_OF_CUTS = 3

    PIN_GROUP_NAME = "PinGroup"
    COLLISION_BODY_NAME = "ClothBody"

    def AddBodyAndClothCollision(meshObject):
        if "Body" in meshObject.name:
            QumaClothCollsion.__CreateClothCollisionBody(meshObject)
        elif "Clothes" in meshObject.name:
            QumaClothCollsion.__SetClothCollision(meshObject)

    def __CreateClothCollisionBody(bodyObject):

        if QumaClothCollsion.__HasChild(bodyObject.parent, 
                                        QumaClothCollsion.COLLISION_BODY_NAME):
            return

        # 2. Create the collision body
        collisionBody = bodyObject.copy()
        collisionBody.data = bodyObject.data.copy() # linked = False
        collisionBody.name = QumaClothCollsion.COLLISION_BODY_NAME
        bpy.context.scene.collection.objects.link(collisionBody)

        # 3. Remove shader
        materialArray = collisionBody.data.materials
        materialArray.clear()

        # 4. Remove Solidfy Modifier
        if collisionBody.modifiers.get("Solidify"):
            collisionBody.modifiers.remove(collisionBody.modifiers.get("Solidify"))

        # 5. Add Collision Modifier
        collisionBody.modifiers.get("Collision") or collisionBody.modifiers.new("Collision", 'COLLISION')

        # 6. Set Thickness outer
        collisionBody.collision.thickness_outer = QumaClothCollsion.COLLISION_BODY_OUTER_THICKNESS

    def __SetClothCollision(clothObject):

        # 1. Add Collision Modifier
        clothColModifier = (clothObject.modifiers.get("Collision") or clothObject.modifiers.new("Collision", 'CLOTH'))

        # 2. Check Self Collision
        clothColModifier.collision_settings.distance_min = QumaClothCollsion.CLOTH_OBJECT_COLLISION_MIN_DISTANCE
        clothColModifier.collision_settings.use_self_collision = True
        clothColModifier.collision_settings.self_distance_min = QumaClothCollsion.CLOTH_SELF_COLLISION_MIN_DISTANCE

        # 3. Merge Double
        QumaClothCollsion.__MeshRemoveDoubles(clothObject, QumaClothCollsion.MERGE_THRESHOLD)

        # 4. Subdivide
        QumaClothCollsion.__MeshSubDivide(clothObject, QumaClothCollsion.NO_OF_CUTS)

        # 5. TrisToQuads
        QumaClothCollsion.__MeshTrisToQuads(clothObject)
        
        # 6. Add pin group
        QumaClothCollsion.__SetPinGroups(clothObject)
        clothColModifier.settings.vertex_group_mass = QumaClothCollsion.PIN_GROUP_NAME

    def __SetPinGroups(clothObject):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = clothObject
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        bm = bmesh.from_edit_mesh(clothObject.data)
        
        for vgroup in clothObject.vertex_groups:
            if "Skirt" in vgroup.name:
                bpy.ops.object.vertex_group_set_active(group=vgroup.name)   
                bpy.ops.object.vertex_group_select() 
        
        bpy.ops.mesh.select_all(action='INVERT')
        
        vertices = [v.index for v in bm.verts if (v.select and not v.hide)]
        bpy.ops.object.mode_set(mode='OBJECT')

        pinGroup = clothObject.vertex_groups.new(name = QumaClothCollsion.PIN_GROUP_NAME)
        pinGroup.add(vertices, 1.0, 'ADD')

    def __HasChild(parentObject, childName:str) -> bool:
        for obj in bpy.data.objects:
            if obj.parent == parentObject and childName in obj.name:
                return True
            
        return False
        
    def __MeshRemoveDoubles(meshObject, mergeThresHold):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = meshObject
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold = mergeThresHold)
        bpy.ops.object.mode_set(mode='OBJECT')

    def __MeshSubDivide(meshObject, noOfCuts):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = meshObject
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(number_cuts = noOfCuts)
        bpy.ops.object.mode_set(mode='OBJECT')
        
    def __MeshTrisToQuads(meshObject):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = meshObject
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.mode_set(mode='OBJECT')

