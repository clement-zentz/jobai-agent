# app/scrapers/base.py
from typing import List, Dict
from abc import ABC, abstractmethod


class JobScraper(ABC):
    
    @abstractmethod
    async def search(self, query: str, location: str | None = None) -> List[Dict]:
        """Return a list of raw job offers."""
        pass

    @staticmethod
    def normalize(offer: Dict) -> Dict:
        """Ensure all scrapers output the same schema."""
        return {
            "title": offer.get("title"),
            "company": offer.get("company"),
            "location": offer.get("location"),
            "description": offer.get("description"),
            "url": offer.get("url"),
            "platform": offer.get("platform"),
        }