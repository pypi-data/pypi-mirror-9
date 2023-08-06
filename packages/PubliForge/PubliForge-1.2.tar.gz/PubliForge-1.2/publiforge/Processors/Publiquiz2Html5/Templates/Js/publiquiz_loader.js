/**
 * @projectDescription publiquiz_loader.js
 * Javascript quiz loader.
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: publiquiz_loader.js c2bad54e2f56 2015/02/18 14:08:26 Tien $
 */

/**
 *
 * Copyright (C) Prismallia, Paris, 2014. All rights reserved.
 *
 * This program is free software. You can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
 * WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 *
 */


/*jshint globalstrict: true*/
/*global jQuery: true */
/*global window: true */


"use strict";

jQuery(window).ready( function($) {

    // Retrieve base score for quiz
    var baseScore = -1;
    if ($("#quiz_base_score").length > 0)
        baseScore = parseInt($("#quiz_base_score").text(), 10);

    // Retrieve nb retry for quiz
    var quizNbRetry = -1;
    if ($("#quiz_nb_retry").length > 0)
        quizNbRetry = parseInt($("#quiz_nb_retry").text(), 10);

    // Publiquiz default option
    var prefix = "pquiz";
    $.publiquiz.defaults.debug = false;
    $.publiquiz.defaults.baseScore = baseScore;
    $.publiquiz.defaults.verifyDuration = 0;
    $.publiquiz.defaults.eventType = "mouse";

    // Init publiquiz plugin
    var $publiquiz = $(".publiquiz");
    if ($publiquiz.length > 0)
        $publiquiz.publiquiz();

    // Manage messages
    var $messages = null;
    var $gMessage = $("#"+prefix+"GlobalMessage");
    var messages = $.find("."+prefix+"Message");
    if (messages.length > 0) {
        $messages = $(messages);
        if ($gMessage.length === 0) {
            $gMessage = $("<div>")
                .attr("id", prefix+"GlobalMessage")
                .addClass(prefix+"Message");
            $gMessage.insertBefore($($messages[0]));
        }
        $gMessage.hide();
    }

    // Set button events
    $("."+prefix+"Button").click( function(ev) {
        ev.preventDefault();
        var $this = $(this);
        var _id = $this.attr("id");
        if (_id.search("submit") > -1) {
            // Call publiquiz plugin function
            $publiquiz.publiquiz("disable");
            $publiquiz.publiquiz("insertUserAnswers");

            // Hide button validate
            $(this).addClass("hidden");

            // Verify quiz answer
            $publiquiz.publiquiz("verifyAnswer");

            // Hide button verify if exist
            if ($("#"+prefix+"VerifyAnswer"))
                $("#"+prefix+"VerifyAnswer").addClass("hidden");

            // Manage retry and manage buttons by score
            var res = $.publiquiz.engine.computeScores();
            if (quizNbRetry > 0 && res.score != res.total) {
                if ($("#"+prefix+"Retry"))
                    $("#"+prefix+"Retry").removeClass("hidden");
            } else {
                // Call publiquiz plugin function
                $publiquiz.publiquiz("textAnswer");

                // Call namespace "publiquiz" function for scoring
                $.publiquiz.engine.displayScore();

                // Display correction
                _onRightAnswer();
            }

            // Quiz messages
            if ($messages) {
                var percent = (res.score*100)/res.total;
                $messages.each( function() {
                    var $msg = $(this);
                    var range = $msg.data("score-range").split("-");
                    if (percent >= range[0] && percent <= range[1]) {
                        var text = $msg.text().split("|");
                        if (text.length > 1)
                            $.shuffle(text);
                        $gMessage.text(text[0]);
                        $gMessage.show();
                    }
                });
            }

        } else if (_id.search("UserAnswer") > -1) {
            _onUserAnswer();
        } else if (_id.search("RightAnswer") > -1) {
            _onRightAnswer();
        } else if (_id.search("VerifyAnswer") > -1) {
            $publiquiz.publiquiz("verifyAnswer");
        } else if (_id.search("Retry") > -1) {
            quizNbRetry -= 1;

            // Call publiquiz plugin function
            $publiquiz.publiquiz("retry");
            $publiquiz.publiquiz("enable");

            // Hide button Retry
            $(this).addClass("hidden");

            // Display button Validate
            if ($("#submit"))
                $("#submit").removeClass("hidden");

            // Hide messages
            if ($messages)
                $gMessage.hide();
        }
    });


    /**********************************************************************
     *                          Private function
     *********************************************************************/

    /**
     * Display quiz answer.
     */
    function _onRightAnswer() {
        // Hide button quiz answer
        if ($("#"+prefix+"RightAnswer"))
            $("#"+prefix+"RightAnswer").addClass("hidden");

        // Display button user answer
        if ($("#"+prefix+"UserAnswer"))
            $("#"+prefix+"UserAnswer").removeClass("hidden");

        _displayAnswer("_correct");
    }

    /**
     * Display user answer.
     */
    function _onUserAnswer(){
        // Hide button user answer
        if ($("#"+prefix+"UserAnswer"))
            $("#"+prefix+"UserAnswer").addClass("hidden");

        // Display button quiz answer
        if ($("#"+prefix+"RightAnswer"))
            $("#"+prefix+"RightAnswer").removeClass("hidden");

        _displayAnswer("_user");
    }

    /**
     * Display answer by mode.
     *
     * @param {String} mode.
     */
    function _displayAnswer(mode) {
        // Call publiquiz pugin function
        $publiquiz.publiquiz("quizAnswer", mode);
    }

});
