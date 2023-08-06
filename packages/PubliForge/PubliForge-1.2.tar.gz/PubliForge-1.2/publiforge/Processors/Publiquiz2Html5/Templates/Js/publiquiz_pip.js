/** 
 * @projectDescription publiquiz_basics.js 
 * Plugin jQuery for quiz choices.
 *
 * @author prismallia.fr
 * @version 0.1 
 * $Id: publiquiz_pip.js 4c826a5ecf0e 2015/02/19 10:03:13 Tien $
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


/******************************************************************************
 *
 *                                  Pip
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.engine.pip = {
    
    /**
     * Configure quiz.
     */
    pipConfigure: function($quiz) {
    },

    /**
     * Set event click.
     *
     * @param {Object} jquery Object quiz.
     */
    pipEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.engine.pip._setDraggableItem($quiz.find("."+prefix+"Item"), prefix);

        // Event "drop" for pquizDrop
        $.publiquiz.engine.pip._setDroppableItem($quiz, $quiz.find("."+prefix+"Drop"));

        // Event "drop" for pquizItems
        $.publiquiz.engine.pip._setDroppableItem($quiz, $quiz.find("."+prefix+"Items"));
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pipDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Item").prop("draggable", false);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pipHelp: function($quiz) {
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pipRetry: function($quiz) {
        $.publiquiz.engine.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pipComputeScore: function($quiz) {
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

        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var total = 0;
        var score = 0;
        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            total++;
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var data = $item.data("item-value");
                if (data == value)
                    score += 1;
            } else if ($item.length == 0 && value == "") {
                score += 1;
            }
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
    pipScore: function($quiz) {
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.pip:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pipTextAnswer: function($quiz) {
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pipInsertUserAnswers: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"Item").each( function() {
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
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pipQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.engine.correction($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.engine.correctionCategories($quiz.find("#"+quzId+"_user"));

        // On enleve la correction
        if (isMultiple) {
            $quiz.find("."+prefix+"ItemDropped").remove();
        } else {
            $quiz.find("."+prefix+"ItemDropped").each( function() {
                var $item = $(this);
                $item.appendTo($items)
                    .removeClass(prefix+"ItemDropped " +
                        prefix+"ItemImageDropped");
            });
        }

        // On place la correction en deplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.text("");
            $dropbox.removeClass("answerOk answerKo");
            var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            if (isMultiple)
                $item = $item.clone();
                if (mode == "_correct") {
                    if (correctionOnly) {
                        $dropbox.addClass("answerOk");
                    } else {
                        if ((!userAnswers[key] && value != "") ||
                            (userAnswers[key] && value == "") ||
                            (userAnswers[key] && userAnswers[key] != value))
                            $dropbox.addClass("answerKo");
                        else
                            $dropbox.addClass("answerOk");
                    }
                }
                $item.appendTo($dropbox)
                    .addClass(prefix+"ItemDropped " +
                        prefix+"ItemImageDropped");
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pipVerifyAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var data = $item.data("item-value");
                if (data == value)
                    $dropbox.addClass("answerOk");
                else
                    $dropbox.addClass("answerKo");
            }
        });

        var timer = setTimeout($.publiquiz.engine.clearVerify, $.publiquiz.engine.duration);
        $.publiquiz.engine.timers.push(timer);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Add drag on item.
     *
     * @params {Object} $item : jQuery object item.
     * @params {String} prefix : use for construct class name.
     */
    _setDraggableItem: function($item, prefix) {
        var format = "text/html";
        $item.on({
            dragstart: function(ev) {
                var $target = $(ev.target);
                while (!$target.hasClass(prefix+"Item"))
                    $target = $target.parent();
                if ($target.attr("draggable") == "false") {
                    ev.preventDefault();
                    return;
                }
                $.publiquiz.engine.clearVerify();
                ev.dataTransfer.setData(format, $target.attr("id"));
            },
            dragover: function(ev) { 
                ev.preventDefault();
                var $dropbox = $(ev.target);
                if (ev.target.nodeName.toLowerCase() == "img")
                    $dropbox = $dropbox.parent().parent();
                else
                    $dropbox = $dropbox.parent();

                if ($dropbox.hasClass(prefix+"Items")) {
                    $dropbox.addClass("dragOver");
                    $dropbox.find("."+prefix+"Item").addClass("dragOver");
                }
            },
            dragleave: function() { 
                $(this).removeClass("dragOver");
            }
        }); 
    },

    /**
     * Add drop on item.
     *
     * @params {Object} $quiz: jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     */
    _setDroppableItem: function($quiz, $item) {
        var $this = this;
        var format = "text/html";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        $item.on({
            dragover: function(ev) { 
                ev.preventDefault();
                var $dropbox = $(ev.target);
                if ($dropbox.hasClass(prefix+"Items")) {
                    $dropbox.addClass("dragOver");
                    $dropbox.find("."+prefix+"Item").addClass("dragOver");
                } else {
                    $dropbox.addClass("pipDragOver");
                }
            },
            dragenter: function(ev) { 
                ev.preventDefault();
                var $dropbox = $(ev.target);
                if ($dropbox.hasClass(prefix+"Items")) {
                    $dropbox.addClass("dragOver");
                    $dropbox.find("."+prefix+"Item").addClass("dragOver");
                } else {
                    $dropbox.addClass("pipDragOver");
                }
            },
            dragleave: function() { 
                var $dropbox = $(this);
                $dropbox.removeClass("pipDragOver dragOver");
                $dropbox.find(".dragOver").removeClass("dragOver");
                $dropbox.find(".pipDragOver").removeClass("pipDragOver");
            },
            drop: function(ev) {
                ev.preventDefault();
                var $dropbox = $(ev.target);
                var dropboxId = "";
                
                if (ev.target.nodeName.toLowerCase() == "img")
                    $dropbox = $dropbox.parent();

                if ($dropbox.hasClass(prefix+"Drop")) {
                    dropboxId = $dropbox.attr("id");
                    dropboxId = dropboxId.substring(0, dropboxId.length - 4);
                } else if ($dropbox.hasClass(prefix+"Item")) {
                    dropboxId = $dropbox.attr("id");
                    dropboxId = dropboxId.substring(0, dropboxId.length - 8);
                } else if ($dropbox.hasClass(prefix+"Items")) {
                    dropboxId = $dropbox.attr("id");
                    dropboxId = dropboxId.substring(0, dropboxId.length - 6);
                }

                // On récupère l'id  de l'item en cours de deplacement
                var itemQuizId = ev.dataTransfer.getData(format);
                itemQuizId = itemQuizId.substring(0, itemQuizId.length - 8);

                // On a dropper dans un block ou item d'un autre exercice
                if (itemQuizId != dropboxId) {
                    $dropbox.removeClass("dragOver");
                    $dropbox.removeClass("pipDragOver");
                    return;
                }

                // On récupère l'item en cours de deplacement
                var data = ev.dataTransfer.getData(format);
                var $item = $quiz.find("#"+data);

                // On le déplace dans la boite a items
                if ($dropbox.hasClass(prefix+"Items") || 
                        $dropbox.parent().hasClass(prefix+"Items")) {

                    // L'item que l'on deplace vient de la boite a items
                    if ($item.parent().hasClass(prefix+"Items")) {
                        $dropbox = $item.parent();
                        $dropbox.removeClass("dragOver pipDragOver");
                        $dropbox.find(".dragOver").removeClass("dragOver");
                        $dropbox.find(".pipDragOver").removeClass("pipDragOver");
                        return;
                    }

                    // On passe sur un item qui est dans la boite a items
                    // On récupere la boite a items
                    if ($dropbox.parent().hasClass(prefix+"Items")) {
                        $dropbox.removeClass("dragOver pipDragOver");
                        $dropbox = $dropbox.parent();
                    }

                    if (isMultiple) {
                        $item.remove();
                    } else {
                        $item.appendTo($dropbox)
                            .removeClass(prefix+"ItemDropped " +
                                    prefix+"ItemImageDropped " +
                                    "dragOver pipDragOver");
                        $this.setDraggableItem($item, prefix);
                    }

                    $dropbox.removeClass("dragOver pipDragOver");
                    $dropbox.find(".dragOver").removeClass("dragOver");
                    $dropbox.find(".pipDragOver").removeClass("pipDragOver");
                    return;
                }

                // Si le block a déjà un element, on enlève celui en place
                if ($dropbox.hasClass(prefix+"Item")) {
                    var $tmp = $dropbox.parent();
                    if (isMultiple) {
                        $dropbox.remove();
                    } else {
                        $dropbox.removeClass("dragOver pipDragOver " +
                                prefix+"ItemDropped " +
                                prefix+"ItemImageDropped")
                            .appendTo($quiz.find("#"+quzId+"_items"));
                        $.publiquiz.engine.setDraggableItem($dropbox, prefix);
                    }
                    $dropbox = $tmp;
                } else if ($dropbox.hasClass(prefix+"Drop") && 
                        $dropbox.find("."+prefix+"Item").length > 0) {
                    var $itm = $dropbox.find("."+prefix+"Item");
                    if(isMultiple) {
                        $itm.remove();
                    } else {
                        $itm.removeClass(prefix+"ItemDropped " +
                                prefix+"ItemImageDropped")
                            .appendTo($quiz.find("#"+quzId+"_items"));
                        $.publiquiz.engine.pip._setDraggableItem($itm, prefix);
                    }
                }

                // On déplace l'item dans la dropbox
                $dropbox.text("");
                $dropbox.removeClass("dragOver pipDragOver");
                if (isMultiple && $item.parent().hasClass(prefix+"Items")) {
                    var count = $quiz.find("."+prefix+"Item").length;
                    $item = $item.clone();
                    $item.attr("id", quzId+"_item"+$.publiquiz.engine.formatNumber(count += 100, 3));
                }
                $item.appendTo($dropbox)
                    .addClass(prefix+"ItemDropped " +prefix+"ItemImageDropped")
                    .removeClass("dragOver pipDragOver");
                $.publiquiz.engine.pip._setDraggableItem($item, prefix);
            },
            dragend: function(ev) {
                //ev.dataTransfer.clearData(format);
            }
        });
    }

};

// Register function
$.publiquiz.engine.register("pip", { 
        configure: $.publiquiz.engine.pip.pipConfigure,
        enable: $.publiquiz.engine.pip.pipEnable,
        disable: $.publiquiz.engine.pip.pipDisable,
        help: $.publiquiz.engine.pip.pipHelp,
        retry: $.publiquiz.engine.pip.pipRetry,
        textAnswer: $.publiquiz.engine.pip.pipTextAnswer,
        insertUserAnswers: $.publiquiz.engine.pip.pipInsertUserAnswers,
        quizAnswer: $.publiquiz.engine.pip.pipQuizAnswer,
        verifyAnswer: $.publiquiz.engine.pip.pipVerifyAnswer,
        computeScore: $.publiquiz.engine.pip.pipComputeScore,
        quizScore: $.publiquiz.engine.pip.pipScore
    });

}(jQuery));
