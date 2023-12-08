import os
from os.path import join
import shutil
import json
from pprint import pprint
import urllib.request

data = open("branches")

result = []
id = 0

exceptions = {
    "oak": "jackrabbit-oak",
    "math": "commons-math",
    "log4j2": "logging-log4j2",
    "mng": "maven",  # ?????
}

for line in data:
    branch = line.split("/")[2].strip()
    id += 1
    [_, project, commit] = branch.split("_")
    project_name = project.split("-")[0].lower()

    subject = exceptions[project_name] if project_name in exceptions else project_name

    link = "https://github.com/bugs-dot-jar/{}/raw/{}/.bugs-dot-jar/test-results.txt".format(
        subject, branch
    )
    info = "https://github.com/tdurieux/bugs-dot-jar-dissection/raw/ef280eac8ee5e62f862b958986653714d0b9023b/data/{}/{}.json".format(
        subject, commit
    )

    original_data = {}
    source_file = ""

    # print(link)
    print(info)
    with urllib.request.urlopen(info) as f:
        original_data = json.load(f)
        pprint(original_data)
        patch_info = original_data["patch"].split(" ")
        source_file = patch_info[2][2:] if len(patch_info) > 2 else ""
        pprint(source_file)
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
            "passing_test": [],
            "failing_test": original_data["failing_tests"],
            "test_timeout": 5,
            "count_neg": len(original_data["failing_tests"]),
            "count_pos": 0,
        }
    )

file = open("meta-data.json", "w")

# print(result)

file.write(json.dumps(result, indent=4))
