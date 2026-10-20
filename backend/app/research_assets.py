"""Only published, cited, content-addressed illustration files are readable."""
import hashlib
import os
from pathlib import Path
import re
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from .research_db import get_research_session
from .research_http import ResearchError
from .research_v2 import require_release

router = APIRouter(prefix='/api/v2', tags=['research-assets'])


@router.get('/assets/{sha256}')
def asset(sha256: str, release_id: uuid.UUID | None = None, session=Depends(get_research_session)):
    release = require_release(session, release_id)
    if not re.fullmatch('[0-9a-f]{64}', sha256):
        raise ResearchError(404, 'asset-not-found', '找不到這份研究的圖解。')
    row = session.execute(text('''SELECT a.media_type,a.byte_size FROM research.assets a
        JOIN research.release_assets ra USING(sha256) WHERE ra.release_id=:r AND a.sha256=:sha LIMIT 1'''),
        {'r': release['release_id'], 'sha': sha256}).mappings().first()
    path = Path(os.getenv('RESEARCH_ASSET_ROOT', '/home/app/research-assets')) / sha256
    if not row:
        raise ResearchError(404, 'asset-not-found', '找不到這份研究的圖解。')
    if path.is_symlink() or not path.is_file() or path.stat().st_size != row['byte_size'] or hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
        raise ResearchError(503, 'asset-unavailable', '圖解目前無法讀取，研究文字仍可閱讀。', True)
    return FileResponse(path, media_type=row['media_type'], headers={
        'Cache-Control': 'public,max-age=86400,immutable', 'ETag': '"' + sha256 + '"',
        'Content-Security-Policy': "default-src 'none'; sandbox"})
