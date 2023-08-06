// $Id$

/*global jQuery: true */

"use strict";

jQuery(document).ready(function($) {
    // Open unique closed task
    var $currentTask = $('.taskCurrent');
    var $collapseTasks = $('.taskBar').children('span').children('.collapse');
    if (!$currentTask.length && $collapseTasks.length == 1) {
        window.location = $collapseTasks.attr('href'); 
    }
    if ($collapseTasks.length == 1) {
        $collapseTasks.hide();
    }

    // Open new task slowly
    $('#newTask').hide().slideDown();

    // Close task slowly
    $collapseTasks.click(function() {
        var href = $(this).attr('href');
        if ($currentTask.length) {
            $currentTask.slideUp(function() {
                window.location = href;
            });
            return false;
        }
        return true;
    });
});
