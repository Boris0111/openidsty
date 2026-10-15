#!/usr/bin/env python3
"""產業地圖結構驗證器。

只檢查結構，不檢查內容正確性。欄位定義見 industry-map/README.md。

用法:
    python scripts/validate_map.py              # 全量檢查
    python scripts/validate_map.py --skip-prose # 只檢查 frontmatter
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date as calendar_date
from urllib.parse import urlsplit
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAP_DIR = ROOT / "industry-map"
SEGMENT_DIRS = ("ai-server", "semiconductor")
THEMES_DIR = "themes"
SOURCES_FILE = "sources.yaml"

LAYERS = {"ai-server", "semiconductor"}
THEME_STATUSES = ("emerging", "validating", "scaling", "mature", "fading")
MARKETS = ("TW", "US", "KR", "JP", "HK", "DE", "NL")
PRESENCE = ("present", "none")
SOURCE_TYPES = ("filings", "earnings_call", "industry_media", "official_stats")

SEGMENT_PROSE = ("環節定義", "技術變數", "玩家格局", "傳導鏈", "監測指標", "風險")
THEME_PROSE = ("狀態判定依據",)

SEGMENT_FIELDS = (
    "segment", "name_zh", "layer", "position", "market_coverage",
    "companies", "upstream", "downstream", "themes", "kpis", "signals",
)
THEME_FIELDS = ("theme", "name_zh", "status", "segments", "beneficiaries", "milestones")

# 代號格式 -> 市場。各式互斥；市場為 None 表示未上市主體。
TICKER_FORMS = (
    (re.compile(r"^\d{4}\.TW$"), "TW"),
    (re.compile(r"^\d{4}\.TWO$"), "TW"),
    (re.compile(r"^[A-Z]{1,5}$"), "US"),
    (re.compile(r"^\d{6}\.KS$"), "KR"),
    (re.compile(r"^[0-9A-Z]{4}\.T$"), "JP"),
    (re.compile(r"^\d{4,5}\.HK$"), "HK"),
    (re.compile(r"^[A-Z0-9]{1,6}\.DE$"), "DE"),
    (re.compile(r"^[A-Z0-9]{1,6}\.AS$"), "NL"),
    (re.compile(r"^PRIVATE:[a-z0-9-]+$"), None),
)
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}(-Q[1-4]|-\d{2})?$")
CHECKED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.S)


class Errors:
    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def add(self, path, message: str) -> None:
        if isinstance(path, Path):
            try:
                rel = path.relative_to(ROOT).as_posix()
            except ValueError:
                rel = path.as_posix()
        else:
            rel = str(path)
        self.items.append((rel, message))

    def __bool__(self) -> bool:
        return bool(self.items)


def ticker_market(ticker: str):
    """回傳 (格式是否合法, 所屬市場或 None 表示未上市)。"""
    for pattern, market in TICKER_FORMS:
        if pattern.match(ticker):
            return True, market
    return False, None


def parse_doc(path: Path, errors: Errors):
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.add(path, "缺少 YAML frontmatter（檔案須以 --- 開頭並以 --- 結束該區塊）")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.add(path, "frontmatter YAML 解析失敗: {}".format(exc))
        return None
    if not isinstance(data, dict):
        errors.add(path, "frontmatter 必須是一個對應表（mapping）")
        return None
    return data, match.group(2)


def check_required(path: Path, data: dict, fields, errors: Errors) -> None:
    for field in fields:
        if field not in data:
            errors.add(path, "缺少必填欄位: {}".format(field))
        elif data[field] is None:
            errors.add(path, "必填欄位為空: {}".format(field))


def check_list(path: Path, data: dict, field: str, errors: Errors, min_len: int = 0, report: bool = True):
    value = data.get(field)
    if value is None:
        return []
    if not isinstance(value, list):
        if report:
            errors.add(path, "欄位 {} 必須是陣列".format(field))
        return []
    if report and len(value) < min_len:
        errors.add(path, "欄位 {} 至少需要 {} 筆，目前 {} 筆".format(field, min_len, len(value)))
    return value


def check_prose(path: Path, body: str, required, errors: Errors) -> None:
    found = re.findall(r"^##\s+(.+?)\s*$", body, re.M)
    for heading in required:
        if heading not in found:
            errors.add(path, "缺少必要段落: ## {}".format(heading))
    present = [h for h in found if h in required]
    expected = [h for h in required if h in found]
    if present != expected:
        errors.add(
            path,
            "段落順序須為 {}，目前為 {}".format(" → ".join(required), " → ".join(present)),
        )


def load_segments(errors: Errors):
    segments = {}
    for dirname in SEGMENT_DIRS:
        directory = MAP_DIR / dirname
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            parsed = parse_doc(path, errors)
            if parsed is None:
                continue
            data, body = parsed
            check_required(path, data, SEGMENT_FIELDS, errors)
            seg_id = data.get("segment")
            if not isinstance(seg_id, str) or not ID_RE.match(seg_id):
                errors.add(path, "segment 識別碼須為 kebab-case: {!r}".format(seg_id))
                continue
            if seg_id != path.stem:
                errors.add(path, "segment ({}) 與檔名 ({}) 不一致".format(seg_id, path.stem))
            if seg_id in segments:
                errors.add(path, "segment 識別碼重複: {}（另見 {}）".format(seg_id, segments[seg_id]["_rel"]))
                continue
            layer = data.get("layer")
            if layer not in LAYERS:
                errors.add(path, "layer 須為 {}，目前為 {!r}".format(" | ".join(sorted(LAYERS)), layer))
            elif layer != dirname:
                errors.add(path, "layer ({}) 與所在目錄 ({}) 不一致".format(layer, dirname))
            position = data.get("position")
            if not isinstance(position, int) or isinstance(position, bool) or not 1 <= position <= 99:
                errors.add(path, "position 須為 1–99 的整數，目前為 {!r}".format(position))
            check_companies(path, data, errors)
            check_market_coverage(path, data, errors)
            for field in ("upstream", "downstream", "themes"):
                check_list(path, data, field, errors)
            for field in ("kpis", "signals"):
                check_list(path, data, field, errors, min_len=1)
            up = check_list(path, data, "upstream", errors, report=False)
            down = check_list(path, data, "downstream", errors, report=False)
            if not up and not down:
                errors.add(path, "孤島環節：upstream 與 downstream 皆為空，未連接到地圖其他部分")
            data["_path"] = path
            data["_rel"] = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
            data["_body"] = body
            segments[seg_id] = data
    return segments


def check_companies(path: Path, data: dict, errors: Errors) -> None:
    companies = check_list(path, data, "companies", errors, min_len=1)
    markets = set()
    for index, entry in enumerate(companies):
        label = "companies[{}]".format(index)
        if not isinstance(entry, dict):
            errors.add(path, "{} 必須是對應表".format(label))
            continue
        for field in ("ticker", "name_zh", "role", "tier"):
            if field not in entry or entry[field] is None:
                errors.add(path, "{} 缺少必填欄位: {}".format(label, field))
        ticker = entry.get("ticker")
        if isinstance(ticker, str):
            valid, market = ticker_market(ticker)
            if not valid:
                errors.add(path, "{} 代號格式不符規範: {!r}（見 README 代號格式）".format(label, ticker))
            elif market:
                markets.add(market)
        elif ticker is not None:
            errors.add(path, "{} ticker 須為字串（數字開頭的代號需加引號）".format(label))
        tier = entry.get("tier")
        if tier is not None and (not isinstance(tier, int) or isinstance(tier, bool) or not 1 <= tier <= 3):
            errors.add(path, "{} tier 須為 1–3 的整數，目前為 {!r}".format(label, tier))
    data["_markets"] = markets


def check_market_coverage(path: Path, data: dict, errors: Errors) -> None:
    coverage = data.get("market_coverage")
    if not isinstance(coverage, dict):
        if coverage is not None:
            errors.add(path, "market_coverage 必須是對應表，含 tw 與 us")
        return
    markets = data.get("_markets", set())
    for key, code in (("tw", "TW"), ("us", "US")):
        value = coverage.get(key)
        if value not in PRESENCE:
            errors.add(path, "market_coverage.{} 須為 {}，目前為 {!r}".format(key, " | ".join(PRESENCE), value))
            continue
        has = code in markets
        if value == "present" and not has:
            errors.add(path, "market_coverage.{} 宣告 present，但 companies 無任何 {} 市場的代號".format(key, code))
        if value == "none" and has:
            errors.add(path, "market_coverage.{} 宣告 none，但 companies 含 {} 市場的代號".format(key, code))
    led_by = coverage.get("led_by")
    if led_by is None:
        return
    if not isinstance(led_by, list):
        errors.add(path, "market_coverage.led_by 必須是陣列")
        return
    for code in led_by:
        if code not in MARKETS:
            errors.add(path, "market_coverage.led_by 含未知市場代碼 {!r}（可用 {}）".format(code, ", ".join(MARKETS)))
        elif code not in markets:
            errors.add(path, "market_coverage.led_by 列出 {}，但 companies 無該市場的代號".format(code))


def load_themes(errors: Errors):
    themes = {}
    directory = MAP_DIR / THEMES_DIR
    if not directory.is_dir():
        return themes
    for path in sorted(directory.glob("*.md")):
        parsed = parse_doc(path, errors)
        if parsed is None:
            continue
        data, body = parsed
        check_required(path, data, THEME_FIELDS, errors)
        theme_id = data.get("theme")
        if not isinstance(theme_id, str) or not ID_RE.match(theme_id):
            errors.add(path, "theme 識別碼須為 kebab-case: {!r}".format(theme_id))
            continue
        if theme_id != path.stem:
            errors.add(path, "theme ({}) 與檔名 ({}) 不一致".format(theme_id, path.stem))
        if theme_id in themes:
            errors.add(path, "theme 識別碼重複: {}".format(theme_id))
            continue
        status = data.get("status")
        if status not in THEME_STATUSES:
            errors.add(path, "status 須為 {}，目前為 {!r}".format(" | ".join(THEME_STATUSES), status))
        check_list(path, data, "segments", errors, min_len=1)
        check_list(path, data, "beneficiaries", errors, min_len=1)
        check_milestones(path, data, errors)
        data["_path"] = path
        data["_body"] = body
        themes[theme_id] = data
    return themes


def check_milestones(path: Path, data: dict, errors: Errors) -> None:
    identifiers = set()
    for index, entry in enumerate(check_list(path, data, "milestones", errors, min_len=1)):
        label = "milestones[{}]".format(index)
        if not isinstance(entry, dict):
            errors.add(path, "{} 必須是對應表".format(label))
            continue
        for field in ("date", "event", "evidence"):
            if field not in entry or entry[field] is None:
                errors.add(path, "{} 缺少必填欄位: {}".format(label, field))
        date = entry.get("date")
        if date is not None and not DATE_RE.match(str(date)):
            errors.add(path, "{}.date 須為 YYYY、YYYY-Qn 或 YYYY-MM，目前為 {!r}".format(label, date))
        if 'id' in entry:
            identifier = entry['id']
            if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
                errors.add(path, f'{label}.id 須為 kebab-case')
            elif identifier in identifiers:
                errors.add(path, f'{label}.id 里程碑識別碼重複')
            else:
                identifiers.add(identifier)


def check_assessments(segments: dict, themes: dict, errors: Errors, skip_prose=False) -> None:
    """References and shape only; source content and economic reasoning need review."""
    source_ids = set()
    try:
        registry = yaml.safe_load((MAP_DIR / SOURCES_FILE).read_text(encoding='utf-8'))
        if isinstance(registry, dict):
            for groups in registry.values():
                if isinstance(groups, dict):
                    for entries in groups.values():
                        if isinstance(entries, list):
                            source_ids.update(e['id'] for e in entries if isinstance(e, dict) and isinstance(e.get('id'), str))
    except (OSError, yaml.YAMLError):
        pass  # check_sources reports the registry error.
    confidence = {'well-supported', 'inference', 'needs-verification'}
    for theme in themes.values():
        if 'assessment' not in theme:
            continue
        path, assessment = theme['_path'], theme['assessment']
        if not isinstance(assessment, dict):
            errors.add(path, 'assessment 須為對應表'); continue

        def text(value, label):
            if not isinstance(value, str) or not value.strip():
                errors.add(path, f'assessment.{label} 須為非空文字')

        def day(value, label, nullable=False):
            if value is None and nullable:
                return
            try:
                if not isinstance(value, str) or not CHECKED_RE.fullmatch(value):
                    raise ValueError()
                calendar_date.fromisoformat(value)
            except ValueError:
                errors.add(path, f'assessment.{label} 須為有效 YYYY-MM-DD')

        def items(key, minimum=0):
            value = assessment.get(key)
            if not isinstance(value, list) or len(value) < minimum:
                errors.add(path, f'assessment.{key} 須為陣列且至少 {minimum} 筆')
                return []
            return value

        def identified(key, minimum=0):
            result = {}
            for i, value in enumerate(items(key, minimum)):
                label = f'{key}[{i}]'
                if not isinstance(value, dict):
                    errors.add(path, f'assessment.{label} 須為對應表'); continue
                identifier = value.get('id')
                if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
                    errors.add(path, f'assessment.{label}.id 須為 kebab-case'); continue
                if identifier in result:
                    errors.add(path, f'assessment.{label}.id 識別碼重複'); continue
                result[identifier] = value
            return result

        def refs(value, known, label, minimum=1):
            if not isinstance(value, list) or len(value) < minimum:
                errors.add(path, f'assessment.{label} 須為陣列且至少 {minimum} 筆'); return
            for reference in value:
                if not isinstance(reference, str) or reference not in known:
                    errors.add(path, f'assessment.{label} 引用不存在的識別碼: {reference}')

        text(assessment.get('summary'), 'summary')
        if not isinstance(assessment.get('confidence'), str) or assessment['confidence'] not in confidence:
            errors.add(path, 'assessment.confidence 不合法')
        day(assessment.get('reviewed'), 'reviewed')
        checked = re.search(r'查核日期[：:]\s*(\d{4}-\d{2}-\d{2})', theme['_body'])
        if not skip_prose and (not checked or checked[1] != assessment.get('reviewed')):
            errors.add(path, 'assessment.reviewed 與散文查核日期不一致')
        for key, minimum in [('conditions', 1), ('gaps', 0)]:
            for i, value in enumerate(items(key, minimum)):
                text(value, f'{key}[{i}]')
        for i, value in enumerate(items('next_checks', 1)):
            if not isinstance(value, dict):
                errors.add(path, f'assessment.next_checks[{i}] 須為對應表'); continue
            for key in ('question', 'evidence_required'):
                text(value.get(key), f'next_checks[{i}].{key}')
        evidence = identified('evidence', 1)
        for identifier, value in evidence.items():
            label = f'evidence.{identifier}'
            if not isinstance(value.get('source_id'), str) or value['source_id'] not in source_ids:
                errors.add(path, f'assessment.{label}.source_id 引用不存在的來源')
            try:
                url = urlsplit(value.get('url', ''))
                valid_url = url.scheme == 'https' and bool(url.hostname) and not url.username and not url.password
            except (ValueError, TypeError, AttributeError):
                valid_url = False
            if not valid_url:
                errors.add(path, f'assessment.{label}.url 須為完整 HTTPS')
            for key in ('excerpt', 'period'):
                text(value.get(key), f'{label}.{key}')
            day(value.get('published'), f'{label}.published', nullable=True)
        claims = identified('claims', 1)
        for identifier, value in claims.items():
            label = f'claims.{identifier}'
            text(value.get('statement'), f'{label}.statement')
            if value.get('stance') not in ('supporting', 'counter') or not isinstance(value.get('confidence'), str) or value['confidence'] not in confidence:
                errors.add(path, f'assessment.{label} stance／confidence 不合法')
            refs(value.get('evidence_ids'), evidence, f'{label}.evidence_ids')
        for identifier, value in identified('paths').items():
            label = f'paths.{identifier}'
            text(value.get('mechanism'), f'{label}.mechanism')
            if value.get('direction') not in ('positive', 'negative', 'mixed', 'unknown'):
                errors.add(path, f'assessment.{label}.direction 不合法')
            if not isinstance(value.get('conditions'), list) or not value['conditions']:
                errors.add(path, f'assessment.{label}.conditions 至少一筆')
            else:
                for condition in value['conditions']: text(condition, f'{label}.conditions')
            refs(value.get('claim_ids'), claims, f'{label}.claim_ids')
            steps = value.get('steps')
            if not isinstance(steps, list) or not steps:
                errors.add(path, f'assessment.{label}.steps 至少一筆'); continue
            previous = None
            for i, step in enumerate(steps):
                valid = isinstance(step, dict)
                if valid:
                    origin, target, kind, via = (step.get(k) for k in ('from', 'to', 'type', 'via'))
                    valid = isinstance(origin, str) and isinstance(target, str) and origin in segments and target in segments and origin != target
                if valid and previous is not None and origin != previous: valid = False
                if valid:
                    if kind in ('upstream', 'downstream'):
                        valid = target in (segments[origin].get(kind) or [])
                    elif kind == 'theme':
                        valid = isinstance(via, str) and via in themes and origin in (themes[via].get('segments') or []) and target in (themes[via].get('segments') or [])
                    elif kind == 'sibling':
                        valid = isinstance(via, str) and via in segments and via in segments[origin]['downstream'] and target in segments[via]['upstream']
                    else: valid = False
                if not valid:
                    errors.add(path, f'assessment.{label}.steps[{i}] 傳導步驟不符合宣告關係')
                previous = step.get('to') if isinstance(step, dict) else None
        milestone_ids = {m['id'] for m in theme.get('milestones', []) if isinstance(m, dict) and isinstance(m.get('id'), str)}
        reviewed_milestones = set()
        for i, value in enumerate(items('milestone_reviews')):
            label = f'milestone_reviews[{i}]'
            if not isinstance(value, dict):
                errors.add(path, f'assessment.{label} 須為對應表'); continue
            milestone_id = value.get('milestone_id')
            if not isinstance(milestone_id, str) or milestone_id not in milestone_ids or milestone_id in reviewed_milestones:
                errors.add(path, f'assessment.{label}.milestone_id 無法解析或重複')
            if isinstance(milestone_id, str): reviewed_milestones.add(milestone_id)
            state = value.get('state')
            if state not in ('unconfirmed', 'confirmed', 'contradicted'):
                errors.add(path, f'assessment.{label}.state 不合法')
            text(value.get('note'), f'{label}.note')
            day(value.get('reviewed'), f'{label}.reviewed')
            day(value.get('occurred'), f'{label}.occurred', nullable=True)
            refs(value.get('evidence_ids'), evidence, f'{label}.evidence_ids', 1 if state in ('confirmed', 'contradicted') else 0)
        if 'change_reason' in assessment:
            text(assessment['change_reason'], 'change_reason')


def check_cross_refs(segments: dict, themes: dict, errors: Errors) -> None:
    all_tickers = set()
    for seg in segments.values():
        for entry in seg.get("companies") or []:
            if isinstance(entry, dict) and isinstance(entry.get("ticker"), str):
                all_tickers.add(entry["ticker"])

    for seg_id, seg in segments.items():
        path = seg["_path"]
        for field, mirror in (("upstream", "downstream"), ("downstream", "upstream")):
            for ref in seg.get(field) or []:
                if ref not in segments:
                    errors.add(path, "{} 引用不存在的環節: {}".format(field, ref))
                    continue
                if seg_id not in (segments[ref].get(mirror) or []):
                    errors.add(
                        path,
                        "單向關係：{}.{} 含 {}，但 {}.{} 未含 {}（需同時修正 {}）".format(
                            seg_id, field, ref, ref, mirror, seg_id, segments[ref]["_rel"]
                        ),
                    )
        for ref in seg.get("themes") or []:
            if ref not in themes:
                errors.add(path, "themes 引用不存在的題材: {}".format(ref))
            elif seg_id not in (themes[ref].get("segments") or []):
                errors.add(
                    path,
                    "單向關聯：{}.themes 含 {}，但題材 {}.segments 未含 {}".format(seg_id, ref, ref, seg_id),
                )

    for theme_id, theme in themes.items():
        path = theme["_path"]
        for ref in theme.get("segments") or []:
            if ref not in segments:
                errors.add(path, "segments 引用不存在的環節: {}".format(ref))
            elif theme_id not in (segments[ref].get("themes") or []):
                errors.add(
                    path,
                    "單向關聯：{}.segments 含 {}，但環節 {}.themes 未含 {}".format(theme_id, ref, ref, theme_id),
                )
        for ticker in theme.get("beneficiaries") or []:
            if ticker not in all_tickers:
                errors.add(path, "beneficiaries 的代號未出現在任何環節的 companies 中: {}".format(ticker))


def check_sources(segments: dict, themes: dict, errors: Errors) -> int:
    path = MAP_DIR / SOURCES_FILE
    if not path.is_file():
        return 0
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.add(path, "YAML 解析失敗: {}".format(exc))
        return 0
    if not isinstance(data, dict):
        errors.add(path, "最外層須為對應表，依市場分組（tw / us / ...）")
        return 0

    count = 0
    identifiers = set()
    for market, groups in data.items():
        if not isinstance(groups, dict):
            errors.add(path, "{} 之下須為對應表，依資料類型分組".format(market))
            continue
        for source_type, entries in groups.items():
            if source_type not in SOURCE_TYPES:
                errors.add(
                    path,
                    "{}.{} 為未知資料類型（可用 {}）".format(market, source_type, ", ".join(SOURCE_TYPES)),
                )
            if not isinstance(entries, list):
                errors.add(path, "{}.{} 之下須為陣列".format(market, source_type))
                continue
            for index, entry in enumerate(entries):
                count += 1
                label = "{}.{}[{}]".format(market, source_type, index)
                if not isinstance(entry, dict):
                    errors.add(path, "{} 必須是對應表".format(label))
                    continue
                for field in ("id", "name", "url", "type", "access", "reachability", "checked"):
                    if field not in entry or entry[field] is None:
                        errors.add(path, "{} 缺少必填欄位: {}".format(label, field))
                sid = entry.get('id')
                if not isinstance(sid, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', sid):
                    errors.add(path, '{}.id 須為 kebab-case'.format(label))
                elif sid in identifiers:
                    errors.add(path, '{}.id 來源識別碼重複: {}'.format(label, sid))
                else:
                    identifiers.add(sid)
                if not isinstance(entry.get('url'), str) or not entry['url'].startswith('https://'):
                    errors.add(path, '{}.url 須為 HTTPS'.format(label))
                ingestion = entry.get('ingestion')
                if ingestion is not None:
                    adapters = {'manual','tw','tsmc','delta','nvidia','microsoft','sec-submissions','sec-facts','rss','tpca','moea','census','eia','aaon-metrics','tsmc-metrics'}
                    if not isinstance(ingestion, dict) or ingestion.get('adapter') not in adapters:
                        errors.add(path, '{}.ingestion adapter 不合法'.format(label))
                    else:
                        for url_key in ('url','fallback'):
                            if ingestion.get(url_key) and (not isinstance(ingestion[url_key],str) or not ingestion[url_key].startswith('https://')):
                                errors.add(path, '{}.ingestion.{} 須為 HTTPS'.format(label,url_key))
                        pages = ingestion.get('max_pages',1)
                        if type(pages) is not int or not 1 <= pages <= 200:
                            errors.add(path, '{}.ingestion.max_pages 須為 1–200'.format(label))
                        if ingestion['adapter'] in ('aaon-metrics','tsmc-metrics'):
                            if type(ingestion.get('max_reports',8)) is not int or not 1<=ingestion.get('max_reports',8)<=8:
                                errors.add(path, '{}.ingestion.max_reports 須為 1–8'.format(label))
                            if type(ingestion.get('history_days',730)) is not int or not 1<=ingestion.get('history_days',730)<=730:
                                errors.add(path, '{}.ingestion.history_days 須為 1–730'.format(label))
                if entry.get("type") not in (None, source_type):
                    errors.add(
                        path,
                        "{}.type ({!r}) 與所在分組 ({}) 不一致".format(label, entry.get("type"), source_type),
                    )
                if entry.get("access") not in (None, "free"):
                    errors.add(
                        path,
                        "{}.access 為 {!r}：註冊表僅限免費公開來源，需付費或需 API key 的來源不得列入".format(
                            label, entry.get("access")
                        ),
                    )
                if entry.get("reachability") not in (None, "verified", "unverified"):
                    errors.add(
                        path,
                        "{}.reachability 須為 verified | unverified，目前為 {!r}".format(
                            label, entry.get("reachability")
                        ),
                    )
                checked = entry.get("checked")
                if checked is not None and not CHECKED_RE.match(str(checked)):
                    errors.add(path, "{}.checked 須為 YYYY-MM-DD，目前為 {!r}".format(label, checked))
                for key, known in [('segments', segments), ('themes', themes)]:
                    refs = entry.get(key, [])
                    if not isinstance(refs, list):
                        errors.add(path, '{}.{} 須為陣列'.format(label, key))
                        continue
                    for ref in refs:
                        if not isinstance(ref,str) or ref not in known:
                            errors.add(path, '{}.{} 引用不存在的{}: {}'.format(label, key, '環節' if key=='segments' else '題材', ref))
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="驗證產業地圖結構")
    parser.add_argument("--skip-prose", action="store_true", help="只檢查 frontmatter，供骨架階段使用")
    parser.add_argument("--map-dir", help="覆寫地圖目錄（供 fixture 測試使用）")
    args = parser.parse_args()

    global MAP_DIR
    if args.map_dir:
        MAP_DIR = Path(args.map_dir).resolve()

    if not MAP_DIR.is_dir():
        print("找不到地圖目錄: {}".format(MAP_DIR), file=sys.stderr)
        return 2

    errors = Errors()
    segments = load_segments(errors)
    themes = load_themes(errors)
    check_cross_refs(segments, themes, errors)
    source_count = check_sources(segments, themes, errors)
    check_assessments(segments, themes, errors, skip_prose=args.skip_prose)

    if not args.skip_prose:
        for seg in segments.values():
            check_prose(seg["_path"], seg["_body"], SEGMENT_PROSE, errors)
        for theme in themes.values():
            check_prose(theme["_path"], theme["_body"], THEME_PROSE, errors)

    mode = "frontmatter only" if args.skip_prose else "full"
    if errors:
        print("驗證失敗（{}）：{} 個問題\n".format(mode, len(errors.items)), file=sys.stderr)
        for rel, message in errors.items:
            print("  {}: {}".format(rel, message), file=sys.stderr)
        return 1

    print(
        "驗證通過（{}）：{} 個環節、{} 個題材、{} 筆來源".format(
            mode, len(segments), len(themes), source_count
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
