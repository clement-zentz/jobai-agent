# SPDX-License-Identifier: AGPL-3.0-or-later
# scripts/python/generate_fixtures.py

import os
from datetime import datetime, timedelta, timezone
from app.extraction.email.imap_client import IMAPClient
from app.extraction.email.provider import detect_provider
from app.extraction.email.email_alert_fetcher import EmailExtractionService
from app.utils.manage_fixture import create_fixture, remove_all_fixtures


import logging

logger = logging.getLogger(__name__)

PLATFORMS = {
    "indeed": "alert@indeed.com",
    "linkedin": "jobalerts-noreply@linkedin.com"
}

def fetch_recent_email_uids(client: IMAPClient, sender_address: str, days_back: int):
    """
    Fetch recent email UIDs from the IMAP inbox for a given sender.

    Searches for emails received within the last `days_back` days from the specified
    sender address, fetches each email, and extracts its UID, message object, and
    parsed date. Results are sorted by descending date (most recent first).

    Args:
        client (IMAPClient): Connected IMAP client instance.
        sender_address (str): Email address of the sender to filter messages.
        days_back (int): Number of days to look back for recent emails.

    Returns:
        List[Tuple[int, Message, datetime]]: List of tuples containing UID, message object,
        and parsed message date, sorted by descending date.
    """

    since = (
        datetime.now(timezone.utc) - timedelta(days=days_back)
    ).strftime("%d-%b-%Y")

    uids = client.search("SINCE", since)

    results = []

    for uid in uids:
        msg = client.fetch_email(uid)
        if not msg:
            continue

        sender = IMAPClient.decode(msg.get("From")).lower()
        if sender_address not in sender:
            continue

        msg_dt = EmailExtractionService.parse_msg_date(msg)
        if not msg_dt:
            continue

        results.append((uid, msg, msg_dt))

    # Sort by descending date (most recent first)
    results.sort(key=lambda tup: tup[2], reverse=True)
    return results

def generate_recent_fixtures(days_back: int=7, max_per_platform: int=3, folder: str="INBOX"):
    """
    Generate or regenerate HTML fixtures for recent job alert emails.

    This function connects to the IMAP inbox using credentials from environment variables,
    fetches recent emails from supported platforms (Indeed, LinkedIn), and creates cleaned
    HTML fixture files for testing and development. Only the most recent emails (up to
    `max_per_platform` per platform) within the last `days_back` days are processed.
    Previous fixtures are removed before generating new ones.

    Args:
        days_back (int): Number of days to look back for recent emails.
        max_per_platform (int): Maximum number of emails to process per platform.
        folder (str): IMAP folder to search for job alert emails.

    Raises:
        RuntimeError: If EMAIL_ADDRESS or EMAIL_PASSWORD environment variables are missing.

    Side Effects:
        - Deletes all previous fixture files.
        - Creates new fixture files in the configured fixture directories.

    Example:
        generate_recent_fixtures(days_back=5, max_per_platform=2, folder="INBOX")
    """

    # Remove previous fixtures
    remove_all_fixtures()

    email_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    if not email_address or not password:
        raise RuntimeError("EMAIL_ADDRESS or EMAIL_PASSWORD is missing")
    
    provider = detect_provider(email_address)
    client = IMAPClient(
        host=provider.host,
        username=email_address,
        password=password,
        port=provider.port,
    )

    client.connect()
    client.select_folder(folder)

    for platform, sender_address in PLATFORMS.items():
        logger.info(f"\n🔍 Processing platform: {platform}")

        # 1. Fetch + sort by date
        messages = fetch_recent_email_uids(
            client=client,
            sender_address=sender_address,
            days_back=days_back,
        )

        if not messages:
            logger.warning(f"⚠️ No emails found for {platform}")

        # 2. Take the N most recent
        selected = messages[:max_per_platform]

        logger.info(
            f"Keeping {len(selected)} emails out of {len(messages)}")
        
        # 3. Generate fixtures
        for uid, msg, msg_dt in selected:
            subject = IMAPClient.decode(msg.get("Subject"))
            html = IMAPClient.extract_html(msg)

            if not html:
                logger.warning(f"Skipping UID {uid} (no HTML)")
                continue

            logger.info(f"✅ Generating fixture for UID {uid} - {subject}")

            create_fixture(
                platform=platform,
                html=html,
                msg_date=msg_dt,
                subject=subject,
            )

    if client.conn is not None:
        client.conn.logout()

if __name__ == "__main__":
    generate_recent_fixtures()

