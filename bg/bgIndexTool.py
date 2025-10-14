#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_bg_index_remote.py
使用 GitHub API 获取远程仓库目录结构，生成 bg_index.json。
"""

import json
import requests
from datetime import datetime
import time

# ===== 配置部分 =====
OWNER = "time-of-flowers"
REPO = "Assets-for-HVIVAS"
BRANCH = "main"
ROOT_PATH = "bg"
OUTPUT_FILE = "bg_index.json"

# 可识别的图片后缀
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
# 访问间隔（避免 GitHub API 速率限制）
REQUEST_DELAY = 0.3

# （可选）私有仓库或高频访问可使用个人访问令牌
GITHUB_TOKEN = ''
# GITHUB_TOKEN = "ghp_xxx"

# ====================


def github_api_request(url):
    """带重试与可选 Token 的请求封装"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    for _ in range(3):
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        time.sleep(1)
    print(f"⚠️ 请求失败: {url} ({r.status_code})")
    return None


def build_structure(api_url):
    """递归获取目录结构"""
    time.sleep(REQUEST_DELAY)
    data = github_api_request(api_url)
    if not data:
        return {}

    files = []
    structure = {}

    for item in data:
        name = item["name"]
        if item["type"] == "file":
            if any(name.lower().endswith(ext) for ext in IMAGE_EXTS):
                files.append(name)
        elif item["type"] == "dir":
            sub_struct = build_structure(item["url"])
            if sub_struct:
                structure[name] = sub_struct

    # 如果当前目录只包含图片文件，则直接返回列表
    if structure:
        if files:
            structure["."] = files
        return structure
    else:
        return files


def main():
    root_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{ROOT_PATH}?ref={BRANCH}"
    print(f"[+] Fetching remote structure from {root_url}")
    structure = build_structure(root_url)

    result = {
        "version": 2,
        "lastUpdate": datetime.utcnow().isoformat() + "Z",
        "structure": structure
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = count_images(structure)
    print(f"[✔] 生成完成：{OUTPUT_FILE}（共 {total} 张图片）")


def count_images(node):
    """递归统计图片数量"""
    if isinstance(node, list):
        return len(node)
    elif isinstance(node, dict):
        return sum(count_images(v) for v in node.values())
    return 0


if __name__ == "__main__":
    main()
