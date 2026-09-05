from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, func, text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Matches the Postgres ENUM already created by schema.sql — create_type=False so
# SQLAlchemy never tries to (re)create it, it only binds to the existing type.
role_name_enum = ENUM(
    "EMPLOYEE", "HR_MANAGER", "HR_PAYROLL_USER", "HR_PAYROLL_MANAGER", "ADMIN",
    name="role_name",
    create_type=False,
)

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id", ondelete="RESTRICT"), primary_key=True),
)

class Role(Base):
    __tablename__ = "role"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(role_name_enum, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

class AppUser(Base):
    """Maps to schema.sql's app_user table — note there is no full_name column here;
    a user's display name comes from the linked employee row (employee_id), when present.
    Admin-only accounts (e.g. the seeded admin@Pexo.com) have employee_id = NULL."""
    __tablename__ = "app_user"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    employee_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())

    roles = relationship("Role", secondary=user_role, lazy="selectin")

class RefreshToken(Base):
    """Not part of the original schema.sql — see refresh_token.sql for the additive
    migration to run against Neon before this will work."""
    __tablename__ = "refresh_token"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())
