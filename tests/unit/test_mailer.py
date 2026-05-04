from __future__ import annotations

import pytest

from infra.config import SmtpConfig
from infra.mailer import Email, NoopMailer, SmtpMailer


def test_email_rfc822_includes_reply_to():
    e = Email(sender="a@x", to="b@x", subject="Hi", body="hello", reply_to="c@x")
    raw = e.as_rfc822()
    assert "Reply-To: c@x" in raw
    assert raw.endswith("hello")


def test_email_rfc822_no_reply_to():
    e = Email(sender="a@x", to="b@x", subject="Hi", body="hello")
    assert "Reply-To" not in e.as_rfc822()


def test_noop_mailer_does_not_raise():
    NoopMailer().send(Email(sender="a", to="b", subject="s", body="b"))


def test_smtp_mailer_raises_when_unconfigured():
    cfg = SmtpConfig(server="", port=587, username="", password="")
    with pytest.raises(RuntimeError):
        SmtpMailer(cfg).send(Email(sender="a", to="b", subject="s", body="b"))
