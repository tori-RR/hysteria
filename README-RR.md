# RR Hysteria security rebuild

Personal fork of HyNetworks/hysteria. No proxy protocol changes.

Branch `rr/v2.14.0-go1.27.4` pins upstream `app/v2.14.0` at `c2b181e0b0e72b077e4b0b7297735af14d1f9929` and builds Linux amd64 using Go 1.27.4 (CGO disabled). Run `python3 rr-build.py` with that exact Go on PATH. The script verifies all three modules, tests `app/cmd`, builds the binary, and emits SHA256SUMS, build-info and provenance under ignored `rr-dist/`. Go may update workspace checksums without changing dependency versions. quic-go metadata is read from upstream core/go.mod.

Distribution version: `v2.14.0-rr-go1.27.4`. This is not an official upstream release. A newer compiler does not certify all dependencies as vulnerability-free. Binary assets belong in GitHub Releases, never Git source history. No VPS configuration, credentials or client subscriptions are stored here.
