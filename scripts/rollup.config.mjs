import merge from 'deepmerge';
import { createBasicConfig } from '@open-wc/building-rollup';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import styles from "rollup-plugin-styles";
import replace from '@rollup/plugin-replace';

const baseConfig = createBasicConfig();

export default merge(baseConfig, {
    input: [
        'build/react_app.js',
    ],
    output: {
        dir: './static/js',
        entryFileNames: '[name].js',
        // Add for nicer debugging:
        sourcemap: true
    },
    plugins: [
        json(),
        styles(),
        nodeResolve({browser: true, preferBuiltins: false}),
        commonjs(),
        replace({
            'process.env.NODE_ENV': JSON.stringify( 'production' )
        })
    ],
});
