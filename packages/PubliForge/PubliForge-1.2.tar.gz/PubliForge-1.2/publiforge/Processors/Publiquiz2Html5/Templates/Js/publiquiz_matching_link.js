/** 
 * @projectDescription publiquiz_matching_link.js 
 * Plugin jQuery for quiz engine "matching" render "link".
 *
 * @author prismallia.fr
 * @version 0.1 
 * $Id: publiquiz_matching_link.js 21698534b7a3 2015/02/18 16:42:56 Tien $
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
 *                              Matching Link
 *
******************************************************************************/

(function ($) {

"use strict";

// Rappel des méthode précédentes
var matchingConfigureBase = $.publiquiz.engine.matching.matchingConfigure;
var matchingEnableBase = $.publiquiz.engine.matching.matchingEnable;
var matchingDisableBase =  $.publiquiz.engine.matching.matchingDisable;
var matchingHelpBase = $.publiquiz.engine.matching.matchingHelp;
var matchingRetryBase = $.publiquiz.engine.matching.matchingRetry;
var matchingTextAnswerBase = $.publiquiz.engine.matching.matchingTextAnswer;
var matchingInsertUserAnswersBase = $.publiquiz.engine.matching.matchingInsertUserAnswers;
var matchingQuizAnswerBase = $.publiquiz.engine.matching.matchingQuizAnswer;
var matchingVerifyAnswerBase = $.publiquiz.engine.matching.matchingVerifyAnswer;
var matchingComputeScoreBase = $.publiquiz.engine.matching.matchingComputeScore;
var matchingScoreBase = $.publiquiz.engine.matching.matchingScore;


// Redéfinition du plugin matching
$.publiquiz.engine.matching = {
 
    // Référence a l'object image qui va saugarder un etat du canvas
    canvasImg: null,
    // Référence a l'object image qui va saugarder un l'etat d'origine du canvas
    canvasImgOrigin: null,
    // Référence au coter du point A choisie
    canvasSelectionSide: null,
    // Référence a l'index du point choisie
    canvasPointIdx: null,
    // Référence au tableau contenant les point selectionne a gauche
    canvasPointLeftSelected: [],
    // Référence au tableau contenant les point selectionne a droite
    canvasPointRightSelected: [],
    // Référence a l'index du point A
    canvasPointA: null,
    // Référence du coter du point A
    canvasSidePointA: null,
    // Référence a la position en X des points
    canvasOffsetPointX: 20,
    // Référence au rayon des points de l'interface
    canvasPointRadius: 8,        
    // Référence a la taille du trait tracer
    canvasdrawLineWidth: 2,
    // Référence au couleur de la ligne entre les points
    canvasLineColor: "#7f7f7f",
    // Référence au couleur de la ligne entre les points correcte
    canvasLineColorOk: "#1fbe1f",
    // Référence au couleur de la ligne entre les points correcte
    canvasLineColorKo: "#ff0000",

    // Référence durée de la fonction "verify"
    duration: 3000,
    // Référence au tableau contenant les timer pour la fonction "verify"
    timers: [],


    /**
     * Configure quiz.
     */
    matchingConfigure: function($quiz) {
        if (!$quiz.data("engine-options") || 
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingConfigureBase($quiz);
            return;
        }

        var $this = $.publiquiz.engine.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas[0].isDrawing = false;

        // On melange les items
        $.publiquiz.engine.shuffleItems($quiz.find("."+prefix+"MatchingLinkItems"));

        // Set width/height of canvas
        var h = 0;
        var w = 0;
        $quiz.find("."+prefix+"MatchingLinkItems").each( function() {
            w = this.clientWidth;
            if(this.clientHeight > h)
                h = this.clientHeight;
        });
        $canvas[0].width = w;
        $canvas[0].height = h;

        // Draw canvas point
        var canvasOffsetY = $canvas[0].offsetTop;

        var $left = $quiz.find("#"+quzId+"_items_left");
        $left.find("."+prefix+"MatchingLinkItem").each( function() {
            var elem = this;
            var X = $this.canvasOffsetPointX; 
            var Y = (elem.offsetTop - canvasOffsetY) + (elem.clientHeight/2) + ($this.canvasPointRadius/2);
            $this.drawCanvasArc($canvas, X, Y);
        });

        var $right = $quiz.find("#"+quzId+"_items_right");
        $right.find("."+prefix+"MatchingLinkItem").each( function() {
            var elem = this;
            var X = $canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius; 
            var Y = (elem.offsetTop - canvasOffsetY) + (elem.clientHeight/2) + ($this.canvasPointRadius/2);
            $this.drawCanvasArc($canvas, X, Y);
        });

        // Save canvas state
        $this.canvasImg = new Image();
        $this.canvasImgOrigin =  new Image();
        $this.canvasImg.src = $canvas[0].toDataURL();
        $this.canvasImgOrigin.src = $canvas[0].toDataURL();
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    matchingEnable: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingEnableBase($quiz);
            return;
        }
        $.publiquiz.engine.matching.enableCanvasSelectionPointA($quiz);
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingDisable: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingDisableBase($quiz);
            return;
        }
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas.unbind("mousedown");
        $canvas.unbind("mousemove");
        $canvas.unbind("mouseup");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingHelp: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingHelpBase($quiz);
            return;
        }
        $.publiquiz.engine.displayHelp($quiz);
    },

    /**
     * Retry quiz, keep only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingRetry: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingRetryBase($quiz);
            return;
        }

        var $this = $.publiquiz.engine.matching;
        $this.clearVerify($quiz);
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        // On selectionne uniquement les bonnes réponses
        tmpCanvasPointLeftSelected = [];
        tmpCanvasPointRightSelected = [];
        $.each(res, function(key, value) {
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var position = $.inArray($itemLeft[0], $leftItems);
            var index = $.inArray(position, $this.canvasPointLeftSelected);
            if (index >= 0) {
                var $itemRight = $($rightItems[$this.canvasPointRightSelected[index]]);
                if (value == $itemRight.data("item-value")) {
                    tmpCanvasPointLeftSelected.push(position);
                    tmpCanvasPointRightSelected.push($this.canvasPointRightSelected[index]);
                }
            }
        });
        $this.canvasPointLeftSelected = tmpCanvasPointLeftSelected;
        $this.canvasPointRightSelected = tmpCanvasPointRightSelected;

        // On enleve les reponses
        $this.canvasRefresh($canvas, $this.canvasImgOrigin);

        // On trace uniquement les bonnes réponses
        $.each($this.canvasPointLeftSelected, function(idx, value) {
            var color = $this.canvasLineColor;
            var $itemLeft = $($leftItems[value]);
            var $itemRight = $($rightItems[$this.canvasPointRightSelected[idx]]);

            var coordinateA = [];
            coordinateA.push($this.canvasOffsetPointX);
            coordinateA.push(($itemLeft[0].offsetTop - $canvas[0].offsetTop) + ($itemLeft[0].clientHeight/2) + ($this.canvasPointRadius/2));

            var coordinateB = [];
            coordinateB.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
            coordinateB.push(($itemRight[0].offsetTop - $canvas[0].offsetTop) + ($itemRight[0].clientHeight/2) + ($this.canvasPointRadius/2));

            $this.drawCanvasLine($canvas, coordinateA, coordinateB, color);
        });

        // On sauvegarde l'etat du canvas
        $this.canvasImg.src = $canvas[0].toDataURL();
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    matchingComputeScore: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 )
            return matchingComputeScoreBase($quiz);

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

        var $this = $.publiquiz.engine.matching;
        $this.clearVerify($quiz);
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));

        var total = 0;
        var score = 0;
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        $.each(res, function(key, value) {
            total += 1;
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var position = $.inArray($itemLeft[0], $leftItems);
            var index = $.inArray(position, $this.canvasPointLeftSelected);
            if (index >= 0) {
                var $itemRight = $($rightItems[$this.canvasPointRightSelected[index]]);
                if (value == $itemRight.data("item-value"))
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
    matchingScore: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingScoreBase($quiz);
            return;
        }
        if($.publiquiz.defaults.debug)
            console.log("$.publiquiz.engine.matching:score");
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingTextAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingTextAnswerBase($quiz);
            return;
        }
        $.publiquiz.engine.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingInsertUserAnswers: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingInsertUserAnswersBase($quiz);
            return;
        }

        var $this = $.publiquiz.engine.matching;
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        $.each($this.canvasPointLeftSelected, function(idx) {
            var $itemLeft = $($leftItems[this]);
            var $itemRight = $($rightItems[$this.canvasPointRightSelected[idx]]);
            var key = $itemLeft.attr("id");
            key = key.substring(key.length - 3, key.length);
            if (answer !== "")
                answer += "::";
            answer += key + $itemRight.data("item-value");
        });

        $.publiquiz.engine.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    matchingQuizAnswer: function($quiz, mode) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingQuizAnswerBase($quiz, mode);
            return;
        }

        var $this = $.publiquiz.engine.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var correctionOnly = $quiz.data("display-correction-only");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var answers = $.publiquiz.engine.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_user"));

        // On enleve les reponses
        $this.canvasRefresh($canvas, $this.canvasImgOrigin);

        // On place la correction
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");
        $.each(answers, function(key, value) {
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var $itemRight = $rightItems.filter("[data-item-value=\""+value+"\"]");

            var coordinateA = [];
            coordinateA.push($this.canvasOffsetPointX);
            coordinateA.push(($itemLeft[0].offsetTop - $canvas[0].offsetTop) + ($itemLeft[0].clientHeight/2) + ($this.canvasPointRadius/2));

            var coordinateB = [];
            coordinateB.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
            coordinateB.push(($itemRight[0].offsetTop - $canvas[0].offsetTop) + ($itemRight[0].clientHeight/2) + ($this.canvasPointRadius/2));
    
            var color = $this.canvasLineColor;
            if (mode == "_correct") {
                color = $this.canvasLineColorOk;
                if (!correctionOnly) {
                    if (!userAnswers[key] || userAnswers[key] != value)
                        color = $this.canvasLineColorKo;
                }
            }
            $this.drawCanvasLine($canvas, coordinateA, coordinateB, color);
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingVerifyAnswerBase($quiz);
            return;
        }

        var $this = $.publiquiz.engine.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var answers = $.publiquiz.engine.correction($quiz.find("#"+quzId+"_correct"));
        
        // On enleve les reponses
        $this.canvasRefresh($canvas, $this.canvasImgOrigin);

        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");
        $.each(answers, function(key, value) {
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var position = $.inArray($itemLeft[0], $leftItems);
            var index = $.inArray(position, $this.canvasPointLeftSelected);
            if (index >= 0) {
                var $itemRight = $($rightItems[$this.canvasPointRightSelected[index]]);

                var color = $this.canvasLineColorKo;
                if (value == $itemRight.data("item-value"))
                    color = $this.canvasLineColorOk;

                var coordinateA = [];
                coordinateA.push($this.canvasOffsetPointX);
                coordinateA.push(($itemLeft[0].offsetTop - $canvas[0].offsetTop) + ($itemLeft[0].clientHeight/2) + ($this.canvasPointRadius/2));

                var coordinateB = [];
                coordinateB.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
                coordinateB.push(($itemRight[0].offsetTop - $canvas[0].offsetTop) + ($itemRight[0].clientHeight/2) + ($this.canvasPointRadius/2));

                $this.drawCanvasLine($canvas, coordinateA, coordinateB, color);
            }

        });

        var timer = setTimeout( function() {
                $this.clearVerify($quiz);
            }, $this.duration);

        $this.timers.push(timer);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Suppression des informations de verification du quiz
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    clearVerify: function($quiz) {
        $.each(this.timers, function() {
            clearTimeout(this);
        });

        var $this = $.publiquiz.engine.matching;
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $this.canvasRefresh($canvas, $this.canvasImg);
    },

    /**
     * Mise en place de l'event pour la selection du point A
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    enableCanvasSelectionPointA: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas.on({
            mousedown: function(ev) { 
                ev.preventDefault();
                $.publiquiz.engine.matching.onCanvasSelectPointA($quiz, ev);
            }
        });
    },

    /**
     * Mise en place de l'event pour la selection du point B
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    enableCanvasSelectionPointB: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas.on({
            mousemove: function(ev) { 
                ev.preventDefault();
                $.publiquiz.engine.matching.onCanvasMouseMove($quiz, ev);
            },
            mouseup: function(ev) { 
                ev.preventDefault();
                $.publiquiz.engine.matching.onCanvasSelectPointB($quiz, ev);
            }
        });
    },

    /**
     * Matching link helper, dessine les points du canvas
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {int} X : position X du point a dessiner.
     * @params {int} Y : position Y du point a dessiner.
     */
    drawCanvasArc: function($canvas, X, Y) {
        var context = $canvas[0].getContext("2d");
        context.beginPath();
        context.arc(
            X, Y,
            $.publiquiz.engine.matching.canvasPointRadius, 0, Math.PI * 2);
        context.fill();
        context.closePath();
    },

    /**
     * Matching link helper, dessine les points du canvas
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {Array} coordinateA : position du point A.
     * @params {Array} coordinateB : position du point B.
     * @params {String} color : couleur de la ligne a dessiner.
     */
    drawCanvasLine: function($canvas, coordinateA, coordinateB, color) {
        var $this =this;
        var context = $canvas[0].getContext("2d");
        context.lineWidth = $this.canvasdrawLineWidth;
        context.lineCap = "round";
        context.beginPath();

        context.moveTo(coordinateA[0], coordinateA[1]);
        context.lineTo(coordinateB[0], coordinateB[1]);

        context.strokeStyle = color;
        context.stroke();
        context.closePath();
    },

    /**
     * Helper, Redessine le canvas avec une image.
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {Object} image : javascript object.
     */
    canvasRefresh: function($canvas, image) {
        var context = $canvas[0].getContext("2d");
        context.clearRect(0, 0, $canvas.width(), $canvas.height());
        context.drawImage(image, 0, 0);
    },

    /**
     * Helper, Localise le point sous la souris dans le canvas.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     * @return {Array} coordinate.
     */
    eventCoordinateInCanvas: function($quiz, ev) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var coordinate = [];
        coordinate.push(ev.pageX - $canvas[0].offsetLeft);
        coordinate.push(ev.pageY - $canvas[0].offsetTop);
        return coordinate;
    },

    /**
     * Helper, Détermine si les coordonnées sont sur un point.
     *
     * @params {Object} $quiz: object jquery quiz.
     * @params {Array} coordinate: coordonnée.
     * @return {Boolean}
     */
    isOnCorrectPoint: function($quiz, coordinate) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var find = false;

        $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem").each( function(idx) {
            var elem = this;
            if ( (coordinate[0] >= $this.canvasOffsetPointX - $this.canvasPointRadius) && 
                 (coordinate[0] <= $this.canvasOffsetPointX + $this.canvasPointRadius) &&
                 (coordinate[1] >= (elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) - $this.canvasPointRadius) && 
                 (coordinate[1] <= (elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) + $this.canvasPointRadius) ) {

                    find = true;
                    $.publiquiz.engine.matching.canvasSelectionSide = "left";
                    $.publiquiz.engine.matching.canvasPointIdx = idx;
                    return false;
            }
        });
        
        if (find)
            return find;

        $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem").each( function(idx) {
            var elem = this;
            if( (coordinate[0] + ($this.canvasPointRadius*2) >= $canvas.width() - $this.canvasOffsetPointX) &&
                (coordinate[0] - ($this.canvasPointRadius*2) <= $canvas.width() - $this.canvasOffsetPointX) &&
                (coordinate[1] >= (elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) - $this.canvasPointRadius) && 
                (coordinate[1] <= (elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) + $this.canvasPointRadius) ) {

                    find = true;
                    $.publiquiz.engine.matching.canvasSelectionSide = "right";
                    $.publiquiz.engine.matching.canvasPointIdx = idx;
                    return false;
            }
        });

        return find;
    },

    /**
     * Matching link, selection du point de départ
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasSelectPointA: function($quiz, ev) {
        var $this = this;
        $this.clearVerify($quiz);
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var coordinate = $this.eventCoordinateInCanvas($quiz, ev);
        if (!$this.isOnCorrectPoint($quiz, coordinate))
            return;

        // On valide que le point n'est pas encore utiliser
        // si c'est le cas on supprime le précédent tracer
        if (($this.canvasSelectionSide == "left" && $.inArray($this.canvasPointIdx, $this.canvasPointLeftSelected) >= 0) ||
                ($this.canvasSelectionSide == "right" && $.inArray($this.canvasPointIdx, $this.canvasPointRightSelected) >= 0 )) {

            // On supprime les points correspondant dans les tableaux
            var idx = null;
            if ($this.canvasSelectionSide == "left")
                idx = $.inArray($this.canvasPointIdx, $this.canvasPointLeftSelected);
            else
                idx = $.inArray($this.canvasPointIdx, $this.canvasPointRightSelected);
            $this.canvasPointLeftSelected.splice(idx, 1);
            $this.canvasPointRightSelected.splice(idx, 1);

            // On replace le canvas d'origin
            $this.canvasRefresh($canvas, $this.canvasImgOrigin);

            // On retrace les lignes
            $.each($this.canvasPointLeftSelected, function(pos) {
                var coordinateA = [];
                var elemLeft = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[$this.canvasPointLeftSelected[pos]];
                coordinateA.push($this.canvasOffsetPointX);
                coordinateA.push((elemLeft.offsetTop - $canvas[0].offsetTop) + (elemLeft.clientHeight/2) + ($this.canvasPointRadius/2));

                var coordinateB = [];
                var elemRight = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[$this.canvasPointRightSelected[pos]];
                coordinateB.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
                coordinateB.push((elemRight.offsetTop - $canvas[0].offsetTop) + (elemRight.clientHeight/2) + ($this.canvasPointRadius/2));

                $this.drawCanvasLine($canvas, coordinateA, coordinateB, $this.canvasLineColor);
            });
        }

        // On sauvegarde les paramètres du point selectionner
        $this.canvasPointA = $this.canvasPointIdx;
        $this.canvasSidePointA = $this.canvasSelectionSide;
        if ($this.canvasSidePointA == "left")
            $this.canvasPointLeftSelected.push($this.canvasPointA);
        else
            $this.canvasPointRightSelected.push($this.canvasPointA);

        // On sauvegarde l'etat du canvas
        $this.canvasImg.src = $canvas[0].toDataURL();

        // Events
        $canvas[0].isDrawing = true;
        $this.enableCanvasSelectionPointB($quiz);
    },

    /**
     * Matching link, déplacement de la souris
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasMouseMove: function($quiz, ev) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");

        if (!$canvas[0].isDrawing)
            return;

        var coordinate = $this.eventCoordinateInCanvas($quiz, ev);
        $this.canvasRefresh($canvas, $this.canvasImg);

        var elem;
        var coordinateA = [];
        if ($this.canvasSidePointA == "left") {
            elem = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[$this.canvasPointA];
            coordinateA.push($this.canvasOffsetPointX);
            coordinateA.push((elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) + ($this.canvasPointRadius/2));
        } else {
            elem = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[$this.canvasPointA];
            coordinateA.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
            coordinateA.push((elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2) + ($this.canvasPointRadius/2));
        }
        
        $this.drawCanvasLine($canvas, coordinateA, coordinate, $this.canvasLineColor);
    },

    /**
     * Matching link, On relanche le bouton de la souris
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasSelectPointB: function($quiz, ev) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas[0].isDrawing = false;
        $this.matchingDisable($quiz);

        var coordinate = $this.eventCoordinateInCanvas($quiz, ev);
        $this.canvasRefresh($canvas, $this.canvasImg);

        // On valide que le point B est correct
        // et que le point B et le point A ne sont pas du même coter
        if (!$this.isOnCorrectPoint($quiz, coordinate) || 
                $this.canvasSelectionSide == $this.canvasSidePointA) {
            if ($this.canvasSelectionSide == "left")
                $this.canvasPointLeftSelected.pop();
            else
                $this.canvasPointRightSelected.pop();
            $this.enableCanvasSelectionPointA($quiz);
            return;
        }

        // On valide que le point B n'est pas encore utiliser
        if (($this.canvasSelectionSide == "left" && 
                $.inArray($this.canvasPointIdx, $this.canvasPointLeftSelected) >= 0) ||
            ($this.canvasSelectionSide == "right" && 
                $.inArray($this.canvasPointIdx, $this.canvasPointRightSelected) >= 0) ) {
                
            if ($this.canvasSelectionSide == "left")
                $this.canvasPointRightSelected.pop();
            else
                $this.canvasPointLeftSelected.pop();

            $this.enableCanvasSelectionPointA($quiz);
            return;
        }

        // On sauvegarde les paramètres du point selectionner
        if ($this.canvasSelectionSide == "left")
            $this.canvasPointLeftSelected.push($this.canvasPointIdx);
        else
            $this.canvasPointRightSelected.push($this.canvasPointIdx);

        // On trace la ligne entre le point A et le point B
        var coordinateA = [];
        var elemLeft = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[$this.canvasPointLeftSelected[$this.canvasPointLeftSelected.length -1]];
        coordinateA.push($this.canvasOffsetPointX);
        coordinateA.push((elemLeft.offsetTop - $canvas[0].offsetTop) + (elemLeft.clientHeight/2) + ($this.canvasPointRadius/2));

        var coordinateB = [];
        var elemRight = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[$this.canvasPointRightSelected[$this.canvasPointRightSelected.length -1]];
        coordinateB.push($canvas.width() - $this.canvasOffsetPointX + $this.canvasPointRadius);
        coordinateB.push((elemRight.offsetTop - $canvas[0].offsetTop) + (elemRight.clientHeight/2) + ($this.canvasPointRadius/2));

        $this.drawCanvasLine($canvas, coordinateA, coordinateB, $this.canvasLineColor);

        // On sauvegarde l'etat du canvas
        $this.canvasImg.src = $canvas[0].toDataURL();

        // Event
        $this.enableCanvasSelectionPointA($quiz);
    }

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
