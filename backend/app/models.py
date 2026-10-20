from datetime import datetime, timezone
from sqlalchemy import String, JSON, DateTime, Date, Numeric, ForeignKey, UniqueConstraint, Text, Integer, Float, Boolean,Index
from datetime import date
from decimal import Decimal
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
    active: Mapped[bool] = mapped_column(Boolean,default=True,server_default='true')

class ThemeAssessmentVersion(Base):
    __tablename__ = 'theme_assessment_versions'
    __table_args__ = (UniqueConstraint('theme_id','version_number',name='uq_theme_version'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[str] = mapped_column(ForeignKey('themes.id'),index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSON)
    content_hash: Mapped[str] = mapped_column(String(64))
    reviewed: Mapped[str | None] = mapped_column(String(10))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=now)
    reason: Mapped[str] = mapped_column(Text)

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
    __table_args__ = (Index('ix_event_segments_scope_relevance','segment_id','relevance','event_id'),)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)
    segment_id: Mapped[str] = mapped_column(ForeignKey('segments.id', ondelete='CASCADE'), primary_key=True)
    relevance: Mapped[str] = mapped_column(String(20))
    evidence: Mapped[list] = mapped_column(JSON)

class EventTheme(Base):
    __tablename__ = 'event_themes'
    __table_args__ = (Index('ix_event_themes_scope_relevance','theme_id','relevance','event_id'),)
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

class Indicator(Base):
    __tablename__ = 'indicators'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    kind: Mapped[str] = mapped_column(String(20))
    unit: Mapped[str] = mapped_column(String(40))
    frequency: Mapped[str] = mapped_column(String(20))
    basis: Mapped[str] = mapped_column(String(40))
    data: Mapped[dict] = mapped_column(JSON)

class ThemeIndicator(Base):
    __tablename__ = 'theme_indicators'
    theme_id: Mapped[str] = mapped_column(ForeignKey('themes.id'), primary_key=True)
    indicator_id: Mapped[str] = mapped_column(ForeignKey('indicators.id'), primary_key=True)

class IndicatorObservation(Base):
    __tablename__ = 'indicator_observations'
    __table_args__ = (UniqueConstraint('identity', 'revision', name='uq_indicator_revision'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[str] = mapped_column(ForeignKey('indicators.id'), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey('sources.id'))
    identity: Mapped[str] = mapped_column(String(64), index=True)
    document_identity: Mapped[str] = mapped_column(String(500))
    dataset: Mapped[str] = mapped_column(String(100))
    entity: Mapped[str] = mapped_column(String(100))
    original_period: Mapped[str] = mapped_column(String(150))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date, index=True)
    basis: Mapped[str] = mapped_column(String(40))
    scope: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(40))
    currency: Mapped[str | None] = mapped_column(String(10))
    value: Mapped[Decimal] = mapped_column(Numeric(28, 8))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_precision: Mapped[str] = mapped_column(String(20), default='unknown')
    date_semantics: Mapped[str] = mapped_column(String(30), default='unknown')
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    url: Mapped[str] = mapped_column(Text)
    raw_excerpt: Mapped[str] = mapped_column(Text)
    raw: Mapped[dict] = mapped_column(JSON)
    revision: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64))
    valid: Mapped[bool] = mapped_column(Boolean, default=True)
    invalid_reason: Mapped[str | None] = mapped_column(Text)

class TechnicalDocument(Base):
    __tablename__ = 'technical_documents'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey('sources.id'), index=True)
    title: Mapped[str] = mapped_column(Text)
    doc_kind: Mapped[str] = mapped_column(String(40))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    data: Mapped[dict] = mapped_column(JSON)

class TechnicalObservation(Base):
    __tablename__ = 'technical_observations'
    __table_args__ = (UniqueConstraint('document_id','observation_key',name='uq_document_observation'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey('technical_documents.id'), index=True)
    observation_key: Mapped[str] = mapped_column(String(64))
    official_version: Mapped[str | None] = mapped_column(String(200))
    content_hash: Mapped[str] = mapped_column(String(64))
    raw_hash: Mapped[str | None] = mapped_column(String(64))
    parser_version: Mapped[str] = mapped_column(String(60))
    url: Mapped[str] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    data: Mapped[dict] = mapped_column(JSON)

class TechnicalReview(Base):
    __tablename__ = 'technical_reviews'
    __table_args__ = (UniqueConstraint('observation_id',name='uq_document_review'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey('technical_observations.id'),index=True)
    status: Mapped[str] = mapped_column(String(30))
    reviewed: Mapped[str | None] = mapped_column(String(10))
    reason: Mapped[str | None] = mapped_column(Text)
    version_id: Mapped[str | None] = mapped_column(String(100))
