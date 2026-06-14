import os
import json
import re

def fold_simple_brace(match):
    """通用的将整个 {...} 块内部的换行和多余空格压缩为一个空格的函数"""
    return re.sub(r'\s+', ' ', match.group(0))

def process_blockstates(raw_json):
    """处理 blockstates 状态文件：折叠 variants 和 multipart 里的模型指向对象"""
    # 匹配形如 { "model": "...", "weight": 1, "y": 90 } 的对象块
    # 只要花括号里包含 "model": "..." 就会被折叠为一行
    return re.sub(r'\{\s*"model"\s*:\s*"[^"]+"[^}]*\}', fold_simple_brace, raw_json)

def process_models(raw_json):
    """处理 models 模型文件：折叠坐标/UV数组，折叠 faces/rotation 对象"""
    # 1. 折叠 3 个数字的数组
    raw_json = re.sub(r'\[\s+([-\d.]+),\s+([-\d.]+),\s+([-\d.]+)\s+\]', r'[\1, \2, \3]', raw_json)
    # 2. 折叠 4 个数字的数组
    raw_json = re.sub(r'\[\s+([-\d.]+),\s+([-\d.]+),\s+([-\d.]+),\s+([-\d.]+)\s+\]', r'[\1, \2, \3, \4]', raw_json)

    # 3. 折叠 faces 里的方向对象 以及 elements 里的 rotation 对象
    def fold_object_to_single_line(match):
        key = match.group(1)     # 键名
        content = match.group(2) # {} 内部的内容
        clean_content = re.sub(r'\s+', ' ', content).strip()
        return f'"{key}": {{ {clean_content} }}'

    target_keys = "north|south|east|west|up|down|rotation"
    pattern = rf'"({target_keys})"\s*:\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}'
    raw_json = re.sub(pattern, fold_object_to_single_line, raw_json)
    
    return raw_json

def format_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"解析错误跳过: {filepath}")
            return

    # 1. 基础格式化（缩进为2个空格）
    raw_json = json.dumps(data, indent=2, ensure_ascii=False)

    # 2. 判断 json 文件类型并分发处理
    if "variants" in data or "multipart" in data:
        file_type = 'blockstates'
        raw_json = process_blockstates(raw_json)
    else:
        file_type = 'models'
        raw_json = process_models(raw_json)

    # 3. 确保文件末尾有且只有一个换行符
    raw_json = raw_json.rstrip() + '\n'

    # 4. 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(raw_json)
    print(f"[{file_type.upper()}] 已格式化: {filepath}")

if __name__ == "__main__":
    # 仅遍历当前目录及所有子目录下的 .json 文件
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".json"):
                format_json_file(os.path.join(root, file))
