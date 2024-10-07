#!/bin/bash

set -e -u

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
base_dir=$(dirname "$script_dir")

cd "$base_dir/medex_client"
rm -rf "$base_dir/medex_client/dist"
npm run build
cd "$base_dir"
docker build --no-cache .