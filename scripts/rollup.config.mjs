import merge from 'deepmerge';
import { createBasicConfig } from '@open-wc/building-rollup';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import builtins from 'rollup-plugin-node-builtins';
import styles from "rollup-plugin-styles";

const baseConfig = createBasicConfig();

export default merge(baseConfig, {
  input: [
      'build/panels/barchart.mjs',
      'build/panels/basic_stats.mjs',
      'build/panels/boxplot.mjs',
      'build/panels/heatmap.mjs',
      'build/panels/histogram.mjs',
      'build/panels/layout.mjs',
      'build/panels/logout.mjs',
      'build/panels/patient_filter.mjs',
      'build/panels/scatter_plot.mjs',
      'build/panels/table_browser.mjs',
      'build/panels/tutorial.mjs',
  ],
  output: {
      dir: './static/js',
      entryFileNames: '[name].js',
      // Add for nicer debugging:
      // sourcemap: true
  },
  plugins: [
      json(),
      styles(),
      nodeResolve({browser: true, preferBuiltins: false}),
      commonjs(),
      builtins(),
  ],
});
