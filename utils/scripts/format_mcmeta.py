import os
import json
import re

def fold_simple_brace(match):
    """通用的将整个 {...} 块内部的换行和多余空格压缩为一个空格的函数"""
    return re.sub(r'\s+', ' ', match.group(0))

def process_mcmeta(raw_json):
    """处理 .mcmeta 动画文件：保持数组纵向排列，只折叠 {} 对象"""
    # 匹配 mcmeta 中包含 "index" 的动画帧对象，例如：
    # {
    #   "index": 8,
    #   "time": 20
    # }
    # 会被折叠为 { "index": 8, "time": 20 }
    return re.sub(r'\{\s*"index"\s*:\s*\d+[^}]*\}', fold_simple_brace, raw_json)

def format_mcmeta_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"解析错误跳过: {filepath}")
            return

    # 1. 基础格式化（缩进为2个空格，这会自动把数组的每个元素独立成行）
    raw_json = json.dumps(data, indent=2, ensure_ascii=False)

    # 2. 正则处理：只合并 {} 对象的换行，不影响外层数组的换行
    raw_json = process_mcmeta(raw_json)

    # 3. 确保文件末尾有且只有一个换行符
    raw_json = raw_json.rstrip() + '\n'

    # 4. 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(raw_json)
    print(f"[MCMETA] 已格式化: {filepath}")

if __name__ == "__main__":
    # 仅遍历当前目录及所有子目录下的 .mcmeta 文件
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".mcmeta"):
                format_mcmeta_file(os.path.join(root, file))
