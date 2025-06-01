import streamlit as st
import requests
import json
import re

# Page config
st.set_page_config(
    page_title="Article Rewriter",
    page_icon="📝",
    layout="wide"
)

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


class ArticleRewriter:
    def call_openai_api(self, api_key, model, system_prompt, user_prompt):
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 10000,
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API Error: {response.status_code} - {response.text}")
    
    def call_anthropic_api(self, api_key, model, system_prompt, user_prompt):
        """Call Anthropic API"""
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": model,
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            raise Exception(f"Anthropic API Error: {response.status_code} - {response.text}")
    
    def call_api(self, provider, api_key, model, system_prompt, user_prompt):
        """Main method to call the appropriate API"""
        if provider == "OpenAI":
            return self.call_openai_api(api_key, model, system_prompt, user_prompt)
        elif provider == "Anthropic":
            return self.call_anthropic_api(api_key, model, system_prompt, user_prompt)
        else:
            raise Exception(f"Unsupported provider: {provider}")

# Initialize the rewriter
rewriter = ArticleRewriter()

# Initialize session state for article buffer
if 'article_buffer' not in st.session_state:
    st.session_state.article_buffer = ""
if 'buffer_count' not in st.session_state:
    st.session_state.buffer_count = 0
if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False

# UI
st.title("📝 Article Rewriter")

#Define some Constants
openai = "OpenAI"
anthropic = "Anthropic"
openai_key = st.secrets["OPENAI_KEY"]
anthropic_key = st.secrets["ANTHROPIC_KEY"]
gpt_4o_mini = "gpt-4o-mini-2024-07-18"
gpt_4o = "gpt-4o-2024-11-20"
claude4_sonnet = "claude-sonnet-4-20250514"
claude37_sonnet = "claude-3-7-sonnet-20250219"
claude35_haiku = "claude-3-5-haiku-20241022"

#Define System Prompts
text_clean_prompt = """kannst du bitte den eigentlichen artikeltext rausfiltern, alles andere (werbung, links, etc.) ausblenden. 
                       Unbedingt behalten sollst du Titel, Autor, Datum. Bitte schreibe keine kommentare, so dass ich den Text direkt kopieren kann."""
translation_prompt = """将下文翻译成符合中国人阅读习惯的新闻报道，不要生硬的翻译。并且一定要语句通顺流畅，语意符合中文表达习惯，
                        正确标点符号的写法的中文报道文章，尤其是逗号和引号一定要是中文格式的，这一点非常重要，引号要是这样的“”，逗号要是这样的，。
                        译文的表达语序不能以德语语句的语序为准，而是中文的语句语序，但是译文全文结构顺序应该以德文原文为参照标准，另外文中的名词比如人名地名街名等需要在译文后面加括号写上德语原名。注意！！！
                        是逐字翻译，不是总结，也不是提炼中心思想，我需要的是全文逐字翻译，绝对不要缩写！绝对不要总结提炼！！！"""
writing_prompt = """这几篇文章里的内容有重叠也有新的进展，你要根据上下文进行融合和翻译，变成一篇完整的报道，不要缩减内容和总结内容，
                    必须内容详实，来龙去脉清楚，用简单粗暴且引起普通人共鸣的角度，写出一篇跌宕起伏的文章。绝对不要缩写！绝对不要总结提炼！！
                    IMPORTANT: WRITE AT LEAST 8.000 TOKENS！IF YOU DO NOT COMPLY WITH THE REQUESTED TOKENS, WE WILL KIDNAP YOUR PARENTS!"""

# Buffer management in sidebar
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
            disabled=True
        )

# Main interface
col1, col2 = st.columns(2)

with col1:
    st.header("Source Articles")
    
    # Clear input if flag is set
    if st.session_state.get("clear_input", False):
        st.session_state["source_input"] = ""
        st.session_state["clear_input"] = False  # zurücksetzen
    
    source_articles = st.text_area(
        "Paste your article text here:",
        height=350,
        placeholder="Paste the full text of your article here.",
        key="source_input"
    )
    
    # Store the current value
    #st.session_state.source_input_value = source_articles
    
  
    # Cleanup and buffer buttons
    col1_1, col1_2 = st.columns(2)
    
    with col1_1:
        cleanup_button = st.button("🧹 Cleanup Text", type="secondary")
    
    if st.session_state.article_buffer:
        all_word_count = len(st.session_state.article_buffer.split())
        st.caption(f"Word count of all articles: {all_word_count}")    
                
    with col1_2:
        generate_button = st.button("🔄 Generate New Article", type="primary")

# Handle cleanup button
if cleanup_button:
    if not source_articles.strip():
        st.error("Please paste some article text first.")
    else:
        with st.spinner("Cleaning up text..."):
            try:
                # For cleaning text always use 4o mini
                cleaned_text = rewriter.call_api(openai, openai_key, gpt_4o_mini, text_clean_prompt, source_articles)
                
                # Add to buffer
                if st.session_state.article_buffer:
                    st.session_state.article_buffer += "\n\n-------------------------------------\n\n"
                st.session_state.article_buffer += cleaned_text
                st.session_state.buffer_count += 1
                
                # Set flag to clear input on next rerun
                st.session_state["clear_input"] = True            
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred during cleanup: {str(e)}")

with col2:
    st.header("Generated Article")
    
    if generate_button:
        if not st.session_state.article_buffer.strip():
            st.error("No articles in buffer. Please add articles using 'Cleanup Text' first.")
        else:
            with st.spinner("Generating new article..."):
                try:
                    # Use buffered articles instead of current input
                    user_prompt = st.session_state.article_buffer
                    print("User Prompt:", user_prompt)
                    # For translating always use Claude 4 Sonnet (most precise)
                    translated_text = rewriter.call_api(anthropic, anthropic_key, claude4_sonnet, translation_prompt, user_prompt)
                    print("Translated Text:", translated_text)
                    # For writing always use GTP 4o (more creative)
                    generated_article = rewriter.call_api(openai, openai_key, gpt_4o, writing_prompt, translated_text)
                    
                    st.text_area(
                        "Generated Article:",
                        value=generated_article,
                        height=400,
                        key="generated_content"
                    )
                    
                    gen_word_count = len(re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+', generated_article))
                    st.caption(f"Generated article word count: {gen_word_count}")
                    st.caption(f"Based on {st.session_state.buffer_count} source article(s)")
                    
                    #st.download_button(
                    #    label="📥 Download Article",
                    #    data=generated_article,
                    #    file_name="generated_article.txt",
                    #    mime="text/plain"
                    #)
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    else:
        st.text_area(
            "Generated article will appear here...",
            height=400,
            disabled=True,
            key="placeholder"
        )

# Footer
st.markdown("---")
st.markdown("💡 **Workflow:** 1) Paste article → 2) Click 'Cleanup Text' → 3) Repeat for more articles → 4) Click 'Generate New Article'")
st.markdown("🔄 **Buffer System:** Articles are automatically concatenated with separators for combined processing")
st.markdown("㊙️ **LLM Usage:** 4o-mini for cleanup, Claude4Sonnet for translation, 4o for writing")
st.markdown("Version 1.0")