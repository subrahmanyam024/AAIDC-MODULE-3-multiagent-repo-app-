# agents/repo_analyzer.py
from tools.file_loader import load_files_from_directory, extract_zip_to_dir
import os
import json
import re

def analyze_repo(path_or_zip: str, workdir="./temp_repo"):
    if path_or_zip.endswith(".zip") or (os.path.isfile(path_or_zip) and path_or_zip.lower().endswith(".zip")):
        extract_zip_to_dir(path_or_zip, workdir)
        repo_dir = workdir
    else:
        repo_dir = path_or_zip

    files = load_files_from_directory(repo_dir)
    
    readme = next((f["content"] for f in files if f["path"].lower().startswith("readme")), "")
    readme_path = next((f["path"] for f in files if f["path"].lower().startswith("readme")), None)
    
    langs = {}
    for f in files:
        ext = os.path.splitext(f["path"])[1]
        if ext:
            langs[ext] = langs.get(ext, 0) + 1
    
    dependencies = extract_dependencies(files)
    missing_sections = check_missing_sections(files, readme)
    project_type = detect_project_type(files, langs)
    repo_structure = analyze_structure(files)
    best_practices = check_best_practices(files)
    
    return {
        "repo_dir": repo_dir,
        "files": files,
        "readme": readme,
        "readme_path": readme_path,
        "langs": langs,
        "dependencies": dependencies,
        "missing": missing_sections,
        "project_type": project_type,
        "structure": repo_structure,
        "best_practices": best_practices,
        "total_files": len(files),
        "repo_size": sum(f.get("size", 0) for f in files)
    }

def extract_dependencies(files):
    deps = {"python": [], "node": [], "java": [], "ruby": [], "go": [], "rust": []}
    
    for f in files:
        path = f["path"].lower()
        content = f["content"]
        
        if path == "requirements.txt":
            deps["python"].extend([line.split("==")[0].split(">")[0].strip() for line in content.split("\n") if line.strip() and not line.startswith("#")])
        elif path == "setup.py" or path == "pyproject.toml":
            deps["python"].extend(extract_python_deps(content))
        elif path == "package.json":
            try:
                pkg = json.loads(content)
                deps["node"].extend(list(pkg.get("dependencies", {}).keys())[:10])
            except: pass
        elif path == "gemfile":
            deps["ruby"].extend([line.split()[1].strip("'\"") for line in content.split("\n") if line.strip().startswith("gem")])
        elif path == "go.mod":
            deps["go"].extend([line.split()[0] for line in content.split("\n") if line.strip() and not line.startswith("//")])
        elif path == "cargo.toml":
            deps["rust"].extend(extract_toml_deps(content))
    
    return {k: list(set(v))[:5] for k, v in deps.items() if v}

def extract_python_deps(content):
    deps = []
    patterns = [r"install_requires\s*=\s*\[(.*?)\]", r"dependencies\s*=\s*\[(.*?)\]"]
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            deps.extend([d.strip().strip("'\"") for d in deps_str.split(",")])
    return deps

def extract_toml_deps(content):
    deps = []
    for line in content.split("\n"):
        if "=" in line and not line.startswith("["):
            try:
                key = line.split("=")[0].strip()
                deps.append(key)
            except: pass
    return deps

def detect_project_type(files, langs):
    paths = {f["path"].lower() for f in files}
    
    if any("setup.py" in p or "pyproject.toml" in p or "requirements.txt" in p for p in paths):
        return "Python Library"
    elif any("package.json" in p for p in paths):
        return "Node.js/JavaScript"
    elif any("pom.xml" in p or "build.gradle" in p for p in paths):
        return "Java/JVM"
    elif any("go.mod" in p for p in paths):
        return "Go"
    elif any("cargo.toml" in p for p in paths):
        return "Rust"
    elif any(".cs" in p or ".csproj" in p for p in paths):
        return "C# / .NET"
    elif any("dockerfile" in p for p in paths):
        return "Docker/Container"
    else:
        if langs.get(".py", 0) > langs.get(".js", 0):
            return "Python"
        elif langs.get(".js", 0) > 0:
            return "JavaScript"
        else:
            return "Unknown"

def analyze_structure(files):
    structure = {
        "has_src": False,
        "has_tests": False,
        "has_docs": False,
        "has_examples": False,
        "has_docker": False,
        "has_ci": False,
        "directory_tree": {}
    }
    
    paths = {f["path"].lower() for f in files}
    
    structure["has_src"] = any(p.startswith("src/") or p.startswith("lib/") for p in paths)
    structure["has_tests"] = any("test" in p for p in paths)
    structure["has_docs"] = any(p.startswith("docs/") or p.startswith("documentation/") for p in paths)
    structure["has_examples"] = any(p.startswith("examples/") or p.startswith("sample/") for p in paths)
    structure["has_docker"] = any("dockerfile" in p or "docker-compose" in p for p in paths)
    structure["has_ci"] = any(".github/workflows" in p or ".gitlab-ci" in p or ".travis" in p or "jenkinsfile" in p for p in paths)
    
    return structure

def check_missing_sections(files, readme):
    paths = {f["path"].lower() for f in files}
    missing = []
    
    checks = {
        "LICENSE": any("license" in p for p in paths),
        "CONTRIBUTING.md": any("contribut" in p for p in paths),
        "CODE_OF_CONDUCT.md": any("conduct" in p for p in paths),
        "Tests": any("test" in p for p in paths),
        "Documentation": any("doc" in p for p in paths),
        "Examples": any("example" in p or "sample" in p for p in paths),
        "CI/CD": any(".github" in p or ".gitlab-ci" in p or ".travis" in p for p in paths),
        ".gitignore": any(".gitignore" in p for p in paths),
    }
    
    readme_sections = {
        "Installation": "install" in readme.lower(),
        "Usage": "usage" in readme.lower() or "how to use" in readme.lower(),
        "Features": "feature" in readme.lower() or "capabilities" in readme.lower(),
        "Contributing": "contribut" in readme.lower(),
        "License": "license" in readme.lower() or "licens" in readme.lower()
    }
    
    for section, exists in checks.items():
        if not exists:
            missing.append(f"Missing: {section}")
    
    for section, exists in readme_sections.items():
        if readme and not exists:
            missing.append(f"README missing: {section} section")
    
    return missing

def check_best_practices(files):
    practices = {
        "has_changelog": False,
        "has_security_policy": False,
        "has_pull_request_template": False,
        "has_issue_templates": False,
        "has_code_of_conduct": False,
        "has_badges": False
    }
    
    paths = {f["path"].lower() for f in files}
    content_map = {f["path"].lower(): f["content"] for f in files}
    
    practices["has_changelog"] = any("changelog" in p or "history" in p for p in paths)
    practices["has_security_policy"] = any("security" in p for p in paths)
    practices["has_pull_request_template"] = any("pull_request_template" in p for p in paths)
    practices["has_issue_templates"] = any("issue_template" in p for p in paths)
    practices["has_code_of_conduct"] = any("conduct" in p for p in paths)
    
    for p, content in content_map.items():
        if "readme" in p and ("badge" in content or "build" in content or "coverage" in content):
            practices["has_badges"] = True
            break
    
    return practices
