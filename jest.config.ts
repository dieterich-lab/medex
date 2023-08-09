/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    moduleDirectories: ['node_modules', 'src_ts'],
    testMatch: ['**/?(*.)+(spec|test).?(m)[tj]s?(x)'],
    transform: {},
    moduleFileExtensions: ["js", "jsx", "mjs"],
};