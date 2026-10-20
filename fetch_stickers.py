#!/usr/bin/env python3
"""
fetch_stickers.py
批量下载与构建 Muse 萌系表情包库 (41张精选多场景/多风格动图)
涵盖 8 大核心场景：
01_praise_求夸撒娇 (praise_01 ~ praise_05)
02_angry_炸毛暴躁 (angry_01 ~ angry_05)
03_crazy_发疯宕机 (crazy_01 ~ crazy_06)
04_cry_委屈认怂 (cry_01 ~ cry_05)
05_layflat_摸鱼摆烂 (layflat_01 ~ layflat_05)
06_eat_干饭时刻 (eat_01 ~ eat_05)
07_comfort_贴贴安慰 (comfort_01 ~ comfort_05)
08_drama_吃瓜看戏 (drama_01 ~ drama_05)
"""

import os
import re
import sys
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STICKERS_DIR = os.path.join(BASE_DIR, "assets", "stickers")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

STICKER_DEFINITIONS = {
    # 01_praise_求夸撒娇 (5张)
    "praise_01": {
        "desc": "线条小狗摇尾巴",
        "category": "01_praise_求夸撒娇",
        "queries": ["maltese-dog-tail-wag", "puppy-wagging-tail", "cute-dog-happy"],
        "fallback_url": "https://media.tenor.com/bUI-CVBU2rQAAAAM/zoey-hyper.gif"
    },
    "praise_02": {
        "desc": "猫咪探头求摸摸",
        "category": "01_praise_求夸撒娇",
        "queries": ["cat-pet-head-cute", "cat-pat-head", "cat-asking-for-pets"],
        "fallback_url": "https://media.tenor.com/o2WBnZirgp4AAAAM/kaede-azusagawa-rascal-does-not-dream-of-bunny-girl-senpai.gif"
    },
    "praise_03": {
        "desc": "邀功得瑟",
        "category": "01_praise_求夸撒娇",
        "queries": ["anime-smug-proud", "smug-proud-cute", "bragging-anime"],
        "fallback_url": "https://media.tenor.com/iQBfhDPbOlMAAAAM/yu-gi-oh-sevens-yuga-ohdo.gif"
    },
    "praise_04": {
        "desc": "夸我求摸头",
        "category": "01_praise_求夸撒娇",
        "queries": ["pat-my-head-cute", "praise-me-anime", "cute-love-happy"],
        "fallback_url": "https://media.tenor.com/cHWUMHoUr64AAAAM/love-kisses.gif"
    },
    "praise_05": {
        "desc": "撒娇蹦跶摇摆",
        "category": "01_praise_求夸撒娇",
        "queries": ["cute-puppy-happy-dance", "maltese-puppy-dance", "happy-wiggle-cute"],
        "fallback_url": "https://media.tenor.com/WEKotXEEf_EAAAAM/lucu.gif"
    },

    # 02_angry_炸毛暴躁 (5张)
    "angry_01": {
        "desc": "小猫掀桌",
        "category": "02_angry_炸毛暴躁",
        "queries": ["cat-flip-table", "cat-table-flip", "angry-table-flip"],
        "fallback_url": "https://media.tenor.com/f4X6M9xiDK8AAAAM/table-flip-angry.gif"
    },
    "angry_02": {
        "desc": "平底锅敲人",
        "category": "02_angry_炸毛暴躁",
        "queries": ["frying-pan-hit-anime", "frying-pan-bonk", "rapunzel-frying-pan"],
        "fallback_url": "https://media.tenor.com/-nUvNvpdFJYAAAAM/working-wagnaria.gif"
    },
    "angry_03": {
        "desc": "气成河豚",
        "category": "02_angry_炸毛暴躁",
        "queries": ["angry-pout-cute", "pout-angry-anime", "pouting-cheeks"],
        "fallback_url": "https://media.tenor.com/VDkev4sPJnMAAAAM/mad-angry.gif"
    },
    "angry_04": {
        "desc": "替你出头",
        "category": "02_angry_炸毛暴躁",
        "queries": ["angry-protect-cat", "fighting-for-you-cute", "protect-angry-meme"],
        "fallback_url": "https://media.tenor.com/FhB1fAE8F9cAAAAM/angry-cat.gif"
    },
    "angry_05": {
        "desc": "暴躁炸毛猫咪",
        "category": "02_angry_炸毛暴躁",
        "queries": ["angry-cat-screaming", "cute-angry-rage", "cat-hiss-mad"],
        "fallback_url": "https://media.tenor.com/CaY_SzDYXt8AAAAM/aggy-cat.gif"
    },

    # 03_crazy_发疯宕机 (6张)
    "crazy_01": {
        "desc": "吉伊卡哇乌萨奇尖叫",
        "category": "03_crazy_发疯宕机",
        "queries": ["chiikawa-usagi-scream", "usagi-screaming", "chiikawa-usagi"],
        "fallback_url": "https://media.tenor.com/ff0iUIePpKIAAAAM/usagi-usagi-crying.gif"
    },
    "crazy_02": {
        "desc": "满地乱爬",
        "category": "03_crazy_发疯宕机",
        "queries": ["crawling-fast-funny", "crawling-meme-fast", "fast-crawl-floor"],
        "fallback_url": "https://media.tenor.com/tXRmFKhbgpsAAAAM/chiikawa-usagi.gif"
    },
    "crazy_03": {
        "desc": "大脑过载",
        "category": "03_crazy_发疯宕机",
        "queries": ["brain-overload-anime", "head-explode-meme", "system-overload-cute"],
        "fallback_url": "https://media.tenor.com/MTTrIdfNjeUAAAAM/chiikawa-usagi.gif"
    },
    "crazy_04": {
        "desc": "外星信号接收中",
        "category": "03_crazy_发疯宕机",
        "queries": ["alien-signal-static", "receiving-transmission-meme", "static-cat-brain"],
        "fallback_url": "https://media.tenor.com/leL6Fda5_44AAAAM/usagi-chiikawa.gif"
    },
    "crazy_05": {
        "desc": "发狂疯狂旋转",
        "category": "03_crazy_发疯宕机",
        "queries": ["chiikawa-crazy-spin", "spinning-crazy-meme", "usagi-spin"],
        "fallback_url": "https://media.tenor.com/WhEybUxEYjIAAAAM/chiikawa-usagi.gif"
    },
    "crazy_06": {
        "desc": "宕机眩晕眼冒金星",
        "category": "03_crazy_发疯宕机",
        "queries": ["dizzy-stars-anime", "dizzy-cat-faint", "brain-blank-screen"],
        "fallback_url": "https://media.tenor.com/m9aWupYVvCcAAAAM/chiikawa-chiikawa-dancing.gif"
    },

    # 04_cry_委屈认怂 (5张)
    "cry_01": {
        "desc": "眼泪汪汪",
        "category": "04_cry_委屈认怂",
        "queries": ["chiikawa-crying-tears", "cute-crying-tears", "watery-eyes-anime-cry"],
        "fallback_url": "https://media.tenor.com/qJJxbXPGqcUAAAAM/momonga-chii-kawa.gif"
    },
    "cry_02": {
        "desc": "缩在墙角画圈圈",
        "category": "04_cry_委屈认怂",
        "queries": ["sitting-in-corner-crying", "sad-corner-anime", "sitting-in-corner-sad"],
        "fallback_url": "https://media.tenor.com/xrSi98HyjLoAAAAM/chiikawa-hachiware.gif"
    },
    "cry_03": {
        "desc": "本宝宝知豆错了",
        "category": "04_cry_委屈认怂",
        "queries": ["im-sorry-cute-cat", "sorry-apologize-cat", "kneel-apology-anime"],
        "fallback_url": "https://media.tenor.com/xwHA4XpQti4AAAAM/dogs-unhappy.gif"
    },
    "cry_04": {
        "desc": "委屈抽泣",
        "category": "04_cry_委屈认怂",
        "queries": ["sob-cute-anime", "sniffling-crying-cute", "sad-kitten-crying"],
        "fallback_url": "https://media.tenor.com/siSz3-JwXyYAAAAM/hachiware-chiikawa.gif"
    },
    "cry_05": {
        "desc": "抱头认怂求放过",
        "category": "04_cry_委屈认怂",
        "queries": ["bow-apology-anime", "forgive-me-please-cute", "guilty-cat-sorry"],
        "fallback_url": "https://media.tenor.com/SZe9o3V-xMoAAAAM/3-rabbit-things.gif"
    },

    # 05_layflat_摸鱼摆烂 (5张)
    "layflat_01": {
        "desc": "卡皮巴拉佛系泡汤",
        "category": "05_layflat_摸鱼摆烂",
        "queries": ["capybara-bath-orange", "capybara-bath-onsen", "capybara-onsen"],
        "fallback_url": "https://media.tenor.com/BAa9ZAJiqxoAAAAM/capybara-onsen.gif"
    },
    "layflat_02": {
        "desc": "猫猫瘫成煎饼",
        "category": "05_layflat_摸鱼摆烂",
        "queries": ["flat-cat-sleep", "cat-flat-pancake", "flat-sleeping-cat"],
        "fallback_url": "https://media.tenor.com/MoeAPGA5MLQAAAAM/chillin-marketmove.gif"
    },
    "layflat_03": {
        "desc": "不想努力了",
        "category": "05_layflat_摸鱼摆烂",
        "queries": ["give-up-lay-down", "lazy-lay-flat-anime", "i-give-up-floor"],
        "fallback_url": "https://media.tenor.com/wfbRdVwYy8kAAAAM/cappy-capybara.gif"
    },
    "layflat_04": {
        "desc": "佛系放空",
        "category": "05_layflat_摸鱼摆烂",
        "queries": ["capybara-relax", "capybara-relax-chill", "capybara-zen"],
        "fallback_url": "https://media.tenor.com/12eG7K5tnj8AAAAM/funny-animals-shower.gif"
    },
    "layflat_05": {
        "desc": "眼神呆滞神游",
        "category": "05_layflat_摸鱼摆烂",
        "queries": ["cat-stare-blank-space", "spacing-out-blank-stare", "blank-stare-cat"],
        "fallback_url": "https://media.tenor.com/qWteDNhZTsQAAAAM/trex-capybara-walk-in-pool.gif"
    },

    # 06_eat_干饭时刻 (5张)
    "eat_01": {
        "desc": "大口狂炫汉堡",
        "category": "06_eat_干饭时刻",
        "queries": ["cute-eating-burger", "eating-burger-fast-cute", "anime-eating-burger"],
        "fallback_url": "https://media.tenor.com/pQKcEhv0OvoAAAAM/brown-cony.gif"
    },
    "eat_02": {
        "desc": "抱奶茶吨吨吨",
        "category": "06_eat_干饭时刻",
        "queries": ["drinking-boba-cute", "boba-drink-anime", "drinking-milk-tea-cute"],
        "fallback_url": "https://media.tenor.com/weQtyhtb3LgAAAAM/fluffy-dog.gif"
    },
    "eat_03": {
        "desc": "肚子咕咕叫",
        "category": "06_eat_干饭时刻",
        "queries": ["hungry-tummy-rumble", "starving-cute-cat", "hungry-stomach-growl"],
        "fallback_url": "https://media.tenor.com/qqgov1d8e9oAAAAM/maltese-dog.gif"
    },
    "eat_04": {
        "desc": "仓鼠狂炫零食",
        "category": "06_eat_干饭时刻",
        "queries": ["hamster-eating-cute", "hamster-munching-snacks", "munching-chips-cute"],
        "fallback_url": "https://media.tenor.com/_vt4JuglR-MAAAAM/fluffy-dog.gif"
    },
    "eat_05": {
        "desc": "快乐干饭炫拉面",
        "category": "06_eat_干饭时刻",
        "queries": ["anime-eating-delicious", "happy-eating-ramen", "yummy-delicious-food-anime"],
        "fallback_url": "https://media.tenor.com/B_znqJ-MnGAAAAAM/maltese-maltese-dance.gif"
    },

    # 07_comfort_贴贴安慰 (5张)
    "comfort_01": {
        "desc": "隔空熊抱",
        "category": "07_comfort_贴贴安慰",
        "queries": ["bear-hug-cute", "big-bear-hug-cute", "warm-hug-anime"],
        "fallback_url": "https://media.tenor.com/iLC-_u_3rJsAAAAM/milk-and-mocha-milk-and-mocha-hug.gif"
    },
    "comfort_02": {
        "desc": "给揉揉脑壳",
        "category": "07_comfort_贴贴安慰",
        "queries": ["pat-head-comfort", "pat-head-comfort-cat", "gentle-head-pat"],
        "fallback_url": "https://media.tenor.com/h_edhSz2dHQAAAAM/catbottleflip-thrown-bottle.gif"
    },
    "comfort_03": {
        "desc": "递热饮顺毛",
        "category": "07_comfort_贴贴安慰",
        "queries": ["warm-drink-comfort-tea", "warm-tea-give-hot-drink", "giving-hot-cocoa"],
        "fallback_url": "https://media.tenor.com/izTvzDEtcigAAAAM/flip-off-cat.gif"
    },
    "comfort_04": {
        "desc": "摸摸贴贴",
        "category": "07_comfort_贴贴安慰",
        "queries": ["cute-cuddle-comfort", "snuggle-cuddle-cute", "warm-blanket-hug"],
        "fallback_url": "https://media.tenor.com/nYyPA3PEBvgAAAAM/funny-animals-cute.gif"
    },
    "comfort_05": {
        "desc": "拍拍安慰",
        "category": "07_comfort_贴贴安慰",
        "queries": ["there-there-pat-cat", "there-there-comfort", "soothing-pat-cat"],
        "fallback_url": "https://media.tenor.com/d7tqdsawh-MAAAAM/tableflip-cat.gif"
    },

    # 08_drama_吃瓜看戏 (5张)
    "drama_01": {
        "desc": "Loopy战术后仰",
        "category": "08_drama_吃瓜看戏",
        "queries": ["loopy-lean-back", "loopy-meme", "loopy-cute"],
        "fallback_url": "https://media.tenor.com/5AEXDy9Q9SQAAAAM/hi-emily-konnichiwa-emily.gif"
    },
    "drama_02": {
        "desc": "搬小板凳嚼爆米花",
        "category": "08_drama_吃瓜看戏",
        "queries": ["eating-popcorn-drama", "popcorn-watching-meme", "eating-popcorn-cute"],
        "fallback_url": "https://media.tenor.com/-QsgQJ2PlmEAAAAM/usagi-chiikawa.gif"
    },
    "drama_03": {
        "desc": "暗中观察坏笑",
        "category": "08_drama_吃瓜看戏",
        "queries": ["peeking-smirk-cat", "peeking-evil-smile", "peeking-cat-smirk"],
        "fallback_url": "https://media.tenor.com/rq_bYUWgOW8AAAAM/hit-that-capybara.gif"
    },
    "drama_04": {
        "desc": "战术喝茶吃瓜",
        "category": "08_drama_吃瓜看戏",
        "queries": ["sipping-tea-meme", "sipping-tea-drama", "tea-gossip-meme"],
        "fallback_url": "https://media.tenor.com/k5IQn-dnFP4AAAAM/seal-dog-black-dog.gif"
    },
    "drama_05": {
        "desc": "拿望远镜暗中观察",
        "category": "08_drama_吃瓜看戏",
        "queries": ["watching-drama-funny", "observing-drama-binocular", "peeking-behind-wall"],
        "fallback_url": "https://media.tenor.com/ff0iUIePpKIAAAAM/usagi-usagi-crying.gif"
    }
}

def search_gif(queries):
    for q in queries:
        url = f"https://tenor.com/search/{urllib.parse.quote(q)}-gifs"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
            gifs = list(set(re.findall(r'https://media\.tenor\.com/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+\.gif', html)))
            if gifs:
                return gifs[0]
        except Exception:
            continue
    return None

def fetch_single(item):
    name, meta = item
    dest_path = os.path.join(STICKERS_DIR, f"{name}.gif")
    
    url = search_gif(meta["queries"])
    if not url:
        url = meta["fallback_url"]
        
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=12).read()
        with open(dest_path, "wb") as f:
            f.write(data)
        size_kb = len(data) / 1024
        print(f"[OK] {name}.gif ({meta['desc']}) - {size_kb:.1f} KB <- {url}")
        return name, True, size_kb
    except Exception as e:
        print(f"[FAIL] {name}.gif ({meta['desc']}) - {e}")
        return name, False, 0

def main():
    os.makedirs(STICKERS_DIR, exist_ok=True)
    print(f"=== 开始下载表情包至 {STICKERS_DIR} ===")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_single, STICKER_DEFINITIONS.items()))
        
    success = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 50)
    print(f"下载完成统计: 成功 {success}/{total} 张，耗时: {elapsed:.2f}s")
    print("=" * 50)
    
    # 统计分类
    categories = {}
    for name, ok, kb in results:
        cat = STICKER_DEFINITIONS[name]["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, ok, kb))
        
    for cat, items in sorted(categories.items()):
        print(f"\n📂 分类: {cat} ({len(items)}张)")
        for n, ok, kb in items:
            status = "✅" if ok else "❌"
            desc = STICKER_DEFINITIONS[n]["desc"]
            print(f"  {status} {n}.gif : {desc} ({kb:.1f} KB)")

if __name__ == "__main__":
    main()
