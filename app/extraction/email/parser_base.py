# SPDX-License-Identifier: AGPL-3.0-or-later
# app/extraction/parser_base.py

from abc import ABC, abstractmethod


class EmailParser(ABC):

    @abstractmethod
    def matches(self, sender: str, subject: str) -> bool:
        """Return True if this parser can handle the email."""
        pass

    @abstractmethod
    def parse(self, html: str) -> list[dict]:
        """Return a list of job dicts with title, company, url, location, platform."""
        pass
