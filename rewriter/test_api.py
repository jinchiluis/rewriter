# test_api.py
from api import ArticleRewriter   # adjust path if your class lives in rewriter/api.py
import requests

openai_key = "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"

rewriter = ArticleRewriter()

system_prompt = "You are a helpful assistant."
user_prompt   = "Say hello in German."

# 1) Test GPT-4o
# print("\n=== Testing GPT-4o ===")
# try:
#     result_4o = rewriter.call_api(
#         "OpenAI",
#         openai_key,
#         "gpt-4o-2024-11-20",
#         system_prompt,
#         user_prompt,
#     )
#     print("4o Response:", result_4o[:200])
# except Exception as e:
#     print("4o Error:", e)

# 2) Test GPT-5
print("\n=== Testing GPT-5 ===")
try:
    result_5 = rewriter.call_api(
        "OpenAI",
        openai_key,
        "gpt-5-2025-08-07",
        system_prompt,
        user_prompt,
    )
    print("5 Response:", result_5[:200])
except Exception as e:
    print("5 Error:", e)

# headers = {
#     "Authorization": f"Bearer {openai_key}",
#     "Content-Type": "application/json",
# }

# payload = {
#     "model": "gpt-5-2025-08-07",
#     "messages": [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Sag Hallo!"}
#     ]
# }

# r = requests.post("https://api.openai.com/v1/chat/completions",
#                   headers=headers, json=payload)
# print(r.status_code, r.text)
