'use strict'
module.exports = {
    NODE_ENV: '"production"',
    PUBLIC_URL: '"/static"',
    INDEXER_URL: JSON.stringify(process.env.INDEXER_URL || "http://localhost:4100/"),
    INDEXER_TOKEN: JSON.stringify(process.env.INDEXER_TOKEN || ''),
}
