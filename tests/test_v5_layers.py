from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
JS=(BASE/'site/app.js').read_text()
HTML=(BASE/'site/index.html').read_text()

def test_layer_controls_exist():
    for name in ['layerPolls','layerRoots','layerNews','layerFinance','layerDebates','layerLegislation']:
        assert f'id="{name}"' in HTML
        assert name in JS

def test_map_data_layers_present():
    assert 'mapEvents' in JS
    assert 'renderMapEvents()' in JS
    assert 'snapshot.finance' in JS and 'snapshot.news' in JS
    assert 'snapshot.debates' in JS and 'snapshot.legislation' in JS

def test_vines_share_topic_only():
    assert "const key=f.poll.state+':'+f.poll.topic" in JS
    assert 'groups.get(key)' in JS
    assert 'stateLayer(stems,code)' in JS
    assert 'Shared published-survey issue' in JS
    assert 'flowerPos[i-1]' not in JS

def test_empty_data_is_honest():
    assert 'State-associated evidence is pinned within borders' in JS
    assert 'mapPollSelection()' in JS
    assert 'A published filing or candidate-cycle aggregate' in JS
    assert 'not a representative public-opinion measurement' in JS

def test_debate_in_current_snapshot_has_original_url():
    data=json.loads((BASE/'site/data/snapshot.json').read_text())
    assert data['debates']
    assert all(d.get('source_url','').startswith('https://') and d.get('state') for d in data['debates'])
