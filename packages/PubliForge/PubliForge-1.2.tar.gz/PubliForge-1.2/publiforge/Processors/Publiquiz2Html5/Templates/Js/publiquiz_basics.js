/** 
 * @projectDescription publiquiz_basics.js 
 * Plugin jQuery for quiz choices.
 *
 * @author prismallia.fr
 * @version 0.1 
 * $Id: publiquiz_basics.js 21698534b7a3 2015/02/18 16:42:56 Tien $
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
/*global setTimeout: true */
/*global clearTimeout: true */


/******************************************************************************
 *
 *                              Plugin publiquiz
 *
******************************************************************************/

(function ($) {

"use strict";

$.fn.publiquiz = function(options, args) {

    var $this = this;

    // Options
    var opts = handleOptions(options, args);
    if (opts === false) 
        return $this;
    $.publiquiz.defaults.prefix = opts.prefix;
    if (opts.baseScore > -1)
        $.publiquiz.defaults.baseScore = opts.baseScore;


    /**********************************************************************
     *                              Library
    **********************************************************************/

    /**
     * Process the args that were passed to the plugin fn
     *
     * @param {Object} options, object can be String or {}.
     */
    function handleOptions(options, args) {
        if (options && options.constructor == String) {

            $.publiquiz.engine.clearVerify();

            $this.each( function() {
                var $quiz = $(this);
                if (!$quiz.attr("data-engine"))
                    return;
                var engine = $quiz.data("engine");
                var prefix = $quiz.data("prefix");

                switch (options) {
                    case ("validate"):
                        validate($quiz);
                        break;
                    case ("enable"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.enable[subEngine]($element);
                                $.publiquiz.engine.hideTextAnswer($element);
                            });
                        } else {
                            $.publiquiz.engine.enable[engine]($quiz);
                            $.publiquiz.engine.hideTextAnswer($quiz);
                        }
                        break;
                    case ("disable"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.disable[subEngine]($element);
                            });
                        } else {
                            $.publiquiz.engine.disable[engine]($quiz);
                        }
                        break;
                    case ("retry"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.retry[subEngine]($element);
                            });
                        } else {
                            $.publiquiz.engine.retry[engine]($quiz);
                        }
                        break;
                    case ("textAnswer"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.textAnswer[subEngine]($element);
                            });
                        } else {
                            $.publiquiz.engine.textAnswer[engine]($quiz);
                        }
                        break;
                    case ("insertUserAnswers"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.insertUserAnswers[subEngine]($element);
                            });
                        } else {
                            $.publiquiz.engine.insertUserAnswers[engine]($quiz);
                        }
                        break;
                    case ("quizAnswer"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.quizAnswer[subEngine]($element, args);
                            });
                        } else {
                            $.publiquiz.engine.quizAnswer[engine]($quiz, args);
                        }
                        break;
                    case ("verifyAnswer"):
                        if (engine == "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                var subEngine = $element.data("engine");
                                $.publiquiz.engine.verifyAnswer[subEngine]($element);
                            });
                        } else {
                            $.publiquiz.engine.verifyAnswer[engine]($quiz);
                        }
                        break;
                    default:
                        $.fn.publiquiz[options]($quiz, args);
                }
            });
            return false;
        } 
        
        return $.extend({}, $.publiquiz.defaults, options || {});
    }

    /**********************************************************************
     *                          Library function
     *********************************************************************/

    function validate($quiz) {
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");

        if (engine == "composite") {
            $quiz.find("."+prefix+"Element").each( function() {
                var $element = $(this);
                var subEngine = $element.data("engine");
                $.publiquiz.engine.disable[subEngine]($element);
                $.publiquiz.engine.textAnswer[subEngine]($element);
                $.publiquiz.engine.insertUserAnswers[subEngine]($element);
            });
        } else {
            $.publiquiz.engine.disable[engine]($quiz);
            $.publiquiz.engine.textAnswer[engine]($quiz);
            $.publiquiz.engine.insertUserAnswers[engine]($quiz);
        }
    }

    function activateQuiz($quiz) {
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var prefix = opts.prefix;
        $quiz.data("prefix", opts.prefix);
        $quiz.data("verify-duration", opts.verifyDuration);
        $quiz.data("display-correction-only", opts.displayCorrectionOnly);

        if (opts.debug) {
            console.log("Plugin:publiquiz:main:engine: " + engine);
            console.log("Plugin:publiquiz:main:quzId: " + $quiz.data("quiz-id"));
            console.log("Plugin:publiquiz:main:prefix: " + prefix);
        }

        // Configure quiz
        $.publiquiz.engine.configure[engine]($quiz);

        // Set enable quiz
        $.publiquiz.engine.enable[engine]($quiz);


        /******************************************************************
         *                      Register Score function
         *****************************************************************/

        $.publiquiz.engine.registerScoreFunc(
                quzId, 
                $quiz,
                $.publiquiz.engine.computeScore[engine]
            );


        /******************************************************************
         *                              Events
         *****************************************************************/

        // Set button events
        $quiz.find("."+prefix+"Button").click( function(ev) {
            ev.preventDefault();
            var $btn = $(this);
            var id = $btn.attr("id");
            if (id.search("_help-link") != -1 ) {
                $.publiquiz.engine.help[engine]($quiz);
            }
        });
    }


    /**********************************************************************
     *                          Plug-in main function
     *********************************************************************/

    return $this.each( function() {
        var $quiz = $(this);
        var engine = $quiz.data("engine");
        var prefix = opts.prefix;

        if (engine == "composite") {
            // Activate sub quiz
            $quiz.data("prefix", opts.prefix);
            $quiz.find("."+prefix+"Element").each( function() {
                var $element = $(this);
                var subEngine = $element.data("engine");
                if (subEngine && $.publiquiz.engine.enable[subEngine])
                    activateQuiz($element);
            });

            // Set events on quiz button
            $quiz.find("."+prefix+"Button").click( function(ev) {
                ev.preventDefault();
                var $btn = $(this);
                var id = $btn.attr("id");
                if (id.search("_help-link") != -1 ) {
                    $.publiquiz.engine.displayHelp($quiz);
                }
            });
        } else {
            if (!engine || !$.publiquiz.engine.enable[engine])
                return false;

            activateQuiz($quiz);
        }
        return null;
    });
};

}(jQuery));


/******************************************************************************
 *
 *                                  Choices
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.choices = {
    
    /**
     * Configure quiz.
     */
    choicesConfigure: function($quiz) {
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    choicesEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice input").removeAttr("disabled"); 
        $quiz.find("."+prefix+"Choice").click( function(ev) {
            var $target = $(this);
            if(ev.target.nodeName.toLowerCase() == "audio")
                return;
            while (!$target.hasClass(prefix+"Choice"))
                $target = $target.parentNode;
            $.publiquiz.engine.choices._onChoice($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").unbind("click");
        $quiz.find("."+prefix+"Choice input").attr("disabled", "disabled"); 
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesRetry: function($quiz) {
        $.publiquiz.engine.retryChoices($quiz, "Choice");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    choicesComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (engine == "choices-radio") {
            return $.publiquiz.engine.scoreForQuizChoicesRadio($quiz);
        } else {
            if (isCheckRadio)
                return $.publiquiz.engine.choices._scoreForQuizChoicesCheckRadio($quiz);
            else
                return $.publiquiz.engine.scoreForQuizChoicesCheck($quiz, "Choice");
        }
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.choices:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesInsertUserAnswers: function($quiz) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.engine.choices._insertUserAnswersQuizChoicesCheckRadio($quiz);
        else
            $.publiquiz.engine.insertUserAnswersQuizChoices($quiz, "Choice");
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    choicesQuizAnswer: function($quiz, mode) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.engine.choices._displayQuizChoicesAnswerCheckRadio($quiz, mode);
        else
            $.publiquiz.engine.displayQuizChoicesAnswer($quiz, "Choice", mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyAnswer: function($quiz) {
        $.publiquiz.engine.verifyQuizChoicesAnswer($quiz);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on choice.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery receive click.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.engine.clearVerify();
        
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var $input = $elem.find("input");
        var $engine = $quiz.find("#"+quzId+"_engine");
        if (engine == "choices-radio") {
            if ($elem.hasClass("selected"))
                return;

            $engine.find("."+prefix+"Choice.selected").removeClass("selected");
            $elem.addClass("selected");
            if ($input)
                $input.prop("checked", true);
        } else {
            if ($quiz.data("engine-options") && 
                    $quiz.data("engine-options").search("radio") > -1 ) {
                if ($elem.hasClass("selected"))
                    return;

                var group = $elem.data("group");
                $engine.find("."+prefix+"Choice")
                    .filter("[data-group=\""+group+"\"]").removeClass("selected");
                $elem.addClass("selected");
                if ($input)
                    $input.prop("checked", true);
            } else {
                if ($elem.hasClass("selected")) {
                    $elem.removeClass("selected");
                    if ($input)
                        $input.prop("checked", false);
                } else {
                    $elem.addClass("selected");
                    if ($input)
                        $input.prop("checked", true);
                }
            }
        }
    },

    /**
     * Score for quiz engine choice-check with option "radio".
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _scoreForQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("#"+quzId+"_engine");
        var res = $.publiquiz.engine.correction(
                $quiz.find("#"+quzId+"_correct"));

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Compute score
        var total = choices.length;
        var score = 0;
        $.each(choices, function() {
            var group = this;
            if (res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"true\"]")
                                .hasClass("selected"))
                score += 1;
            else if (!res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"false\"]")
                                .hasClass("selected"))
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Insert user answers in html for quiz choices-check with option "radio"
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _insertUserAnswersQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+"Choice.selected").each( function() {
            var $item = $(this);
            var name = $item.data("name");
            var group = $item.data("group");
            if (answer !== "")
                answer += "::";
            answer += group+name;
        });

        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz choices-check with option "radio".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    _displayQuizChoicesAnswerCheckRadio: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");

        // Reset quiz
        $quiz.find("."+prefix+"Choice input").prop("checked", false);
        $quiz.find("."+prefix+"Choice").removeClass(
                "selected answerOk answerKo");

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Display pquizChoice selected
        var $engine = $quiz.find("#"+quzId+"_engine");
        var answers = $.publiquiz.engine.correction(
                $quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.engine.correction(
                    $quiz.find("#"+quzId+"_user"));

        $.each(choices, function() {
            var group = this;
            var $choice = null;
            if(mode == "_correct") {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"true\"]");
                else
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"false\"]");
            } else {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\""+answers[group]+"\"]");
            }
            
            if ($choice) {
                $choice.addClass("selected");
                if (mode == "_correct") {
                    if (correctionOnly) {
                        $choice.addClass("answerOk");
                    } else {
                        if (!userAnswers[group] || 
                                (userAnswers[group] != 
                                    $choice.data("name").toString()))
                            $choice.addClass("answerKo");
                        else 
                            $choice.addClass("answerOk");
                    }
                }
                var $input = $choice.find("input");
                if ($input.length > 0)
                    $input.prop("checked", true);
            }
        });
    }
};

// Register function
$.publiquiz.engine.register("choices-radio", { 
        configure: $.publiquiz.engine.choices.choicesConfigure,
        enable: $.publiquiz.engine.choices.choicesEnable,
        disable: $.publiquiz.engine.choices.choicesDisable,
        help: $.publiquiz.engine.choices.choicesHelp,
        retry: $.publiquiz.engine.choices.choicesRetry,
        textAnswer: $.publiquiz.engine.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.engine.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.choices.choicesQuizAnswer,
        verifyAnswer: $.publiquiz.engine.choices.choicesVerifyAnswer,
        computeScore: $.publiquiz.engine.choices.choicesComputeScore,
        quizScore: $.publiquiz.engine.choices.choicesScore
    });

$.publiquiz.engine.register("choices-check", { 
        configure: $.publiquiz.engine.choices.choicesConfigure,
        enable: $.publiquiz.engine.choices.choicesEnable,
        disable: $.publiquiz.engine.choices.choicesDisable,
        help: $.publiquiz.engine.choices.choicesHelp,
        retry: $.publiquiz.engine.choices.choicesRetry,
        textAnswer: $.publiquiz.engine.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.engine.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.choices.choicesQuizAnswer,
        verifyAnswer: $.publiquiz.engine.choices.choicesVerifyAnswer,
        computeScore: $.publiquiz.engine.choices.choicesComputeScore,
        quizScore: $.publiquiz.engine.choices.choicesScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Blanks
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.blanks = {
    
    /**
     * Configure quiz.
     */
    blanksConfigure: function($quiz) {
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        if (engine == "blanks-fill")
            $.publiquiz.engine.blanks._configureBlanksFill($quiz);
        else if (engine == "blanks-select")
            $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"Items"));
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    blanksEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event change on choice
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            $choice.prop("disabled", false);
            $choice.removeClass("disabled");
        }).on({
            input: function(ev) {
                $.publiquiz.engine.clearVerify();
            }
        });

        // Event "draggable" on item
        $quiz.find("."+prefix+"Item").prop("draggable", true);
        $.publiquiz.engine.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            $choice.prop("disabled", true);
            $choice.addClass("disabled");
        }).unbind("input");

        $quiz.find("."+prefix+"Item").prop("draggable", false);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksRetry: function($quiz) {
        $.publiquiz.engine.retryBlanks($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    blanksComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var engine = $quiz.data("engine");
        if (engine == "blanks-fill")
            return $.publiquiz.engine.blanks._computeScoreBlanksFill($quiz);
        else
            return $.publiquiz.engine.scoreForQuizCmpCheck($quiz);
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksScore: function($quiz) {
        if ($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.choices:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");

        if (engine == "blanks-fill") {
            var answer = "";
            $quiz.find("."+prefix+"Choice").each( function() {
                var $item = $(this);
                var id = $item.attr("id");
                var value = $item.val().trim();
                if (value !== "") {
                    if (answer !== "")
                        answer += "::";
                    answer += id.substring(id.length - 3, id.length) + value;
                }
            });
            $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
        } else {
            $.publiquiz.engine.inserUserAnswersQuizDrop($quiz);
        }
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    blanksQuizAnswer: function($quiz, mode) {
        var engine = $quiz.data("engine");
        if (engine == "blanks-fill")
            $.publiquiz.engine.displayQuizAnswerBlanksFill($quiz, mode);
        else
            $.publiquiz.engine.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        if (engine == "blanks-fill")
            $.publiquiz.engine.blanks._verifyBlanksFill($quiz);
        else
            $.publiquiz.engine.verifyQuizCmpAnswer($quiz);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Verify user answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _verifyBlanksFill: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }

        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            var data = $item.val().trim();
            if (data !== "") {
                if ($.publiquiz.engine.isValideBlanksFillAnswer(data, value, isStrict, options))
                    $item.addClass("answerOk");
                else
                    $item.addClass("answerKo");
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.engine.clearVerify, duration);
            $.publiquiz.engine.timers.push(timer);
        }
    },

    /**
     * Configure quiz blanks fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _configureBlanksFill: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").each( function() {
            if (this.parentNode.nodeName.toLowerCase() == "td" || 
                this.parentNode.parentNode.nodeName.toLowerCase == "td")
                return;
            if (this.nodeName.toLowerCase() == "textarea")
                return;

            var $choice = $(this);
            var id = $choice.attr("id");
            var key = id.substring(id.length - 3, id.length);
            var answers = $.publiquiz.engine.correction($("#"+quzId+"_correct")); 
            var value = answers[key];

            var answer = "";
            $(value.split("|")).each( function(ids, data) {
                if (data.length > answer)
                    answer = data;
            });

            var w = answer.length * 2;
            if(w < 20)
                w = 20;
            if (!$choice.attr("style"))
                $choice.css("width", w+"ex");
        });
    },

    /**
     * This function use for compute score for engine blanks-fill.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _computeScoreBlanksFill: function ($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }

        var total = $quiz.find("."+prefix+"Choice").length;
        var score = 0.0;

        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            var data = $item.val().trim();

            if ($.publiquiz.engine.isValideBlanksFillAnswer(data, value, isStrict, options))
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

};

// Register function
$.publiquiz.engine.register("blanks-fill", { 
        configure: $.publiquiz.engine.blanks.blanksConfigure,
        enable: $.publiquiz.engine.blanks.blanksEnable,
        disable: $.publiquiz.engine.blanks.blanksDisable,
        help: $.publiquiz.engine.blanks.blanksHelp,
        retry: $.publiquiz.engine.blanks.blanksRetry,
        textAnswer: $.publiquiz.engine.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.engine.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.blanks.blanksQuizAnswer,
        verifyAnswer: $.publiquiz.engine.blanks.blanksVerifyAnswer,
        computeScore: $.publiquiz.engine.blanks.blanksComputeScore,
        quizScore: $.publiquiz.engine.blanks.blanksScore
    });

$.publiquiz.engine.register("blanks-select", { 
        configure: $.publiquiz.engine.blanks.blanksConfigure,
        enable: $.publiquiz.engine.blanks.blanksEnable,
        disable: $.publiquiz.engine.blanks.blanksDisable,
        help: $.publiquiz.engine.blanks.blanksHelp,
        retry: $.publiquiz.engine.blanks.blanksRetry,
        textAnswer: $.publiquiz.engine.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.engine.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.blanks.blanksQuizAnswer,
        verifyAnswer: $.publiquiz.engine.blanks.blanksVerifyAnswer,
        computeScore: $.publiquiz.engine.blanks.blanksComputeScore,
        quizScore: $.publiquiz.engine.blanks.blanksScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Sort
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.sort = {
    
    /**
     * Configure quiz.
     */
    sortConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"Items"));
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    sortEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $quiz.find("."+prefix+"Item").prop("draggable", true);
        $.publiquiz.engine.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Item").prop("draggable", false);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortRetry: function($quiz) {
        $.publiquiz.engine.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    sortComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        return $.publiquiz.engine.scoreForQuizCmpRadio($quiz);
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.sort:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortInsertUserAnswers: function($quiz) {
        $.publiquiz.engine.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    sortQuizAnswer: function($quiz, mode) {
        $.publiquiz.engine.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyAnswer: function($quiz) {
        $.publiquiz.engine.verifyQuizCmpAnswer($quiz);
    }


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.engine.register("sort", { 
        configure: $.publiquiz.engine.sort.sortConfigure,
        enable: $.publiquiz.engine.sort.sortEnable,
        disable: $.publiquiz.engine.sort.sortDisable,
        help: $.publiquiz.engine.sort.sortHelp,
        retry: $.publiquiz.engine.sort.sortRetry,
        textAnswer: $.publiquiz.engine.sort.sortTextAnswer,
        insertUserAnswers: $.publiquiz.engine.sort.sortInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.sort.sortQuizAnswer,
        verifyAnswer: $.publiquiz.engine.sort.sortVerifyAnswer,
        computeScore: $.publiquiz.engine.sort.sortComputeScore,
        quizScore: $.publiquiz.engine.sort.sortScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Matching
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.matching = {

    /**
     * Configure quiz.
     */
    matchingConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"Items"));
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    matchingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $quiz.find("."+prefix+"Item").prop("draggable", true);
        $.publiquiz.engine.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Draggable item
        $quiz.find("."+prefix+"Item").prop("draggable", false);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingRetry: function($quiz) {
        $.publiquiz.engine.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    matchingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        return $.publiquiz.engine.scoreForQuizCmpCheck($quiz);
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.matching:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingInsertUserAnswers: function($quiz) {
        $.publiquiz.engine.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    matchingQuizAnswer: function($quiz, mode) {
        $.publiquiz.engine.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyAnswer: function($quiz) {
        $.publiquiz.engine.verifyQuizCmpAnswer($quiz);
    }


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.engine.register("matching", { 
        configure: $.publiquiz.engine.matching.matchingConfigure,
        enable: $.publiquiz.engine.matching.matchingEnable,
        disable: $.publiquiz.engine.matching.matchingDisable,
        help: $.publiquiz.engine.matching.matchingHelp,
        retry: $.publiquiz.engine.matching.matchingRetry,
        textAnswer: $.publiquiz.engine.matching.matchingTextAnswer,
        insertUserAnswers: $.publiquiz.engine.matching.matchingInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.matching.matchingQuizAnswer,
        verifyAnswer: $.publiquiz.engine.matching.matchingVerifyAnswer,
        computeScore: $.publiquiz.engine.matching.matchingComputeScore,
        quizScore: $.publiquiz.engine.matching.matchingScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                 Pointing
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.pointing = {
    
    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            $.publiquiz.engine.clearVerify();
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.engine.pointing._onPoint($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $.publiquiz.engine.retryChoices($quiz, "Point");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var quzId = $quiz.data("quiz-id");
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 ) {
            return $.publiquiz.engine.scoreForQuizChoicesRadio($quiz);
        } else {
            return $.publiquiz.engine.scoreForQuizChoicesCheck($quiz, "Point");
        }
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.pointing:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        $.publiquiz.engine.insertUserAnswersQuizChoices($quiz, "Point");
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        $.publiquiz.engine.displayQuizChoicesAnswer($quiz, "Point", mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyAnswer: function($quiz) {
        $.publiquiz.engine.verifyQuizChoicesAnswer($quiz);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 ) {
            $quiz.find("."+prefix+"Point").removeClass("selected");
            $elem.addClass("selected"); 
        } else {
            if ($elem.hasClass("selected"))
                $elem.removeClass("selected");
            else
                $elem.addClass("selected");
        }
    }

};

// Register function
$.publiquiz.engine.register("pointing", { 
        configure: $.publiquiz.engine.pointing.pointingConfigure,
        enable: $.publiquiz.engine.pointing.pointingEnable,
        disable: $.publiquiz.engine.pointing.pointingDisable,
        help: $.publiquiz.engine.pointing.pointingHelp,
        retry: $.publiquiz.engine.pointing.pointingRetry,
        textAnswer: $.publiquiz.engine.pointing.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.engine.pointing.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.pointing.pointingQuizAnswer,
        verifyAnswer: $.publiquiz.engine.pointing.pointingVerifyAnswer,
        computeScore: $.publiquiz.engine.pointing.pointingComputeScore,
        quizScore: $.publiquiz.engine.pointing.pointingScore
    });

}(jQuery));


/******************************************************************************
 *
 *                              Pointing-categories
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.pointingCategories = {
    
    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for category
        $quiz.find("."+prefix+"Category").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Category"))
                $target = $target.parentNode;
            $.publiquiz.engine.pointingCategories._onCategory($quiz, $target);
        });

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.engine.pointingCategories._onPoint($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
        $quiz.find("."+prefix+"Category").unbind("click");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $.publiquiz.engine.retryPointingCategory($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        var result = {};
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0;
        var total = 0;
        var res = $.publiquiz.engine.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && res[category].search(pointId) > -1)
                score += 1;

            total += 1;
        });

        result.score = score;
        result.total = total;
        return result;
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.pointingCategories:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category) {
                if (answer !== "")
                    answer += "::";
                answer += category + pointId;
            }
        });

        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var answers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+mode));

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            $point.removeClass("answerOk answerKo");
            var classList = $point.attr("class").split(/\s+/);
            if (classList.length > 1)
                $point.removeClass(classList[classList.length - 1]);
        });

        // On place les couleurs de la correction
        $.each(answers, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var color = $categoryColor.attr("class").split(/\s+/)[1];

            $.each(value.split("|"), function(idx, data) {
                var $point = $quiz.find("."+prefix+"Point").filter("[data-choice-id=\""+data+"\"]");
                if ($point.length > 0) {
                    if (mode == "_correct") {
                        if (correctionOnly) {
                            $point.addClass("answerOk");
                        } else {
                            if (!$point.data("category-id") || $point.data("category-id") != key)
                                $point.addClass("answerKo");
                            else
                                $point.addClass("answerOk");
                        }
                    }
                    $point.addClass(color);
                }
            });
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            if (category) {
                var pointId = $point.data("choice-id");
                if (res[category].search(pointId) > -1)
                    $point.addClass("answerOk");
                else
                    $point.addClass("answerKo");
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.engine.clearVerify, duration);
            $.publiquiz.engine.timers.push(timer);
        }
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        $.publiquiz.engine.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            color = $categoryColor.attr("class").split(/\s+/)[1];
        }

        if (!category)
            return;

        var classList = $elem.attr("class").split(/\s+/);
        if (classList.length > 1)
            $elem.removeClass(classList[classList.length - 1]);
        $elem.data("category-id", category);
        $elem.addClass(color);
        return;
    }

};

// Register function
$.publiquiz.engine.register("pointing-categories", { 
        configure: $.publiquiz.engine.pointingCategories.pointingConfigure,
        enable: $.publiquiz.engine.pointingCategories.pointingEnable,
        disable: $.publiquiz.engine.pointingCategories.pointingDisable,
        help: $.publiquiz.engine.pointingCategories.pointingHelp,
        retry: $.publiquiz.engine.pointingCategories.pointingRetry,
        textAnswer: $.publiquiz.engine.pointingCategories.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.engine.pointingCategories.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.pointingCategories.pointingQuizAnswer,
        verifyAnswer: $.publiquiz.engine.pointingCategories.pointingVerifyAnswer,
        computeScore: $.publiquiz.engine.pointingCategories.pointingComputeScore,
        quizScore: $.publiquiz.engine.pointingCategories.pointingScore
    });

}(jQuery));



/******************************************************************************
 *
 *                                  Categories
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.categories = {
    
    /**
     * Configure quiz.
     */
    categoriesConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        
        // Shuffle items for mode "basket"
        $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"CategoriesItems"));

        // Shuffle items for mode "color"
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"CategoriesChoices"));
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    categoriesEnable: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item for mode "basket"
        $quiz.find("."+prefix+"CategoryItem").prop("draggable", true);
        $.publiquiz.engine.setDraggableItem($quiz, $quiz.find("."+prefix+"CategoryItem"), "Category");

        // Event for mode "color"
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) {

            // Event "click" on category for mode "color"
            $quiz.find("."+prefix+"Category").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Category"))
                    $target = $target.parentNode;
                $.publiquiz.engine.categories._onCategory($quiz, $target);
            });

            // Event "click" for point
            $quiz.find("."+prefix+"Choice").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Choice"))
                    $target = $target.parentNode;
                $.publiquiz.engine.categories._onChoice($quiz, $target);
            });

        }
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"CategoryItem").prop("draggable", false);

        // Disable for mode "color"
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").unbind("click");
            $quiz.find("."+prefix+"Category").unbind("click");
        }
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesRetry: function($quiz) {
        $.publiquiz.engine.retryCategories($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    categoriesComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) 
            return $.publiquiz.engine.categories._computeScoreColor($quiz);
        else
            return $.publiquiz.engine.categories._computeScoreBasket($quiz);
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.categories:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesInsertUserAnswers: function($quiz) {
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) 
            $.publiquiz.engine.categories._insertUserAnswersColor($quiz);
        else
            $.publiquiz.engine.categories._insertUserAnswersBasket($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    categoriesQuizAnswer: function($quiz, mode) {
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) 
            $.publiquiz.engine.categories._quizAnswersColor($quiz, mode);
        else
            $.publiquiz.engine.categories._quizAnswersBasket($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyAnswer: function($quiz) {
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.engine.categories._verifyAnswersColor($quiz);
        else
            $.publiquiz.engine.categories._verifyAnswersBasket($quiz);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizChoice.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.engine.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            color = $categoryColor.attr("class").split(/\s+/)[1];
        }

        if (!category)
            return;

        if (isMultiple) {
            // On verifie que le target n'appartient pas deja cette categorie si
            // c'est le cas on retire la categorie
            var hasCategory = false;
            $elem.find("."+prefix+"ItemColor").each( function() {
                var $item = $(this);
                if ($item.data("category-id") == category) {
                    $item.remove();
                    hasCategory = true;
                    return false;
                }
            });

            if (hasCategory)
                return;

            // Ajout d'un item color
            var $item = $(document.createElement("span"));
            $item.addClass(prefix+"ItemColor " + color);
            $item.data("category-id", category);
            $item.appendTo($elem);

        } else {
            var classList = $elem.attr("class").split(/\s+/);
            if (classList.length > 1)
                $elem.removeClass(classList[classList.length - 1]);
            $elem.data("category-id", category);
            $elem.addClass(color);
        }
    },

    /**
     * This function compute score for categories mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var total = 0;
        var score = 0;
        var res = $.publiquiz.engine.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        // Listes des intrus
        var values = [];
        var intrus = [];
        $.each(res, function(key, value) { values = $.merge(values, value.split("|")); });
        $quiz.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value");
            if( $.inArray(value, values) == -1)
                intrus.push(value); 
        });

        // Score
        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            // Vrai items
            $.each(value.split("|"), function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score += 1;
                total += 1;
            });

            // Intrus
            $.each(intrus, function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score -= 1;
            });
        });

        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreColor: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var score = 0;
        var total = 0;
        var res = $.publiquiz.engine.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));

        // Total
        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        // Score
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value");
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if ($.inArray(value, res[category].split("|")) >= 0)
                        score += 1;
                });
            } else {
                var category = $choice.data("category-id");
                if (category && $.inArray(value, res[category].split("|")) >= 0)
                    score += 1;
            }
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Insert user answers in html for mode "basket"
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _insertUserAnswersBasket: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"CategoryDrop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                if (answer !== "")
                    answer += "::";
                answer += key + value;
            });
        });

        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Insert user answers in html for mode "color"
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _insertUserAnswersColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var answer = "";
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value");
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if (answer !== "")
                        answer += "::";
                    answer += category + value;
                });
            } else {
                var category = $choice.data("category-id");
                if (category) {
                    if (answer !== "")
                        answer += "::";
                    answer += category + value;
                }
            }
        });

        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+"_user"));

        // On enleve la correction
        if (isMultiple) {
            $quiz.find("."+prefix+"CategoryItemDropped").remove();
        } else {
            $quiz.find("."+prefix+"CategoryItemDropped").each( function() {
                var $item = $(this);
                $item.appendTo($items)
                    .removeClass(prefix+"CategoryItemDropped answerKo");
            });
        }

        // On place la correction en deplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $items.removeClass("answer");
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.removeClass("answer");
            $.each(value.split("|"), function(idx, data) {
                var $item = $items.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                if (isMultiple)
                    $item = $item.clone();   
                if (mode == "_correct") {
                    if (correctionOnly) {
                        $item.addClass("answerOk");
                    } else {
                        if (!userAnswers[key] || $.inArray(data, userAnswers[key].split("|")) < 0 )
                            $item.addClass("answerKo");
                        else
                            $item.addClass("answerOk");
                    }
                }
                $item.appendTo($dropbox)
                    .addClass(prefix+"CategoryItemDropped");
            });

            if (mode == "_correct")
                $dropbox.addClass("answer");
        });

        if (mode != "_correct" || isMultiple)
            return;

        // Gestion des intrus
        $items.addClass("answer");
        $items.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value");
            var used = false;
            $.each(userAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    used = true;
                    return false;
                }
            });
            if (correctionOnly) {
                $item.addClass("answerOk");
            } else {
                if (used)
                    $item.addClass("answerKo");
                else
                    $item.addClass("answerOk");
            }
        });
    },

    /**
     * Display right/user answer for quiz mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersColor: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+"_user"));

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").remove();
            } else {
                $choice.removeClass("answerOk answerKo");
                var classList = $choice.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $choice.removeClass(classList[classList.length - 1]);
            }
        });

        // On place les couleurs de la correction
        $.each(answers, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category")
                .filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var color = $categoryColor.attr("class").split(/\s+/)[1];

            $.each(value.split("|"), function(idx, value) {
                var $choice = $quiz.find("."+prefix+"Choice")
                    .filter("[data-choice-value=\""+value+"\"]");
                if ($choice.length > 0) {
                    if (isMultiple) {
                        var $item = $(document.createElement("span"));
                        $item.addClass(prefix+"ItemColor " + color);
                        $item.appendTo($choice);
                        if (mode == "_correct") {
                            if (correctionOnly) {
                                $item.addClass("answerOk");
                            } else {
                                if(!userAnswers[key] || 
                                        $.inArray(value, userAnswers[key].split("|")) == -1)
                                    $item.addClass("answerKo");
                                else
                                    $item.addClass("answerOk");
                            }
                        }
                    } else {
                        if (mode == "_correct") {
                            if (correctionOnly) {
                                $choice.addClass("answerOk");
                            } else {
                                if (!$choice.data("category-id") || 
                                        $choice.data("category-id") != key)
                                    $choice.addClass("answerKo");
                                else
                                    $choice.addClass("answerOk");
                            }
                        }
                        $choice.addClass(color);
                    }
                }
            });
        });
    },

    /**
     * Verify user answer for mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _verifyAnswersBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.engine.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.addClass("answer");
            var values = value.split("|");
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var data = $item.data("item-value");
                if ($.inArray(data, values) >= 0)
                    $item.addClass("answerOk");
                else
                    $item.addClass("answerKo");
            });
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.engine.clearVerify, duration);
            $.publiquiz.engine.timers.push(timer);
        }
    },

    /**
     * Verify user answer for mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _verifyAnswersColor: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var res = $.publiquiz.engine.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value");
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if ($.inArray(value, res[category].split("|")) >= 0)
                        $item.addClass("answerOk");
                    else
                        $item.addClass("answerKo");
                });
            } else {
                var category = $choice.data("category-id");
                if (category) {
                    if ($.inArray(value, res[category].split("|")) > -1)
                        $choice.addClass("answerOk");
                    else
                        $choice.addClass("answerKo");
                }
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.engine.clearVerify, duration);
            $.publiquiz.engine.timers.push(timer);
        }
    }

};

// Register function
$.publiquiz.engine.register("categories", { 
        configure: $.publiquiz.engine.categories.categoriesConfigure,
        enable: $.publiquiz.engine.categories.categoriesEnable,
        disable: $.publiquiz.engine.categories.categoriesDisable,
        help: $.publiquiz.engine.categories.categoriesHelp,
        retry: $.publiquiz.engine.categories.categoriesRetry,
        textAnswer: $.publiquiz.engine.categories.categoriesTextAnswer,
        insertUserAnswers: $.publiquiz.engine.categories.categoriesInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.categories.categoriesQuizAnswer,
        verifyAnswer: $.publiquiz.engine.categories.categoriesVerifyAnswer,
        computeScore: $.publiquiz.engine.categories.categoriesComputeScore,
        quizScore: $.publiquiz.engine.categories.categoriesScore
    });

}(jQuery));



/******************************************************************************
 *
 *                              Production
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.production = {
    
    /**
     * Configure quiz.
     */
    productionConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    productionEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Production").each( function() {
            var $this= $(this);
            $this.attr("disabled", false);
            $this.removeClass("disabled");
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Production").each( function() {
            var $this= $(this);
            $this.attr("disabled", true);
            $this.addClass("disabled");
        });
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionRetry: function($quiz) {
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    productionComputeScore: function($quiz) {
        var result = {};
        result.score = 0;
        result.total = 0;
        return result;
    },
        
    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.production:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = $("."+prefix+"Production").val();
        answer = answer.replace(/\n/g, "#R#");
        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    productionQuizAnswer: function($quiz, mode) {
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionVerifyAnswer: function($quiz) {
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.engine.register("production", { 
        configure: $.publiquiz.engine.production.productionConfigure,
        enable: $.publiquiz.engine.production.productionEnable,
        disable: $.publiquiz.engine.production.productionDisable,
        help: $.publiquiz.engine.production.productionHelp,
        retry: $.publiquiz.engine.production.productionRetry,
        textAnswer: $.publiquiz.engine.production.productionTextAnswer,
        insertUserAnswers: $.publiquiz.engine.production.productionInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.production.productionQuizAnswer,
        verifyAnswer: $.publiquiz.engine.production.productionVerifyAnswer,
        computeScore: $.publiquiz.engine.production.productionComputeScore,
        quizScore: $.publiquiz.engine.production.productionScore
    });

}(jQuery));
