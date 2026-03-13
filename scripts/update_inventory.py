import json
import os
import sys


def update_json(payload_data):
    file_path = "transforms.json"
    staging_key = "next-release-placeholder"

    new_items = payload.get('new_transforms', [])
    if not new_items:
        return ""
    
    with open(file_path, "r") as f:
        data = json.load(f)

    if staging_key not in data["transformsData"]:
        data["transformsData"][staging_key] = {
            "systemVersion": {
                "majorVersion": 0,
                "minorVersion": 0,
                "patchVersion": 0,
                "packageDate": "PENDING",
            },
            "transforms": [],
        }

    changelog = []
    for item in new_items:
        new_entry = {
            "transformId": item['id'],
            "userName": item['user'],
            "transformType": "CSC",
            "transformUrl": f"https://raw.githubusercontent.com/ampas/{payload['submodule']}/{payload['sha']}/{item['file']}"
        }
        # Prevent duplicates
        if item['id'] not in [t['transformId'] for t in data["transformsData"][staging_key]["transforms"]]:
            data["transformsData"][staging_key]["transforms"].append(new_entry)
            changelog.append(f"- `{item['id']}`")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    # Return changelog text for the PR body
    return "\n".join(new_entries)


if __name__ == "__main__":
    # Payload passed as a JSON string argument from the workflow
    raw_payload = json.loads(sys.argv[1])
    changelog = update_json(json.loads(raw_payload))
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(f"changelog<<EOF\n{changelog}\nEOF", file=fh)
