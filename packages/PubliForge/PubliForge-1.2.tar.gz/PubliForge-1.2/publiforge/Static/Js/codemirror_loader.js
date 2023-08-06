// $Id$

/*global jQuery: true */
/*global CodeMirror: true */

jQuery(document).ready(function($) {
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            CodeMirror.fromTextArea(this, {
                lineNumbers: true
            });
        }
    });
});
