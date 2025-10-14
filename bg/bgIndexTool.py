#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_bg_index.py
在 bg/ 目录中运行，自动生成 bg_index.json 文件（无 _root 层级）。
完全兼容 flattenStructure() 的解析逻辑。
"""

import os
import json
from datetime import datetime

# 可识别的图片扩展名
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}

# 忽略文件列表（可按需调整）
IGNORE_FILES = {'bg_index.json', 'generate_bg_index.py'}


def build_structure(path):
    """
    递归扫描目录，构建嵌套结构：
    - 当前目录仅包含图片 → 返回 list
    - 否则 → 返回 dict，子目录为键，数组或对象为值
    """
    items = sorted(os.listdir(path))
    images = [f for f in items
              if os.path.splitext(f)[1].lower() in IMAGE_EXTS and f not in IGNORE_FILES]
    dirs = [f for f in items if os.path.isdir(os.path.join(path, f))]

    if not dirs:
        # 没有子目录，直接返回图片数组
        return images

    structure = {}
    # 若本层也有图片，可单独作为 "root" 分类
    if images:
        structure["."] = images

    for d in dirs:
        sub_path = os.path.join(path, d)
        sub_struct = build_structure(sub_path)
        if sub_struct:
            structure[d] = sub_struct

    return structure


def generate_index():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    structure = build_structure(root_dir)

    data = {
        "version": 2,
        "lastUpdate": datetime.utcnow().isoformat() + "Z",
        "structure": structure
    }

    out_path = os.path.join(root_dir, "bg_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[✔] bg_index.json 已生成，共 {count_images(structure)} 张图片")


def count_images(node):
    """递归计数所有图片数量"""
    if isinstance(node, list):
        return len(node)
    elif isinstance(node, dict):
        return sum(count_images(v) for v in node.values())
    return 0


if __name__ == "__main__":
    generate_index()
