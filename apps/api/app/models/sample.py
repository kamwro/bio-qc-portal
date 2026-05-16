from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.qc_metric import QCMetric
    from app.models.run import SequencingRun


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sequencing_runs.id", ondelete="CASCADE"), nullable=False
    )
    sample_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    run: Mapped[SequencingRun] = relationship(back_populates="samples")
    qc_metric: Mapped[QCMetric | None] = relationship(
        back_populates="sample", cascade="all, delete-orphan", uselist=False
    )
