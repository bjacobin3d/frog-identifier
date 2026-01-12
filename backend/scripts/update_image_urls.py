#!/usr/bin/env python3
"""Update the database with species image URLs."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

# Get database URL
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "frog_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "frog_password")
DB_NAME = os.getenv("DB_NAME", "frog_identifier")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Image URL mappings
IMAGE_URLS = [
    (1, "/uploads/species/1.jpg"),
    (2, "/uploads/species/2.jpg"),
    (3, "/uploads/species/3.jpg"),
    (4, "/uploads/species/4.jpg"),
    (5, "/uploads/species/5.jpg"),
    (6, "/uploads/species/6.jpg"),
    (7, "/uploads/species/7.jpg"),
    (8, "/uploads/species/8.jpg"),
    (9, "/uploads/species/9.jpg"),
    (10, "/uploads/species/10.jpg"),
    (11, "/uploads/species/11.jpg"),
    (12, "/uploads/species/12.jpg"),
    (13, "/uploads/species/13.jpg"),
    (14, "/uploads/species/14.jpg"),
    (15, "/uploads/species/15.jpg"),
    (16, "/uploads/species/16.jpg"),
    (17, "/uploads/species/17.jpg"),
    (18, "/uploads/species/18.jpg"),
    (19, "/uploads/species/19.png"),
    (20, "/uploads/species/20.jpg"),
    (21, "/uploads/species/21.jpg"),
    (22, "/uploads/species/22.jpg"),
    (23, "/uploads/species/23.jpg"),
    (24, "/uploads/species/24.jpg"),
    (25, "/uploads/species/25.jpg"),
    (26, "/uploads/species/26.jpg"),
    (27, "/uploads/species/27.jpg"),
]


def main():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        for species_id, image_url in IMAGE_URLS:
            conn.execute(
                text("UPDATE frog_species SET image_url = :url WHERE id = :id"),
                {"url": image_url, "id": species_id}
            )
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT id, common_name, image_url FROM frog_species ORDER BY id"))
        print("Updated species image URLs:")
        print("-" * 60)
        for row in result:
            print(f"  [{row.id:2d}] {row.common_name}: {row.image_url}")
    
    print("\n✅ All image URLs updated!")


if __name__ == "__main__":
    main()
