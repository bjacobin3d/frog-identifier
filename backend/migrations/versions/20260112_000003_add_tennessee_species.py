"""Add Tennessee frog and toad species

Revision ID: 20260112_000003
Revises: 20260112_000002
Create Date: 2026-01-12

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260112_000003'
down_revision: Union[str, None] = '20260112_000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tennessee frogs and toads not already in the database
TENNESSEE_SPECIES_DATA = [
    # Toads (Family Bufonidae)
    {
        "common_name": "American Toad",
        "scientific_name": "Anaxyrus americanus",
        "description": "A common, robust toad with warty skin and prominent parotoid glands. Known for its long, musical trill that can last 30 seconds.",
        "habitat": "Forests, fields, backyards, and gardens. Breeds in shallow ponds, ditches, and temporary pools.",
        "range": "Eastern North America from Manitoba to Georgia, including all of Tennessee.",
    },
    {
        "common_name": "Fowler's Toad",
        "scientific_name": "Anaxyrus fowleri",
        "description": "Similar to American Toad but with a shorter, nasal 'waaah' call. Has 3 or more warts per dark dorsal spot.",
        "habitat": "Sandy areas, beaches, agricultural fields, and open woodlands near breeding ponds.",
        "range": "Eastern United States from New Hampshire to Texas, common throughout Tennessee.",
    },
    # Cricket Frogs
    {
        "common_name": "Southern Cricket Frog",
        "scientific_name": "Acris gryllus",
        "description": "A tiny, warty frog with a clicking call resembling pebbles being struck. Distinguished from Northern Cricket Frog by call and range.",
        "habitat": "Edges of permanent water bodies with emergent vegetation, including ponds, marshes, and slow streams.",
        "range": "Southeastern coastal plain, found in southwestern Tennessee.",
    },
    # Treefrogs
    {
        "common_name": "Bird-voiced Treefrog",
        "scientific_name": "Dryophytes avivoca",
        "description": "A gray or greenish treefrog with a distinctive bird-like whistling call. Has a pale yellowish wash on the inner thigh.",
        "habitat": "Wooded swamps, river bottoms, and cypress-tupelo swamps.",
        "range": "Southeastern United States, found in western Tennessee river bottoms.",
    },
    # Chorus Frogs
    {
        "common_name": "Mountain Chorus Frog",
        "scientific_name": "Pseudacris brachyphona",
        "description": "A small chorus frog with dark triangular marks between the eyes. Call is a harsh, nasal 'wreek' repeated rapidly.",
        "habitat": "Wooded hillsides, ravines, and forested valleys near temporary pools.",
        "range": "Appalachian Mountains from Pennsylvania to Alabama, found in eastern Tennessee.",
    },
    {
        "common_name": "Upland Chorus Frog",
        "scientific_name": "Pseudacris feriarum",
        "description": "A small frog with three dark dorsal stripes and a rising trill call like running a finger along a comb.",
        "habitat": "Grasslands, agricultural areas, open woodlands, and roadside ditches near temporary pools.",
        "range": "Southeastern and central United States, common throughout Tennessee.",
    },
    # Narrow-mouthed Toads
    {
        "common_name": "Eastern Narrow-mouthed Toad",
        "scientific_name": "Gastrophryne carolinensis",
        "description": "A small, plump toad with a pointed snout and fold of skin behind the head. Call is a sheep-like bleat.",
        "habitat": "Moist areas under logs, rocks, and debris near temporary pools. Often found in urban areas.",
        "range": "Southeastern United States from Maryland to Texas, found across Tennessee.",
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
            for species in TENNESSEE_SPECIES_DATA
        ]
    )


def downgrade() -> None:
    # Delete the Tennessee species we added
    scientific_names = [s["scientific_name"] for s in TENNESSEE_SPECIES_DATA]
    names_str = ", ".join([f"'{name}'" for name in scientific_names])
    op.execute(f"DELETE FROM frog_species WHERE scientific_name IN ({names_str})")
