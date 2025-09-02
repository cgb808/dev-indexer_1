import json, os, tempfile, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'training' / 'jarvis_mix' / 'build_jarvis_mix.py'
MANIFEST = ROOT / 'training' / 'jarvis_mix' / 'mix_manifest.example.json'


def test_builder_runs():
    out = tempfile.NamedTemporaryFile(delete=False).name
    cmd = [sys.executable, str(BUILDER), '--manifest', str(MANIFEST), '--output', out, '--seed', '123']
    subprocess.check_call(cmd)
    # Basic assertions
    lines = open(out).read().strip().splitlines()
    assert lines, 'no output'
    first = json.loads(lines[0])
    assert 'messages' in first and 'meta' in first
    assert '__builder' in first
    os.remove(out)
