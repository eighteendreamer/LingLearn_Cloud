"""create password reset codes table

Revision ID: auth_password_reset_001
Revises: admin_001
Create Date: 2026-05-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = "auth_password_reset_001"
down_revision = "admin_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_codes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("email", sa.String(128), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("request_ip", sa.String(45), nullable=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expired_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index(
        "idx_password_reset_user_status",
        "password_reset_codes",
        ["user_id", "used_at", "expired_at"],
    )
    op.create_index(
        "idx_password_reset_email_created_at",
        "password_reset_codes",
        ["email", "created_at"],
    )
    op.create_index(
        "idx_password_reset_ip_created_at",
        "password_reset_codes",
        ["request_ip", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_password_reset_ip_created_at", table_name="password_reset_codes")
    op.drop_index("idx_password_reset_email_created_at", table_name="password_reset_codes")
    op.drop_index("idx_password_reset_user_status", table_name="password_reset_codes")
    op.drop_table("password_reset_codes")
