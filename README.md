# BezotCorp APT Repository

Public APT repository for BezotCorp Debian packages.

This repository contains distribution artifacts and APT metadata only. Product source code remains in its own repository, and each distributed package remains subject to the licence and terms of its corresponding product.

## Repository layout

- `pool/main/` stores published Debian packages, grouped by package.
- `dists/stable/` stores APT metadata for the stable channel.
- `public/` stores public repository-signing material.

The repository is designed for multiple BezotCorp products, versions, and architectures.
