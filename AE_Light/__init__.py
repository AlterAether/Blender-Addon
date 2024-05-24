bl_info = {
    "name": "AE Light",
    "blender": (3, 0, 0),
    "category": "Object",
    "version": (1, 1, 1),
    "author": "Alteraether",
    "description": "Manage lights in your scene and create new lights with diffusers",
}

import bpy
import mathutils

class AELIGHT_PT_main_panel(bpy.types.Panel):
    bl_label = "AE Light"
    bl_idname = "AELIGHT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AE Light'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene.ae_light_props, "light_intensity")
        layout.prop(scene.ae_light_props, "light_color")
        
        row = layout.row()
        row.operator("ae_light.turn_on", text="Turn On All Lights")
        row.operator("ae_light.turn_off", text="Turn Off All Lights")
        
        layout.operator("ae_light.adjust_intensity", text="Reset Intensity")
        layout.operator("ae_light.change_color", text="Change Color")
        layout.operator("ae_light.create_light", text="Create Light")

class AELightProperties(bpy.types.PropertyGroup):
    light_intensity: bpy.props.FloatProperty(
        name="Intensity",
        description="Intensity of the lights",
        default=10.0,  # Set default intensity to 10 watts
        min=0.0,
        max=100.0  # Increased max value for more flexibility
    )
    
    light_color: bpy.props.FloatVectorProperty(
        name="Color",
        description="Color of the lights",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

class AELIGHT_OT_turn_on(bpy.types.Operator):
    bl_label = "Turn On All Lights"
    bl_idname = "ae_light.turn_on"
    
    def execute(self, context):
        for obj in context.scene.objects:
            if obj.type == 'LIGHT':
                obj.hide_viewport = False
                obj.hide_render = False
        return {'FINISHED'}

class AELIGHT_OT_turn_off(bpy.types.Operator):
    bl_label = "Turn Off All Lights"
    bl_idname = "ae_light.turn_off"
    
    def execute(self, context):
        for obj in context.scene.objects:
            if obj.type == 'LIGHT':
                obj.hide_viewport = True
                obj.hide_render = True
        return {'FINISHED'}

class AELIGHT_OT_adjust_intensity(bpy.types.Operator):
    bl_label = "Adjust Light Intensity"
    bl_idname = "ae_light.adjust_intensity"
    
    def execute(self, context):
        intensity = context.scene.ae_light_props.light_intensity
        for obj in context.scene.objects:
            if obj.type == 'LIGHT':
                obj.data.energy = intensity
        return {'FINISHED'}

class AELIGHT_OT_change_color(bpy.types.Operator):
    bl_label = "Change Light Color"
    bl_idname = "ae_light.change_color"
    
    def execute(self, context):
        color = context.scene.ae_light_props.light_color
        for obj in context.scene.objects:
            if obj.type == 'LIGHT':
                obj.data.color = color
        return {'FINISHED'}

class AELIGHT_OT_create_light(bpy.types.Operator):
    bl_label = "Create Light with Diffuser"
    bl_idname = "ae_light.create_light"
    
    def execute(self, context):
        # Create a new collection for the light setup
        collection_name = "Light_01"
        if collection_name not in bpy.data.collections:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
        else:
            new_collection = bpy.data.collections[collection_name]

        # Create an empty object (sphere)
        bpy.ops.object.empty_add(type='SPHERE')
        empty = context.active_object
        empty.name = "Controller"
        new_collection.objects.link(empty)
        bpy.context.scene.collection.objects.unlink(empty)
        
        # Create a new area light
        bpy.ops.object.light_add(type='AREA', location=empty.location)
        light = context.active_object
        light.name = "AE Light"
        light.data.energy = context.scene.ae_light_props.light_intensity
        light.data.color = context.scene.ae_light_props.light_color
        light.parent = empty  # Parent the light to the empty object
        new_collection.objects.link(light)
        bpy.context.scene.collection.objects.unlink(light)
        
        # Create a plane for the diffuser 10 cm away from the light
        bpy.ops.mesh.primitive_plane_add(size=2, location=light.location + mathutils.Vector((0, 0, -0.1)))
        plane = context.active_object
        plane.name = "Diffuser"
        
        # Create a translucent material for the plane
        mat = bpy.data.materials.new(name="DiffuserMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        nodes.clear()  # Clear default nodes
        
        # Add Translucent BSDF node
        translucent_node = nodes.new(type="ShaderNodeBsdfTranslucent")
        translucent_node.location = (0, 0)
        
        # Add Material Output node
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (200, 0)
        
        # Link nodes
        links.new(translucent_node.outputs[0], output_node.inputs[0])
        
        plane.data.materials.append(mat)
        
        plane.parent = light  # Parent the plane to the light
        new_collection.objects.link(plane)
        bpy.context.scene.collection.objects.unlink(plane)
        
        # Select the empty object
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AELIGHT_PT_main_panel)
    bpy.utils.register_class(AELightProperties)
    bpy.utils.register_class(AELIGHT_OT_turn_on)
    bpy.utils.register_class(AELIGHT_OT_turn_off)
    bpy.utils.register_class(AELIGHT_OT_adjust_intensity)
    bpy.utils.register_class(AELIGHT_OT_change_color)
    bpy.utils.register_class(AELIGHT_OT_create_light)
    
    bpy.types.Scene.ae_light_props = bpy.props.PointerProperty(type=AELightProperties)

def unregister():
    bpy.utils.unregister_class(AELIGHT_PT_main_panel)
    bpy.utils.unregister_class(AELightProperties)
    bpy.utils.unregister_class(AELIGHT_OT_turn_on)
    bpy.utils.unregister_class(AELIGHT_OT_turn_off)
    bpy.utils.unregister_class(AELIGHT_OT_adjust_intensity)
    bpy.utils.unregister_class(AELIGHT_OT_change_color)
    bpy.utils.unregister_class(AELIGHT_OT_create_light)
    
    del bpy.types.Scene.ae_light_props

if __name__ == "__main__":
    register()
