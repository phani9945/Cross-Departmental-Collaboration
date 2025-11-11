from __future__ import annotations

from typing import Optional


async def send_email(to: str, subject: str, body: str) -> None:
    # Implement vendor email integration here, e.g., SendGrid/Mailgun
    # This is a stub for demonstration.
    return None


async def send_slack(channel: str, text: str) -> None:
    # Implement Slack webhook or SDK integration
    # This is a stub for demonstration.
    return None


