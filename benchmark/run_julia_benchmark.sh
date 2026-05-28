#!/bin/bash
# Julia Sorting benchmarks (serial: 1 thread, parallel: 64 threads) via BenchmarkTools.jl.
#
# Default BENCHMARK_SIZES: 1e3..1e6 (2×/4×/8× steps). Wall clock: BENCHMARK_TIMEOUT_SEC (default 600)
# for the combined serial + parallel run (same total cap as C++/Python).
#
# Large arrays without huge test files:
#   export USE_CUDA_DATA=1
#   export BENCHMARK_SIZES=1000000    # or 1000000,10000000
#   export FORCE_CPU_DATA=1         # optional: skip GPU; chunked CPU RNG
#
# One-time on a new machine:
#   julia --project=/path/to/Sorting -e 'using Pkg; Pkg.instantiate()'

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SORT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BENCHMARK_SCRIPT="$SCRIPT_DIR/julia_benchmark.jl"
TEST_DATA_DIR="$SCRIPT_DIR/../test_data"

export BENCHMARK_SIZES="${BENCHMARK_SIZES:-1000,10000,20000,40000,80000,100000,200000,400000,800000,1000000}"
export BENCHMARK_TIMEOUT_SEC="${BENCHMARK_TIMEOUT_SEC:-600}"
export USE_CUDA_DATA="${USE_CUDA_DATA:-0}"

run_with_timeout() {
  local to="${BENCHMARK_TIMEOUT_SEC:?}"
  if command -v timeout &>/dev/null; then
    timeout "$to" "$@"
  elif command -v gtimeout &>/dev/null; then
    gtimeout "$to" "$@"
  else
    python3 - "$to" "$@" <<'PY'
import subprocess, sys
to = int(sys.argv[1])
cmd = sys.argv[2:]
try:
    subprocess.run(cmd, check=True, timeout=to)
except subprocess.TimeoutExpired:
    print(f"Benchmark timed out after {to}s", file=sys.stderr)
    sys.exit(124)
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
PY
  fi
}

if ! declare -p JULIA_CMD &>/dev/null || [[ ${#JULIA_CMD[@]} -eq 0 ]]; then
    JULIA_CMD=(julia --project="$SORT_ROOT")
fi

if ! command -v julia &>/dev/null; then
    echo "Error: julia not found"
    exit 1
fi

if [[ "${USE_CUDA_DATA}" != "1" ]]; then
    if [ ! -d "$TEST_DATA_DIR" ] || [ -z "$(ls -A "$TEST_DATA_DIR"/*.txt 2>/dev/null)" ]; then
        echo "Generating test data under $TEST_DATA_DIR (set USE_CUDA_DATA=1 to skip)..."
        export BENCHMARK_SIZES
        python3 "$SCRIPT_DIR/test_data_generator.py"
    fi
fi

if ! "${JULIA_CMD[@]}" -e 'using BenchmarkTools; using Statistics' >/dev/null 2>&1; then
    echo "Julia dependencies are not initialized for $SORT_ROOT."
    echo "Run: julia --project=\"$SORT_ROOT\" -e 'using Pkg; Pkg.instantiate()'"
    exit 1
fi

echo "=========================================="
echo " Julia Sorting Benchmark"
echo " BENCHMARK_SIZES=$BENCHMARK_SIZES  BENCHMARK_TIMEOUT_SEC=$BENCHMARK_TIMEOUT_SEC  USE_CUDA_DATA=$USE_CUDA_DATA"
echo "=========================================="

JULIA_CMD_QUOTED="$(printf '%q ' "${JULIA_CMD[@]}")"
BENCHMARK_SCRIPT_QUOTED="$(printf '%q' "$BENCHMARK_SCRIPT")"

run_with_timeout bash -c "
set -euo pipefail
echo ''
echo 'Step 1: SERIAL (1 thread)...'
echo '---------------------------------------------------'
${JULIA_CMD_QUOTED} -t 1 ${BENCHMARK_SCRIPT_QUOTED} serial
echo ''
echo '=========================================='
echo ''
echo 'Step 2: PARALLEL (64 threads)...'
echo '------------------------------------------------------'
${JULIA_CMD_QUOTED} -t 64 ${BENCHMARK_SCRIPT_QUOTED} parallel
"

echo ""
echo "=========================================="
echo "Benchmark complete!"
echo "=========================================="
