"""Bring previously collected data from a V6/V7 install into the next garden.
Usage: python tools/import_existing_snapshot.py '/path/to/old/site/data/snapshot.json'
"""
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'worker'))
from audit import audit_snapshot


def import_snapshot(source, destination=None):
    src=Path(source).expanduser().resolve()
    dest=Path(destination) if destination else ROOT/'site/data/snapshot.json'
    if not src.is_file():
        raise ValueError('Old snapshot file not found: '+str(src))
    incoming=json.loads(src.read_text(encoding='utf-8'))
    if not isinstance(incoming.get('polls'),list):
        raise ValueError('The old snapshot is missing its polls list.')
    issues=audit_snapshot(incoming)
    if issues:
        raise ValueError('Old snapshot failed the project data audit; no files were changed: '+ '; '.join(issues[:4]))
    original=json.loads(dest.read_text()) if dest.exists() else {}
    if len(incoming.get('polls',[])) < len(original.get('polls',[])):
        raise ValueError('Old snapshot has fewer polls than destination. Refusing to overwrite newer data.')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():shutil.copy2(dest,dest.with_suffix(dest.suffix+'.backup'))
    # Atomic replacement so interrupted transfer does not truncate the snapshot.
    temp=dest.with_suffix('.importing')
    temp.write_text(json.dumps(incoming,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    temp.replace(dest)
    return {key:len(incoming.get(key,[])) for key in ('polls','finance','legislation','debates','news')}

if __name__=='__main__':
    if len(sys.argv)!=2:
        print('Usage: python tools/import_existing_snapshot.py "/path/to/old/site/data/snapshot.json"')
        raise SystemExit(2)
    try:
        result=import_snapshot(sys.argv[1]);print('Imported your existing garden records:',json.dumps(result))
        print('Previous V8 snapshot preserved as site/data/snapshot.json.backup')
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as exc:
        print('Import stopped safely:',exc,file=sys.stderr);raise SystemExit(1)
