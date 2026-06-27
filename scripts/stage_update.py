import json
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Error: Missing payload file argument.")
        sys.exit(1)

    payload_file = sys.argv[1]
    
    try:
        with open(payload_file, 'r') as f:
            payload = json.load(f)
            
        submodule = payload.get('submodule', 'unknown')
        sha = payload.get('sha', 'unknown')
        short_sha = sha[:7]
        commit_msg = payload.get('commit_msg', 'No commit message provided.')
        new_transforms = payload.get('new_transforms', [])

        # Create staging directory if it doesn't exist
        os.makedirs('staging', exist_ok=True)

        # Build a structured data bundle for this specific push
        fragment_data = {
            "submodule": submodule,
            "sha": sha,
            "commit_msg": commit_msg,
            "new_transforms": new_transforms
        }

        # Save as an isolated JSON fragment file
        fragment_filename = f"staging/update-{submodule}-{short_sha}.json"
        with open(fragment_filename, 'w') as f:
            json.dump(fragment_data, f, indent=2)
            
        print(f"Successfully staged fragment: {fragment_filename}")
        
        # Output a clean changelog line for the GitHub Actions summary step
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print(f"msg={commit_msg}", file=fh)
                print(f"count={len(new_transforms)}", file=fh)

    except Exception as e:
        print(f"Error processing staging fragment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()