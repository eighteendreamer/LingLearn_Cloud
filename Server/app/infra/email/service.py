from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from email.utils import formataddr
from urllib.parse import quote

import httpx

from app.core.config import get_settings
from app.core.exceptions import InfrastructureError

logger = logging.getLogger(__name__)


class EmailService:
    async def send_password_reset_code(
        self,
        *,
        to_email: str,
        code: str,
        ttl_minutes: int,
    ) -> None:
        settings = get_settings()
        if not settings.email_enabled:
            logger.info("Email delivery is disabled; password reset email skipped.")
            return

        if settings.email_provider.lower() != "aliyun":
            raise InfrastructureError(message="Unsupported email provider.")

        recipient = settings.email_test_email if settings.email_test_mode else to_email
        if not recipient:
            raise InfrastructureError(message="Email recipient is not configured.")

        subject = "LingLearn Cloud 密码重置验证码"
        html_body = self._build_password_reset_html(
            code=code,
            ttl_minutes=ttl_minutes,
            original_email=to_email if settings.email_test_mode else None,
        )
        text_body = f"您的 LingLearn Cloud 密码重置验证码是 {code}，{ttl_minutes} 分钟内有效。"
        if settings.email_test_mode:
            text_body += f" 原始收件人：{to_email}"

        await self._send_aliyun_single_mail(
            to_email=recipient,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    async def _send_aliyun_single_mail(
        self,
        *,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> None:
        settings = get_settings()
        if not settings.email_api_key or not settings.email_secret_key:
            raise InfrastructureError(message="Email credentials are not configured.")
        if not settings.email_sender_email:
            raise InfrastructureError(message="Email sender is not configured.")

        params = {
            "AccessKeyId": settings.email_api_key,
            "Action": "SingleSendMail",
            "AccountName": settings.email_sender_email,
            "AddressType": "1",
            "Format": "JSON",
            "FromAlias": settings.email_sender_name,
            "HtmlBody": html_body,
            "RegionId": "cn-hangzhou",
            "ReplyToAddress": "false",
            "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": str(uuid.uuid4()),
            "SignatureVersion": "1.0",
            "Subject": subject,
            "TagName": "password_reset",
            "TextBody": text_body,
            "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ToAddress": to_email,
            "Version": "2015-11-23",
        }
        signed_params = {
            **params,
            "Signature": self._build_aliyun_signature(params, settings.email_secret_key),
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://dm.aliyuncs.com/",
                data=signed_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            logger.warning("Aliyun mail request failed: %s", response.text)
            raise InfrastructureError(message="Failed to send password reset email.")

        payload = response.json()
        if "Code" in payload:
            logger.warning("Aliyun mail response error: %s", payload)
            raise InfrastructureError(message="Failed to send password reset email.")

    @staticmethod
    def _build_aliyun_signature(params: dict[str, str], secret_key: str) -> str:
        canonicalized_query = "&".join(
            f"{EmailService._quote_rfc3986(key)}={EmailService._quote_rfc3986(value)}"
            for key, value in sorted(params.items())
        )
        string_to_sign = f"POST&%2F&{EmailService._quote_rfc3986(canonicalized_query)}"
        digest = hmac.new(
            f"{secret_key}&".encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    @staticmethod
    def _quote_rfc3986(value: str) -> str:
        return quote(str(value), safe="~")

    @staticmethod
    def _build_password_reset_html(
        *,
        code: str,
        ttl_minutes: int,
        original_email: str | None,
    ) -> str:
        test_mode_note = (
            f"<p style='color:#64748b;font-size:13px'>测试模式：原始收件人为 {original_email}</p>"
            if original_email
            else ""
        )
        sender = formataddr(("LingLearn Cloud", "no-reply@linglearn.cloud"))
        return f"""
        <div style="font-family:Arial,'Microsoft YaHei',sans-serif;line-height:1.7;color:#0f172a">
          <p>您好，</p>
          <p>您正在找回 LingLearn Cloud 账号密码。验证码为：</p>
          <p style="font-size:28px;font-weight:700;letter-spacing:6px;color:#059669">{code}</p>
          <p>验证码 {ttl_minutes} 分钟内有效。若非本人操作，请忽略本邮件。</p>
          {test_mode_note}
          <p style="color:#64748b;font-size:13px">此邮件由 {sender} 自动发送，请勿直接回复。</p>
        </div>
        """


email_service = EmailService()
