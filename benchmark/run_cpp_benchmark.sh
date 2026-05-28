#!/bin/bash
# Build and run C++ Sorting benchmarks (reads BENCHMARK_SIZES; default 1e3..1e6 incl. geometric steps).
# Wall clock: BENCHMARK_TIMEOUT_SEC (default 600). Uses timeout/gtimeout if present; else Python subprocess timeout.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CPP_SRC="$SCRIPT_DIR/cpp_benchmark.cpp"
CPP_BIN="$SCRIPT_DIR/cpp_benchmark"
TEST_DATA_DIR="$SCRIPT_DIR/../test_data"
export BENCHMARK_SIZES="${BENCHMARK_SIZES:-1000,10000,20000,40000,80000,100000,200000,400000,800000,1000000}"
export BENCHMARK_TIMEOUT_SEC="${BENCHMARK_TIMEOUT_SEC:-600}"

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

if ! command -v g++ &>/dev/null; then
    echo "Error: g++ not found"
    exit 1
fi

if [ ! -d "$TEST_DATA_DIR" ] || [ -z "$(ls -A "$TEST_DATA_DIR"/*.txt 2>/dev/null)" ]; then
    echo "Generating test data for BENCHMARK_SIZES=$BENCHMARK_SIZES..."
    python3 "$SCRIPT_DIR/test_data_generator.py"
fi

echo "=========================================="
echo " C++ Sorting Benchmark"
echo " BENCHMARK_SIZES=$BENCHMARK_SIZES  BENCHMARK_TIMEOUT_SEC=$BENCHMARK_TIMEOUT_SEC"
echo "=========================================="

echo "Building..."
if g++ -std=c++17 -O2 -fopenmp "$CPP_SRC" -o "$CPP_BIN"; then
    echo "Build succeeded (OpenMP)."
else
    echo "OpenMP build failed, trying without OpenMP..."
    g++ -std=c++17 -O2 "$CPP_SRC" -o "$CPP_BIN"
fi

echo ""
(cd "$SCRIPT_DIR" && run_with_timeout env BENCHMARK_SIZES="$BENCHMARK_SIZES" "$CPP_BIN")

echo ""
echo "Benchmark complete!"
