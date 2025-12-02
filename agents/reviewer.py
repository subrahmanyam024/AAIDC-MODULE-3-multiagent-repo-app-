# agents/reviewer.py

def review(repo_summary, improved_data):
    issues = []
    recommendations = []
    completeness_checks = {}
    
    readme = repo_summary.get("readme", "")
    structure = repo_summary.get("structure", {})
    missing = repo_summary.get("missing", [])
    best_practices = repo_summary.get("best_practices", {})
    project_type = repo_summary.get("project_type", "")
    dependencies = repo_summary.get("dependencies", {})
    
    if not readme:
        issues.append("❌ No README found - this is critical for project visibility")
    
    if improved_data:
        if isinstance(improved_data, dict):
            improvements_list = improved_data.get("improvements", [])
            quality_score = improved_data.get("quality_score", 50)
        else:
            improvements_list = []
            quality_score = 50
        
        if improvements_list:
            for improvement in improvements_list[:3]:
                recommendations.append(f"💡 {improvement}")
    
    completeness_checks["has_license"] = any("license" in str(m).lower() for m in missing) == False
    completeness_checks["has_tests"] = structure.get("has_tests", False)
    completeness_checks["has_docs"] = structure.get("has_docs", False)
    completeness_checks["has_examples"] = structure.get("has_examples", False)
    completeness_checks["has_ci"] = structure.get("has_ci", False)
    completeness_checks["has_contributing"] = any("contribut" in str(m).lower() for m in missing) == False
    
    if not completeness_checks["has_license"]:
        issues.append("⚠️  No LICENSE file - add to clarify usage rights")
    
    if not completeness_checks["has_tests"]:
        issues.append("⚠️  No tests found - add test suite for credibility")
    
    if not completeness_checks["has_contributing"]:
        issues.append("⚠️  No CONTRIBUTING.md - make it easy for contributors to help")
    
    if not completeness_checks["has_ci"]:
        recommendations.append("💡 Add CI/CD pipeline (GitHub Actions, GitLab CI) to automate testing")
    
    if not best_practices.get("has_changelog"):
        recommendations.append("💡 Add CHANGELOG to track version history")
    
    if not best_practices.get("has_pull_request_template"):
        recommendations.append("💡 Add PR template to maintain code quality standards")
    
    if not best_practices.get("has_badges"):
        recommendations.append("💡 Add badges (build status, coverage, downloads) for credibility")
    
    readme_lower = readme.lower()
    
    section_checks = {
        "Installation": "install" in readme_lower or "setup" in readme_lower or "getting started" in readme_lower,
        "Usage": "usage" in readme_lower or "quickstart" in readme_lower or "example" in readme_lower,
        "Features": "feature" in readme_lower or "capabilities" in readme_lower,
        "Contributing": "contribut" in readme_lower or "guidelines" in readme_lower,
        "License": "license" in readme_lower,
        "API Reference": "api" in readme_lower or "documentation" in readme_lower
    }
    
    missing_sections = [sec for sec, exists in section_checks.items() if not exists]
    
    validation_results = {
        "critical_issues": len([i for i in issues if "❌" in i]),
        "warnings": len([i for i in issues if "⚠️" in i]),
        "recommendations_count": len(recommendations),
        "missing_readme_sections": missing_sections,
        "completeness": completeness_checks,
        "overall_health": calculate_health_score(issues, recommendations, completeness_checks)
    }
    
    return {
        "issues": issues,
        "recommendations": recommendations,
        "validation_results": validation_results,
        "action_items": generate_action_items(issues, recommendations),
        "priority_fixes": get_priority_fixes(issues, missing_sections)
    }

def calculate_health_score(issues, recommendations, completeness):
    score = 100
    score -= len([i for i in issues if "❌" in i]) * 20
    score -= len([i for i in issues if "⚠️" in i]) * 10
    score -= len(recommendations) * 5
    
    if not completeness.get("has_license"):
        score -= 15
    if not completeness.get("has_tests"):
        score -= 10
    if not completeness.get("has_docs"):
        score -= 5
    
    return max(0, min(100, score))

def generate_action_items(issues, recommendations):
    actions = []
    
    if any("No README" in i for i in issues):
        actions.append({
            "priority": "P0 - CRITICAL",
            "task": "Create comprehensive README.md",
            "details": "Include features, installation, usage, and contribution guidelines"
        })
    
    if any("No LICENSE" in i for i in issues):
        actions.append({
            "priority": "P1 - HIGH",
            "task": "Add LICENSE file",
            "details": "Choose appropriate license (MIT, Apache 2.0, GPL, etc.)"
        })
    
    if any("No tests" in i for i in issues):
        actions.append({
            "priority": "P1 - HIGH",
            "task": "Add test suite",
            "details": "Create tests folder with unit and integration tests"
        })
    
    for rec in recommendations[:3]:
        if "CI/CD" in rec:
            actions.append({
                "priority": "P2 - MEDIUM",
                "task": "Set up CI/CD pipeline",
                "details": "Use GitHub Actions, GitLab CI, or similar"
            })
        elif "badges" in rec:
            actions.append({
                "priority": "P3 - LOW",
                "task": "Add status badges",
                "details": "Build status, coverage, downloads badges"
            })
    
    return actions[:5]

def get_priority_fixes(issues, missing_sections):
    if any("No README" in i for i in issues):
        return ["Create README.md", "Add Installation section", "Add Usage examples"]
    elif any("No LICENSE" in i for i in issues):
        return ["Add LICENSE file", "Create CONTRIBUTING.md", "Add examples"]
    elif "Installation" in missing_sections:
        return ["Add Installation section", "Add Usage examples", "Add code samples"]
    else:
        return ["Add badges", "Improve documentation", "Add contributing guide"]
