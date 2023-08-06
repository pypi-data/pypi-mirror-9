/** 
 * @projectDescription publiquiz.js 
 * Javascript for quiz on library jquery, create namespace for basics 
 * functions for quiz.
 *
 * @author prismallia.fr
 * @version 0.1 
 * $Id: publiquiz.js 4c826a5ecf0e 2015/02/19 10:03:13 Tien $
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
 *                              Namespace publiquiz
 *
******************************************************************************/

(function ($) {

"use strict";

// Extend event, add property "dataTransfer" for save item drag 
$.event.props.push("dataTransfer");

// Define namespace publiquiz if not exist
if (!$.publiquiz)
    $.publiquiz = {};

// Define defaults options 
$.publiquiz.defaults =  {
            debug: false,
            prefix: "pquiz",
            baseScore: -1,
            displayCorrectionOnly: false,
            verifyDuration: 3000,
            eventType: "mouse"
        };

// Define namespace publiquiz.engine
$.publiquiz.engine = {

    /**
     * Define variables for register function.
     */
    enable: {},
    disable: {},
    configure: {},
    help: {},
    retry: {},
    textAnswer: {},
    insertUserAnswers: {},
    quizAnswer: {},
    verifyAnswer: {},
    computeScore: {},
    quizScore: {},
    scoreFunc: {},

    // Référence au tableau contenant les timer pour la fonction "verify"
    timers: [],

    /**
     * Register function score by quiz id.
     *
     * @param {String} quzId, id of quiz.
     * @param {Object} $quiz, object jquery quiz.
     * @param {OBject} func, functions for compute score.
     */
    registerScoreFunc: function(quzId, $quiz, func) {
        this.scoreFunc[quzId] = {quiz: $quiz, func: func}; 
    },

    /**
     * Register function.
     *
     * @param {String} engine: type of engine apply function.
     * @param {Dictionnary} functions: function we want register.
     */
    register: function(engine, functions) {
        var $this = this;
        $.each(functions, function(key, func) {
            switch (key) {
                case ("enable"):
                    $this.enable[engine] = func;
                    break;
                case ("disable"):
                    $this.disable[engine] = func;
                    break;
                case ("configure"):
                    $this.configure[engine] = func;
                    break;
                case ("help"):
                    $this.help[engine] = func;
                    break;
                case ("retry"):
                    $this.retry[engine] = func;
                    break;
                case ("textAnswer"):
                    $this.textAnswer[engine] = func;
                    break;
                case ("insertUserAnswers"):
                    $this.insertUserAnswers[engine] = func;
                    break;
                case ("quizAnswer"):
                    $this.quizAnswer[engine] = func;
                    break;
                case ("verifyAnswer"):
                    $this.verifyAnswer[engine] = func;
                    break;
                case ("computeScore"):
                    $this.computeScore[engine] = func;
                    break;
                case ("quizScore"):
                    $this.quizScore[engine] = func;
                    break;
                default:
                    console.log("Namespace publiquiz unknown function: '"+key+"' for engine: '"+engine+"'");
            }
        });
    },


    /**********************************************************************
     *                          Quiz Ui function
     *********************************************************************/

    /**
     * Add drag on item.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    setDraggableItem: function($quiz, $item, suffix) {
        if ($item.length === 0)
            return;
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var evtStart = "mousedown";
        var evtMove = "mousemove";
        var evtEnd = "mouseup";
        if ($.publiquiz.defaults.eventType != "mouse") {
            evtStart = "touchstart";
            evtMove = "touchmove";
            evtEnd = "touchend";
        }

        if ($item.find("img").length > 0)
            $item.find("img").on("dragstart", function(ev) { ev.preventDefault(); });

        $item.bind(evtStart, function(ev) {
            var $target = $(ev.target);
            while (!$target.hasClass(prefix+suffix+"Item"))
                $target = $target.parent();
            if ($item.attr("draggable") == "false")
                return;
            $this.clearVerify();
            $target.addClass("dragging");
            var $ghost = $this.makeGhost($target, ev);
            var $dropbox = null;
            $(document).bind(evtMove, function(e) {
                if (!$target.hasClass("dragging"))
                    return;
                e.preventDefault();
                $dropbox = $this.dragItem($quiz, $ghost, suffix, e);
            });
            $(document).bind(evtEnd, function(e) {
                if (!$target.hasClass("dragging"))
                    return;
                $ghost.remove();
                $this.dropItem($quiz, $dropbox, $target, suffix);
                $dropbox = null;
            });
        });
    },

    /**
     * Helper, drag item and return a valide dropbox object.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $ghost : jQuery object ghost.
     * @params {String} suffix : String suffix class name.
     * @params {Event} ev : Object event.
     * @return Object dropbox.
     */
    dragItem: function($quiz, $ghost, suffix, ev) {
        var $this = this;
        var $dropbox = null;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver");

        var pos = $this.eventPosition($ghost, ev);
        $ghost.css("left", pos[0]+"px");
        $ghost.css("top", pos[1]+"px");

        var bodyHeight = $(document).height();
        var scrollHeight = $(document).scrollTop();
        var pageHeight = $(window).height();

        /*console.log("bodyHeight: "+bodyHeight);*/
        /*console.log("scrollHeight: "+scrollHeight);*/
        /*console.log("pageHeight: " + pageHeight);*/
        
        var elemPosY = pos[1]+$ghost.height()+20;
        if (elemPosY > (pageHeight+scrollHeight)) {
            var offset = elemPosY - (pageHeight+scrollHeight);
            window.scrollTo(0, scrollHeight+offset);
        }

        var $elementOver = $(document.elementFromPoint(pos[2], pos[3]));
        if ($elementOver.length === 0)
            return $dropbox;
        if ($elementOver[0] == $ghost[0]) {
            $ghost.css("display", "none");
            $elementOver = $(document.elementFromPoint(pos[2], pos[3]));
            $ghost.css("display", "block");
        }

        if ($elementOver[0].nodeName.toLowerCase() == "img" && $elementOver.parent().hasClass(prefix+suffix+"Item"))
            $elementOver = $elementOver.parent();

        var dropId = $elementOver.attr("id");
        if ($elementOver.attr("class") && $elementOver.attr("class").search(prefix+suffix+"Drop") > -1) {
            dropId = dropId.substring(0, dropId.length - 4);
            if (dropId == quzId) {
                $dropbox = $elementOver;
                $dropbox.addClass("dragOver");
            }
        } else if ($elementOver.hasClass(prefix+suffix+"Item") && $elementOver.parent().hasClass(prefix+suffix+"Drop")) {
            dropId = dropId.substring(0, dropId.length - 8);
            if (dropId == quzId) {
                $dropbox = $elementOver.parent();
                $dropbox.addClass("dragOver");
            }
        } else {
            $dropbox = null;
        }
        
        return $dropbox;
    },

    /**
     * Helper, drop item.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $dropbox : jQuery object dropbox.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    dropItem: function($quiz, $dropbox, $item, suffix) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var evtStart = "mousedown";
        var evtMove = "mousemove";
        var evtEnd = "mouseup";
        if ($.publiquiz.defaults.eventType != "mouse") {
            evtStart = "touchstart";
            evtMove = "touchmove";
            evtEnd = "touchend";
        }
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("multiple") > -1 )
                isMultiple = true;

        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver");
        $item.removeClass("dragging");

        // On remet l'item dans la boite a items
        if ($dropbox === null) {
            if ($item.parent().hasClass(prefix+suffix+"Drop")) {
                if (engine != "categories")
                    $item.parent().text(".................");
                $this.cancelItemDrop($quiz, $item, suffix);
            }
            $(document).unbind(evtMove);
            $(document).unbind(evtEnd);
            return;
        }

        // Si le block a déjà un element, on enlève celui en place
        if (engine != "categories") {
            var $itm = $dropbox.find("."+prefix+suffix+"Item");
            if ($itm.length > 0)
                $this.cancelItemDrop($quiz, $itm, suffix);

            // Si l'ancien emplacement de l'item était un pquizDrop
            if ($item.parent().hasClass(prefix+suffix+"Drop") && engine != "blanks-color")
                $item.parent().text(".................");
        } else {
            // On vérifie que la boite de drop n'as pas encore l'item
            var find = $dropbox.find("."+prefix+suffix+"Item").filter("[data-item-value=\""+$item.data("item-value")+"\"]");
            if (isMultiple && find.length > 0) {
                $dropbox.removeClass("dragOver");
                if ($item.parent().hasClass(prefix+suffix+"Drop")) {
                    $item.remove();
                } else {
                    $item.unbind(evtStart);
                    $(document).unbind(evtMove);
                    $(document).unbind(evtEnd);
                    $this.setDraggableItem($quiz, $item, suffix);
                }
                return;
            }
        }

        // On déplace l'item dans la dropbox
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        var count = 0;
        if (engine == "blanks-color") {
            var color = $item.find("."+prefix+"ItemColor").css("background-color");
            $dropbox.css("fill", color);
            $dropbox.data("choice-value", $item.data("item-value"));
            $this.setDraggableItem($quiz, $item, suffix);
        } else if (engine == "categories") {
            $dropbox.removeClass("dragOver");
            if (isMultiple && $item.parent().hasClass(prefix+"CategoriesItems")) {
                count = $quiz.find("."+prefix+suffix+"Item").length;
                $this.setDraggableItem($quiz, $item, suffix);
                $item = $item.clone();
                $item.attr("id", quzId+"_item"+$.publiquiz.engine.formatNumber(count += 100, 3));
            }
            $item.appendTo($dropbox)
                .addClass(prefix+"CategoryItemDropped");
            $dropbox.find("."+prefix+suffix+"Item").removeClass("dragOver");
            $this.setDraggableItem($quiz, $item, suffix);
        } else {
            $dropbox.text("");
            $dropbox.removeClass("dragOver");
            if (isMultiple && $item.parent().hasClass(prefix+suffix+"Items")) {
                count = $quiz.find("."+prefix+suffix+"Item").length;
                $this.setDraggableItem($quiz, $item, suffix);
                $item = $item.clone();
                $item.attr("id", quzId+"_item"+$this.formatNumber(count += 100, 3));
            }
            $item.appendTo($dropbox)
                   .addClass(prefix+"ItemDropped");
            $this.setDraggableItem($quiz, $item, suffix);

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0)
                $item.addClass(prefix+"InlineItemImageDropped");
            else if (engine == "matching" &&
                $item.children("img").length > 0)
            $item.addClass(prefix+"BlockItemImageDropped");
        }
    },

    /**
     * Helper, get event position (mouse or touch).
     *
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @return Array: position X/Y, original position
     */
    eventPosition: function($target, ev) {
        var scrollHeight = $(document).scrollTop();

        var first = null;
        var originalX = null;
        var originalY = null;
        var posX = null;
        var posY = null;

        if ($.publiquiz.defaults.eventType != "mouse") {
            var touches = ev.originalEvent.changedTouches;
            first = touches[0];

            originalX = first.screenX;
            originalY = first.screenY;
            posX = originalX-$target.width();
            posY = originalY-$target.height()+scrollHeight;
        } else {
            if (ev.pageX || ev.pageY) {
                originalX = ev.pageX;
                originalY = ev.pageY;
            } else {
                originalX = ev.clientX + document.body.scrollLeft - document.body.clientLeft;
                originalY = ev.clientY + document.body.scrollTop  - document.body.clientTop;
            }
            posX = originalX-$target.width();
            posY = originalY-$target.height();

            // If page scroll
            originalY = originalY - scrollHeight;
        }

        return [posX, posY, originalX, originalY];
    },

    /**
     * Helper, make ghost of item touch.
     *
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @return Object ghost.
     */
    makeGhost: function($target, ev) {
        var $this = this;
        var pos = $this.eventPosition($target, ev);
        var posX = pos[0];
        var posY = pos[1];

        var $ghost = $target.clone();

        // Specific when we are in opener
        if ($target.children("img").length > 0) {
            $ghost.children("img").css("width", $target.children("img").css("width"));
            $ghost.children("img").css("height", $target.children("img").css("height"));
        }

        $ghost.appendTo($("body"));
        $ghost.css("opacity", "0.25");
        $ghost.css("position", "absolute");
        $ghost.css("left", (posX+($target.width()-$ghost.width()))+"px");
        $ghost.css("top", (posY+($target.height()-$ghost.height()))+"px");
        return $ghost;
    },

    /**
     * Helper, cancel a item dropped.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    cancelItemDrop: function($quiz, $item, suffix) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 ) {
            $item.remove();
            return;
        }

        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var evtStart = "mousedown";
        var evtMove = "mousemove";
        var evtEnd = "mouseup";
        if ($.publiquiz.defaults.eventType != "mouse") {
            evtStart = "touchstart";
            evtMove = "touchmove";
            evtEnd = "touchend";
        }

        $item.removeClass(prefix+"ItemDropped " +
                prefix+"CategoryItemDropped " +
                prefix+"InlineItemImageDropped " +
                prefix+"BlockItemImageDropped")
            .appendTo($quiz.find("#"+quzId+"_items"));
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        $this.setDraggableItem($quiz, $item, suffix);
    },

    /**
     * Function call for display/hide help
     *
     * @param {Object} $quiz, object jquery quiz.
     */
    displayHelp: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $hlp = $quiz.find("#"+quzId+"_help-slot");
        if ($hlp.css("display") == "none")
            $hlp.slideDown("slow");
        else
            $hlp.slideUp("slow");
    },

    /**
     * Display quiz text answer.
     *
     * @param {Object} quiz.
     */
    displayTextAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0)
            $answer.slideDown("slow");
    },

    /**
     * Hide quiz text answer.
     *
     * @param {Object} quiz.
     */
    hideTextAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0 && $answer.css("display") != "none")
            $answer.slideUp("slow");
    },


    /**********************************************************************
     *                          Quiz retry function
     *********************************************************************/

    /**
     * Retry quiz choices, keep only right answer.
     *
     * @param {Object} quiz.
     * @params {String} suffix : suffix string for select object.
     */
    retryChoices: function($quiz, suffix) {
        var $this = this;
        $this.clearVerify();
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;
        if (engine == "choices-radio") {
            $quiz.find("."+prefix+suffix+" input").prop("checked", false);
            $quiz.find("."+prefix+suffix).removeClass("selected");
        } else {
            var quzId = $quiz.data("quiz-id");
            var res = $this.correction($quiz.find("#"+quzId+"_correct"));

            if (isCheckRadio) {
                var $engine = $quiz.find("#"+quzId+"_engine");

                // Get group
                var choices = [];
                $quiz.find("."+prefix+"Choice").each( function() {
                    var group = $(this).data("group");
                    if ($.inArray(group, choices) < 0 )
                        choices.push(group);
                });
                
                // Keep only right choice
                $.each(choices, function() {
                    var group = this;
                    var $item = null;
                    if (res[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"false\"]")
                                        .hasClass("selected")) {
                        $item = $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"false\"]");
                        $item.find("input").prop("checked", false);
                        $item.removeClass("selected");
                    } else if (!res[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"true\"]")
                                        .hasClass("selected")) {
                        $item = $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"true\"]");
                        $item.find("input").prop("checked", false);
                        $item.removeClass("selected");
                    }
                });
            } else {
                $quiz.find("."+prefix+suffix).each( function() {
                    var $elem = $(this);
                    var _id = $elem.attr("id");
                    var key = _id.substring(_id.length - 3, _id.length);

                    if ($elem.hasClass("selected") && !(key in res)) {
                        $elem.find("input").prop("checked", false);
                        $elem.removeClass("selected");
                    }
                });
            }
        }
    },

    /**
     * Retry quiz blanks, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryBlanks: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var engine = $quiz.data("engine");
        if (engine == "blanks-fill") {
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

            var res = $this.correction($quiz.find("#"+quzId+"_correct"));
            $.each(res, function(key, value) {
                var $item = $quiz.find("#"+quzId+"_"+key);
                var data = $item.val().trim();

                if (!$this.isValideBlanksFillAnswer(data, value, isStrict, options))
                    $item.val("");

            });
        } else {
            $this.retryQuizCmp($quiz);
        }
    },

    /**
     * Retry quiz pointing category, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryPointingCategory: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && res[category].search(pointId) == -1) {
                var classList = $point.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $point.removeClass(classList[classList.length - 1]);
            }

        });
    },

    /**
     * Retry quiz categories, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryCategories: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));

        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $choice = $(this);
                var value = $choice.data("choice-value");
                if (isMultiple) {
                    $choice.find("."+prefix+"ItemColor").each( function() {
                        var $item = $(this);
                        var category = $item.data("category-id");
                        if (category && $.inArray(value, res[category].split("|")) == -1)
                            $item.remove();
                    });
                } else {
                    var category = $choice.data("category-id");
                    if (category && $.inArray(value, res[category].split("|")) == -1) {
                        var classList = $choice.attr("class").split(/\s+/);
                        if (classList.length > 1)
                            $choice.removeClass(classList[classList.length - 1]);
                    }
                }
            });
        } else {
            var $items = $quiz.find("#"+quzId+"_items");
            $.each(res, function(key, value) {
                var $dropbox = $quiz.find("#"+quzId+"_"+key);
                var values = value.split("|");
                $dropbox.find("."+prefix+"CategoryItem").each( function() {
                    var $item = $(this);
                    var data = $item.data("item-value");
                    if ($.inArray(data, values) == -1) {
                        if (isMultiple)
                            $item.remove();
                        else
                            $item.appendTo($items).removeClass(prefix+"CategoryItemDropped");
                    }
                });
            });
        }
    },

    /**
     * Retry quiz engine compared mode check.
     *
     * @params {Object} $quiz : Object jquery quiz.
     */
    retryQuizCmp: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var $items = $quiz.find("#"+quzId+"_items");

        var res;
        if (engine == "pip")
            res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));
        else
            res = $this.correction($quiz.find("#"+quzId+"_correct"));
    
        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && $item.data("item-value") != value ) {
                if (isMultiple) {
                    $item.remove();
                } else {
                    $item.removeClass(prefix+"ItemDropped "+
                        prefix+"ItemImageDropped" +
                        prefix+"InlineItemImageDropped " +
                        prefix+"BlockItemImageDropped")
                        .appendTo($items);
                }

                if (engine != "pip")
                    $dropbox.text(".................");
            }
        });
    },


    /**********************************************************************
     *                  Quiz insert user anwer function
     *********************************************************************/

    /**
     * Insert user answers in html for quiz compare
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     */
    insertUserAnswersQuizChoices: function($quiz, suffix) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+suffix+".selected").each( function() {
            var $item = $(this);
            var _id = $item.attr("id");
            _id = _id.substring(_id.length - 3, _id.length) + "x";
            if (answer !== "")
                answer += "::";
            answer += _id;
        });

        $this.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Insert user answers in html for quiz drop
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    inserUserAnswersQuizDrop: function ($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this); 
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var value = $item.data("item-value");
                if (answer !== "")
                    answer += "::";
                var id = $dropbox.attr("id"); 
                answer += id.substring(id.length - 3, id.length) + value;
            }
        });

       $this.writeUserAnswers($quiz, quzId, answer);
    },


    /**********************************************************************
     *                          Quiz score function
     *********************************************************************/

    /**
     * Show quiz score.
     */
    displayQuizScore: function($quiz) {
    },

    /**
     * Show global score.
     */
    displayScore: function() {
        var result = this.computeScores();
        var score = result.score;
        var total = result.total;
        var baseScore = $.publiquiz.defaults.baseScore;
        if (baseScore > -1) {
            score = (score * baseScore) / total.toFixed(1);
            score = Math.round(score);
            total = baseScore;
        }

        if (total === 0)
            return;

        var $elem = $("#"+$.publiquiz.defaults.prefix+"GlobalScore");
        $elem.text(score + " / " + total);
        $elem.removeClass("hidden");
    },

    /**
     * Compute score for all quiz register.
     *
     * @return {Dictionnary}.
     */
    computeScores: function() {
        var score = 0.0;
        var total = 0;
        $.each(this.scoreFunc, function(quzId, data) {
            var res = data.func(data.quiz);
            score += res.score;
            total += res.total;
        });
        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode radio.
     *
     * @param {Object} jquery Object quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesRadio: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if (! $item.hasClass("selected")) {
                correct = false;
                return false;
            }
            return false;
        });
        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode check.
     * Le score se calcule par rapport au poids de la réponse, la réponse
     * fausse vaut toujours '-1' point.
     *
     * @param {Object} jquery Object quiz.
     * @params {String} suffix : suffix string for select object.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesCheck: function($quiz, suffix) {
        var $this = this;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0.0;
        var total = $quiz.find("."+prefix+suffix).length;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        // On determine le poids d'une reponse correcte
        var weight_correct = total / Object.keys(res).length;

        $quiz.find("."+prefix+suffix).each( function() {
            var $elem = $(this);
            var _id = $elem.attr("id");
            var key = _id.substring(_id.length - 3, _id.length);

            if ($elem.hasClass("selected") && key in res)
                score += weight_correct;
            else if ($elem.hasClass("selected") && !(key in res))
                score -= 1;
        });

        score = Math.round(score);
        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode check.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpCheck: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));
    
        var total = 0;
        total = $quiz.find("."+prefix+"Drop").length;
        var score = 0;

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && $item.data("item-value") == value)
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode radio.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpRadio: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length === 0) {
                correct = false;
                return false;
            }
            if ($item.data("item-value") != value) {
                correct = false;
                return false;
            }
            return null;
        });

        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },


    /**********************************************************************
     *                      Quiz verify function
     *********************************************************************/

    /**
     * Suppression des informations de verification du quiz
     */
    clearVerify: function() {
        $.each($.publiquiz.engine.timers, function() {
            clearTimeout(this);
        });
        $($.find(".answer")).removeClass("answer");
        $($.find(".answerKo")).removeClass("answerKo");
        $($.find(".answerOk")).removeClass("answerOk");
    },

    /**
     * Verify user answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    verifyQuizChoicesAnswer: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");

        var rightAnswers = $this.correction($quiz.find("#"+quzId+"_correct"));
        if (engine == "pointing") {
            $quiz.find("."+prefix+"Point").each( function() {
                var $item = $(this);
                var key = $item.attr("id");
                key = key.substring(key.length - 3, key.length);
                if ($item.hasClass("selected")) {
                    if (rightAnswers[key])
                        $item.addClass("answerOk");
                    else
                        $item.addClass("answerKo");
                }
            });
        } else {
            var isCheckRadio = false;
            if ($quiz.data("engine-options") && 
                    $quiz.data("engine-options").search("radio") > -1 )
                isCheckRadio = true;
            if (isCheckRadio) {
                var $engine = $quiz.find("#"+quzId+"_engine");

                // Get group
                var choices = [];
                $quiz.find("."+prefix+"Choice").each( function() {
                    var group = $(this).data("group");
                    if ($.inArray(group, choices) < 0 )
                        choices.push(group);
                });

                // Verify user answer
                $.each(choices, function() {
                    var group = this;
                    if (rightAnswers[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"true\"]")
                                        .hasClass("selected")) {
                        $engine.find("."+prefix+"Choice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter("[data-name=\"true\"]")
                            .addClass("answerOk");
                    } else if (rightAnswers[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"false\"]")
                                        .hasClass("selected")) {
                        $engine.find("."+prefix+"Choice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter("[data-name=\"false\"]")
                            .addClass("answerKo");
                    } else if (!rightAnswers[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"false\"]")
                                        .hasClass("selected")) {
                        $engine.find("."+prefix+"Choice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter("[data-name=\"false\"]")
                            .addClass("answerOk");
                    } else if (!rightAnswers[group] && $engine.find("."+prefix+"Choice")
                                        .filter("[data-group=\""+group+"\"]")
                                        .filter("[data-name=\"true\"]")
                                        .hasClass("selected")) {
                        $engine.find("."+prefix+"Choice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter("[data-name=\"true\"]")
                            .addClass("answerKo");
                    }
                });
            } else {
                $quiz.find("."+prefix+"Choice").each( function() {
                    var $item = $(this);
                    var key = $item.attr("id");
                    key = key.substring(key.length - 3, key.length);
                    if ($item.hasClass("selected")) {
                        if (rightAnswers[key])
                            $item.addClass("answerOk");
                        else
                            $item.addClass("answerKo");
                    }
                });
            }
        }

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($this.clearVerify, duration);
            $this.timers.push(timer);
        }
    },

    /**
     * Verify user answer for quiz cmp.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    verifyQuizCmpAnswer: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0)
                if($item.data("item-value") == value)
                    $dropbox.addClass("answerOk");
                else
                    $dropbox.addClass("answerKo");
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($this.clearVerify, duration);
            $this.timers.push(timer);
        }
    },


    /**********************************************************************
     *                      Quiz correction function
     *********************************************************************/

    /**
     * Display right/user answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizChoicesAnswer: function($quiz, suffix, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var correctionOnly = $quiz.data("display-correction-only");

        var isModeRadio = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("radio") > -1 )
            isModeRadio = true;

        // Reset quiz
        $quiz.find("."+prefix+suffix+" input").prop("checked", false);
        $quiz.find("."+prefix+suffix).removeClass("selected answerOk answerKo");

        // Display pquizChoice selected
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        $quiz.find("."+prefix+suffix).each( function() {
            var $item = $(this);
            var key = $item.attr("id");
            key = key.substring(key.length - 3, key.length);
            if (answers[key]) {
                $item.addClass("selected");

                // If Input set checked
                var $input = $item.find("input");
                if ($input.length > 0)
                    $input.prop("checked", true);

                // Set answerOk/Ko
                if (mode == "_correct") {
                    if (correctionOnly) {
                        $item.addClass("answerOk");
                    } else {
                        if (!userAnswers[key])
                            $item.addClass("answerKo");
                        else
                            $item.addClass("answerOk");
                    }
                }
            } 
            
            if (correctionOnly || mode != "_correct")
                return true;

            if ((!userAnswers[key] && answers[key]) || (userAnswers[key] && !answers[key]))
                $item.addClass("answerKo");
            else {
                if (engine != "choices-radio" && !isModeRadio)
                    $item.addClass("answerOk");
            }
        });
    },

    /**
     * Display right/user answer for quiz drag and drop.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizCmpAnswer: function($quiz, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var isMultiple = false;
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        // On vide les champs
        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this); 
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                if (isMultiple) {
                    $item.remove();
                } else {
                    $item.removeClass(prefix+"ItemDropped "+
                        prefix+"InlineItemImageDropped " +
                        prefix+"BlockItemImageDropped")
                        .appendTo($quiz.find("#"+quzId+"_items"));
                }
                $dropbox.text(".................")
                    .removeClass("answerOk answerKo");
            }
        });

        var $items = $quiz.find("#"+quzId+"_items");
        $items.find("."+prefix+"Item").removeClass("answerKo answerOk hidden");

        // On place la correction en deplacant les items
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            if ($item.length > 1)
                $item = $($item[0]);
            if (isMultiple)
                $item = $item.clone();
            $dropbox.text("");
            if (mode == "_correct") {
                if (correctionOnly) {
                    $dropbox.addClass("answerOk");
                } else {
                    if (!userAnswers[key] || userAnswers[key] != value)
                        $dropbox.addClass("answerKo");
                    else 
                        $dropbox.addClass("answerOk");
                }
            }
            $item.appendTo($dropbox)
                .addClass(prefix+"ItemDropped");

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0)
                $item.addClass(prefix+"InlineItemImageDropped");
            else if (engine == "matching" && $item.children("img").length > 0)
                $item.addClass(prefix+"BlockItemImageDropped");
        });

        if (mode != "_correct" || isMultiple)
            return;

        // Gestion des intrus
        var values = [];
        var droppeds = [];
        $.each(userAnswers, function(key, value) { values.push(value); });
        $.each(answers, function(key, value) { 
            if( $.inArray(value, droppeds) == -1)
                droppeds.push(value); 
        });
        $quiz.find("#"+quzId+"_items")
                .find("."+prefix+"Item").each( function() {
            var $item = $(this);
            var value = $item.data("item-value");

            // S'il y a plusieurs etiquette de meme valeur dans la correction on les cache
            if ($.inArray(value, droppeds) >= 0)
                $item.addClass("hidden");

            if (correctionOnly && $.inArray(value, values) < 0) {
                $item.addClass("answerOk");
            } else {
                if ($.inArray(value, values) < 0)
                    $item.addClass("answerOk");
                else
                    $item.addClass("answerKo");
            }
        });
    },

    /**
     * Display right/user answer for quiz engine blanks-fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {String} mode : display correct/user answer.
     */
    displayQuizAnswerBlanksFill: function($quiz, mode) {
        var $this = this;
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");

        // On vide les champs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $item = $(this);
            $item.val("");
            $item.removeClass("answerOk answerKo");
        });

        var quzId = $quiz.data("quiz-id");
        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") && 
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));
        $.each(answers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                // Set text
                var data = value.split("|").join(" / ");
                data = data.replace(new RegExp(/_/g), " ");
                $item.val(data);

                // Validate user answer in mode correction
                if (mode == "_correct") {
                    if (correctionOnly) {
                        $item.addClass("answerOk");
                    } else {
                        if ((!userAnswers[key] && value !== "") ||
                            !$this.isValideBlanksFillAnswer(userAnswers[key], value, isStrict, options))
                            $item.addClass("answerKo");
                        else
                            $item.addClass("answerOk");
                    }
                }
            }
        });
    },



    /**********************************************************************
     *                          Quiz library function
     *********************************************************************/

    /**
     * Shuffle items.
     *
     * @params {Object} $items : object jquery items.
     */
    shuffleItems: function($items) {
        $items.each( function() {
            var $container = $(this);
            var shuffle = $container.hasClass("shuffle");
            if(!shuffle)
                $container.shuffle();
        });
    },

    /**
     * Get the correction of quiz in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correction: function ($elem) {
        var res = {};
        var data = $elem.text();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        $.each(data.split("::"), function() {
            var value = this;
            if (value && value !== "") {
                var k = value.substring(0, 3);
                var v = value.substring(3, value.length);
                res[k] = v;
            }
        });
        return res;
    },

    /**
     * Get the correction of quiz categories in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correctionCategories: function($elem){
        var res = {};
        var data = $elem.text();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        $.each(data.split("::"), function(idx, value) {
            if (value && value !== "") {
                var key = value.substring(0, 3);
                var data = value.substring(3, value.length);
                if ($.inArray(key, Object.keys(res)) >= 0 )
                    data = res[key] + "|" + data;
                res[key] = data;
            }
        });

        return res;
    },

    /**
     * Write user answer in DOM.
     *
     * @param {Object} quiz.
     * @param {String} quiz id.
     * @param {String} user answer.
     */
    writeUserAnswers: function($quiz, quzId, answer) {
        var $userAnswer = $quiz.find("#"+quzId+"_user");
        if ($userAnswer.length === 0) {
            var prefix = $quiz.data("prefix");
            var engine = $quiz.data("engine");
            var $quizAnswer = null;
            if (engine != "production") 
                $quizAnswer = $quiz.find("#"+quzId+"_correct");
            else
                $quizAnswer = $quiz.find("."+prefix+"Production");

            $userAnswer = $("<div>")
                    .attr("id", quzId+"_user")
                    .addClass("hidden");
            $userAnswer.insertAfter($quizAnswer);
        }
        $userAnswer.text(answer);
    },

    /**
     * Helper, function contruct string for compare.
     *
     * @param {String} text origin.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {String} text for compare.
     */
    constructCmpString: function(text, isStrict, options) {
        var r = text.trim();
        r = r.replace("-", " - ");
        r = r.replace("+", " + ");
        r = r.replace("/", " / ");
        r = r.replace("*", " * ");
        r = r.replace("=", " = ");
        r = r.replace(new RegExp(/æ/g),"ae");
        r = r.replace(new RegExp(/œ/g),"oe");
        r = r.replace(new RegExp(/\s{2,}/g),"");

        if (!isStrict) {
            r = r.toLowerCase();
            r = r.replace(new RegExp(/\s/g),"");
            r = this.removePunctuation(r);
            r = this.removeAccent(r);
            return r;
        }

        if ($.inArray("total", options) > -1 || options.length < 1)
            return r;

        if ($.inArray("accent", options) == -1)
            r = this.removeAccent(r);

        if ($.inArray("punctuation", options) == -1)
            r = this.removePunctuation(r);

        if ($.inArray("upper", options) == -1)
            r = r.toLowerCase();

        return r;
    },

    removePunctuation: function(text) {
        return text.replace(new RegExp(/[\.,#!?$%\^&;:{}\_`~()]/g)," ");
    },

    removeAccent: function(text) {
        var r = text.replace(new RegExp(/[àáâ]/g),"a");
        r = r.replace(new RegExp(/ç/g),"c");
        r = r.replace(new RegExp(/[èéê]/g),"e");
        r = r.replace(new RegExp(/[îï]/g),"i");
        r = r.replace(new RegExp(/[ùúû]/g),"u");
        return r;
    },

    /**
     * Helper, use for validate user answer for engine blanks-fill.
     *
     * @params {String} userAnswer : answer of player.
     * @params {String} rightAnswer : the right answer.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {Boolean}.
     */
    isValideBlanksFillAnswer: function (userAnswer, rightAnswer, isStrict, options) {
        var $this = this;
        if (!userAnswer)
            userAnswer = "";

        userAnswer = $this.constructCmpString(userAnswer, isStrict, options);

        var answer = [];
        $.each(rightAnswer.split("|"), function() {
            var txt = this;
            txt = $this.constructCmpString(txt, isStrict, options);
            answer.push(txt);
        });

        if ($.inArray(userAnswer, answer) > -1)
            return true;

        return false;
    },

    /**
     * Helper, function format number "3" -> "003".
     *
     * @param {String} str, number to format.
     * @return {Int} max, length max of format.
     */
    formatNumber: function (str, max) {
        str = str.toString();
        return str.length < max ? this.formatNumber("0" + str, max) : str;
    }
};

}(jQuery));


/******************************************************************************
 *
 *                                  Plugin shuffle
 *
******************************************************************************/

(function ($) {

"use strict";

/**
 * To shuffle all <li> elements within each '.member' <div>:
 * $(".member").shuffle("li");
 *
 * To shuffle all children of each <ul>:
 * $("ul").shuffle();
*/
$.fn.shuffle = function(selector) {

    var $elems = selector ? $(this).find(selector) : $(this).children(),
        $parents = $elems.parent();

    $parents.each(function(){
        $(this).children(selector).sort(function() {
            return Math.round(Math.random()) - 0.5;
        }).detach().appendTo(this);
    });

    return this;
};

/**
 * To shuffle an array
*/
$.shuffle = function(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
};

})(jQuery);
