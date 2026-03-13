import json
import os
import sys


def create_staging_fragment(payload_file):
    staging_dir = "staging"

    try:
        with open(payload_file, "r") as f:
            payload = json.load(f)

        new_items = payload.get("new_transforms", [])
        if not new_items:
            return ""

        # Ensure staging directory exists
        os.makedirs(staging_dir, exist_ok=True)

        # Create a unique filename based on the SHA or a UUID
        short_sha = payload["sha"][:7]
        fragment_path = os.path.join(staging_dir, f"update_{short_sha}.json")

        fragment_data = {
            "submodule": payload["submodule"],
            "sha": payload["sha"],
            "transforms": [],
        }

        changelog = []
        for item in new_items:
            entry = {
                "transformId": item["id"],
                "userName": item["user"],
                "transformType": "CSC",
                "transformUrl": f"https://raw.githubusercontent.com/ampas/{payload['submodule']}/{payload['sha']}/{item['file']}",
            }
            fragment_data["transforms"].append(entry)
            changelog.append(f"- `{item['id']}`")

        # Write the fragment file
        with open(fragment_path, "w") as f:
            json.dump(fragment_data, f, indent=2)

        return "\n".join(changelog)

    except Exception as e:
        print(f"Error creating fragment: {e}")
        sys.exit(1)


if __name__ == "__main__":
    payload_path = sys.argv[1]
    changes = create_staging_fragment(payload_path)

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(f"changelog<<EOF\n{changes}\nEOF", file=fh)
