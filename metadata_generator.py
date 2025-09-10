import os
from os.path import join
import shutil
import json
from pprint import pprint
import urllib.request

# Read existing metadata if it exists
existing_metadata = []
existing_branches = set()
try:
    with open("meta-data.json", "r") as f:
        existing_metadata = json.load(f)
        existing_branches = {entry["branch"] for entry in existing_metadata}
        print(f"Found {len(existing_metadata)} existing entries")
except FileNotFoundError:
    print("No existing meta-data.json found, creating new one")

data = open("branches")

result = existing_metadata.copy()  # Start with existing data
id = len(existing_metadata)  # Continue ID sequence

exceptions = {
    "oak": "jackrabbit-oak",
    "math": "commons-math",
    "log4j2": "logging-log4j2",
    "mng": "maven",  # ?????
}

new_entries_count = 0

for line in data:
    branch = line.split("/")[2].strip()
    
    # Skip if branch already exists
    if branch in existing_branches:
        print(f"Skipping existing branch: {branch}")
        continue
    
    print(f"Processing new branch: {branch}")
    new_entries_count += 1
    
    id += 1
    hotfix_prefix = "_HOTFIX"
    if hotfix_prefix in branch:
        updated_branch = branch.replace(hotfix_prefix, "")
    else: 
        updated_branch = branch
    [_, project, commit] = updated_branch.split("_")
    project_name = project.split("-")[0].lower()

    subject = exceptions[project_name] if project_name in exceptions else project_name

    link = "https://github.com/carolhanna01/{}/raw/{}/.bugs-dot-jar/test-results.txt".format(
        subject, branch
    )
    info = "https://raw.githubusercontent.com/carolhanna01/bugs-dot-jar-dissection/meta-data-for-cerberus/data/{}/{}.json".format(
        subject, commit
    )

    original_data = {}
    source_file = ""

    # print(link)
    print(info)
    with urllib.request.urlopen(info) as f:
        original_data = json.load(f)
        print("original data: ",original_data)
        patch_info = original_data["patch"].split(" ")
        source_file = patch_info[2][2:] if len(patch_info) > 2 else ""
        print("source file: ",source_file)
        if "src/main" not in source_file and source_file != '':
            input()

    os.makedirs(subject,exist_ok=True)
    os.makedirs(join(subject,commit),exist_ok=True)

    result.append(
        {
            "id": id,
            "subject": subject,
            "bug_id": commit,
            "branch": branch,
            "project_name": source_file.split("src/main")[0],
            "source_file": source_file,
            "source_directory": "src/main/java",
            "class_directory": "target/classes",
            "test_directory": "src/test/java",
            "test_class_directory": "target/test-classes",
            "java_version": 8,
            "build_script": "build_subject",
            "config_script": "config_subject",
            "clean_script": "clean_subject",
            "test_script": "test_subject",
            "bug_type": "Test Failure",
            "build_system": "maven",
            "line_numbers": [],
            "dependencies": [],
            "passing_test_identifiers": [],
            "failing_test_identifiers": original_data["failing_tests"],
            "test_timeout": 20,
            "count_neg": len(original_data["failing_tests"]),
            "count_pos": 0,
            # Adding format_updater.py functionality directly
            "src": {
                "root_abspath": "/experiment/bugsdotjar/{}/{}/src".format(subject, commit),
                "entrypoint": {}
            },
            "output_dir_abspath": "/output",
            "language": "java",
        }
    )

file = open("meta-data.json", "w")

# print(result)

file.write(json.dumps(result, indent=4))
file.close()
