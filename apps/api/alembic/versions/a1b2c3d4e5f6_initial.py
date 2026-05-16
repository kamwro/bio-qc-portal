"""initial

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sequencing_runs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("platform", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "samples",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("sample_name", sa.String(255), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["run_id"], ["sequencing_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "qc_metrics",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("sample_id", sa.String(36), nullable=False),
        sa.Column("total_reads", sa.Integer(), nullable=False),
        sa.Column("q30_score", sa.Float(), nullable=False),
        sa.Column("gc_content", sa.Float(), nullable=False),
        sa.Column("duplication_rate", sa.Float(), nullable=False),
        sa.Column("adapter_content", sa.Float(), nullable=False),
        sa.Column("mean_read_quality", sa.Float(), nullable=False),
        sa.Column("qc_status", sa.String(10), nullable=False),
        sa.ForeignKeyConstraint(["sample_id"], ["samples.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sample_id"),
    )


def downgrade() -> None:
    op.drop_table("qc_metrics")
    op.drop_table("samples")
    op.drop_table("sequencing_runs")
    op.drop_table("projects")
