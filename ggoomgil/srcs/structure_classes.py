import json

with open("classifications.json", "r", encoding="utf-8") as f:
    classifications: list[dict] = json.load(f)

classes: list[dict] = []

# First level
for classification in classifications:
    if not any(c["name"] == classification["depth_1"] for c in classes):
        classes.append({
            "name": classification["depth_1"],
            "children": []
        })

# Second level
for classification in classifications:
    parent = next(c for c in classes if c["name"] == classification["depth_1"])
    if not any(c["name"] == classification["depth_2"] for c in parent["children"]):
        parent["children"].append({
            "name": classification["depth_2"],
            "children": []
        })

# Third level
for classification in classifications:
    parent = next(c for c in classes if c["name"] == classification["depth_1"])
    depth2_parent = next(c for c in parent["children"] if c["name"] == classification["depth_2"])
    if not any(c["name"] == classification["depth_3"] for c in depth2_parent["children"]):
        depth2_parent["children"].append({
            "name": classification["depth_3"],
            "children": []
        })

# Fourth level
for classification in classifications:
    parent = next(c for c in classes if c["name"] == classification["depth_1"])
    depth2_parent = next(c for c in parent["children"] if c["name"] == classification["depth_2"])
    depth3_parent = next(c for c in depth2_parent["children"] if c["name"] == classification["depth_3"])
    if not any(c["name"] == classification["depth_4"] for c in depth3_parent["children"]):
        depth3_parent["children"].append({
            "name": classification["depth_4"],
            "children": []
        })

with open("structure_classes.json", "w", encoding="utf-8") as f:
    json.dump(classes, f, ensure_ascii=False, indent=4)

