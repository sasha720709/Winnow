#!/usr/bin/env bash
# Runs once when the dev container is created.
set -euo pipefail

# C toolchain and tools for measuring speed and memory.
#   build-essential: gcc, make
#   gdb, valgrind:   debugging and memory checks for the C library
#   time:            /usr/bin/time -v shows peak memory of a run
#   pv:              progress bar when streaming the big Wikipedia dump
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    build-essential gdb valgrind time pv bzip2
sudo rm -rf /var/lib/apt/lists/*

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "Versions:"
python --version
gcc --version | head -1
terraform -version | head -1
aws --version
