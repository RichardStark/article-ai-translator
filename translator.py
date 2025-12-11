from typing import Dict

import streamlit as st
from openai import OpenAI


SYSTEM_PROMPT = (
    "你是资深技术翻译。请将输入 Markdown 翻译为中文："
    "保持 Markdown 结构；保留占位符原样；不要翻译代码、变量名、占位符或技术栈专有名词。"
)


def translate_article(markdown_with_placeholders: str, code_blocks: Dict[str, str]) -> str:
    """
    调用 OpenAI 兼容接口翻译文本，并将占位符替换回原始代码块。
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or None
    base_url = st.secrets.get("OPENAI_BASE_URL") or None
    model = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY 配置")

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": markdown_with_placeholders},
        ],
    )
    translated = response.choices[0].message.content or ""
    for placeholder, code in code_blocks.items():
        translated = translated.replace(placeholder, code)
    return translated

