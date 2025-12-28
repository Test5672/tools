import json
import zipfile
import hashlib
import os
import uuid
from pathlib import Path

def generate_sprite():
    try:
        n_input = input("Enter the number of list views to create (default 1): ")
        n = int(n_input) if n_input.strip() else 1
    except ValueError:
        n = 1

    sprite_name = "ListManager"
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>'.encode('utf-8')
    svg_md5 = hashlib.md5(svg_content).hexdigest()
    svg_filename = f"{svg_md5}.svg"

    sprite_data = {
        "isStage": False,
        "name": sprite_name,
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {
                "name": "blank", "bitmapResolution": 1, "dataFormat": "svg",
                "assetId": svg_md5, "md5ext": svg_filename,
                "rotationCenterX": 0, "rotationCenterY": 0
            }
        ],
        "sounds": [], "volume": 100, "layerOrder": 1, "visible": True,
        "x": 0, "y": 0, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "all around"
    }

    def gen_id(): return str(uuid.uuid4())[:20]

    for i in range(1, n + 1):
        list_name = f"list_{i}"
        list_id = gen_id()
        ptr_var_id = gen_id()
        
        # Register List and Pointer Variable
        sprite_data["lists"][list_id] = [list_name, []]
        sprite_data["variables"][ptr_var_id] = [f"pointer_{i}", 0]

        # --- BLOCK 1: "list_i view = new list" ---
        def_1 = gen_id()
        proto_1 = gen_id()
        del_1 = gen_id()
        set_1 = gen_id()
        hacked_get = gen_id()
        proccode_1 = f"{list_name} view = new list"

        sprite_data["blocks"][def_1] = {
            "opcode": "procedures_definition", "next": del_1, "parent": None,
            "inputs": {"custom_block": [1, proto_1]}, "fields": {},
            "shadow": True, "topLevel": True, "x": 100, "y": i * 500
        }
        
        sprite_data["blocks"][proto_1] = {
            "opcode": "procedures_prototype", "next": None, "parent": def_1,
            "inputs": {}, "fields": {}, "shadow": True, "topLevel": False,
            "mutation": {
                "tagName": "mutation", "children": [], "proccode": proccode_1,
                "argumentids": "[]", "argumentnames": "[]", "argumentdefaults": "[]", "warp": "true"
            }
        }

        sprite_data["blocks"][del_1] = {
            "opcode": "data_deletealloflist", "next": set_1, "parent": def_1,
            "inputs": {}, "fields": {"LIST": [list_name, list_id]}, "shadow": False
        }

        sprite_data["blocks"][set_1] = {
            "opcode": "data_setvariableto", "next": None, "parent": del_1,
            "inputs": {"VALUE": [3, hacked_get, [10, ""]]},
            "fields": {"VARIABLE": [f"pointer_{i}", ptr_var_id]}, "shadow": False
        }

        sprite_data["blocks"][hacked_get] = {
            "opcode": "data_variable", "next": None, "parent": set_1,
            "inputs": {}, "fields": {"VARIABLE": [list_name, list_id]}, "shadow": False
        }

        # --- BLOCK 2: "list_i view = value" ---
        def_2 = gen_id()
        proto_2 = gen_id()
        hacked_set = gen_id()
        arg_reporter_id = gen_id()
        arg_guid = "arg_" + gen_id()
        proccode_2 = f"{list_name} view = %s"

        sprite_data["blocks"][def_2] = {
            "opcode": "procedures_definition", "next": hacked_set, "parent": None,
            "inputs": {"custom_block": [1, proto_2]}, "fields": {},
            "shadow": True, "topLevel": True, "x": 500, "y": i * 500
        }

        sprite_data["blocks"][proto_2] = {
            "opcode": "procedures_prototype", "next": None, "parent": def_2,
            "inputs": {}, "fields": {}, "shadow": True, "topLevel": False,
            "mutation": {
                "tagName": "mutation", "children": [], "proccode": proccode_2,
                "argumentids": f'["{arg_guid}"]', "argumentnames": '["value"]',
                "argumentdefaults": '[""]', "warp": "true"
            }
        }

        sprite_data["blocks"][arg_reporter_id] = {
            "opcode": "argument_reporter_string_number", "next": None, "parent": hacked_set,
            "inputs": {}, "fields": {"VALUE": ["value", None]}, "shadow": False
        }

        sprite_data["blocks"][hacked_set] = {
            "opcode": "data_setvariableto", "next": None, "parent": def_2,
            "inputs": {"VALUE": [3, arg_reporter_id, [10, ""]]},
            "fields": {"VARIABLE": [list_name, list_id]}, "shadow": False
        }

        # --- USAGE SCRIPT (The Green Flag Script) ---
        flag_id = gen_id()
        call_1_id = gen_id()
        call_2_id = gen_id()

        # "When Green Flag Clicked"
        sprite_data["blocks"][flag_id] = {
            "opcode": "event_whenflagclicked", "next": call_1_id, "parent": None,
            "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 1000, "y": i * 200
        }

        # Call: "list_i view = new list"
        sprite_data["blocks"][call_1_id] = {
            "opcode": "procedures_call", "next": call_2_id, "parent": flag_id,
            "inputs": {}, "fields": {}, "shadow": False,
            "mutation": {
                "tagName": "mutation", "children": [], "proccode": proccode_1,
                "argumentids": "[]", "warp": "true"
            }
        }

        # Call: "list_i view = (pointer_i)"
        # This demonstrates self-assignment/viewing
        sprite_data["blocks"][call_2_id] = {
            "opcode": "procedures_call", "next": None, "parent": call_1_id,
            "inputs": {
                arg_guid: [3, [12, f"pointer_{i}", ptr_var_id], [10, "Hello"]]
            },
            "fields": {}, "shadow": False,
            "mutation": {
                "tagName": "mutation", "children": [], "proccode": proccode_2,
                "argumentids": f'["{arg_guid}"]', "warp": "true"
            }
        }

    # Save
    downloads_path = str(Path.home() / "Downloads")
    file_path = os.path.join(downloads_path, "sprite.sprite3")

    with zipfile.ZipFile(file_path, 'w') as sprite_zip:
        sprite_zip.writestr('sprite.json', json.dumps(sprite_data))
        sprite_zip.writestr(svg_filename, svg_content)

    print(f"\n[SUCCESS] File: {file_path}")
    print(f"[NOTE] Look for the 'When Green Flag Clicked' stacks at X:1000 in the editor.")

if __name__ == "__main__":
    generate_sprite()
