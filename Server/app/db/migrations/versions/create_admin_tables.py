"""create admin tables

Revision ID: admin_001
Revises: 
Create Date: 2026-05-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'admin_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建管理员角色表
    op.create_table(
        'admin_roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('permissions', sa.String(2000), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('is_super', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uk_admin_role_name'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_admin_role_status', 'admin_roles', ['status'])

    # 创建管理员用户表
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(64), nullable=False),
        sa.Column('email', sa.String(128), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('real_name', sa.String(64), nullable=True),
        sa.Column('phone', sa.String(32), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['role_id'], ['admin_roles.id']),
        sa.UniqueConstraint('username', name='uk_admin_username'),
        sa.UniqueConstraint('email', name='uk_admin_email'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_admin_status', 'admin_users', ['status'])


    # 创建管理员操作日志表
    op.create_table(
        'admin_operation_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('module', sa.String(64), nullable=False),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('target_type', sa.String(64), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('request_data', sa.String(2000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id']),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_admin_log_user_time', 'admin_operation_logs', ['admin_user_id', 'created_at'])
    op.create_index('idx_admin_log_module_action', 'admin_operation_logs', ['module', 'action', 'created_at'])

    # 插入默认超级管理员角色
    op.execute("""
        INSERT INTO admin_roles (name, description, permissions, is_super, status)
        VALUES ('超级管理员', '拥有所有权限', '["*"]', 1, 'active')
    """)

    # 插入默认管理员用户 (用户名: admin, 密码: admin123)
    # 密码哈希是 'admin123' 的 bcrypt 哈希值
    op.execute("""
        INSERT INTO admin_users (username, email, password_hash, real_name, role_id, status)
        VALUES ('admin', 'admin@linglearn.com', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF3UjqyK',
                '系统管理员', 1, 'active')
    """)


def downgrade() -> None:
    op.drop_table('admin_operation_logs')
    op.drop_table('admin_users')
    op.drop_table('admin_roles')
