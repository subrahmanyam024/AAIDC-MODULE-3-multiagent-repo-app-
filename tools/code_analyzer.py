import re
from typing import Dict, List
from pathlib import Path


class CodeAnalyzer:
    def __init__(self):
        self.patterns = {
            "python": {
                "imports": r"^(?:from|import)\s+",
                "functions": r"^def\s+(\w+)",
                "classes": r"^class\s+(\w+)",
                "async": r"^async\s+def"
            },
            "javascript": {
                "imports": r"(?:import|require)\s+",
                "functions": r"(?:function|const|let|var)\s+(\w+)",
                "classes": r"class\s+(\w+)",
                "async": r"async\s+"
            }
        }

    def analyze_file(self, file_path: str, content: str) -> Dict:
        ext = Path(file_path).suffix.lower()
        lang = self._detect_language(ext)

        return {
            "file": file_path,
            "language": lang,
            "size": len(content),
            "lines": len(content.split("\n")),
            "functions": self._extract_functions(content, lang),
            "classes": self._extract_classes(content, lang),
            "imports_count": self._count_imports(content, lang),
            "has_async": self._has_async(content, lang),
            "complexity_indicators": self._analyze_complexity(content)
        }

    def analyze_repository(self, files: List[Dict]) -> Dict:
        analysis = {
            "total_files": len(files),
            "total_lines": 0,
            "languages": {},
            "file_analyses": []
        }

        for file_info in files:
            file_analysis = self.analyze_file(file_info["path"], file_info["content"])
            analysis["file_analyses"].append(file_analysis)
            analysis["total_lines"] += file_analysis["lines"]

            lang = file_analysis["language"]
            if lang not in analysis["languages"]:
                analysis["languages"][lang] = 0
            analysis["languages"][lang] += 1

        return analysis

    def _detect_language(self, ext: str) -> str:
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".md": "markdown",
            ".txt": "text",
            ".json": "json",
            ".yaml": "yaml"
        }
        return lang_map.get(ext, "unknown")

    def _extract_functions(self, content: str, lang: str) -> List[str]:
        if lang not in self.patterns:
            return []

        pattern = self.patterns[lang].get("functions", "")
        if not pattern:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return list(set(matches))[:10]

    def _extract_classes(self, content: str, lang: str) -> List[str]:
        if lang not in self.patterns:
            return []

        pattern = self.patterns[lang].get("classes", "")
        if not pattern:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return list(set(matches))[:10]

    def _count_imports(self, content: str, lang: str) -> int:
        if lang not in self.patterns:
            return 0

        pattern = self.patterns[lang].get("imports", "")
        if not pattern:
            return 0

        return len(re.findall(pattern, content, re.MULTILINE))

    def _has_async(self, content: str, lang: str) -> bool:
        if lang not in self.patterns:
            return False

        pattern = self.patterns[lang].get("async", "")
        if not pattern:
            return False

        return bool(re.search(pattern, content, re.MULTILINE))

    def _analyze_complexity(self, content: str) -> Dict:
        lines = content.split("\n")
        return {
            "nested_depth": self._calculate_nesting(lines),
            "long_lines": sum(1 for line in lines if len(line) > 100),
            "comments": sum(1 for line in lines if "#" in line or "//" in line),
            "empty_lines": sum(1 for line in lines if not line.strip())
        }

    def _calculate_nesting(self, lines: List[str]) -> int:
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        return max_indent
