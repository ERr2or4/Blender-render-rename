import bpy
import os
from datetime import datetime

# 插件信息
bl_info = {
    "name": "自动命名渲染结果（带版本号、备注和折叠栏）",
    "blender": (2, 80, 0),
    "category": "Render",
}

# 注册自定义属性
def register_properties():
    bpy.types.Scene.use_timestamp = bpy.props.BoolProperty(
        name="使用时间戳",
        description="在文件名中包含时间戳",
        default=True
    )
    bpy.types.Scene.use_project_scene = bpy.props.BoolProperty(
        name="使用项目名",
        description="在文件名中包含项目名称",
        default=False
    )
    bpy.types.Scene.use_file_scene = bpy.props.BoolProperty(
        name="使用工程名",
        description="在文件名中包含工程名称",
        default=False
    )
    bpy.types.Scene.render_project_name = bpy.props.StringProperty(
        name="项目名称",
        description="用于命名渲染文件",
        default="MyProject"
    )
    bpy.types.Scene.render_save_path = bpy.props.StringProperty(
        name="保存路径",
        description="渲染结果的保存位置",
        default="//renders/",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.render_version = bpy.props.IntProperty(
        name="渲染版本号",
        description="用于区分渲染版本的递增数字",
        default=1
    )
    bpy.types.Scene.render_version_note = bpy.props.StringProperty(
        name="版本备注",
        description="当前渲染版本的备注",
        default=""
    )
    bpy.types.Scene.generated_filename = bpy.props.StringProperty(
        name="生成的文件名",
        description="自动生成的文件名",
        default=""
    )
    bpy.types.Scene.show_advanced_options = bpy.props.BoolProperty(
        name="显示高级选项",
        description="显示或隐藏命名的高级选项",
        default=False
    )

def unregister_properties():
    del bpy.types.Scene.use_timestamp
    del bpy.types.Scene.use_project_scene
    del bpy.types.Scene.use_file_scene
    del bpy.types.Scene.render_project_name
    del bpy.types.Scene.render_save_path
    del bpy.types.Scene.render_version
    del bpy.types.Scene.render_version_note
    del bpy.types.Scene.generated_filename
    del bpy.types.Scene.show_advanced_options

# 操作类：生成文件名并设置为渲染输出路径
class GenerateFilenameOperator(bpy.types.Operator):
    """根据选中的规则生成文件名并同步到渲染设置"""
    bl_idname = "render.generate_filename"
    bl_label = "生成文件名并设置为渲染路径"

    def execute(self, context):
        scene = context.scene
        parts = []
        
        # 根据选择的复选框添加文件名部分
        if scene.use_project_scene:
            project_name = scene.render_project_name
            parts.append(project_name)
        
        if scene.use_file_scene:
            scene_name = bpy.path.display_name_from_filepath(bpy.data.filepath) or "UnnamedScene"
            parts.append(scene_name)
      
        if scene.use_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parts.append(timestamp)
        
        # 加入渲染版本号，并递增版本号
        version_str = f"v{scene.render_version:03}"
        parts.append(version_str)
        
        # 添加备注内容（如果有）
        if scene.render_version_note.strip():
            note = scene.render_version_note.replace(" ", "_")  # 替换空格为下划线
            parts.append(note)
        
        # 组合文件名
        filename = "_".join(parts) + ".png"
        scene.generated_filename = filename

        # 设置渲染文件路径
        file_path = os.path.join(bpy.path.abspath(scene.render_save_path), filename)
        scene.render.filepath = file_path

        # 自动递增版本号
        scene.render_version += 1
        
        self.report({'INFO'}, f"渲染文件名设置为: {file_path}")
        return {'FINISHED'}

# 自定义面板
class FilenameGeneratorPanel(bpy.types.Panel):
    bl_label = "文件名生成器"
    bl_idname = "RENDER_PT_filename_generator_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "文件名生成"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 项目名称和路径输入
        layout.prop(scene, "render_project_name", text="项目名称")
        layout.prop(scene, "render_save_path", text="保存路径")

        # 手动调整版本号
        layout.prop(scene, "render_version", text="当前版本号")
        layout.prop(scene, "render_version_note", text="版本备注")

        # 折叠栏 - 高级命名选项
        layout.prop(scene, "show_advanced_options", text="显示高级选项")
        if scene.show_advanced_options:
            layout.label(text="命名选项：")
            layout.prop(scene, "use_project_scene", text="使用项目名")
            layout.prop(scene, "use_file_scene", text="使用工程名")
            layout.prop(scene, "use_timestamp", text="使用时间戳")

        # 生成文件名并同步到渲染路径
        layout.operator("render.generate_filename", text="生成文件名并设置为渲染路径")

        # 显示生成的文件名
        layout.label(text="生成的文件名:")
        layout.prop(scene, "generated_filename", text="")

# 注册和取消注册
def register():
    register_properties()
    bpy.utils.register_class(GenerateFilenameOperator)
    bpy.utils.register_class(FilenameGeneratorPanel)

def unregister():
    unregister_properties()
    bpy.utils.unregister_class(FilenameGeneratorPanel)
    bpy.utils.unregister_class(GenerateFilenameOperator)

if __name__ == "__main__":
    register()
