#!/usr/bin/env python3
"""Build the pinned upstream Hysteria release with an explicit Go toolchain."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
UPSTREAM = 'ca8fbd874fd6ca82413948de6dc5924405e103e1'
GO_VERSION = 'go1.27.3'
VERSION = 'v2.13.0-rr-go1.27.3'

def run(args, **kw):
    return subprocess.check_output(args, cwd=ROOT / 'app', text=True, **kw)

def main():
    env = dict(os.environ, GOTOOLCHAIN='local', CGO_ENABLED='0', GOOS='linux', GOARCH='amd64', GOAMD64='v1')
    assert run(['go', 'env', 'GOVERSION'], env=env).strip() == GO_VERSION, 'Go version mismatch'
    assert run(['git', 'rev-parse', 'HEAD:app']).strip() == run(['git', 'rev-parse', UPSTREAM + ':app']).strip(), 'Upstream app code changed'
    run(['go', 'mod', 'verify'], env=env)
    run(['go', 'test', './cmd/...'], env=env)
    output = ROOT / 'rr-dist'
    output.mkdir(exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    fields = {'appVersion': VERSION, 'appType': 'rr-security-rebuild', 'appDate': stamp,
              'appToolchain': GO_VERSION + ' linux/amd64', 'appCommit': run(['git', 'rev-parse', 'HEAD']).strip(),
              'appPlatform': 'linux', 'appArch': 'amd64', 'libVersion': 'v0.63.1-0.20261004180939-a10df75c260c'}
    flags = '-s -w ' + ' '.join('-X "github.com/apernet/hysteria/app/v2/cmd.' + k + '=' + v + '"' for k, v in fields.items())
    binary = output / 'hysteria-linux-amd64'
    run(['go', 'build', '-trimpath', '-ldflags', flags, '-o', str(binary), '.'], env=env)
    info = run(['go', 'version', '-m', str(binary)], env=env)
    assert info.splitlines()[0].endswith(GO_VERSION)
    (output / 'build-info.txt').write_text(info + '\n' + run([str(binary), 'version']))
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(digest + '  ' + binary.name + '\n')
    (output / 'provenance.json').write_text(json.dumps({'upstream_repository': 'HyNetworks/hysteria', 'upstream_tag': 'app/v2.13.0', 'upstream_commit': UPSTREAM, 'fork_commit': fields['appCommit'], 'go': GO_VERSION, 'version': VERSION, 'built_at': stamp, 'sha256': digest, 'target': 'linux/amd64', 'cgo': False, 'tests': 'go mod verify; go test ./cmd/...'}, indent=2) + '\n')
    print(digest, binary)

if __name__ == '__main__':
    main()
