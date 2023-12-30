import bpy

class QumaShaderModifier:

    VALID_MATERIAL_NAME_HEADER = "N00_"

    FACE_OBJECT_NAME = "Face"
    SKIN_MATERIAL_NAME = "_SKIN"

    def AddLightShaderToObject(meshObject, saturation, value):
        materialArray = meshObject.data.materials

        for material in materialArray:
            if not QumaShaderModifier.__ValidateMaterialName(meshObject.name, material.name):
                continue

            QumaShaderModifier.__AddLightShaderToMaterial(material)

        QumaShaderModifier.SetSaturation(meshObject, saturation)
        QumaShaderModifier.SetValue(meshObject, value)

    def SetSaturation(meshObject, saturation):
        materialArray = meshObject.data.materials

        for material in materialArray:
            if not QumaShaderModifier.__ValidateMaterialName(meshObject.name, material.name):
                continue

            QumaShaderModifier.__SetSaturation(material, saturation)

    def SetValue(meshObject, value):
        materialArray = meshObject.data.materials

        for material in materialArray:
            if not QumaShaderModifier.__ValidateMaterialName(meshObject.name, material.name):
                continue

            QumaShaderModifier.__SetValue(material, value)
    
    def __ValidateMaterialName(objectName, materialName)->bool:
        if QumaShaderModifier.FACE_OBJECT_NAME in objectName:
            flag1 = QumaShaderModifier.SKIN_MATERIAL_NAME in materialName
            flag2 = QumaShaderModifier.VALID_MATERIAL_NAME_HEADER in materialName
            return flag1 and flag2
        else:
            return QumaShaderModifier.VALID_MATERIAL_NAME_HEADER in materialName

    def __SetSaturation(mat, saturation):
        nodes = mat.node_tree.nodes

        hueSaturationNode = QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "HUE_SAT")
        hueSaturationNode.inputs['Saturation'].default_value = saturation

    def __SetValue(mat, value):
        nodes = mat.node_tree.nodes

        hueSaturationNode = QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "HUE_SAT")
        hueSaturationNode.inputs['Value'].default_value = value

    def __AddLightShaderToMaterial(mat):
        nodes = mat.node_tree.nodes

        if not QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "BSDF_DIFFUSE"):
            diffuseBSDFNode = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            mixShaderNode = mat.node_tree.nodes.new('ShaderNodeMixShader')
            
            baseColorNode = QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "TEX_IMAGE")
            outputNode = QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "OUTPUT_MATERIAL")
            mixShaderInputNode = None

            for input in outputNode.inputs:
                for link in input.links:
                    mixShaderInputNode = link.from_node
                    break;

            if mixShaderInputNode is not None:
                mat.node_tree.links.new(baseColorNode.outputs[0], diffuseBSDFNode.inputs[0])
                mat.node_tree.links.new(diffuseBSDFNode.outputs[0], mixShaderNode.inputs[2])
                mat.node_tree.links.new(mixShaderInputNode.outputs[0], mixShaderNode.inputs[1])
                mat.node_tree.links.new(mixShaderNode.outputs[0], outputNode.inputs[0])

            if not QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "HUE_SAT"):
                hueSaturationNode = mat.node_tree.nodes.new('ShaderNodeHueSaturation')
                emissionNode = QumaShaderModifier.__FindShaderNodeWithTypeName(nodes, "EMISSION")
                mat.node_tree.links.new(emissionNode.inputs[0], hueSaturationNode.outputs[0])
                mat.node_tree.links.new(baseColorNode.outputs[0], hueSaturationNode.inputs[4])

    def __FindShaderNodeWithTypeName(nodes, type):
        for node in nodes:
            if node.type == type:
                return node
            
        return None
