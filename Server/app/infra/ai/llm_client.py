import asyncio
import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, InfrastructureError


class LLMClient:
    """Backend-owned large language model client."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> dict:
        provider = self.settings.llm_provider.strip().lower()
        if provider != "zhipu":
            raise BadRequestError(message=f"Unsupported LLM provider: {self.settings.llm_provider}.")

        api_key = self.settings.llm_api_key.strip()
        if not api_key:
            raise InfrastructureError(message="LLM API key is not configured.")

        payload = {
            "model": kwargs.get("model") or self.settings.llm_model,
            "messages": messages,
            "stream": False,
        }
        return await asyncio.to_thread(self._post_json, payload, api_key)

    def _post_json(self, payload: dict, api_key: str) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(
            self.settings.llm_base_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        try:
            with urllib_request.urlopen(req, timeout=self.settings.llm_timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise InfrastructureError(
                message=f"LLM upstream returned HTTP {exc.code}: {detail or 'No detail.'}",
            ) from exc
        except urllib_error.URLError as exc:
            raise InfrastructureError(message=f"LLM upstream request failed: {exc.reason}.") from exc
        except Exception as exc:
            raise InfrastructureError(message=f"LLM upstream request failed: {exc}.") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InfrastructureError(message="LLM upstream returned invalid JSON.") from exc
