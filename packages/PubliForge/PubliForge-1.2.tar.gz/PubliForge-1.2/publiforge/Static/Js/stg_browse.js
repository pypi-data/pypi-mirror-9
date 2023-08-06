// $Id: stg_browse.js 256337fbba27 2014/11/08 16:08:58 Patrick $

/*global jQuery: true */
/*global setTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Description
    // ------------------------------------------------------------------------

    var $descriptionContent = $('#browseDescriptionContent').hide();
    $('<a href="#" class="toggle"><img src="/Static/Images/open_false.png" alt="toggle"/></a>')
        .prependTo($('#browseDescription').show())
        .click(function() {
            var $imageToggle = $(this).children('img');
            if ($descriptionContent.is(':visible')) {
                $descriptionContent.slideUp(function() {
                    $imageToggle.attr('src', '/Static/Images/open_false.png');
                    $.updateContentHeight();
               });
            } else {
                $.updateContentHeight(-$descriptionContent.outerHeight());
                $descriptionContent.slideDown(function() {
                    $imageToggle.attr('src', '/Static/Images/open_true.png');
                });
            }
            return false;
        });
    $.updateContentHeight();

    // ------------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------------

    $("input[name='ccl!']").click(function(event) {
        $("#actionParams").slideUp("slow", function() {
            $("#actionParams").remove();
        });
        return false;
    });

    $(".actionParamsDirRen, .actionParamsDirDel, .actionParamsFilRen,"
      + " .actionParamsFilDel, .actionParamsFilUpl").click(function(event) {
          $("#actionParams").remove();
          var $parent = $(this).parent();
          var $actionParams = $("#" + $(this).attr("class")).clone();
          var name = $actionParams.children(".button").attr("name")
                  .substring(0, 4) + $parent.data("id") + ".x";
          $actionParams
              .attr("id", "actionParams")
              .children(".button").attr("name", name)
              .end().find("input[type='text'], input[type='file']")
              .attr("name", function(idx, attr) { return attr.substring(7); })
              .end().find("input[name='new_name']")
              .attr("value", $parent.data("id"))
              .end().find("input[name='ccl!']")
              .click(function(event) {
                  $("#actionParams").slideUp("slow", function() {
                      $("#actionParams").remove();
                  });
                  return false;
              })
              .end()
              .insertAfter($parent)
              .hide().slideDown("slow")
              .parents("tr").attr("id", "current");
          return false;
      });
});
