import os
import argparse
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
from tqdm import tqdm
from openai import OpenAI
import yaml

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_IGNORE_DIRS = {
    'env',          # Python virtual environment
    'venv',         # Alternative virtual environment name
    '.git',         # Git directory
    '__pycache__',  # Python cache
    'node_modules'  # Node.js modules
}

class RepoSumm:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL, max_tokens: int = 500):
        """Initialize RepoSumm with configurable settings."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from config.yaml if it exists."""
        config_path = Path("config.yaml")
        default_config = {
            "excluded_dirs": [".git", "__pycache__", "node_modules", "venv"],
            "file_extensions": [".py", ".js", ".ts", ".c", ".cpp", ".md", ".yaml", ".json"],
            "chunk_size": 2000,
            "temperature": 0.5
        }
        
        if config_path.exists():
            with open(config_path, "r") as f:
                return {**default_config, **yaml.safe_load(f)}
        return default_config

    def summarize_code(self, code_snippet: str) -> str:
        """Summarize code snippet using OpenAI API with improved prompt."""
        try:
            messages = [
                {"role": "system", "content": (
                    "You are an expert code analyzer. Provide concise but comprehensive "
                    "summaries focusing on: 1) Main functionality 2) Key components "
                    "3) Important dependencies 4) Notable patterns or algorithms "
                    "5) Potential improvements or issues"
                )},
                {"role": "user", "content": f"""Analyze and summarize this code:

{code_snippet}"""}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error summarizing code: {str(e)}"

    def process_file(self, file_path: Path) -> Dict:
        """Process a single file and return its summary."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_snippet = f.read()

            messages = [
                {"role": "system", "content": (
                    "You are an expert code analyzer. Provide concise but comprehensive "
                    "summaries focusing on: 1) Main functionality 2) Key components "
                    "3) Important dependencies 4) Notable patterns or algorithms "
                    "5) Potential improvements or issues"
                )},
                {"role": "user", "content": f"""Analyze and summarize this code:

{code_snippet}"""}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )

            return {
                "file_path": str(file_path),
                "summary": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "file_path": str(file_path),
                "summary": f"Error processing file: {str(e)}"
            }

    def process_directory(self, directory_path: str, output_format: str = "markdown", output_file: Optional[str] = None) -> None:
        """Process all files in the given directory."""
        # まず対象ファイルのリストを作成
        files_to_process = []
        for root, dirs, files in os.walk(directory_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS]
            
            for file in files:
                file_path = Path(os.path.join(root, file))
                if (file_path.suffix in self.config["file_extensions"] and
                    not any(excluded in str(file_path) for excluded in self.config["excluded_dirs"])):
                    files_to_process.append(file_path)

        summaries = []
        # tqdmで進捗バーを表示しながら処理
        for file_path in tqdm(files_to_process, desc="Processing files", unit="file"):
            summary = self.process_file(file_path)
            summaries.append(summary)

        # 結果を保存
        self._save_results(summaries, output_format, output_file)

    def _save_results(self, summaries: List[Dict], output_format: str = "markdown", output_file: Optional[str] = None) -> None:
        """Save or display the analysis results."""
        output = ""
        if output_format == "markdown":
            output += "# Repository Analysis Summary\n\n"
            for summary in summaries:
                output += f"## {summary['file_path']}\n\n"
                output += f"{summary['summary']}\n\n"
        else:  # json format
            output = json.dumps(summaries, indent=2)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Results saved to: {output_file}")
        else:
            print(output)

def main():
    parser = argparse.ArgumentParser(description="Enhanced repository code summarizer")
    parser.add_argument("repo_path", type=str, help="Path to the repository")
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="OpenAI model to use")
    parser.add_argument("--format", type=str, choices=["markdown", "json"], 
                       default="json", help="Output format")
    parser.add_argument("--max-tokens", type=int, default=3000, help="Maximum tokens for response")
    parser.add_argument("--output", type=str, default="./RepoSummary.json", help="Output file path (if not specified, prints to console)")
    
    args = parser.parse_args()
    
    summarizer = RepoSumm(api_key=args.api_key, model=args.model, max_tokens=args.max_tokens)
    summarizer.process_directory(
        directory_path=args.repo_path,
        output_format=args.format,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
