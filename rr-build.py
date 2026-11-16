#!/usr/bin/env python3
"""Build the pinned upstream Hysteria release with an explicit Go toolchain."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
UPSTREAM = 'c2b181e0b0e72b077e4b0b7297735af14d1f9929'
GO_VERSION = 'go1.27.4'
VERSION = 'v2.14.0-rr-go1.27.4'

def run(args, **kw):
    return subprocess.check_output(args, cwd=ROOT / 'app', text=True, **kw)

def main():
    env = dict(os.environ, GOTOOLCHAIN='local', CGO_ENABLED='0', GOOS='linux', GOARCH='amd64', GOAMD64='v1')
    assert run(['go', 'env', 'GOVERSION'], env=env).strip() == GO_VERSION, 'Go version mismatch'
    assert run(['git', 'rev-parse', 'HEAD:app']).strip() == run(['git', 'rev-parse', UPSTREAM + ':app']).strip(), 'Upstream app code changed'
    for module in ('app', 'core', 'extras'):
        assert run(['git', 'rev-parse', 'HEAD:' + module]).strip() == run(['git', 'rev-parse', UPSTREAM + ':' + module]).strip(), 'Upstream module changed: ' + module
        subprocess.check_call(['go', 'mod', 'verify'], cwd=ROOT / module, env=env)
    run(['go', 'test', './cmd/...'], env=env)
    output = ROOT / 'rr-dist'
    output.mkdir(exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    fields = {'appVersion': VERSION, 'appType': 'rr-security-rebuild', 'appDate': stamp,
              'appToolchain': GO_VERSION + ' linux/amd64', 'appCommit': run(['git', 'rev-parse', 'HEAD']).strip(),
              'appPlatform': 'linux', 'appArch': 'amd64', 'libVersion': next(line.split()[1] for line in (ROOT / 'core/go.mod').read_text().splitlines() if line.strip().startswith('github.com/apernet/quic-go '))}
    flags = '-s -w ' + ' '.join('-X "github.com/apernet/hysteria/app/v2/cmd.' + k + '=' + v + '"' for k, v in fields.items())
    binary = output / 'hysteria-linux-amd64'
    run(['go', 'build', '-trimpath', '-ldflags', flags, '-o', str(binary), '.'], env=env)
    info = run(['go', 'version', '-m', str(binary)], env=env)
    assert info.splitlines()[0].endswith(GO_VERSION)
    (output / 'build-info.txt').write_text(info + '\n' + run([str(binary), 'version']))
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(digest + '  ' + binary.name + '\n')
    (output / 'provenance.json').write_text(json.dumps({'upstream_repository': 'HyNetworks/hysteria', 'upstream_tag': 'app/v2.14.0', 'upstream_commit': UPSTREAM, 'fork_commit': fields['appCommit'], 'go': GO_VERSION, 'version': VERSION, 'built_at': stamp, 'sha256': digest, 'target': 'linux/amd64', 'cgo': False, 'tests': 'go mod verify; go test ./cmd/...'}, indent=2) + '\n')
    print(digest, binary)

if __name__ == '__main__':
    main()
