"""Production snapshot audit: reject unsafe/unverifiable imported records.

No credentials, network activity, or guessed values are used here.
"""
from __future__ import annotations
import datetime as dt
import json
import pathlib
import sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAP = ROOT / 'site/data/snapshot.json'
STATES = {r[0] for r in json.loads((ROOT / 'data/states.json').read_text())} | {'DC'}


def valid_https(value):
    try:
        p = urlparse(value)
        return p.scheme == 'https' and bool(p.netloc) and not p.username and not p.password
    except (TypeError, ValueError):
        return False


def audit_snapshot(data):
    problems = []
    if not isinstance(data, dict):
        return ['Snapshot must be a JSON object']
    harvest=data.get('harvest', [])
    if not isinstance(harvest, list):
        problems.append('harvest must be a list')
    else:
        if len(harvest) > 250:
            problems.append('harvest exceeds bounded display history')
        for i, entry in enumerate(harvest):
            if (not isinstance(entry, dict) or not isinstance(entry.get('id'), str)
                or entry.get('kind') not in ('polls', 'news', 'finance', 'legislation', 'debates')
                or entry.get('change') not in ('new', 'revised')
                or not isinstance(entry.get('source_id'), str)):
                problems.append(f'harvest[{i}] invalid event')
                continue
            try:
                dt.datetime.fromisoformat(str(entry['collected_at']).replace('Z', '+00:00'))
            except (ValueError, TypeError, KeyError):
                problems.append(f'harvest[{i}] invalid ingestion date')
    for group in ('polls', 'news', 'finance', 'legislation', 'debates', 'sources'):
        if not isinstance(data.get(group, []), list):
            problems.append(f'{group} must be a list')
            continue
        seen = set()
        for i, item in enumerate(data.get(group, [])):
            prefix = f'{group}[{i}]'
            if not isinstance(item, dict):
                problems.append(f'{prefix} is not an object'); continue
            key = item.get('id')
            if not isinstance(key, str) or not key:
                problems.append(f'{prefix} missing id')
            elif key in seen:
                problems.append(f'{group} duplicate id {key}')
            seen.add(key)
            state = item.get('state')
            if state is not None and state not in STATES:
                problems.append(f'{prefix} invalid state {state}')
            if group == 'polls':
                if not valid_https(item.get('source_url')):
                    problems.append(f'{prefix} missing secure evidence link')
                try:
                    pub = dt.date.fromisoformat(str(item['published_at'])[:10])
                    if pub > dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1):
                        problems.append(f'{prefix} publication in future')
                except (KeyError, ValueError, TypeError):
                    problems.append(f'{prefix} invalid publication date')
                answers = item.get('answers')
                if not isinstance(answers, list) or not answers:
                    problems.append(f'{prefix} no responses'); continue
                labels = set()
                for a in answers:
                    if not isinstance(a, dict):
                        problems.append(f'{prefix} invalid response'); continue
                    label = a.get('choice')
                    if not isinstance(label, str) or not label.strip() or label in labels:
                        problems.append(f'{prefix} missing or duplicate response label')
                    labels.add(label)
                    v = a.get('pct')
                    if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0 <= v <= 100):
                        problems.append(f'{prefix} invalid response share')
            if group in ('news','finance','legislation','debates'):
                link = item.get('source_url') or item.get('url')
                if not valid_https(link):
                    problems.append(f'{prefix} missing secure evidence link')
    return problems


def audit_file(path=SNAP):
    return audit_snapshot(json.loads(pathlib.Path(path).read_text()))


if __name__ == '__main__':
    errors = audit_file(pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else SNAP)
    if errors:
        print('Snapshot validation FAILED:')
        for item in errors: print(' -', item)
        raise SystemExit(1)
    print('Snapshot audit passed.')
