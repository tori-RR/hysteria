# RR Hysteria security rebuild

Personal fork of HyNetworks/hysteria. No proxy protocol changes.

Branch `rr/go1.27.3` pins upstream `app/v2.13.0` at `ca8fbd874fd6ca82413948de6dc5924405e103e1` and builds Linux amd64 using Go 1.27.3 (CGO disabled). Run `python3 rr-build.py` with that exact Go on PATH. The script verifies dependencies, tests `app/cmd`, builds the binary, and emits SHA256SUMS, build-info and provenance under ignored `rr-dist/`. Go may update workspace checksums without changing dependency versions.

Distribution version: `v2.13.0-rr-go1.27.3`. This is not an official upstream release. A newer compiler does not certify all dependencies as vulnerability-free. Binary assets belong in GitHub Releases, never Git source history. No VPS configuration, credentials or client subscriptions are stored here.
