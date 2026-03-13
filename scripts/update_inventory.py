import json
import os
import sys


def update_json(payload_data):
    file_path = "transforms.json"
    staging_key = "next-release-placeholder"

    try:
        with open(payload_file, "r") as f:
            payload = json.load(f)

        new_items = payload.get("new_transforms", [])
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
                "transformId": item["id"],
                "userName": item["user"],
                "transformType": "CSC",
                "transformUrl": f"https://raw.githubusercontent.com/ampas/{payload['submodule']}/{payload['sha']}/{item['file']}",
            }
            # Prevent duplicates
            if item["id"] not in [
                t["transformId"]
                for t in data["transformsData"][staging_key]["transforms"]
            ]:
                data["transformsData"][staging_key]["transforms"].append(new_entry)
                changelog.append(f"- `{item['id']}`")

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        # Return changelog text for the PR body
        return "\n".join(new_entries)

    except Exception as e:
        print(f"Error during JSON update: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Path to payload fil passed from the workflow
    payload_path = sys.argv[1]
    changelog = update_json(payload_path)

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(f"changelog<<EOF\n{changelog}\nEOF", file=fh)
