class ArticleRewriter:
    """Utility class for calling LLM APIs."""

    def call_openai_api(self, api_key, model, system_prompt, user_prompt):
        """Call the OpenAI chat completions API."""
        import requests

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 10000,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def call_anthropic_api(self, api_key, model, system_prompt, user_prompt):
        """Call the Anthropic messages API."""
        import requests

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": model,
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        response = requests.post(
            "https://api.anthropic.com/v1/messages", headers=headers, json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["content"][0]["text"]

    def call_api(self, provider, api_key, model, system_prompt, user_prompt):
        """Dispatch method for the chosen provider."""
        if provider == "OpenAI":
            return self.call_openai_api(api_key, model, system_prompt, user_prompt)
        if provider == "Anthropic":
            return self.call_anthropic_api(api_key, model, system_prompt, user_prompt)
        raise ValueError(f"Unsupported provider: {provider}")
