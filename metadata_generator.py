import os
from os.path import join
import shutil
import json
from pprint import pprint
import urllib.request
import urllib.error

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
    "jcr": "jackrabbit",
    "lucene": "solr",
    "yarn": "hadoop",
    "hdfs": "hadoop",
    "math": "commons-math",
    "log4j2": "logging-log4j2",
    "mng": "maven",  # ?????
}


def check_file_exists(url):
    """Check if a file exists at the given URL"""
    try:
        urllib.request.urlopen(url)
        return True
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def detect_build_system(subject, branch, source_file):
    """
    Detect build system by checking for build files in the repository.
    Checks both root and subdirectories based on source_file path.

    Returns: tuple of (build_system, directories_to_check)
    """
    base_url = f"https://raw.githubusercontent.com/carolhanna01/{subject}/{branch}"

    # Extract potential project subdirectories from source_file
    directories_to_check = [""]  # Start with root

    if source_file:
        # Extract potential project directories (e.g., "lucene/", "solr/core/", etc.)
        if "/" in source_file:
            parts = source_file.split("/")
            # Check progressively deeper directories
            for i in range(1, len(parts)):
                if "src" in parts[i]:
                    break
                subdir = "/".join(parts[:i])
                if subdir and subdir not in directories_to_check:
                    directories_to_check.append(subdir)

    print(f"  Checking directories: {directories_to_check}")

    # Check for build files in order of preference: gradle, maven, ant
    for directory in directories_to_check:
        prefix = f"{directory}/" if directory else ""

        # Check for Gradle
        if check_file_exists(f"{base_url}/{prefix}build.gradle"):
            print(f"  ✓ Found Gradle: {prefix}build.gradle")
            return ("gradle", directory)
        if check_file_exists(f"{base_url}/{prefix}build.gradle.kts"):
            print(f"  ✓ Found Gradle (Kotlin): {prefix}build.gradle.kts")
            return ("gradle", directory)

        # Check for Maven
        if check_file_exists(f"{base_url}/{prefix}pom.xml"):
            print(f"  ✓ Found Maven: {prefix}pom.xml")
            return ("maven", directory)

        # Check for Ant
        if check_file_exists(f"{base_url}/{prefix}build.xml"):
            print(f"  ✓ Found Ant: {prefix}build.xml")
            return ("ant", directory)

    print(f"  ⚠ No build file found, defaulting to maven")
    return ("maven", "")


def infer_directories(source_file, build_system, project_dir):
    """
    Infer directory structure based on source_file path and build system.

    Args:
        source_file: Full path to source file (e.g., "lucene/core/src/java/org/...")
        build_system: Detected build system (gradle, maven, ant)
        project_dir: The subdirectory where build file was found

    Returns: tuple of (project_name, source_dir, class_dir, test_dir, test_class_dir)
    """

    # Extract project_name (path up to src/)
    if "src/" in source_file:
        project_name = source_file.split("src/")[0]
    else:
        project_name = source_file

    # Determine directory structure based on build system and actual source path
    if "src/main/java" in source_file:
        # Maven/Gradle standard layout
        source_directory = "src/main/java"
        test_directory = "src/test/java"

        if build_system == "gradle":
            class_directory = "build/classes/java/main"
            test_class_directory = "build/classes/java/test"
        else:  # maven
            class_directory = "target/classes"
            test_class_directory = "target/test-classes"

    elif "src/java" in source_file:
        # Ant-style layout (common in older projects)
        source_directory = "src/java"
        test_directory = "src/test"

        if build_system == "gradle":
            class_directory = "build/classes/java/main"
            test_class_directory = "build/classes/java/test"
        else:  # ant or fallback
            class_directory = "build/classes/java"
            test_class_directory = "build/classes/test"

    elif source_file.count("src/") >= 1:
        # Generic src/ directory (need to infer from path)
        parts = source_file.split("src/")
        if len(parts) > 1:
            src_type = parts[1].split("/")[0]  # e.g., "java", "main", etc.
            source_directory = f"src/{src_type}"
        else:
            source_directory = "src"

        test_directory = "src/test"

        if build_system == "gradle":
            class_directory = "build/classes/java/main"
            test_class_directory = "build/classes/java/test"
        elif build_system == "ant":
            class_directory = "build/classes"
            test_class_directory = "build/classes/test"
        else:  # maven fallback
            class_directory = "target/classes"
            test_class_directory = "target/test-classes"
    else:
        # No src/ found - use defaults based on build system
        if build_system == "gradle":
            source_directory = "src/main/java"
            class_directory = "build/classes/java/main"
            test_directory = "src/test/java"
            test_class_directory = "build/classes/java/test"
        elif build_system == "ant":
            source_directory = "src"
            class_directory = "build/classes"
            test_directory = "src/test"
            test_class_directory = "build/classes/test"
        else:  # maven
            source_directory = "src/main/java"
            class_directory = "target/classes"
            test_directory = "src/test/java"
            test_class_directory = "target/test-classes"

    return (project_name, source_directory, class_directory, test_directory, test_class_directory)

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
    info = "https://raw.githubusercontent.com/carolhanna01/bugs-dot-jar-dissection/master/data/{}/{}.json".format(
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

    os.makedirs(subject,exist_ok=True)
    os.makedirs(join(subject,commit),exist_ok=True)

    # Detect build system dynamically
    print(f"Detecting build system for {branch}...")
    build_system, project_dir = detect_build_system(subject, branch, source_file)

    # Infer directory structure based on source file and build system
    project_name_value, source_directory, class_directory, test_directory, test_class_directory = \
        infer_directories(source_file, build_system, project_dir)

    print(f"  Build System: {build_system}")
    print(f"  Project Name: {project_name_value}")
    print(f"  Source Dir: {source_directory}")
    print(f"  Class Dir: {class_directory}")
    print(f"  Test Dir: {test_directory}")
    print(f"  Test Class Dir: {test_class_directory}")
    print()

    result.append(
        {
            "id": id,
            "subject": subject,
            "bug_id": commit,
            "branch": branch,
            "project_name": project_name_value,
            "source_file": source_file,
            "source_directory": source_directory,
            "class_directory": class_directory,
            "test_directory": test_directory,
            "test_class_directory": test_class_directory,
            "java_version": 8,
            "build_script": "build_subject",
            "config_script": "config_subject",
            "clean_script": "clean_subject",
            "test_script": "test_subject",
            "bug_type": "Test Failure",
            "build_system": build_system,
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
