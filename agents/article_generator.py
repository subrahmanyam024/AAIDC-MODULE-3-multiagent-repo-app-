import os
from config.config import co
from utils.resilience import llm_retry


class ArticleGeneratorAgent:
    """Generates publication-ready articles from repository context and user instructions."""
    
    def __init__(self):
        self.model = "command-a-03-2025"
        
    @llm_retry
    def generate(self, repo_context: str, user_instructions: str, project_description: str = "") -> str:
        """Generate article based on repo context and user instructions."""
        
        prompt = f"""You are an expert technical writer specializing in creating publication-ready articles about software projects.

Your task is to generate a well-structured, engaging article based on the repository content and user instructions.

Guidelines:
1. Create a professional, publication-ready article
2. Use clear structure with sections and subsections
3. Include code examples where relevant
4. Add [TODO: ...] tags for sections that need manual completion or more information
5. Use technical but accessible language
6. Ensure the article is comprehensive but concise
7. Include relevant technical details from the repository
8. Write with proper markdown formatting

REPOSITORY CONTEXT:
{repo_context}

PROJECT DESCRIPTION (if provided):
{project_description if project_description else "No additional description provided"}

USER INSTRUCTIONS FOR ARTICLE:
{user_instructions}

Please generate a complete, well-structured article following the user's instructions. Include [TODO: ...] tags for any sections that need manual review or additional information."""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=4096
            )
            
            article = response.text.strip()
            return article
            
        except Exception as e:
            raise Exception(f"Failed to generate article: {str(e)}")

    @llm_retry
    def generate_outline(self, repo_context: str, user_instructions: str) -> str:
        """Generate article outline first before full article."""
        
        prompt = f"""You are an expert at creating article outlines. Generate a detailed outline for the article based on the repository and instructions.
Format: Use markdown with numbered/bulleted lists.

REPOSITORY CONTEXT:
{repo_context}

USER INSTRUCTIONS:
{user_instructions}

Provide a comprehensive outline that will guide the article creation. Use clear hierarchical structure with main sections and subsections."""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=2048
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate outline: {str(e)}")

    @llm_retry
    def extract_summary(self, file_content: str) -> str:
        """Extract key summary from file content."""
        
        prompt = f"""Summarize the following file content in 2-3 sentences:

{file_content}

Summary:"""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=200
            )
            
            return response.text.strip()
            
        except Exception as e:
            return "[TODO: Add manual summary]" 
