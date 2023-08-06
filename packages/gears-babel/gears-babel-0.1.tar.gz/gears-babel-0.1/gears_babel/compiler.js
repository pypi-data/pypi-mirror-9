#!/usr/bin/env node
// -*- mode: js -*-
'use strict';

var transform = require('babel').transform,
    source = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function(chunk) {
    source += chunk;
});

process.stdin.on('end', function() {
    // TODO: Get options from command line
    var options = {
        sourceMap: false,
        code: true,
        ast: false,
    };
    process.stdout.write(transform(source, options).code);
});
