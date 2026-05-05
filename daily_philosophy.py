import requests
import json
import xml.etree.ElementTree as ET
import random
import os
from dotenv import load_dotenv

# 加载 .env 文件中的私密变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")

def get_sep_entries():
    """随机抓取一篇最新的 SEP 条目并返回"""
    rss_url = "https://plato.stanford.edu/rss/sep.xml"
    entries = []
    try:
        resp = requests.get(rss_url, timeout=15)
        tree = ET.fromstring(resp.text)
        ns = {"rss": "http://www.w3.org/2005/Atom"}
        for entry in tree.findall(".//rss:entry", ns)[:5]:
            title = entry.find("rss:title", ns).text
            link = entry.find("rss:link", ns).attrib["href"]
            entries.append({"title": title, "link": link})
    except Exception as e:
        print(f"获取 SEP 条目失败：{e}")
    return entries

def call_deepseek(entry):
    """调用 DeepSeek 生成 SEP 条目导读"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    你是一位哲学科普作者。请阅读斯坦福哲学百科的条目 '{entry['title']}' ({entry['link']})，并用中文生成一篇 500 字内的核心摘要。结构分三段：
    1. 一句话点出这个理论的核心命题或争议。
    2. 用哲学系研究生能听懂的话，解释这个理论的主要发展史、主要人物及著作、在现当代哲学中的重要性。
    3. 举一个合适的例子，说明这个哲学概念如何被验证或质疑。
    4. 最后，提出一个引人深思的问题，让读者自行探索。
    请确保引用的观点忠于原文。
    """
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        print(f"DeepSeek API 错误：{resp.status_code} {resp.text}")
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