---
name: code-stats
description: 统计项目代码的详细信息，包括总行数、代码行、注释行、空行，支持多种编程语言
---

# Code Stats - 代码统计工具

统计当前项目中的代码行数，支持JavaScript、TypeScript、Python、Java、C/C++、Go等语言。

## 执行指令

运行Python统计脚本：

```bash
py .claude/skills/code-stats/count_stats.py
```

统计结果包括：
- 各语言的文件数量
- 总行数、代码行数、注释行数、空行数
- 各类别的百分比占比

自动忽略node_modules、.git、dist、build等目录。