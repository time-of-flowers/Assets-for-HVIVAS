#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_bg_index_remote_flat.py
通过 GitHub API 获取远程 bg 目录树，并生成扁平化路径列表 JSON。
"""

import json
import requests
import time
from datetime import datetime

# ================= 配置 =================
OWNER = "time-of-flowers"
REPO = "Assets-for-HVIVAS"
BRANCH = "main"
ROOT_PATH = "bg"
OUTPUT_FILE = "bg_index.json"

# 可识别的图片后缀
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# 请求间隔，避免触发 GitHub API 速率限制
REQUEST_DELAY = 0.3

# 可选：个人访问令牌，私有仓库或高频访问建议使用
GITHUB_TOKEN = ''
# GITHUB_TOKEN = "ghp_XXXXXX"
# =======================================


def github_api_request(url):
    """带可选 token 的请求"""
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


def build_flat_list(api_url, prefix=""):
    """递归获取远程目录的扁平化路径列表"""
    time.sleep(REQUEST_DELAY)
    data = github_api_request(api_url)
    if not data:
        return []

    result = []

    for item in data:
        name = item["name"]
        if item["type"] == "file" and any(name.lower().endswith(ext) for ext in IMAGE_EXTS):
            result.append(prefix + name)
        elif item["type"] == "dir":
            result.extend(build_flat_list(item["url"], prefix + name + "/"))

    return result


def main():
    root_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{ROOT_PATH}?ref={BRANCH}"
    print(f"[+] Fetching remote structure from {root_url}")

    images = build_flat_list(root_url)

    data = {
        "version": 2,
        "lastUpdate": datetime.utcnow().isoformat() + "Z",
        "images": images
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[✔] bg_index.json 已生成，共 {len(images)} 张图片")


if __name__ == "__main__":
    main()
