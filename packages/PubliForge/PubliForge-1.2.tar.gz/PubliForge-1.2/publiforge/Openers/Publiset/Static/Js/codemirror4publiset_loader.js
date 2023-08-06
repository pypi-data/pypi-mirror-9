// $Id: codemirror4publiset_loader.js 6468ab0bd854 2014/12/09 15:53:51 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global CodeMirror: true */
/*global schema2tags: true */
/*global completeAfter: true */
/*global completeIfAfterLt: true */
/*global completeIfInTag: true */

"use strict";

// ============================================================================
// Publiset tags
var inlines = ["sup", "sub", "date", "name", "highlight", "link"];

var tags = {
    "!top": ["division", "file", "!--", "keyword", "subject"],

    // Head
    head: {
        children: ["title", "shorttitle", "subtitle"]
    },
    title: { children: inlines },
    shorttitle: { children: inlines },
    subtitle: { children: inlines },
    keyword: { children: [] },
    subject: { children: [] },

    // Division
    division: {
        attrs: {
            path: null, xpath: null, xslt: null,
            as: null, attributes: null, transform: null },
        children: ["head", "division", "file"]
    },

    
    // File
    file: {
        attrs: { path: null, xpath: null, xslt: null, argument: null },
        children: []
    },

    // Blocks
    p: {
        children: [
            "sup", "sub", "date", "name", "foreign", "highlight", "link"]
    },

    // Inlines
    sup: { children: [] },
    sub: { children: [] },
    date: {
        attrs: { value: null, of: ["birth", "death"] },
        children: ["sup"]
    },
    name: {
        attrs: {
            of: ["person", "company", "book", "newspaper", "party",
                 "movie", "painting"]
        },
        children: ["sup"]
    },
    highlight: { children: inlines },
    link: {
        attrs: { uri: null, idref: null },
        children: ["sup", "sub", "date", "name", "highlight"]
    }
};

// ============================================================================

jQuery(document).ready(function($) {
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            CodeMirror.fromTextArea(this, {
                lineNumbers: true,
                mode: "xml",
                extraKeys: {
                    "'<'": completeAfter,
                    "'/'": completeIfAfterLt,
                    "' '": completeIfInTag,
                    "'='": completeIfInTag,
                    "Alt-Enter": function(cm) {
                        CodeMirror.showHint(
                            cm, CodeMirror.xmlHint, {schemaInfo: tags});
                    }
                }
            });
        }
    });
});
