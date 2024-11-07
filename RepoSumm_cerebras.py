import os
import argparse
from openai import OpenAI
from tqdm import tqdm  # tqdmをインポート

client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

def summarize_code(code_snippet):
    """
    ソースコードのスニペットをOpenAI APIで要約する関数。
    """
    messages = [
        { "role": "system", "content": "You are a helpful assistant who summarizes code and markdown file." },
        { "role": "user", "content": f"Please provide a concise summary of the following code or file. Focus on explaining its primary functionality, key modules, functions, classes, and any parameters or settings it defines. Additionally, if the code interacts with APIs, external libraries, or specific workflows, please clarify those connections.\n\n{code_snippet}" }
    ]

    try:
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )
        rtn = response.choices[0].message.content.strip()
        return rtn
    except Exception as e:
        print(f"Error summarizing code snippet: {e}")
        return "Error processing this snippet. Skipping."

def process_file(file_path):
    """
    ファイルを読み込み、コードを要約して返す。
    """
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()
    
    # コードを適切な長さに分割して要約
    snippets = code.split("\n\n")  # 空行ごとに分割（必要に応じて調整）
    summary_parts = []
    
    for snippet in tqdm(snippets, desc=f"Processing snippets in {os.path.basename(file_path)}"):  # スニペットごとに進捗バーを表示
        if snippet.strip():  # 空でないスニペットに対してのみ要約
            summary = summarize_code(snippet)
            summary_parts.append(summary)

    return "\n".join(summary_parts)

def process_directory(start_path):
    """
    Recursively search for .py, .js, .ts files in the given directory and summarize them,
    excluding files that start with a dot (hidden files).
    """
    summaries = []
    # tqdmでファイルの進捗バーを追加
    for root, _, files in os.walk(start_path):
        files = [file for file in files if not file.startswith(".") and file.endswith((".py", ".js", ".ts", ".c", ".cpp", ".md", ".yaml", "json"))]
        for file in tqdm(files, desc="Processing files"):
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            file_summary = process_file(file_path)
                
            # Save the file path and summary
            relative_path = os.path.relpath(file_path, start_path)
            summaries.append(f"## {relative_path}\n\n{file_summary}\n")
    return summaries

def write_markdown(summaries, output_path="repo_summary.md"):
    """
    要約リストをMarkdownファイルに書き出す。
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Repository Code Summaries\n\n")
        for summary in summaries:
            f.write(summary + "\n")
    print(f"Markdown summary generated at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="リポジトリのコードを要約するスクリプト")
    parser.add_argument("repo_path", type=str, help="要約するリポジトリのパス")
    args = parser.parse_args()
    
    # ディレクトリを再帰的に探索し、要約を生成
    summaries = process_directory(args.repo_path)
    # 要約をMarkdownファイルとして書き出し
    write_markdown(summaries)