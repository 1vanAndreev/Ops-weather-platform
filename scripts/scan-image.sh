#!/usr/bin/env sh
set -eu

IMAGE="${1:-ops-weather-platform:local}"

echo "Scanning ${IMAGE} with Trivy"
trivy image --severity HIGH,CRITICAL --exit-code 1 "${IMAGE}"

