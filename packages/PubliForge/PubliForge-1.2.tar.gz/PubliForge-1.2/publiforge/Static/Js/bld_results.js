// $Id$

/*global jQuery: true */
/*global setTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Progress
    // ------------------------------------------------------------------------

    // Eventually, stop meta refresh
    var refresh = $('#refresh').attr('class');
    var queryString = window.location.search;
    var counter = 1;
    if (refresh && queryString.indexOf('ajax') == -1) {
        setTimeout(function() {
            window.location = queryString ? queryString + '&ajax' : '?ajax';
        }, 1000);
        return;
    }

    // Request for progress
    if (refresh) {
        (function request() {
            $.ajax({
                url: window.location.pathname,
                dataType: 'json',
                success: function(data) {
                    if (!data.working || counter > 20) {
                        window.location = window.location.pathname;
                        return;
                    }
                    $('div.playing').each(function() {
                        $(this).text('['+data.status[this.id.substring(8)][0]+']');
                    });
                    $('div.progressGauge').each(function() {
                        $(this).children().css(
                            'width', (data.status[this.id.substring(9)][1] || 100)+'%');
                    });
                    refresh = data.refresh;
                    counter += 1;
                },
                complete: function() {
                    setTimeout(request, 1000 * refresh);
                }
            });
        })();
    }

    // ------------------------------------------------------------------------
    // Information
    // ------------------------------------------------------------------------

    $('.buildStatus').mouseenter(function() {
        var $status = $(this);
        $('#toolTipContent').remove();
        $.getJSON($status.next().attr('href'), function(data) {
            $('#toolTipContent').remove();
            if (!data.labels) return;
            var labels = data.labels;
            var tpl = '<div class="formItem"><label><em>0</em></label><div>1</div><div class="clear"></div></div>';
            var html = tpl.replace('0', labels['playing']).replace('1', data.playing);
            if (data.agent)
                html += tpl.replace('0', labels['agent']).replace('1', data.agent);
            if (data.message)
                html += tpl.replace('0', labels['message']).replace('1', data.message);
            if (data.values)
                html += tpl.replace('0', labels['values']).replace('1', data.values);
            if (data.files)
                html += tpl.replace('0', labels['files']).replace('1', data.files);
            if (data.log)
                html += tpl.replace('0', labels['log']).replace('1', '<pre id="logLines">' + data.log + '</pre>');

            var $toolTip = $('<div id="toolTipContent" class="status">' + html + '</div>');
            $toolTip.width($status.parent().parent().width() - $status.parent().width()
                           - $status.parent().next().width() - 40)
                .insertAfter($status)
                .offset({
                    left: $status.parent().parent().offset().left,
                    top: $status.offset().top - $toolTip.outerHeight() * .6
                });
        });
    });

    $('.buildStatus').mouseleave(function() {
        $('#toolTipContent').remove();
    });
});
