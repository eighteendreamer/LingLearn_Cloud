import asyncio
import json
from urllib import error as urllib_error
from urllib import request as urllib_request
from collections.abc import AsyncIterator

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError


class LLMClient:
    """Backend-owned large language model client for OpenAI-compatible APIs."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> dict:
        api_key = self.settings.llm_api_key.strip()
        if not api_key:
            raise InfrastructureError(message="LLM API key is not configured.")

        payload = {
            "model": kwargs.get("model") or self.settings.llm_model,
            "messages": messages,
            "stream": False,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        return await asyncio.to_thread(self._post_json, payload, api_key)

    async def stream_chat(self, messages: list[dict[str, str]], **kwargs) -> AsyncIterator[str]:
        api_key = self.settings.llm_api_key.strip()
        if not api_key:
            raise InfrastructureError(message="LLM API key is not configured.")

        payload = {
            "model": kwargs.get("model") or self.settings.llm_model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        queue: asyncio.Queue[str | Exception | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def worker() -> None:
            try:
                for chunk in self._post_stream(payload, api_key):
                    loop.call_soon_threadsafe(queue.put_nowait, chunk)
            except Exception as exc:
                loop.call_soon_threadsafe(queue.put_nowait, exc)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        asyncio.create_task(asyncio.to_thread(worker))
        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

    def _post_json(self, payload: dict, api_key: str) -> dict:
        body = json.dumps(payload).encode("utf-8")
        url = self.settings.llm_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"
        req = urllib_request.Request(
            url,
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

    def _post_stream(self, payload: dict, api_key: str):
        body = json.dumps(payload).encode("utf-8")
        url = self.settings.llm_base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"
        req = urllib_request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        try:
            with urllib_request.urlopen(req, timeout=self.settings.llm_timeout_seconds) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = event.get("choices")
                    if not isinstance(choices, list) or not choices:
                        continue
                    delta = (choices[0] or {}).get("delta") or {}
                    content = delta.get("content") or (choices[0] or {}).get("text")
                    if content:
                        yield str(content)
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise InfrastructureError(
                message=f"LLM upstream returned HTTP {exc.code}: {detail or 'No detail.'}",
            ) from exc
        except urllib_error.URLError as exc:
            raise InfrastructureError(message=f"LLM upstream request failed: {exc.reason}.") from exc
        except Exception as exc:
            raise InfrastructureError(message=f"LLM upstream request failed: {exc}.") from exc
