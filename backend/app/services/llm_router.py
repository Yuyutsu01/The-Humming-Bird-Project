# Resilient Multi-Tier LLM Router & Fallback Engine
import logging
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ResilientLLMRouter:
    """
    Multi-Tier AI Resilience Router for EIOS.
    Orchestrates automatic fallback across four distinct intelligence providers:
      Tier 1: Google Gemini Pro API
      Tier 2: OpenAI GPT-4 API
      Tier 3: Local Ollama LLM (Llama 3.2 on localhost:11434)
      Tier 4: Offline Rule-Based Semantic Engine (Deterministic Fallback)
    """
    
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_url = getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.ollama_model = getattr(settings, "OLLAMA_MODEL", "llama3.2:latest")
        self.use_ollama = getattr(settings, "USE_OLLAMA", True)

    async def query(self, prompt: str) -> Dict[str, Any]:
        """
        Executes multi-tier LLM query with sequential fallback.
        """
        # Tier 1: Try Google Gemini API
        if self.gemini_key:
            try:
                res = await self._query_gemini(prompt)
                if res:
                    logger.info("[LLMRouter] Successfully received response from Tier 1 (Gemini Pro).")
                    return {"text": res, "tier_used": 1, "provider": "Google Gemini", "model": "gemini-pro"}
            except Exception as e:
                logger.warning(f"[LLMRouter] Tier 1 (Gemini) failed: {e}. Falling back to Tier 2...")

        # Tier 2: Try OpenAI GPT-4 API
        if self.openai_key:
            try:
                res = await self._query_openai(prompt)
                if res:
                    logger.info("[LLMRouter] Successfully received response from Tier 2 (OpenAI GPT-4).")
                    return {"text": res, "tier_used": 2, "provider": "OpenAI", "model": "gpt-4"}
            except Exception as e:
                logger.warning(f"[LLMRouter] Tier 2 (OpenAI) failed: {e}. Falling back to Tier 3...")

        # Tier 3: Try Local Ollama LLM
        if self.use_ollama:
            try:
                res = await self._query_ollama(prompt)
                if res:
                    logger.info("[LLMRouter] Successfully received response from Tier 3 (Local Ollama).")
                    return {"text": res, "tier_used": 3, "provider": "Ollama Local", "model": self.ollama_model}
            except Exception as e:
                logger.warning(f"[LLMRouter] Tier 3 (Ollama) failed: {e}. Falling back to Tier 4...")

        # Tier 4: Offline Rule-Based Semantic Fallback Engine
        logger.info("[LLMRouter] Executing Tier 4 (Offline Rule-Based Semantic Engine).")
        res_text = self._semantic_fallback(prompt)
        return {"text": res_text, "tier_used": 4, "provider": "Offline Semantic Engine", "model": "rule-v4"}

    async def _query_gemini(self, prompt: str) -> Optional[str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    async def _query_openai(self, prompt: str) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    async def _query_ollama(self, prompt: str) -> Optional[str]:
        try:
            url = f"{self.ollama_url}/api/generate"
            data = json.dumps({
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=3) as resp:
                result = json.loads(resp.read().decode())
                return result.get("response")
        except Exception as e:
            raise RuntimeError(f"Ollama local error: {e}")

    def _semantic_fallback(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "gold" in prompt_lower:
            return (
                "Gold prices are surging globally due to declining US dollar index (DXY) strength "
                "and heightened central bank accumulation. For India, this expands the import bill "
                "and pressures domestic Rupee exchange rates while boosting LTV ratios for gold loan NBFCs."
            )
        elif "oil" in prompt_lower or "brent" in prompt_lower:
            return (
                "Brent Crude oil spikes act as a direct import tax on India's economy, expanding the current "
                "account deficit, raising logistics input costs, and constraining RBI monetary policy easing."
            )
        else:
            return (
                "Macroeconomic transmission analysis indicates that global interest rate differentials and "
                "commodity price shifts propagate into domestic Indian equity markets, inflation metrics, and yields."
            )

# Instantiate singleton router
llm_router = ResilientLLMRouter()
