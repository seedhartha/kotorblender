import os
import bpy

offset = int(os.environ["OFFSET"]) if "OFFSET" in os.environ else 0
limit = int(os.environ["LIMIT"]) if "LIMIT" in os.environ else 50


def list_model_names(dir):
    global offset, limit
    names = list(
        map(
            lambda path: os.path.splitext(os.path.basename(path))[0],
            filter(lambda path: path.endswith(".mdl"), os.listdir(dir)),
        )
    )
    return (
        [] if len(names) <= offset else names[offset : min(offset + limit, len(names))]
    )


data_dir = os.environ["DATA_DIR"]
if "TSL" in os.environ:
    tsl = int(os.environ["TSL"]) == 1
else:
    tsl = False
out_dir = "./test/out/k2" if tsl else "./test/out/k1"
os.makedirs(out_dir, exist_ok=True)
models = list_model_names(data_dir)
for model in models:
    bpy.ops.wm.read_homefile(use_empty=True)
    assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=f"{data_dir}/{model}.mdl")
    export_path = f"{out_dir}/{model}.mdl"
    assert "FINISHED" in bpy.ops.kb.mdlexport(filepath=export_path)
    assert "FINISHED" in bpy.ops.kb.mdlimport(filepath=export_path)
