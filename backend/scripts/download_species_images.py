#!/usr/bin/env python3
"""
Download Creative Commons licensed images from Wikimedia Commons for frog species.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Species data with their scientific names
SPECIES = [
    {"id": 1, "name": "American Bullfrog", "scientific": "Lithobates catesbeianus"},
    {"id": 2, "name": "Spring Peeper", "scientific": "Pseudacris crucifer"},
    {"id": 3, "name": "Green Tree Frog", "scientific": "Hyla cinerea"},
    {"id": 4, "name": "Pacific Tree Frog", "scientific": "Pseudacris regilla"},
    {"id": 5, "name": "Wood Frog", "scientific": "Lithobates sylvaticus"},
    {"id": 6, "name": "Gray Tree Frog", "scientific": "Hyla versicolor"},
    {"id": 7, "name": "Northern Leopard Frog", "scientific": "Lithobates pipiens"},
    {"id": 8, "name": "Green Frog", "scientific": "Lithobates clamitans"},
    {"id": 9, "name": "Pickerel Frog", "scientific": "Lithobates palustris"},
    {"id": 10, "name": "Western Chorus Frog", "scientific": "Pseudacris triseriata"},
    {"id": 11, "name": "Northern Cricket Frog", "scientific": "Acris crepitans"},
    {"id": 12, "name": "Cope's Gray Treefrog", "scientific": "Hyla chrysoscelis"},
    {"id": 13, "name": "Barking Treefrog", "scientific": "Hyla gratiosa"},
    {"id": 14, "name": "Squirrel Treefrog", "scientific": "Hyla squirella"},
    {"id": 15, "name": "Southern Leopard Frog", "scientific": "Lithobates sphenocephalus"},
    {"id": 16, "name": "Pig Frog", "scientific": "Lithobates grylio"},
    {"id": 17, "name": "River Frog", "scientific": "Lithobates heckscheri"},
    {"id": 18, "name": "Crawfish Frog", "scientific": "Lithobates areolatus"},
    {"id": 19, "name": "Gopher Frog", "scientific": "Lithobates capito"},
    {"id": 20, "name": "Carpenter Frog", "scientific": "Lithobates virgatipes"},
    {"id": 21, "name": "American Toad", "scientific": "Anaxyrus americanus"},
    {"id": 22, "name": "Fowler's Toad", "scientific": "Anaxyrus fowleri"},
    {"id": 23, "name": "Southern Cricket Frog", "scientific": "Acris gryllus"},
    {"id": 24, "name": "Bird-voiced Treefrog", "scientific": "Dryophytes avivoca"},
    {"id": 25, "name": "Mountain Chorus Frog", "scientific": "Pseudacris brachyphona"},
    {"id": 26, "name": "Upland Chorus Frog", "scientific": "Pseudacris feriarum"},
    {"id": 27, "name": "Eastern Narrow-mouthed Toad", "scientific": "Gastrophryne carolinensis"},
]

# Alternative scientific names (old taxonomy)
ALT_NAMES = {
    "Lithobates catesbeianus": "Rana catesbeiana",
    "Lithobates sylvaticus": "Rana sylvatica",
    "Lithobates pipiens": "Rana pipiens",
    "Lithobates clamitans": "Rana clamitans",
    "Anaxyrus americanus": "Bufo americanus",
    "Anaxyrus fowleri": "Bufo fowleri",
    "Dryophytes avivoca": "Hyla avivoca",
}

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
OUTPUT_DIR = Path(__file__).parent.parent / "uploads" / "species"

# User-Agent headers - Wikimedia requires a proper User-Agent
API_HEADERS = {
    "User-Agent": "FrogIdentifier/1.0 (https://github.com/frog-identifier; contact@example.com) Python/requests"
}
# More browser-like for downloads
DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://commons.wikimedia.org/",
}


def search_wikimedia_image(search_term: str) -> dict | None:
    """Search Wikimedia Commons for an image."""
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": "6",  # File namespace
        "gsrsearch": f"filetype:bitmap {search_term}",
        "gsrlimit": "5",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "800",  # Get thumbnail at 800px width
    }
    
    try:
        response = requests.get(WIKIMEDIA_API, params=params, headers=API_HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        
        # Find best image (prefer jpg/png, reasonable size)
        best_image = None
        best_score = 0
        
        for page_id, page in pages.items():
            if int(page_id) < 0:
                continue
                
            imageinfo = page.get("imageinfo", [{}])[0]
            mime = imageinfo.get("mime", "")
            width = imageinfo.get("width", 0)
            height = imageinfo.get("height", 0)
            
            # Score the image
            score = 0
            if mime in ["image/jpeg", "image/png"]:
                score += 10
            if 400 < width < 4000:
                score += 5
            if 400 < height < 4000:
                score += 5
            # Prefer landscape or square
            if width >= height:
                score += 2
                
            if score > best_score:
                best_score = score
                best_image = {
                    "title": page.get("title", ""),
                    "url": imageinfo.get("thumburl") or imageinfo.get("url"),
                    "source_url": imageinfo.get("descriptionurl", ""),
                    "mime": mime,
                }
        
        return best_image
        
    except Exception as e:
        print(f"  Error searching: {e}")
        return None


def download_image(url: str, output_path: Path) -> bool:
    """Download an image from URL."""
    try:
        response = requests.get(url, headers=DOWNLOAD_HEADERS, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Frog Species Images from Wikimedia Commons")
    print("=" * 60)
    print()
    
    results = []
    
    for species in SPECIES:
        species_id = species["id"]
        name = species["name"]
        scientific = species["scientific"]
        
        print(f"[{species_id:2d}] {name} ({scientific})")
        
        # Check if image already exists
        output_path = OUTPUT_DIR / f"{species_id}.jpg"
        if output_path.exists():
            print(f"  ✓ Already exists: {output_path.name}")
            results.append({"id": species_id, "status": "exists", "path": str(output_path)})
            continue
        
        # Try scientific name first
        image = search_wikimedia_image(scientific)
        
        # Try alternative name if no result
        if not image and scientific in ALT_NAMES:
            print(f"  Trying alternative: {ALT_NAMES[scientific]}")
            image = search_wikimedia_image(ALT_NAMES[scientific])
        
        # Try common name as fallback
        if not image:
            print(f"  Trying common name: {name}")
            image = search_wikimedia_image(name)
        
        if image:
            print(f"  Found: {image['title'][:50]}...")
            
            # Determine file extension
            ext = ".jpg"
            if "png" in image.get("mime", ""):
                ext = ".png"
            
            output_path = OUTPUT_DIR / f"{species_id}{ext}"
            
            if download_image(image["url"], output_path):
                print(f"  ✓ Downloaded: {output_path.name}")
                results.append({
                    "id": species_id,
                    "status": "downloaded",
                    "path": str(output_path),
                    "source": image.get("source_url", "")
                })
            else:
                results.append({"id": species_id, "status": "failed"})
        else:
            print(f"  ✗ No image found")
            results.append({"id": species_id, "status": "not_found"})
        
        # Be nice to the API - longer delay to avoid rate limiting
        time.sleep(3)
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    downloaded = sum(1 for r in results if r["status"] == "downloaded")
    existing = sum(1 for r in results if r["status"] == "exists")
    failed = sum(1 for r in results if r["status"] in ["failed", "not_found"])
    
    print(f"  Downloaded: {downloaded}")
    print(f"  Already existed: {existing}")
    print(f"  Failed/Not found: {failed}")
    print()
    
    # Generate SQL to update the database
    print("SQL to update database:")
    print("-" * 40)
    for r in results:
        if r["status"] in ["downloaded", "exists"]:
            path = r.get("path", "").replace(str(OUTPUT_DIR.parent.parent), "")
            if path.startswith("/"):
                path = path[1:]
            print(f"UPDATE frog_species SET image_url = '/uploads/species/{r['id']}.jpg' WHERE id = {r['id']};")


if __name__ == "__main__":
    main()
