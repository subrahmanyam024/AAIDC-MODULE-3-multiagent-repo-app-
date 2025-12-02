# agents/content_improver.py
import json

def improve(repo_summary, metadata):
    readme = repo_summary.get("readme", "")
    project_type = repo_summary.get("project_type", "")
    structure = repo_summary.get("structure", {})
    missing = repo_summary.get("missing", [])
    
    improvements = analyze_readme_quality(readme)
    suggested_structure = generate_readme_structure(project_type, missing)
    suggested_images = get_image_suggestions(project_type)
    suggested_examples = get_example_suggestions(project_type, structure)
    suggested_badges = get_badge_suggestions(project_type, structure)
    
    improved_readme = generate_improved_readme(
        readme, 
        suggested_structure, 
        suggested_badges,
        project_type
    )
    
    return {
        "improved_readme": improved_readme[:2000],
        "improvements": improvements,
        "suggested_images": suggested_images,
        "suggested_badges": suggested_badges,
        "suggested_examples": suggested_examples,
        "quality_score": calculate_quality_score(readme, structure, missing)
    }

def analyze_readme_quality(readme):
    improvements = []
    
    if len(readme) < 100:
        improvements.append("README is too short - expand with more details")
    
    sections = {
        "installation": "install" in readme.lower(),
        "usage": "usage" in readme.lower() or "how" in readme.lower(),
        "features": "feature" in readme.lower(),
        "contributing": "contribut" in readme.lower(),
        "license": "license" in readme.lower()
    }
    
    for section, exists in sections.items():
        if not exists:
            improvements.append(f"Add {section.title()} section")
    
    if "```" not in readme:
        improvements.append("Add code examples with syntax highlighting")
    
    if "!" not in readme and "[" not in readme:
        improvements.append("Add visual elements (images, badges, diagrams)")
    
    return improvements

def generate_readme_structure(project_type, missing):
    structure = []
    
    structure.append("# Project Title")
    structure.append("Brief description (one line)")
    
    if "badge" not in str(missing).lower():
        structure.append("Badges section")
    
    structure.append("## Features")
    structure.append("- Feature 1")
    structure.append("- Feature 2")
    
    structure.append("## Installation")
    
    if "python" in project_type.lower():
        structure.append("```bash\npip install project-name\n```")
    elif "node" in project_type.lower() or "javascript" in project_type.lower():
        structure.append("```bash\nnpm install project-name\n```")
    elif "rust" in project_type.lower():
        structure.append("```bash\ncargo add project-name\n```")
    
    structure.append("## Usage")
    structure.append("```python\n# Example code\n```")
    
    structure.append("## API Reference")
    structure.append("## Configuration")
    structure.append("## Performance")
    structure.append("## Testing")
    structure.append("## Contributing")
    structure.append("## License")
    
    return structure

def generate_improved_readme(readme, structure, badges, project_type):
    if readme:
        return readme
    
    improved = "\n".join(structure)
    
    badge_lines = "\n".join([f"![{b}]()" for b in badges])
    if badge_lines:
        improved = improved.replace("Badges section", badge_lines)
    
    return improved

def get_image_suggestions(project_type):
    suggestions = []
    
    suggestions.append("Architecture diagram")
    suggestions.append("Feature overview diagram")
    
    if "ml" in project_type.lower() or "data" in project_type.lower():
        suggestions.append("Performance comparison chart")
        suggestions.append("Model architecture diagram")
    
    if "web" in project_type.lower():
        suggestions.append("UI screenshot")
        suggestions.append("Workflow diagram")
    
    suggestions.append("Installation steps flowchart")
    
    return suggestions[:5]

def get_example_suggestions(project_type, structure):
    examples = []
    
    examples.append("Basic usage example")
    examples.append("Advanced usage example")
    
    if structure.get("has_api"):
        examples.append("API endpoint examples")
    
    if "ml" in project_type.lower():
        examples.append("Training example")
        examples.append("Inference example")
    
    if "web" in project_type.lower():
        examples.append("Server setup example")
        examples.append("Client integration example")
    
    examples.append("Configuration examples")
    
    return examples[:5]

def get_badge_suggestions(project_type, structure):
    badges = [
        "GitHub Workflow Status",
        "Test Coverage",
        "PyPI version" if "python" in project_type.lower() else "npm version",
        "License",
    ]
    
    if structure.get("has_docs"):
        badges.append("Documentation")
    
    if structure.get("has_ci"):
        badges.append("Build Status")
    
    badges.append("Contributors")
    
    return badges[:6]

def calculate_quality_score(readme, structure, missing):
    score = 50
    
    if len(readme) > 500:
        score += 10
    if len(readme) > 1000:
        score += 10
    
    if structure.get("has_tests"):
        score += 10
    if structure.get("has_docs"):
        score += 10
    if structure.get("has_ci"):
        score += 10
    if structure.get("has_examples"):
        score += 5
    
    score -= len(missing) * 2
    
    return min(100, max(0, score))
