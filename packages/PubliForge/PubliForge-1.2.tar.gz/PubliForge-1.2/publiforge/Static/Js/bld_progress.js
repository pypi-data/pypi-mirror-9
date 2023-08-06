// $Id$

/*global jQuery: true */
/*global setTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // Stop refresh
    var queryString = window.location.search;
    if (queryString.indexOf('ajax') == -1) {
        setTimeout(function() {
            window.location = queryString ? queryString + '&ajax' : '?ajax';
        }, 1000);
        return;
    }

    // Request for progress
    var $agent = $('#agent');
    var $playing = $('#playing');
    var $gauge = $('#progressGauge').children();
    var $step = $('#progressStep');
    var refresh = $('#progress').attr('class');
    (function request() {
        $.ajax({
            url: window.location.pathname,
            dataType: 'json',
            success: function(data) {
                if (!data.working) {
                    window.location =
                        window.location.pathname.replace('progress', 'view') + '#build';
                    return;
                }
                $agent.text(data.agent + ' ');
                $playing.text(data.playing);
                $gauge.animate({width: data.percent + '%'}, 'slow');
                $step.text(data.message);
                refresh = data.refresh;
            },
            complete: function() {
                setTimeout(request, 1000 * refresh);
            }
        });
    })();
});
