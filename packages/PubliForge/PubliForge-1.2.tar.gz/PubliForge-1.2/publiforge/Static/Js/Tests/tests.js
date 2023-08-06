// $Id$

/*global module: true */
/*global test: true */
/*global asyncTest: true */
/*global ok: true */
/*global equal: true */
/*global notEqual: true */
/*global setTimeout: true */
/*global start: true */

/*global $: true */

// ****************************************************************************
// Base
// ****************************************************************************

module( "Base" );

// ----------------------------------------------------------------------------
// Left panel
// ----------------------------------------------------------------------------

test("left panel, opened", 6, function() {
    ok($('#leftClose').length, '<div id="leftClose"> exists');
    ok($('#leftOpen').length, '<div id="leftOpen"> exists');
    equal($('#content2').css('margin-left'), '0px',
          'left margin of #content2 is 0px');
    equal(Math.round($('#content2').offset().left),
          $('#leftPanel').width() - $('#content1').width(),
          'left of #content2 is width of left panel');
    equal($('#leftPanel').css('display'), 'block', 'left panel is visible');
    equal($('#leftPanel').offset().left, 0, 'left of left panel is 0');
}); 

asyncTest("left panel, closed", 3, function() {
    $('#leftClose').click();
    setTimeout(function() {
        equal(-$('#content2').offset().left, $('#content1').width(),
              'right of #content2 is 100%');
        equal($('#leftPanel').css('display'), 'none', 'left panel is not visible');
        equal($('#rightPanel').offset().left, 0, 'left of right panel is 0');
        $('#leftOpen').click();
        start();
    }, 2000);
}); 

// ----------------------------------------------------------------------------
// Flash
// ----------------------------------------------------------------------------

test("alert flash, visible", 1, function() {
    equal($('#flashAlert').css('display'), 'block', 'flash is visible');
});

// asyncTest("alert flash, invisible", 1, function() {
//     setTimeout(function() {
//         equal($('#flashAlert').css('display'), 'none', 'flash is invisible');
//         start();
//     }, 12000);
// }); 

// ----------------------------------------------------------------------------
// Tab set
// ----------------------------------------------------------------------------

test("tab set, tab n°0", 3, function() {
    $('#tab0').click();
    equal($('.tabCurrent a').attr('id'), 'tab0', 'tab0 is selected');
    equal($('#tabContent0').css('display'), 'block', 'tabContent0 is visible');
    equal($('#tabContent1').css('display'), 'none', 'tabContent1 is not visible');
});

asyncTest("tab set, tab n°1", 3, function() {
    $('#tab1').click();
    setTimeout(function() {
        equal($('.tabCurrent a').attr('id'), 'tab1', 'tab1 is selected');
        equal($('#tabContent0').css('display'), 'none', 'tabContent0 is not visible');
        equal($('#tabContent1').css('display'), 'block', 'tabContent1 is visible');
        $('#tab0').click();
        start();
    }, 1000);
});

// ----------------------------------------------------------------------------
// Tool tip
// ----------------------------------------------------------------------------

test("tool tip, show", 2, function() {
    $('#tooltip1').mouseenter();
    ok($('#toolTipContent').length, '<div id="toolTipContent"> has appeared');
    $('#tooltip1').mouseleave();
    equal($('#toolTipContent').length, 0, '<div id="toolTipContent"> has disappeared');
});

// ----------------------------------------------------------------------------
// Buttons
// ----------------------------------------------------------------------------

test("buttons, check all", 2, function() {
    $('#check_all').click();
    equal($('.listCheck:checked').length, 2, 'All buttons are checked');
    $('#check_all').click();
    equal($('.listCheck:checked').length, 0, 'All buttons are unchecked');
});

test("buttons, slow", 1, function() {
    $('#up').click();
    equal($('#up img').attr('src'), '/Static/Images/wait_slow.gif', 'Slow state');
});
