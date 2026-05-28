#!/bin/bash
# Backward-compatible entry point → Julia sorting benchmark.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run_julia_benchmark.sh"
