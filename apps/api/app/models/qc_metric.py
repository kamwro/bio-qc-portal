from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.sample import Sample


class QCMetric(Base):
    __tablename__ = "qc_metrics"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    sample_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("samples.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_reads: Mapped[int] = mapped_column(Integer, nullable=False)
    q30_score: Mapped[float] = mapped_column(Float, nullable=False)
    gc_content: Mapped[float] = mapped_column(Float, nullable=False)
    duplication_rate: Mapped[float] = mapped_column(Float, nullable=False)
    adapter_content: Mapped[float] = mapped_column(Float, nullable=False)
    mean_read_quality: Mapped[float] = mapped_column(Float, nullable=False)
    qc_status: Mapped[str] = mapped_column(String(10), nullable=False)

    sample: Mapped[Sample] = relationship(back_populates="qc_metric")
