#!/usr/bin/env python3
"""Cache public U.S. state topology locally, without credentials.

Uses the public us-atlas@3 Albers topology (Census-derived boundaries). This
script is an optional convenience: unsuccessful access leaves existing data
unchanged and the web app uses its labeled offline fallback.
"""
import json
import os
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'site/data/states-albers-10m.json'
SOURCE='https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json'
EXPECTED={1,2,4,5,6,8,9,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,48,49,50,51,53,54,55,56}

def valid(data):
    if not isinstance(data,dict) or data.get('type')!='Topology':return False
    arcs=data.get('arcs'); geometry=data.get('objects',{}).get('states',{}).get('geometries')
    if not isinstance(arcs,list) or not arcs or not isinstance(geometry,list):return False
    if len(geometry)!=51 or {int(x.get('id',-1)) for x in geometry}!=EXPECTED:return False
    return all(x.get('type') in ('Polygon','MultiPolygon') and x.get('arcs') for x in geometry)

def update():
    if TARGET.exists():
        try:
            if valid(json.loads(TARGET.read_text(encoding='utf-8'))):
                print('Accurate state geometry already cached; no download needed.')
                return 'cached'
        except (OSError,ValueError):pass
    try:
        req=urllib.request.Request(SOURCE,headers={'User-Agent':'GardenOfDemocracy-UniversityResearch/1.0'})
        with urllib.request.urlopen(req,timeout=12) as response:
            raw=response.read(3_000_001)
        if len(raw)>3_000_000:raise ValueError('Unexpectedly large state geometry')
        if not valid(json.loads(raw)):
            raise ValueError('Downloaded data failed geometry and 51-jurisdiction checks')
        temp=TARGET.with_suffix('.download')
        temp.write_bytes(raw)
        os.replace(temp,TARGET)
        print(f'Cached accurate state geometry ({len(raw):,} bytes) to {TARGET.relative_to(ROOT)}')
        return 'downloaded'
    except (OSError,ValueError,TimeoutError,UnicodeError) as error:
        print('Accurate state boundary cache unavailable:',error)
        print('Website stays usable using stationary state-centroid markers when necessary.')
        return 'unavailable'

if __name__=='__main__': update()
