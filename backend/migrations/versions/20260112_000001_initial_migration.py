"""Initial migration - create frog_species and sightings tables

Revision ID: 20260112_000001
Revises: 
Create Date: 2026-01-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260112_000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create frog_species table
    op.create_table(
        'frog_species',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('common_name', sa.String(length=255), nullable=False),
        sa.Column('scientific_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('habitat', sa.Text(), nullable=True),
        sa.Column('range', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('audio_sample_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scientific_name')
    )
    op.create_index(op.f('ix_frog_species_common_name'), 'frog_species', ['common_name'], unique=False)
    
    # Create sightings table
    op.create_table(
        'sightings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('species_id', sa.Integer(), nullable=False),
        sa.Column('detection_type', sa.String(length=20), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('location_name', sa.String(length=255), nullable=True),
        sa.Column('image_path', sa.String(length=500), nullable=True),
        sa.Column('audio_path', sa.String(length=500), nullable=True),
        sa.Column('sighted_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['species_id'], ['frog_species.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sightings_species_id'), 'sightings', ['species_id'], unique=False)
    op.create_index(op.f('ix_sightings_sighted_at'), 'sightings', ['sighted_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sightings_sighted_at'), table_name='sightings')
    op.drop_index(op.f('ix_sightings_species_id'), table_name='sightings')
    op.drop_table('sightings')
    op.drop_index(op.f('ix_frog_species_common_name'), table_name='frog_species')
    op.drop_table('frog_species')
