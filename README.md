# Web Article AI Translator (MVP)

基于 Streamlit 的网页文章翻译工具：输入 URL，调用 Jina Reader 提取 Markdown，保护代码块后将正文翻译为中文，并支持下载原文与译文。

## 功能特性
- 一键获取网页 Markdown（通过 `https://r.jina.ai/<url>`，无需自建爬虫）
- 解析并保护 fenced code blocks，避免代码被翻译
- LLM 翻译（OpenAI 兼容接口，可配置 base_url 和 model）
- 翻译后自动回填代码块
- 支持下载原文/译文 Markdown，文件名自动从 URL slug 或时间戳生成

## 目录结构
```
app.py              # Streamlit UI
translator.py       # LLM 调用与回填
utils.py            # Jina 获取、代码块保护、文件名生成
requirements.txt
.streamlit/secrets.toml (本地配置，不纳入版本控制)
```

## 快速开始
1) 创建虚拟环境并安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) 配置密钥（在本地创建 `.streamlit/secrets.toml`，仓库已忽略）
```toml
OPENAI_API_KEY = "sk-xxxx"
OPENAI_BASE_URL = "https://api.openai.com/v1"   # 或其他兼容网关
OPENAI_MODEL = "gpt-4o-mini"
```

3) 运行
```bash
streamlit run app.py
```

4) 使用步骤
- 输入文章 URL，点击“获取并预处理”
- 检查“占位后的 Markdown”确认代码块被替换为 `__CODE_BLOCK_x__`
- 点击“调用 LLM 翻译”
- 完成后可在底部下载“原文 Markdown”和“翻译后的 Markdown”

## 设计要点
- 遵循流水线：Fetch → Protect → Translate → Reassemble → Render
- 代码块保护使用 `markdown-it-py` 解析 fenced blocks，避免正则误伤
- 文件名生成：优先取 URL slug；失败则使用时间戳，避免覆盖
- 所有 API 密钥通过 `st.secrets` 读取，严禁硬编码

## 常见问题
- 若 Jina Reader 访问失败，会抛出 `FetchMarkdownError`；请检查网络或稍后重试
- 如 LLM 返回为空或出错，UI 会保留原始内容，可重新尝试

## 开发提示
- 需要切换模型/网关时，只改 `.streamlit/secrets.toml`
- 若要双栏展示原文/译文，可在 `app.py` 中添加 `st.columns`

