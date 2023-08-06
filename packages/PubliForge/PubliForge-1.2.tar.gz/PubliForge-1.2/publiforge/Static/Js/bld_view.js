// $Id$

/*global jQuery: true */

"use strict";

jQuery(document).ready(function($) {
    var $logLines = $('#logLines');
    $('<a href="#logLines">' +
      '<img src="/Static/Images/open_true.png" alt="toggle"/></a>')
        .appendTo($('#log'))
        .click(function() {
            var $imageToggle = $(this).children('img');
            if ($logLines.is(':visible')) {
                $logLines.slideUp(function() {
                    $imageToggle.attr('src', '/Static/Images/open_false.png');
                });
            } else {
                $logLines.slideDown(function() {
                    $imageToggle.attr('src', '/Static/Images/open_true.png');
                });
            }
            return false;
        });
    $('#log.end')
        .parent().next('#logLines').hide()
        .children('img').attr('src', '/Static/Images/open_false.png');
});
