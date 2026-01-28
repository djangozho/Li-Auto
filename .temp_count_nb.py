import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'd:\zhoufeng7\Pythonfile\Weibull\索赔单导出_W01.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

cells = data.get('cells', [])
code_lines = 0
comment_lines = 0
blank_lines = 0
total_lines = 0

for cell in cells:
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for line in source:
            total_lines += 1
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1

print("="*70)
print("Jupyter Notebook 代码统计 - 索赔单导出_W01.ipynb")
print("="*70)
print(f"\n总行数:   {total_lines}")
print(f"代码行:   {code_lines}")
print(f"注释行:   {comment_lines}")
print(f"空行:     {blank_lines}")

if total_lines > 0:
    print(f"\n代码占比: {code_lines/total_lines*100:.1f}%")
    print(f"注释占比: {comment_lines/total_lines*100:.1f}%")
    print(f"空行占比: {blank_lines/total_lines*100:.1f}%")
print()