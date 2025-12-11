import streamlit as st

from translator import translate_article
from utils import fetch_markdown_from_url, generate_filename_from_url, protect_code_blocks


def main() -> None:
    st.set_page_config(page_title="Web Article AI Translator", layout="wide")
    st.title("Web Article AI Translator")
    st.write("输入文章链接，提取 Markdown 并翻译（代码块将被保护）。")

    url = st.text_input("文章 URL")
    if st.button("获取并预处理") and url:
        # 保存 URL 到 session_state，用于生成文件名
        st.session_state["url"] = url
        with st.spinner("正在抓取并预处理 Markdown ..."):
            markdown = fetch_markdown_from_url(url)
            protected_md, code_blocks = protect_code_blocks(markdown)

        st.subheader("原始 Markdown")
        st.markdown(markdown, unsafe_allow_html=False)

        st.subheader("占位后的 Markdown（用于送入 LLM）")
        st.markdown(protected_md, unsafe_allow_html=False)

        st.session_state["original_markdown"] = markdown
        st.session_state["protected_markdown"] = protected_md
        st.session_state["code_blocks"] = code_blocks

    if st.button("调用 LLM 翻译") and st.session_state.get("protected_markdown"):
        with st.spinner("正在请求 LLM 翻译 ..."):
            translated = translate_article(
                st.session_state["protected_markdown"],
                st.session_state["code_blocks"],
            )

        st.subheader("翻译结果")
        st.markdown(translated, unsafe_allow_html=False)

        # 保存翻译结果到 session_state
        st.session_state["translated_markdown"] = translated

    # 显示下载按钮（仅在翻译完成且内容不为空时）
    if st.session_state.get("translated_markdown") and st.session_state.get("original_markdown"):
        st.divider()
        st.subheader("下载")
        
        # 生成文件名
        url = st.session_state.get("url", "")
        base_filename = generate_filename_from_url(url) if url else "article"
        
        col1, col2 = st.columns(2)
        
        with col1:
            original_filename = f"{base_filename}_original.md"
            st.download_button(
                label="📥 下载原文 Markdown",
                data=st.session_state["original_markdown"],
                file_name=original_filename,
                mime="text/markdown",
                help="下载原始 Markdown 文件（UTF-8 编码）",
            )
        
        with col2:
            translated_filename = f"{base_filename}_translated.md"
            st.download_button(
                label="📥 下载翻译后的 Markdown",
                data=st.session_state["translated_markdown"],
                file_name=translated_filename,
                mime="text/markdown",
                help="下载翻译后的 Markdown 文件（UTF-8 编码）",
            )


if __name__ == "__main__":
    main()

