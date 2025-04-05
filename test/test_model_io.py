import os
import bpy


K1_MODELS = []
K2_MODELS = []


def list_model_names(dir):
    return map(
        lambda path: os.path.splitext(os.path.basename(path))[0],
        filter(lambda path: path.endswith(".mdl"), os.listdir(dir)),
    )


if "K1_DATA_DIR" in os.environ:
    data_dir = os.environ["K1_DATA_DIR"]
    os.makedirs("./test/out/k1", exist_ok=True)
    models = K1_MODELS
    if not models:
        models = list_model_names(data_dir)
    for model in models:
        bpy.ops.wm.read_homefile(use_empty=True)
        assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=f"{data_dir}/{model}.mdl")
        export_path = f"./test/out/k1/{model}.mdl"
        assert "FINISHED" in bpy.ops.kb.mdlexport(filepath=export_path)
        assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=export_path)

if "K2_DATA_DIR" in os.environ:
    data_dir = os.environ["K2_DATA_DIR"]
    os.makedirs("./test/out/k2", exist_ok=True)
    models = K2_MODELS
    if not models:
        models = list_model_names(data_dir)
    for model in models:
        bpy.ops.wm.read_homefile(use_empty=True)
        assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=f"{data_dir}/{model}.mdl")
        export_path = f"./test/out/k2/{model}.mdl"
        assert "FINISHED" in bpy.ops.kb.mdlexport(
            filepath=export_path, export_for_tsl=True
        )
        assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=export_path)
