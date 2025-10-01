import re
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from log import SupabaseLogger

from rewriter.api import ArticleRewriter


st.set_page_config(page_title="Article Rewriter", page_icon="📝", layout="wide")

# Simple password protection
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    password = st.text_input("Password", type="password")
    if password:
        if password == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Password incorrect")
    st.stop()


rewriter = ArticleRewriter()
logger = SupabaseLogger()

# Buffer state
if "article_buffer" not in st.session_state:
    st.session_state.article_buffer = ""
if "buffer_count" not in st.session_state:
    st.session_state.buffer_count = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# Constants
openai = "OpenAI"
anthropic = "Anthropic"
openai_key = st.secrets["OPENAI_KEY"]
anthropic_key = st.secrets["ANTHROPIC_KEY"]
gpt_4o_mini = "gpt-4o-mini-2024-07-18"
gpt_4o = "gpt-4o-2024-11-20"
gpt_5 = "gpt-5-2025-08-07"
claude45_sonnet = "claude-sonnet-4-5-20250929"
claude4_sonnet = "claude-sonnet-4-20250514"
claude37_sonnet = "claude-3-7-sonnet-20250219"
claude35_haiku = "claude-3-5-haiku-20241022"

# System prompts
text_clean_prompt = (
    "kannst du bitte den eigentlichen artikeltext rausfiltern, alles andere (werbung, links, etc.) ausblenden."
    " Unverändert übernehmen sollst du auch Titel, Autor, Datum. Schreibe keine Kommentare, so dass ich den Text direkt kopieren kann."
)
translation_prompt = (
    "将下文翻译成符合中国人阅读习惯的新闻报道，不要生硬的翻译。并且一定要语句通顺流畅，语意符合中文表达习惯，"
    " 正确标点符号的写法的中文报道文章，尤其是逗号和引号一定要是中文格式的，这一点非常重要，引号要是这样的""，逗号要是这样的，。"
    " 译文的表达语序不能以德语语句的语序为准，而是中文的语句语序，但是译文全文结构顺序应该以德文原文为参照标准，另外文中的名词比如人名地名街名等需要在译文后面加括号写上德语原名。注意！！！"
    " 是逐字翻译，不是总结，也不是提炼中心思想，我需要的是全文逐字翻译，绝对不要缩写！绝对不要总结提炼！！！"
)

# Writing prompts - conditional based on buffer count
single_article_writing_prompt = (
    "这篇文章里是完全遵照德语原文翻译的文章，现在我需要你按照中文新闻报道的习惯，详细报道一篇内容详实，有清晰的来龙去脉的文章。"
    "这是一篇需要尽量还原原文，但是更中国本土化的新闻稿件，字数应该跟给你的译文的字数差不多，语句通顺流畅，有一定的戏剧性，文章结构应该以引人好奇，扣人心弦为目的。"
)

multiple_articles_writing_prompt = (
    f"这{st.session_state.buffer_count}篇文章里的内容有重叠也有新的进展，你要根据上下文进行融合和翻译，变成一篇完整的报道，不要缩减内容和总结内容，"
    " 必须内容详实，来龙去脉清楚，用简单粗暴且引起普通人共鸣的角度，写出一篇跌宕起伏的文章。绝对不要缩写！绝对不要总结提炼！！"
    " IMPORTANT: WRITE AT LEAST 8.000 TOKENS！IF YOU DO NOT COMPLY WITH THE REQUESTED TOKENS, WE WILL KIDNAP YOUR PARENTS!"
)


st.title("📝 Article Rewriter")

st.sidebar.header("Article Buffer")
st.sidebar.info(f"Articles in buffer: {st.session_state.buffer_count}")

if st.sidebar.button("🗑️ Clear Buffer"):
    st.session_state.article_buffer = ""
    st.session_state.buffer_count = 0
    st.sidebar.success("Buffer cleared!")
    st.rerun()

if st.session_state.buffer_count > 0:
    if st.sidebar.button("👁️ Show Buffer"):
        st.sidebar.text_area(
            "Current Buffer Content:",
            value=st.session_state.article_buffer,
            height=200,
            disabled=True,
        )


col1, col2 = st.columns(2)

with col1:
    st.header("Source Articles")

    if st.session_state.get("clear_input", False):
        st.session_state["source_input"] = ""
        st.session_state["clear_input"] = False

    source_articles = st.text_area(
        "Paste your article text here:",
        height=350,
        placeholder="Paste the full text of your article here.",
        key="source_input",
    )

    col1_1, col1_2 = st.columns(2)

    with col1_1:
        cleanup_button = st.button("🧹 Cleanup Text", type="secondary")

    if st.session_state.article_buffer:
        all_word_count = len(st.session_state.article_buffer.split())
        st.caption(f"Word count of all articles: {all_word_count}")

    with col1_2:
        generate_button = st.button("🔄 Generate New Article", type="primary")

if cleanup_button:
    if not source_articles.strip():
        st.error("Please paste some article text first.")
    else:
        with st.spinner("Cleaning up text..."):
            try:
                cleaned_text = rewriter.call_api(
                    openai, openai_key, gpt_4o_mini, text_clean_prompt, source_articles
                )

                if st.session_state.article_buffer:
                    st.session_state.article_buffer += "\n\n------------------------------\n\n"
                st.session_state.article_buffer += cleaned_text
                st.session_state.buffer_count += 1

                st.session_state["clear_input"] = True
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred during cleanup: {e}")

with col2:
    st.header("Generated Article")

    if generate_button:
        if not st.session_state.article_buffer.strip():
            st.error("No articles in buffer. Please add articles using 'Cleanup Text' first.")
        else:
            with st.spinner("Generating new article..."):
                try:
                    user_prompt = st.session_state.article_buffer
                    translated_text = rewriter.call_api(
                        anthropic, anthropic_key, claude4_sonnet, translation_prompt, user_prompt
                    )
                    
                    # Choose writing prompt based on buffer count
                    if st.session_state.buffer_count == 1:
                        writing_prompt = single_article_writing_prompt
                    else:
                        writing_prompt = multiple_articles_writing_prompt
                    
                    generated_article = rewriter.call_api(
                        openai, openai_key, gpt_4o, writing_prompt, translated_text
                    )

                    timestamp = datetime.now(ZoneInfo("Europe/Berlin")).isoformat()
                    log_data = {
                        "user_prompt": user_prompt,
                        "translated_text": translated_text,
                        "writing_prompt": writing_prompt,
                        "generated_article": generated_article,
                        "timestamp": timestamp,
                    }
                    logger.log(log_data)
    
                    st.text_area(
                        "Generated Article:",
                        value=generated_article,
                        height=400,
                        key="generated_content",
                    )

                    gen_word_count = len(re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", generated_article))
                    st.caption(f"Generated article word count: {gen_word_count}")
                    st.caption(f"Based on {st.session_state.buffer_count} source article(s)")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        st.text_area(
            "Generated article will appear here...",
            height=400,
            disabled=True,
            key="placeholder",
        )

st.markdown("---")
st.markdown("💡 **Workflow:** 1) Paste article → 2) Click 'Cleanup Text' → 3) Repeat for more articles → 4) Click 'Generate New Article'")
st.markdown("🔄 **Buffer System:** Articles are automatically concatenated with separators for combined processing")
st.markdown("㊙️ **LLM Usage:** 4o-mini for cleanup, Claude4Sonnet for translation, 4o for writing")
#don't remove this:
st.markdown("Version 1.1")
