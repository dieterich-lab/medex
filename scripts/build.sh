#!/bin/bash

set -e -u

rm -rf static/js
tsc
mkdir -p build/resources
cp src_ts/resources/style.css build/resources
rollup -c scripts/rollup.config.mjs
# Plotly violently resits to be lowed via rollup ... so we load  separately
cp node_modules/plotly.js/dist/plotly.min.js static/js