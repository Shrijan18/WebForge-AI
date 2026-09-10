import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.config.config import settings


IMAGE_CATALOG = {
    "travel": "photo-1500534623283-312aade485b7",
    "nature": "photo-1500534623283-312aade485b7",
    "food": "photo-1517248135467-4c7edcad34c4",
    "restaurant": "photo-1517248135467-4c7edcad34c4",
    "coffee": "photo-1495474472287-4d71bcdd2085",
    "fashion": "photo-1529139574466-a303027c1d8b",
    "product": "photo-1542291026-7eec264c27ff",
    "technology": "photo-1516321318423-f06f85e504b3",
    "software": "photo-1516321318423-f06f85e504b3",
    "business": "photo-1497366811353-6870744d04b2",
    "office": "photo-1497366811353-6870744d04b2",
    "portfolio": "photo-1497366754035-f200968a6e72",
    "people": "photo-1524504388940-b1c1722653e1",
}

DEFAULT_IMAGE_ID = "photo-1516321318423-f06f85e504b3"


class ImageService:

    def enrich_plan(self, plan):
        website_context = " ".join(
            str(plan.get(field, ""))
            for field in ("website_type", "description", "theme")
        ).lower()

        image_assets = plan.get("image_assets") or [
            {
                "purpose": "hero",
                "subject": plan.get("website_type", "website"),
                "search_query": website_context,
                "alt": f"Featured {plan.get('website_type', 'website')} image",
            }
        ]

        enriched_assets = []
        for index, asset in enumerate(image_assets[:6]):
            asset = dict(asset)
            subject = str(asset.get("subject", "")).lower()
            query = asset.get("search_query") or f"{website_context} {subject}"
            result = self._search_unsplash(query)

            if result:
                asset.update(result)
            else:
                image_id = self._find_image_id(website_context, subject)
                asset["recommended_url"] = (
                    f"https://images.unsplash.com/{image_id}"
                    f"?auto=format&fit=crop&w=1600&q=85"
                )
                asset["fallback_url"] = (
                    f"https://images.unsplash.com/{image_id}"
                    f"?auto=format&fit=crop&w=900&q=80"
                )
                asset["source"] = "Unsplash fallback catalog"

            asset["search_query"] = query
            asset["alt"] = asset.get("alt") or (
                f"{asset.get('purpose', 'Featured')} image of "
                f"{asset.get('subject') or plan.get('website_type', 'the subject')}"
            )
            asset["asset_index"] = index
            enriched_assets.append(asset)

        plan["image_assets"] = enriched_assets
        return plan

    @staticmethod
    def _search_unsplash(query):
        access_key = settings.UNSPLASH_ACCESS_KEY
        if not access_key or not query.strip():
            return None

        endpoint = (
            "https://api.unsplash.com/search/photos?per_page=1&query="
            f"{quote(query.strip())}"
        )
        request = Request(
            endpoint,
            headers={
                "Authorization": f"Client-ID {access_key}",
                "Accept-Version": "v1",
                "User-Agent": "WebForge-AI/1.0",
            },
        )

        try:
            with urlopen(request, timeout=12) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            return None

        results = payload.get("results", [])
        if not results:
            return None

        photo = results[0]
        urls = photo.get("urls", {})
        links = photo.get("links", {})
        user = photo.get("user", {})

        image_url = urls.get("regular") or urls.get("small")
        if not image_url:
            return None

        return {
            "recommended_url": image_url,
            "fallback_url": urls.get("small") or image_url,
            "source": "Unsplash API",
            "photo_id": photo.get("id", ""),
            "photographer": user.get("name", "Unsplash contributor"),
            "photographer_url": user.get("links", {}).get("html", ""),
            "unsplash_url": links.get("html", "https://unsplash.com"),
        }

    @staticmethod
    def _find_image_id(*contexts):
        combined = " ".join(contexts)
        for keyword, image_id in IMAGE_CATALOG.items():
            if keyword in combined:
                return image_id
        return DEFAULT_IMAGE_ID
