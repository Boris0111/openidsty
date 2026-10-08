from datetime import datetime, timezone
from sqlalchemy import String, JSON, DateTime, ForeignKey, UniqueConstraint, Text, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def now():
    return datetime.now(timezone.utc)

class Segment(Base):
    __tablename__ = 'segments'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    layer: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[int]
    data: Mapped[dict] = mapped_column(JSON)
    prose: Mapped[str] = mapped_column(Text)

class Theme(Base):
    __tablename__ = 'themes'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    prose: Mapped[str] = mapped_column(Text, default='')
    checked: Mapped[str | None] = mapped_column(String(10))

class Company(Base):
    __tablename__ = 'companies'
    ticker: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    cik: Mapped[str | None] = mapped_column(String(10))

class Role(Base):
    __tablename__ = 'roles'
    ticker: Mapped[str] = mapped_column(ForeignKey('companies.ticker'), primary_key=True)
    segment_id: Mapped[str] = mapped_column(ForeignKey('segments.id'), primary_key=True)
    role: Mapped[str] = mapped_column(Text)
    tier: Mapped[int]

class Relation(Base):
    __tablename__ = 'relations'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    source: Mapped[str] = mapped_column(ForeignKey('companies.ticker'), index=True)
    target: Mapped[str] = mapped_column(ForeignKey('companies.ticker'), index=True)
    kind: Mapped[str] = mapped_column(String(30))
    direction: Mapped[str] = mapped_column(String(20))
    review_status: Mapped[str] = mapped_column(String(20))
    relevance: Mapped[str] = mapped_column(String(20))
    data: Mapped[dict] = mapped_column(JSON)

class Source(Base):
    __tablename__ = 'sources'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default='not_run')
    last_attempt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)
    new_count: Mapped[int] = mapped_column(Integer, default=0)
    data: Mapped[dict] = mapped_column(JSON, default=dict)

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = (UniqueConstraint('source_id', 'external_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey('sources.id'), index=True)
    external_id: Mapped[str] = mapped_column(String(500))
    ticker: Mapped[str | None] = mapped_column(ForeignKey('companies.ticker'), index=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(30))
    lifecycle: Mapped[str] = mapped_column(String(20), default='published')
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    published_precision: Mapped[str] = mapped_column(String(20), default='unknown')
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_semantics: Mapped[str] = mapped_column(String(30), default='unknown')
    period: Mapped[str | None] = mapped_column(String(80))
    basis: Mapped[str | None] = mapped_column(Text)
    routine: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rules_version: Mapped[str | None] = mapped_column(String(40))
    identity: Mapped[str | None] = mapped_column(String(64), unique=True)
    feeds: Mapped[list] = mapped_column(JSON, default=list)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    url: Mapped[str] = mapped_column(Text)
    mentioned: Mapped[list] = mapped_column(JSON, default=list)
    raw: Mapped[dict] = mapped_column(JSON)

class EventSegment(Base):
    __tablename__ = 'event_segments'
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)
    segment_id: Mapped[str] = mapped_column(ForeignKey('segments.id', ondelete='CASCADE'), primary_key=True)
    relevance: Mapped[str] = mapped_column(String(20))
    evidence: Mapped[list] = mapped_column(JSON)

class EventTheme(Base):
    __tablename__ = 'event_themes'
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)
    theme_id: Mapped[str] = mapped_column(ForeignKey('themes.id', ondelete='CASCADE'), primary_key=True)
    relevance: Mapped[str] = mapped_column(String(20))
    evidence: Mapped[list] = mapped_column(JSON)

class Financial(Base):
    __tablename__ = 'financials'
    __table_args__ = (UniqueConstraint('ticker', 'source_id', 'period', 'basis'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(ForeignKey('companies.ticker'), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey('sources.id'))
    period: Mapped[str] = mapped_column(String(30))
    period_end: Mapped[str] = mapped_column(String(10), index=True)
    basis: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(10))
    revenue: Mapped[float | None] = mapped_column(Float)
    revenue_yoy: Mapped[float | None] = mapped_column(Float)
    gross_margin: Mapped[float | None] = mapped_column(Float)
    eps: Mapped[float | None] = mapped_column(Float)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    url: Mapped[str] = mapped_column(Text)
    raw: Mapped[dict] = mapped_column(JSON)

class IngestionRun(Base):
    __tablename__ = 'ingestion_runs'
    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    results: Mapped[dict] = mapped_column(JSON, default=dict)
