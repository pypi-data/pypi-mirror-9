// $Id: base.js 256337fbba27 2014/11/08 16:08:58 Patrick $

/*global jQuery: true */
/*global setTimeout: true */
/*global clearTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------
    
    var shortDelay = 12000;
    var longDelay = 20000;
    var idx = {'closed': 0, 'tabUser': 1, 'tabGroup': 2, 'tabStorage': 3,
               'tabIndexer': 4, 'tabProject': 5, 'tabRole': 6,
               'tabProcessing': 7, 'tabTask': 9, 'tabPack': 9};
    var state = jQuery.cookie('PF_STATE');
    if (!state)
        state = '0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0';
    state = state.split('|');

    // ------------------------------------------------------------------------
    // Left panel
    // ------------------------------------------------------------------------

    var $content2 = $('#content2');
    var $leftPanel = $('#leftPanel');
    var $rightPanel = $('#rightPanel');
    if (!$('#leftClose').length) {
        $('<div id="leftClose"><span>«</span></div>').prependTo($leftPanel);
        $('<div id="leftOpen"><span>»</span></div>').prependTo($rightPanel);
    }
    
    if (state[idx['closed']] == 1) {
        $leftPanel.hide();
        $content2.css({right: '100%'});
        $rightPanel.css({left: '100%', 'width': '100%'});
        $('#leftOpen').show();   
    }
    
    $('#leftClose').click(function() {
        if (state[idx['closed']] == 0) {
            $content2.animate(
                {'margin-left': -$leftPanel.outerWidth(true)}, 'slow',
                function() {
                    $leftPanel.hide();
                    $content2.css({right: '100%', 'margin-left': ''});
                    $rightPanel.css('left', '100%')
                        .animate({width: '100%'}, 'fast');
                    $('#leftOpen').show('slow');   
                });
            state[idx['closed']] = 1;
            $.cookie('PF_STATE', state.join('|'), {path: '/'});
        }
    });

    $('#leftOpen').click(function() {
        if (state[idx['closed']] == 1) {
            var leftPanelWidth = $leftPanel.outerWidth(true);
            $('#leftOpen').hide('fast');
            $rightPanel.animate(
                {width: '-=' + leftPanelWidth}, 'fast',
                function() {
                    $rightPanel.css({width: '', left: ''});
                    $leftPanel.css('left', '').show();
                    $content2
                        .css({'margin-left': -leftPanelWidth, right: ''})
                        .animate({'margin-left': 0}, 'slow');
                });
            state[idx['closed']] = 0;
            $.cookie('PF_STATE', state.join('|'), {path: '/'});
        }
    });

    // ------------------------------------------------------------------------
    // Content zone
    // ------------------------------------------------------------------------

    var $window = $(window);
    var $content = $('#content');
    var $footer = $('#footer');

    $.updateContentHeight = function(delta) {
        if ($content.length && $footer.length &&
            $content.offset().top < $window.height() * .3) {
            $content.css('height', '');
            var leftHeight = $content2.offset().top + $leftPanel.outerHeight()
                    + $footer.outerHeight();
            delta = delta || 0;
            if (leftHeight < $window.height()) {
                var contentHeight = $window.height() - $content.offset().top
                        - ($('div.listPager').outerHeight(true) || 0)
                        - ($('div.listFooter').outerHeight(true) || 0)
                        - $footer.outerHeight() - 8 + delta;
                if (contentHeight > 50)
                    $content.css('height', contentHeight + 'px');
            }
            var $current = $("#current");
            if ($current.length && $current.offset().top > $window.height()) {
                $content.animate({
                    scrollTop: $current.offset().top-$content.offset().top-20
                });
            }
        }
    };
    $.updateContentHeight();
    
    if ($content.length && $footer.length) {
        var timer = null;
        $window.resize(function() {
            clearTimeout(timer);
            timer = setTimeout($.updateContentHeight, 200);
        });
    }

    // ------------------------------------------------------------------------
    // Flash
    // ------------------------------------------------------------------------
    
    $('#flash').hide().slideDown('slow').delay(shortDelay).slideUp('slow', function() {
        $.updateContentHeight();
    });
    $('#flashAlert').hide().slideDown('slow').delay(shortDelay).slideUp('slow', function() {
        $.updateContentHeight();
    });

    // ------------------------------------------------------------------------
    // Tab set
    // ------------------------------------------------------------------------

    $('.tabs li a').click(function() {
        var $this = $(this);
        $('.tabs li').removeClass('tabCurrent');
        $this.parent().addClass('tabCurrent');
        $('.tabContent').hide();
        $('#tabContent' + $this.attr('id').replace('tab', '')).show();
        state[idx[$this.parent().parent().attr('id')]] = $this.attr('id');
        $.cookie('PF_STATE', state.join('|'), {path: '/'});
        return false;
    });

    $('.tabs').each(function() {
        var tab = window.location.hash.replace('#', '');
        if (tab.substring(0, 3) != 'tab')
            tab = state[idx[$(this).attr('id')]];
        $('#' + tab).click();
    });

    // ------------------------------------------------------------------------
    // Tool tip
    // ------------------------------------------------------------------------
    
    $('.toolTip').removeAttr('title').click(function() { return false; });

    $('table.tableToolTip .toolTip').mouseenter(function() {
        var $icon = $(this);
        $('#toolTipContent').remove();
        $('<div id="toolTipContent">...</div>')
            .width($icon.parent().parent().width() - $icon.parent().width() - 15)
            .hide()
            .insertAfter($icon)
            .load('?' + $icon.attr('name') + '.x=10', function() {
                var $toolTip = $(this);
                $toolTip.show().offset({
                    left: $icon.parents('tr').offset().left + 5,
                    top: $icon.offset().top - $toolTip.outerHeight()
                });
            });
    });
    
    $('div.formItemToolTip .toolTip').mouseenter(function() {
        var $icon = $(this);
        $('#toolTipContent').remove();
        $('<div id="toolTipContent">...</div>')
            .hide()
            .insertAfter($icon)
            .load('?' + $icon.attr('name') + '.x=10', function() {
                var $toolTip = $(this);
                $toolTip.show().offset({
                    left: $icon.parent().offset().left,
                    top: $icon.offset().top - $toolTip.outerHeight()
                });
            });
    });
    
    $('.toolTip').mouseleave(function() {
        $('#toolTipContent').remove();
    });
    
    $('table.list').mouseleave(function() {
        $('#toolTipContent').remove();
    });

    // ------------------------------------------------------------------------
    // Buttons
    // ------------------------------------------------------------------------

    // Check all
    $('#check_all')
        .removeAttr('id')
        .prepend($('<input id="check_all" name="check_all" type="checkbox" value="1"/>'))
        .find('#check_all').click(function() {
            $('input.listCheck').prop('checked', $(this).prop('checked'));
        });

    // Slow button
    var slowImgUrl = '/Static/Images/wait_slow.gif';
    var $slowImg = $('<img src="' + slowImgUrl + '" alt="slow"/>');
    $('a.slow').click(function() {
        var $this = $(this);
        if ($this.children('img').length)
            $this.children('img').attr('src', slowImgUrl);
        else
            $this.append(' ').append($slowImg);
    });
    $('input.slow').click(function() {
        var $this = $(this);
        if ($this.attr('src'))
            $this.attr('src', slowImgUrl);
        else
            $this.append(' ').append($slowImg);
    });

    // ------------------------------------------------------------------------
    // Parameters for action
    // ------------------------------------------------------------------------

    $('#actionParams').hide().slideDown('slow', function() {
        $.updateContentHeight();
    });
});
