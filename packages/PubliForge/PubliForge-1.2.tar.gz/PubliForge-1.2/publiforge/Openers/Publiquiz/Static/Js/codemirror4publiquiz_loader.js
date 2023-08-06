// $Id: codemirror4publiquiz_loader.js 5f7d3440a027 2014/12/08 11:07:01 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global CodeMirror: true */
/*global schema2tags: true */
/*global completeAfter: true */
/*global completeIfAfterLt: true */
/*global completeIfInTag: true */
/*global metaHideEmptyFields: true */

"use strict";

var tags = schema2tags(
    jQuery.publidoc.schema, [
        "division", "topic", "quiz",
        "!--", "header", "section", "bibliography", "footer",
        "!--", "keyword", "subject"
    ]);

jQuery(document).ready(function($) {
    metaHideEmptyFields($(".pdocMeta"));
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


