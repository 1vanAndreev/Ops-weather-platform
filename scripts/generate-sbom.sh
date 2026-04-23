#!/usr/bin/env sh
set -eu

IMAGE="${1:-ops-weather-platform:local}"
OUTPUT="${2:-sbom.spdx.json}"

echo "Generating SBOM for ${IMAGE} into ${OUTPUT}"
syft "${IMAGE}" -o spdx-json="${OUTPUT}"

