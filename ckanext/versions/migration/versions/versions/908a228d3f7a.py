"""empty message

Revision ID: 2588d65b7c42
Revises:
Create Date: 2025-04-22 10:00:20.849442

"""

from alembic import op
import sqlalchemy as sa
from ckan.model.types import UuidType
from sqlalchemy.dialects.postgresql import JSONB 

# revision identifiers, used by Alembic.
revision = "908a228d3f7a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    engine = op.get_bind()
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    op.create_table(
        "package_version",
        sa.Column("id", UuidType, primary_key=True),
        sa.Column("package_id", UuidType, sa.ForeignKey("package.id"), nullable=False),
        sa.Column("name", sa.Unicode, nullable=False),
        sa.Column("notes", sa.Unicode, nullable=True),
        sa.Column("data", JSONB, nullable=False),
        sa.Column("creator_user_id", UuidType, sa.ForeignKey("user.id"), nullable=True),
        sa.Column("created", sa.DateTime, server_default=sa.func.current_timestamp()),
    )

    op.create_index("idx_package_version_name", "package_version", ["name", "created"])
    op.create_unique_constraint("uix_package_id_name", "package_version", ["package_id", "name"])

def downgrade():
    op.drop_index("idx_package_version_name")
    op.drop_constraint(None, "package_version", type_="unique")
    op.drop_table("package_version")
