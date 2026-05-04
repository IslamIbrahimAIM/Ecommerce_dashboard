from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from typing import Protocol

from infra.config import SmtpConfig

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Email:
    sender: str
    to: str
    subject: str
    body: str
    reply_to: str | None = None

    def as_rfc822(self) -> str:
        headers = [
            f"Subject: {self.subject}",
            f"To: {self.to}",
            f"From: {self.sender}",
        ]
        if self.reply_to:
            headers.append(f"Reply-To: {self.reply_to}")
        return "\r\n".join(headers) + "\r\n\r\n" + self.body


class Mailer(Protocol):
    def send(self, email: Email) -> None: ...


class SmtpMailer:
    def __init__(self, config: SmtpConfig) -> None:
        self._config = config

    def send(self, email: Email) -> None:
        if not self._config.is_configured:
            raise RuntimeError("SMTP is not configured (missing server/username/password)")
        with smtplib.SMTP(self._config.server, self._config.port) as server:
            server.starttls()
            server.login(self._config.username, self._config.password)
            server.sendmail(email.sender, email.to, email.as_rfc822())


class NoopMailer:
    """Logs emails instead of sending. Use in dev when SMTP creds are absent."""

    def send(self, email: Email) -> None:
        log.info("NoopMailer.send to=%s subject=%s", email.to, email.subject)
