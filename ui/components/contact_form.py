from __future__ import annotations

import streamlit as st

from infra.config import AppConfig
from infra.mailer import Email, Mailer

FIELDS = (
    ("name", "Name", "Please enter your Name"),
    ("subject", "Subject", "Please enter subject"),
    ("email", "Email Address", "Please enter your email: 'abc@email.com'"),
    ("message", "Message", "Enter your Message Here", True),
)


def _validate(values: dict[str, str]) -> str | None:
    for key, label, *_ in FIELDS:
        if not values.get(key, "").strip():
            return f"Please enter your {label}"
    return None


def render(*, config: AppConfig, inbound_mailer: Mailer, autoreply_mailer: Mailer | None) -> None:
    """Streamlit contact form. Renders, validates, dispatches both emails independently."""
    with st.expander(label="Contact Your Analyst"):
        with st.form("contact-your-analyst", clear_on_submit=True):
            values: dict[str, str] = {}
            for spec in FIELDS:
                key, label, placeholder, *rest = spec
                is_textarea = bool(rest and rest[0])
                widget = st.text_area if is_textarea else st.text_input
                values[key] = widget(label=label, placeholder=placeholder)
            submitted = st.form_submit_button(label="Send Message")

    if not submitted:
        return

    err = _validate(values)
    if err:
        st.warning(err)
        return

    inbound = Email(
        sender=config.contact_sender_display,
        to=config.contact_receiver,
        subject=values["subject"],
        body=f"Name: {values['name']}\nMessage: {values['message']}",
        reply_to=values["email"],
    )
    auto = Email(
        sender=config.contact_receiver,
        to=values["email"],
        subject="Auto-Reply: Thank you for your message",
        body=(
            f"Hi {values['name']},\n\nThank you for reaching out.\n"
            f"We have received your message:\n\n{values['message']}\n\n"
            "We will get back to you shortly.\n\nBest regards,\nYour Analyst"
        ),
    )

    inbound_ok = _try_send(inbound_mailer, inbound, "primary")
    auto_ok = _try_send(autoreply_mailer, auto, "auto-reply") if autoreply_mailer else None

    if inbound_ok and (auto_ok in (True, None)):
        st.success("Message sent. You'll receive an auto-reply shortly.")
    elif inbound_ok and auto_ok is False:
        st.success("Message delivered, but the auto-reply could not be sent.")
    else:
        st.error("Sorry — your message could not be delivered.")


def _try_send(mailer: Mailer, email: Email, kind: str) -> bool:
    try:
        mailer.send(email)
        return True
    except Exception as exc:  # noqa: BLE001 — boundary; logged for the user
        st.warning(f"{kind} send failed: {exc}")
        return False
