'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
    NODE_ENV: '"development"',
    INDEXER_URL: JSON.stringify(process.env.INDEXER_URL || "http://localhost:4100/"),
    INDEXER_TOKEN: JSON.stringify(process.env.INDEXER_TOKEN || ''),
})
