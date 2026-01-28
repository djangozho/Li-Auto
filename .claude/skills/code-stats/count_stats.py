#!/usr/bin/env python3
"""
Code Statistics Tool
统计项目代码的详细信息，支持Python、JavaScript等源文件和Jupyter Notebook
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# 文件扩展名映射
EXTENSIONS = {
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.py': 'Python',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.go': 'Go',
    '.ipynb': 'Jupyter Notebook'
}

# 忽略的目录
IGNORE_DIRS = {
    'node_modules', '.git', 'dist', 'build', '__pycache__',
    '.venv', 'venv', 'env', 'target', 'out', '.idea', '.vscode'
}

class CodeStats:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0
        })

    def is_comment_line(self, line, ext):
        """判断是否为注释行"""
        stripped = line.strip()

        if ext in ['.py', '.sh']:
            return stripped.startswith('#')
        elif ext in ['.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.go']:
            return stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*')
        return False

    def analyze_notebook(self, file_path):
        """分析Jupyter Notebook文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            lang = 'Jupyter Notebook'
            self.stats[lang]['files'] += 1

            cells = data.get('cells', [])
            for cell in cells:
                if cell.get('cell_type') == 'code':
                    source = cell.get('source', [])
                    for line in source:
                        self.stats[lang]['total_lines'] += 1
                        stripped = line.strip()

                        if not stripped:
                            self.stats[lang]['blank_lines'] += 1
                        elif stripped.startswith('#'):
                            self.stats[lang]['comment_lines'] += 1
                        else:
                            self.stats[lang]['code_lines'] += 1

        except Exception as e:
            print(f"无法读取Notebook {file_path}: {e}")

    def analyze_file(self, file_path, ext):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            lang = EXTENSIONS[ext]
            self.stats[lang]['files'] += 1

            in_multiline_comment = False

            for line in lines:
                self.stats[lang]['total_lines'] += 1
                stripped = line.strip()

                # 空行
                if not stripped:
                    self.stats[lang]['blank_lines'] += 1
                    continue

                # 多行注释处理
                if '/*' in stripped:
                    in_multiline_comment = True
                if '*/' in stripped:
                    in_multiline_comment = False
                    self.stats[lang]['comment_lines'] += 1
                    continue

                if in_multiline_comment:
                    self.stats[lang]['comment_lines'] += 1
                    continue

                # 单行注释
                if self.is_comment_line(stripped, ext):
                    self.stats[lang]['comment_lines'] += 1
                else:
                    self.stats[lang]['code_lines'] += 1

        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")

    def scan_directory(self, root_dir='.'):
        """扫描目录"""
        root_path = Path(root_dir)

        for file_path in root_path.rglob('*'):
            # 跳过忽略的目录
            if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
                continue

            if file_path.is_file():
                ext = file_path.suffix
                if ext in EXTENSIONS:
                    if ext == '.ipynb':
                        self.analyze_notebook(file_path)
                    else:
                        self.analyze_file(file_path, ext)

    def print_report(self):
        """打印统计报告"""
        print("\n" + "="*80)
        print("代码统计报告 - Code Statistics Report")
        print("="*80 + "\n")

        if not self.stats:
            print("未找到任何代码文件。")
            return

        # 按语言打印
        print(f"{'语言':<15} {'文件数':<8} {'总行数':<10} {'代码行':<10} {'注释行':<10} {'空行':<10}")
        print("-"*80)

        total_files = 0
        total_lines = 0
        total_code = 0
        total_comments = 0
        total_blank = 0

        for lang in sorted(self.stats.keys()):
            s = self.stats[lang]
            print(f"{lang:<15} {s['files']:<8} {s['total_lines']:<10} "
                  f"{s['code_lines']:<10} {s['comment_lines']:<10} {s['blank_lines']:<10}")

            total_files += s['files']
            total_lines += s['total_lines']
            total_code += s['code_lines']
            total_comments += s['comment_lines']
            total_blank += s['blank_lines']

        print("-"*80)
        print(f"{'总计':<15} {total_files:<8} {total_lines:<10} "
              f"{total_code:<10} {total_comments:<10} {total_blank:<10}")
        print("="*80)

        # 统计百分比
        if total_lines > 0:
            code_pct = (total_code / total_lines) * 100
            comment_pct = (total_comments / total_lines) * 100
            blank_pct = (total_blank / total_lines) * 100

            print(f"\n代码占比: {code_pct:.1f}%")
            print(f"注释占比: {comment_pct:.1f}%")
            print(f"空行占比: {blank_pct:.1f}%")

        print()

if __name__ == '__main__':
    import sys
    import io

    # Fix Windows console encoding for Chinese characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    stats = CodeStats()
    print("正在扫描项目文件...")
    stats.scan_directory('.')
    stats.print_report()