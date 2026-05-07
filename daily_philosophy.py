import requests
import json
import xml.etree.ElementTree as ET
import random
import os
import time
from dotenv import load_dotenv

# 加载 .env 文件中的私密变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")

def get_sep_entries():
    # 尝试备用地址
    rss_urls = [
        "https://plato.stanford.edu/rss/sep.xml",
        "https://plato.stanford.edu/rss/recent.xml",  # 备用
    ]
    entries = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; DailyPhilosophyBot/1.0)"}

    for rss_url in rss_urls:
        try:
            resp = requests.get(rss_url, headers=headers, timeout=15)
            print(f"URL: {rss_url} | 状态码: {resp.status_code}")

            if resp.status_code != 200:
                continue

            # 打印原始内容，方便调试结构
            print("原始内容前500字：\n", resp.text[:500])

            tree = ET.fromstring(resp.text)

            # 动态检测命名空间，不硬编码
            # Atom feed 的根标签通常是 {http://www.w3.org/2005/Atom}feed
            atom_ns = "http://www.w3.org/2005/Atom"
            ns = {"atom": atom_ns}

            # 兼容 Atom 和 RSS 两种格式
            found = tree.findall(".//atom:entry", ns)

            if not found:
                # 尝试 RSS 2.0 格式（无命名空间）
                found = tree.findall(".//item")
                print(f"RSS 2.0 模式，找到 {len(found)} 个条目")
                for item in found[:5]:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    if title_el is not None and link_el is not None:
                        title = title_el.text or ""
                        link = link_el.text or ""
                        if title and link:
                            entries.append({"title": title.strip(), "link": link.strip()})
            else:
                print(f"Atom 模式，找到 {len(found)} 个条目")
                for entry in found[:5]:
                    title_el = entry.find("atom:title", ns)
                    link_el = entry.find("atom:link", ns)

                    if title_el is None or link_el is None:
                        continue

                    title = title_el.text or ""

                    # link 可能是 href 属性，也可能是文本
                    link = link_el.attrib.get("href") or link_el.text or ""

                    if title and link:
                        entries.append({"title": title.strip(), "link": link.strip()})

            if entries:
                break  # 成功获取就退出循环

        except ET.ParseError as e:
            print(f"XML 解析失败：{e}")
            print("原始响应：", resp.text[:300])
        except Exception as e:
            print(f"获取失败：{type(e).__name__}: {e}")

    return entries

def call_deepseek(entry, retries=2):
    """调用 DeepSeek 生成 SEP 条目导读（含重试）"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
        你是一位同时具有：
        1. 分析哲学训练
        2. 哲学史意识
        3. 哲学教学经验

        的哲学研究者。

        请阅读 Stanford Encyclopedia of Philosophy 条目：
        '{entry['title']}'
        {entry['link']}

        你的任务不是"总结内容"，而是帮助读者理解：
        "这个哲学问题为何会出现，以及它为何重要。"

        请生成一篇 1200-1800 字左右的中文哲学导读。

        【写作结构】
        1. 问题背景（最重要）
        2. 核心思想
        3. 主要争论
        4. 一个具体例子
        5. 开放问题

        【语言要求】
        - 面向哲学系研究生初学者，避免空洞抒情
        - 人名/书名格式：原文（中文），例如 Immanuel Kant（伊曼努尔·康德）

        不要把哲学理论写成"知识点"，而要写成"人类为何不得不思考这个问题"。
    """
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }

    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=300)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API 错误：{resp.status_code} {resp.text}")
                return None
        except requests.exceptions.Timeout:
            print(f"第 {attempt + 1} 次请求超时，{'重试中……' if attempt < retries else '放弃。'}")
            if attempt < retries:
                time.sleep(5)

    return None

def send_to_feishu(title, summary, link):
    """发送消息卡片到你的飞书群"""
    msg = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "☕ 今日 SEP"}},
            "elements": [{
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{title}**\n\n{summary}\n\n[📖 阅读原文]({link})"
                }
            }]
        }
    }
    return requests.post(FEISHU_WEBHOOK_URL, json=msg).json()

if __name__ == "__main__":
    print("开始今天的哲学推送……")
    entries = get_sep_entries()
    if not entries:
        print("没有获取到 SEP 条目。")
        exit()
    chosen = random.choice(entries)
    print(f"选中：{chosen['title']}")
    summary = call_deepseek(chosen)
    if summary:
        print("AI 摘要生成成功，正在发送到飞书……")
        print(send_to_feishu(chosen["title"], summary, chosen["link"]))
    else:
        print("摘要生成失败，跳过今日推送。")
