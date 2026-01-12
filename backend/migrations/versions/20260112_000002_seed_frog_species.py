"""Seed frog species data

Revision ID: 20260112_000002
Revises: 20260112_000001
Create Date: 2026-01-12

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260112_000002'
down_revision: Union[str, None] = '20260112_000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Seed data for common North American frog species
FROG_SPECIES_DATA = [
    {
        "common_name": "American Bullfrog",
        "scientific_name": "Lithobates catesbeianus",
        "description": "The largest frog native to North America. Known for its deep, resonant 'jug-o-rum' call.",
        "habitat": "Large permanent bodies of water such as lakes, ponds, and slow-moving streams.",
        "range": "Native to eastern North America, introduced throughout the western United States.",
    },
    {
        "common_name": "Spring Peeper",
        "scientific_name": "Pseudacris crucifer",
        "description": "A tiny chorus frog known for its high-pitched peeping call that heralds spring.",
        "habitat": "Wooded areas near temporary ponds, marshes, and swamps.",
        "range": "Eastern North America from Manitoba to Florida.",
    },
    {
        "common_name": "Green Tree Frog",
        "scientific_name": "Hyla cinerea",
        "description": "A bright green arboreal frog with a distinctive white or cream stripe along its side.",
        "habitat": "Swamps, marshes, and areas near lakes and ponds with abundant vegetation.",
        "range": "Southeastern United States from Texas to Virginia.",
    },
    {
        "common_name": "Pacific Tree Frog",
        "scientific_name": "Pseudacris regilla",
        "description": "A small tree frog famous for its 'ribbit' call, often used in movies.",
        "habitat": "Various habitats from forests to grasslands, typically near water.",
        "range": "Pacific coast from British Columbia to Baja California.",
    },
    {
        "common_name": "Wood Frog",
        "scientific_name": "Lithobates sylvaticus",
        "description": "A medium-sized frog with a distinctive dark mask, capable of surviving freezing.",
        "habitat": "Moist woodlands, vernal pools, and forest edges.",
        "range": "Northern North America from Alaska to the Atlantic.",
    },
    {
        "common_name": "Gray Tree Frog",
        "scientific_name": "Hyla versicolor",
        "description": "A master of camouflage that can change color from gray to green.",
        "habitat": "Forested areas near temporary or permanent bodies of water.",
        "range": "Eastern United States and southeastern Canada.",
    },
    {
        "common_name": "Northern Leopard Frog",
        "scientific_name": "Lithobates pipiens",
        "description": "A spotted frog with a distinctive pattern resembling a leopard.",
        "habitat": "Meadows, fields, and areas near ponds, lakes, and marshes.",
        "range": "Northern North America from Canada to the southwestern United States.",
    },
    {
        "common_name": "Green Frog",
        "scientific_name": "Lithobates clamitans",
        "description": "A medium to large frog with a call resembling a loose banjo string.",
        "habitat": "Shallow freshwater including ponds, lakes, swamps, and streams.",
        "range": "Eastern North America from Canada to Florida.",
    },
    {
        "common_name": "Pickerel Frog",
        "scientific_name": "Lithobates palustris",
        "description": "A medium-sized frog with distinctive rectangular spots arranged in parallel rows.",
        "habitat": "Cool, clear streams and springs, as well as shaded ponds.",
        "range": "Eastern North America from Canada to the Gulf states.",
    },
    {
        "common_name": "Western Chorus Frog",
        "scientific_name": "Pseudacris triseriata",
        "description": "A small frog with three dark stripes down its back and a distinctive rising trill.",
        "habitat": "Grasslands, marshes, and agricultural areas near temporary pools.",
        "range": "Central North America from Canada to Arizona.",
    },
    {
        "common_name": "Northern Cricket Frog",
        "scientific_name": "Acris crepitans",
        "description": "A tiny frog with warty skin and a clicking call like pebbles being struck together.",
        "habitat": "Edges of permanent bodies of water with plenty of vegetation.",
        "range": "Eastern and central United States.",
    },
    {
        "common_name": "Cope's Gray Treefrog",
        "scientific_name": "Hyla chrysoscelis",
        "description": "Nearly identical to the Gray Treefrog but with a faster, higher-pitched call.",
        "habitat": "Forested areas, especially near temporary water sources.",
        "range": "Eastern United States, often overlapping with Gray Treefrog.",
    },
    {
        "common_name": "Barking Treefrog",
        "scientific_name": "Hyla gratiosa",
        "description": "The largest native treefrog in the US, named for its dog-like barking call.",
        "habitat": "Pine flatwoods, mixed forests, and areas near fishless ponds.",
        "range": "Southeastern coastal plain from Virginia to Louisiana.",
    },
    {
        "common_name": "Squirrel Treefrog",
        "scientific_name": "Hyla squirella",
        "description": "A small, variable-colored treefrog with a raspy, squirrel-like call.",
        "habitat": "Various habitats including gardens, woodlands, and near buildings.",
        "range": "Southeastern United States coastal areas.",
    },
    {
        "common_name": "Southern Leopard Frog",
        "scientific_name": "Lithobates sphenocephalus",
        "description": "Similar to Northern Leopard Frog with a pointed snout and distinctive call.",
        "habitat": "Freshwater habitats including ponds, lakes, and ditches.",
        "range": "Southeastern United States.",
    },
    {
        "common_name": "Pig Frog",
        "scientific_name": "Lithobates grylio",
        "description": "A large aquatic frog named for its pig-like grunting call.",
        "habitat": "Permanent bodies of water with abundant vegetation.",
        "range": "Southeastern United States coastal plain.",
    },
    {
        "common_name": "River Frog",
        "scientific_name": "Lithobates heckscheri",
        "description": "A large, dark frog found near river swamps and streams.",
        "habitat": "River swamps, streams, and other flowing water bodies.",
        "range": "Southeastern coastal plain from North Carolina to Mississippi.",
    },
    {
        "common_name": "Crawfish Frog",
        "scientific_name": "Lithobates areolatus",
        "description": "A stocky frog that often inhabits crawfish burrows.",
        "habitat": "Prairies and grasslands, often using crawfish burrows for shelter.",
        "range": "Central United States from Indiana to Texas.",
    },
    {
        "common_name": "Gopher Frog",
        "scientific_name": "Lithobates capito",
        "description": "A robust frog that uses gopher tortoise burrows and other underground refuges.",
        "habitat": "Longleaf pine savannas and sandhill communities.",
        "range": "Southeastern coastal plain.",
    },
    {
        "common_name": "Carpenter Frog",
        "scientific_name": "Lithobates virgatipes",
        "description": "A medium-sized frog with a call resembling a carpenter hammering nails.",
        "habitat": "Acidic sphagnum bogs, cedar swamps, and pocosins.",
        "range": "Atlantic coastal plain from New Jersey to Georgia.",
    },
]


def upgrade() -> None:
    # Create a reference to the frog_species table
    frog_species = sa.table(
        'frog_species',
        sa.column('common_name', sa.String),
        sa.column('scientific_name', sa.String),
        sa.column('description', sa.Text),
        sa.column('habitat', sa.Text),
        sa.column('range', sa.Text),
        sa.column('image_url', sa.String),
        sa.column('audio_sample_url', sa.String),
        sa.column('created_at', sa.DateTime),
    )
    
    # Insert seed data
    op.bulk_insert(
        frog_species,
        [
            {
                **species,
                "image_url": None,
                "audio_sample_url": None,
                "created_at": datetime.utcnow(),
            }
            for species in FROG_SPECIES_DATA
        ]
    )


def downgrade() -> None:
    # Delete all seeded species
    op.execute("DELETE FROM frog_species")
