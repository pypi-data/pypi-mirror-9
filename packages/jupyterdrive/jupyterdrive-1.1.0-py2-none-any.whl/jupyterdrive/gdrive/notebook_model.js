// Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.
//
define(function(require) {
    "use strict";

    var IPython = require('base/js/namespace');
    var $ = require('jquery');
    var utils = require('base/js/utils');
    var dialog = require('base/js/dialog');
    var gapi_utils = require('./gapi_utils');
    var drive_utils = require('./drive_utils');

    /**
     * Functions related to the Notebook JSON representation
     *
     * These functions replicate logic that would usually be performed by
     * the notebook server: creating new notebooks, and converting to/from
     * the on-disk format.
     */

    /**
     * Utility method to transform a notebook.
     * @param {Object} notebook JSON representation of a notebook.  Note this
     *     notebook gets mutated in this function.
     * @param {Function} transform_fn that will be applied to every object
     *     that can be a multiline string according to IPEP 17.
     */
    var transform_notebook = function(notebook, transform_fn) {
        if (!notebook['cells']) {
            return;
        }
        notebook['cells'].forEach(function(cell) {
        if (cell['source']) {
            cell['source'] = transform_fn(cell['source'])
        }
        if (cell['outputs']) {
            cell['outputs'].forEach(function(output) {
                if (output['data']) {
                    output['data'] = transform_fn(output['data']);
                }
            });
        }
    });        
    };

    /**
     * Creates a JSON notebook representation from the contents of a file.
     * @param {String} contents The contents of the file, as a string.
     * @return {Object} a JSON representation of the notebook.
     */
    var notebook_from_file_contents = function(contents) {
        var notebook = JSON.parse(contents);
        var unsplit_lines = function(multiline_string) {
            if (Array.isArray(multiline_string)) {
                return multiline_string.join('');
            } else {
                return multiline_string;
            }
        };
        transform_notebook(notebook, unsplit_lines);
        return notebook;
    };

    /**
     * Creates the contents of a file from a JSON notebook representation.
     * @param {Object} notebook a JSON representation of the notebook.
     * @return {Object} The JSON representation with lines split.
     */
    var file_contents_from_notebook = function(notebook) {
        var notebook_copy = JSON.parse(JSON.stringify(notebook));
        var split_lines = function(obj) {
            if(typeof(obj)!=='string'){
                return obj;
            }
            return obj.split('\n').map(function(line, idx, array) {
                if (idx == array.length - 1) {
                    return line;
                } else {
                    return line + '\n';
                }
            });
        };

        transform_notebook(notebook, split_lines);
        return notebook_copy;
    };

    /**
     * Create a JSON representation of a new notebook
     * @param {string} name Notebook name
     * @return {Object} JSON representation of a new notebook.
     */
    var new_notebook = function() {
        return {
            'cells' : [{
                'cell_type': 'code',
                'source': '',
                'outputs': [],
                'language': 'python',
                'metadata': {}
            }],
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 0
        };
    };
    
    return {
        'notebook_from_file_contents': notebook_from_file_contents,
        'file_contents_from_notebook': file_contents_from_notebook,
        'new_notebook': new_notebook
    };
});
