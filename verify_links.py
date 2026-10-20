#!/usr/bin/env python3
"""
verify_links.py
自动获取仓库 remote 信息，拼接全部表情包的 Raw 永久有效直链，
并发校验所有直链 HTTP 状态码，并输出详细状态报告与统计表。
"""

import os
import re
import sys
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STICKERS_DIR = os.path.join(BASE_DIR, "assets", "stickers")

def get_repo_info():
    try:
        remote = subprocess.check_output(
            ["git", "-C", BASE_DIR, "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        remote = ""

    if not remote:
        return "a2557215848-dotcom", "nature-skills"

    # Match https://github.com/owner/repo.git or git@github.com:owner/repo.git
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
    if m:
        return m.group(1), m.group(2)
    return "a2557215848-dotcom", "nature-skills"

def check_url(item):
    filename, url = item
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        code = resp.getcode()
        return filename, url, code, True
    except urllib.error.HTTPError as e:
        return filename, url, e.code, False
    except Exception as e:
        return filename, url, str(e), False

def main():
    owner, repo = get_repo_info()
    print(f"=== 仓库信息: {owner}/{repo} ===")
    
    if not os.path.isdir(STICKERS_DIR):
        print(f"错误: 目录不存在 {STICKERS_DIR}")
        sys.exit(1)

    files = sorted([f for f in os.listdir(STICKERS_DIR) if f.endswith(('.gif', '.png', '.jpg'))])
    if not files:
        print("未检测到表情包文件！")
        sys.exit(1)

    tasks = [(f, f"https://raw.githubusercontent.com/{owner}/{repo}/main/assets/stickers/{f}") for f in files]
    print(f"待校验直链总数: {len(tasks)} 条\n")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_url, tasks))

    success = sum(1 for _, _, _, ok in results if ok)
    print("=" * 70)
    print(f"{'文件名':<18} | {'HTTP状态':<8} | 直链地址")
    print("-" * 70)
    for fname, url, code, ok in results:
        status_icon = "🟢 200" if code == 200 else f"🔴 {code}"
        print(f"{fname:<18} | {status_icon:<8} | {url}")
    print("=" * 70)
    print(f"直链校验结果: 成功 {success}/{len(results)} (HTTP 200)")

    return 0 if success == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
