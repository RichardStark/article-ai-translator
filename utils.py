from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests
from markdown_it import MarkdownIt

JINA_READER_BASE = "https://r.jina.ai/"


class FetchMarkdownError(Exception):
    """Jina Reader 抓取失败。"""


def fetch_markdown_from_url(url: str, timeout: int = 20) -> str:
    """
    使用 Jina Reader 获取目标 URL 的 Markdown。

    Args:
        url: 目标网页 URL。
        timeout: 请求超时时间（秒）。

    Returns:
        Markdown 字符串。

    Raises:
        FetchMarkdownError: 网络错误或非 200 响应。
    """
    try:
        resp = requests.get(f"{JINA_READER_BASE}{url}", timeout=timeout)
    except requests.RequestException as exc:
        raise FetchMarkdownError(f"请求 Jina 失败: {exc}") from exc

    if resp.status_code != 200:
        raise FetchMarkdownError(f"Jina 返回非 200 状态码: {resp.status_code}")

    return resp.text


def protect_code_blocks(markdown: str) -> Tuple[str, Dict[str, str]]:
    """
    提取 Markdown 中的代码块并替换为占位符，返回占位后的文本和代码映射。

    占位符形式：__CODE_BLOCK_{idx}__
    """
    md = MarkdownIt()
    tokens = md.parse(markdown)
    lines: List[str] = markdown.splitlines(keepends=True)

    # 预计算每行起始字符偏移，便于将行号映射到字符串索引。
    offsets: List[int] = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    code_blocks: Dict[str, str] = {}
    ranges: List[Tuple[int, int, str]] = []  # (start_idx, end_idx, placeholder)

    for idx, token in enumerate(tokens):
        if token.type != "fence" or token.map is None:
            continue
        start_line, end_line = token.map
        start_idx = offsets[start_line]
        end_idx = offsets[end_line]
        placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"

        # 保存完整的原始 fenced block（包含 ``` 和语言标记）。
        info = token.info.strip() if token.info else ""
        fenced_block = f"{token.markup}{info and ' ' + info}\n{token.content}{token.markup}\n"
        code_blocks[placeholder] = fenced_block
        ranges.append((start_idx, end_idx, placeholder))

    if not ranges:
        return markdown, code_blocks

    # 按起始位置排序，构建占位后的文本。
    ranges.sort(key=lambda item: item[0])
    result_parts: List[str] = []
    cursor = 0
    for start_idx, end_idx, placeholder in ranges:
        result_parts.append(markdown[cursor:start_idx])
        result_parts.append(placeholder)
        cursor = end_idx
    result_parts.append(markdown[cursor:])

    protected_markdown = "".join(result_parts)
    return protected_markdown, code_blocks


def generate_filename_from_url(url: str, suffix: str = "") -> str:
    """
    从 URL 中提取 slug 或使用时间戳生成文件名。

    Args:
        url: 目标网页 URL。
        suffix: 文件名后缀（如 "_original" 或 "_translated"）。

    Returns:
        生成的文件名（不含扩展名）。
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if path:
            # 提取路径的最后一部分作为 slug
            slug = path.split("/")[-1]
            # 移除文件扩展名（如果有）
            if "." in slug:
                slug = slug.rsplit(".", 1)[0]
            # 清理 slug：只保留字母、数字、连字符和下划线
            slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in slug)
            if slug:
                return f"{slug}{suffix}"
    except Exception:
        pass

    # 如果无法从 URL 提取，使用时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"article_{timestamp}{suffix}"

