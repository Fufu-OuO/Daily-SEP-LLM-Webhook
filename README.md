<!-- markdownlint-disable MD033 MD041 -->
<div align="center">
  <img alt="LOGO" src="./assets/images/logo/DailySEP.png" width="256" height="256" /><br>
logo 由 ChatGPT 生成<br>
<h1>DailySEP</h1>
</div>

1. 自动抓取斯坦福哲学百科（SEP）的最新文章，<br>
2. 通过 DeepSeek 生成中文摘要，<br>
3. 通过飞书自定义机器人推送到飞书群聊。


## 目录

- [**功能**](#功能)
- [**快速开始**](#快速开始)
  - [1. Fork 并克隆项目](#1-fork-并克隆项目)
  - [2. （推荐！）配置 GitHub Secrets](#2-（推荐！）配置-github-secrets)
  - [3. 本地配置](#3-本地配置)
  - [4. 手动测试](#4-手动测试)
- [**默认推送时间**](#默认推送时间)
- [**自定义修改**](#自定义修改)
  - [更换 AI 模型](#更换-ai-模型)
  - [更换知识来源](#更换知识来源)
  - [调整推送时间](#调整推送时间)
- [**常见问题**](#常见问题)
- [**鸣谢**](#鸣谢)

## 功能

- **抓取 SEP 条目**：自动从 SEP 官网获取最新更新的哲学条目。
- **AI 导读**：调用 DeepSeek，将条目嚼成约1000字的核心摘要。
- **飞书推送**：默认于每天早上 7:00 推送到飞书群聊。
- **全自动运行**：支持基于 GitHub Actions 的设置。


## 快速开始

> **准备工作**：GitHub 账号、飞书群聊、DeepSeek API。

### 1. Fork 并克隆项目
1. 点击本仓库右上角的 **Fork**，将项目复制到你的 GitHub 账户下。  
2. 在仓库页面点击 **Code** → 复制仓库地址，本地克隆：

```bash
git clone https://github.com/YOUR_NAME/DailySEP.git
cd DailySEP
```

### 2.（推荐！）配置 GitHub Secrets
1. 在 Fork 后的 GitHub 仓库首页，点击 Settings 选项卡。
2. 左侧菜单选择 Secrets and variables → Actions。
3. 点击 New repository secret，分别添加以下两个密钥：
  - DEEPSEEK_API_KEY → 粘贴你的 DeepSeek API Key。
  - FEISHU_WEBHOOK_URL → 粘贴你的飞书 Webhook 完整地址。
### 3. 本地配置
如选择本地配置，请自行创建 `.env` 文件，内容如下：
```
DEEPSEEK_API_KEY=sk-你的 DeepSeek-API-Key
FEISHU_WEBHOOK_URL=你的飞书 Webhook 地址
```
⚠️请务必自行保管好 `.env` 文件，如需上传，请确认 `.gitignore` 中包含 `.env` ！！！⚠️

### 4. 手动测试
1. 在仓库首页点击 Actions 选项卡。
2. 点击左侧的 Daily Philosophy Card 工作流。
3. 点击右侧 Run workflow → Run workflow，手动触发一次。
4. 耐心等待运行完毕 → 点击该次运行记录 → 查看日志是否成功。
5. 检查飞书群聊，如果顺利，应该已经收到一条机器人消息。

## 自定义修改
### 修改默认推送时间
- 工作流默认设置为每日 UTC 23:00（北京时间早上 7:00）执行；
- 可以通过修改 `.github/workflows/send.yml` 中的 `cron` 表达式来调整时间。
### 更换 AI 模型
- 编辑 `daily_philosophy.py`，将 `model` 字段改为其他模型。
### 更换条目来源
- 脚本默认使用 SEP 的 RSS 获取条目——如果你想换成其他来源的条目，请修改 `get_sep_entries` 函数；
- 同理，可以将 SEP 替换成任意内容来源——只要你可以从 `get_sep_entries` 里头获取内容。
