"""Inbox commands"""

import click
import os
import re
import subprocess
from datetime import datetime


def extract_urls(text):
    """从文本中提取 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def parse_url_with_claude(url, user_note):
    """调用 Claude CLI 解析 URL 内容"""
    prompt = f"""请访问并解析以下链接的内容，提取：标题、正文要点、代码块（如有）。
以结构化 Markdown 格式输出。

链接：{url}
用户备注：{user_note}

请提取并总结内容。"""

    try:
        model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
        result = subprocess.run(
            ["claude", "-p", prompt,
             "--permission-mode", "acceptEdits",
             "--allowedTools", "WebFetch",
             "--effort", "medium",
             "--model", model],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except (OSError, subprocess.CalledProcessError):
        return None


def generate_inbox_filename(content):
    """生成 inbox 文件名: YYYYMMDD_HHMMSS_标题_inbox.md"""
    # 提取前50字符作为标题
    title = content[:50].replace("\n", " ").replace("#", "").replace("/", "_").strip()
    if len(content) > 50:
        title = title[:47] + "..."
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S") + "_" + title + "_inbox.md"


def inbox_add(content, parse):
    """Capture content to inbox"""
    if not content or not content.strip():
        click.echo("Error: 内容不能为空", err=True)
        return

    # 确定 50_Raw/inbox 路径
    inbox_dir = os.path.expanduser("~/.pkm/50_Raw/inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    # 处理 --parse 模式
    final_content = content
    if parse:
        urls = extract_urls(content)
        if urls:
            # 只解析第一个 URL
            url = urls[0]
            user_note = content.replace(url, "").strip()
            parsed_content = parse_url_with_claude(url, user_note)
            if parsed_content:
                final_content = f"{content}\n\n## AI 解析结果\n\n{parsed_content}"
            else:
                click.echo("Warning: URL 解析失败，只保存用户输入", err=True)

    # 生成文件名
    filename = generate_inbox_filename(final_content)
    filepath = os.path.join(inbox_dir, filename)

    # 写入文件
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_content)
    except IOError as e:
        click.echo(f"Error: 无法写入文件: {e}", err=True)
        return

    click.echo(f"Captured to inbox: {filename}")
