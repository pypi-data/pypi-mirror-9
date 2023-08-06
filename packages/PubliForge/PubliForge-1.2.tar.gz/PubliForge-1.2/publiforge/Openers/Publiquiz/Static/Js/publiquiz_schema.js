// $Id: publiquiz_schema.js 32be996f3700 2014/12/23 15:17:21 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                               PUBLIQUIZ SCHEMA
// ****************************************************************************

if (!$.publiquiz) $.publiquiz = {};

$.publiquiz.schemaEngine = [
    "choices-radio", "choices-check", "blanks-fill", "blanks-select",
    "pointing", "pointing-categories", "matching", "sort", "categories",
    "production"];

$.publiquiz.schemaBlockBlanks = [
    "blanks.p", "blanks.list", "blanks.blockquote", "blanks.speech",
    "table", "media"];
$.publiquiz.schemaBlockPointing = [
    "pointing.p", "pointing.list", "pointing.blockquote", "pointing.speech",
    "table", "media"];

$.publiquiz.schemaInlineBlanks = $.publidoc.schemaInline.concat(["blank"]);
$.publiquiz.schemaInlinePointing = $.publidoc.schemaInline.concat(["point"]);

$.publiquiz.schema = $.extend(
    $.publidoc.schema,
    {
        // ------ DIVISION ----------------------------------------------------
        ".division": {
            content: [["division", "topic", "quiz"]]
        },
        division: {
            attributes: {
                type: null, "xml:lang": $.publidoc.schemaAttLang },
            content: [["division.head", "division", "topic", "quiz"]]
        },

        // ------ COMPONENT ---------------------------------------------------
        quiz: {
            attributes: {
                id: null,
                type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["component.head", "instructions", "composite", "help",
                       "answer"].concat($.publiquiz.schemaEngine)]
        },

        // ------ SECTION -----------------------------------------------------
        ".instructions": {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },
        instructions: {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },

        "blanks.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "blanks.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockBlanks)]
        },
        "pointing.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "pointing.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockPointing)]
        },

        ".help": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        help: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        ".answer": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        answer: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },

        // ------ SECTION - Choices -------------------------------------------
        "choices-radio": {
            type: "radio",
            rightElement: "right",
            wrongElement: "wrong",
            content: [["right", "wrong"]]
        },
        "choices-check": {
            type: "checkbox",
            rightElement: "right",
            wrongElement: "wrong",
            content: [["right", "wrong"]]
        },
        right: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },
        wrong: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },

        // ------ SECTION - Blanks --------------------------------------------
        "blanks-fill": {
            attributes: { strict: ["true", "false"] },
            content: [["blanks.section"], $.publiquiz.schemaBlockBlanks]
        },

        "blanks-select": {
            attributes: { multiple: ["true", "false"] },
            content: [["blanks.intruders", "blanks.section"],
                      ["blanks.intruders"].concat(
                          $.publiquiz.schemaBlockBlanks)]
        },
        "blanks.intruders": {
            element: "intruders",
            content: [["blank"]]
        },

        // ------ SECTION - Pointing ------------------------------------------
        pointing: {
            attributes: { type: ["radio", "check"] },
            content: [["pointing.section"],
                      $.publiquiz.schemaBlockPointing]
        },
        "pointing-categories": {
            content: [["pointing-c.categories", "pointing.section"]]
        },
        "pointing-c.categories": {
            element: "categories",
            content: [["pointing-c.category"]]
        },
        "pointing-c.category": {
            element: "category",
            attributes: { id: ["1", "2", "3", "4", "5"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Matching ------------------------------------------
        matching: {
            intrudersElement: "intruders",
            matchElement: "match",
            itemElement: "item",
            attributes: { multiple: ["true", "false"] },
            content: [["matching.intruders", "match"]]
        },
        "matching.intruders": {
            element: "intruders",
            content: [["match.item"]]
        },
        match: {
            content: [["match.item"]]
        },
        "match.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Sort ----------------------------------------------
        sort: {
            comparisonElement: "comparison",
            itemElement: "item",
            attributes: { shuffle: ["true", "false"] },
            content: [["comparison", "sort.item"]]
        },
        comparison: {
            content: [[".text"]]
        },
        "sort.item": {
            element: "item",
            attributes: {
                shuffle: ["1", "2", "3", "4", "5", "6", "7", "8", "9",
                          "10", "11", "12", "13", "14", "15"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Categories ----------------------------------------
        categories: {
            intrudersElement: "intruders",
            categoryElement: "category",
            headElement: "head",
            itemElement: "item",
            attributes: { multiple: ["true", "false"] },
            content: [["category.intruders", "category"]]
        },
        "category.intruders": {
            element: "intruders",
            content: [["category.item"]]
        },
        category: {
            content: [["category.head", "category.item"]]
        },
        "category.head": {
            element: "head",
            content: [["title", "shorttitle", "subtitle"]]
        },
        "category.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Production ----------------------------------------
        production: {
            content: [[]]
        },

        // ------ SECTION - Composite -----------------------------------------
        composite: {
            attributes: { multipage: ["true", "false"] },
            content: [["subquiz"]]
        },
        subquiz: {
            content: [["instructions", "help", "answer"]
                      .concat($.publiquiz.schemaEngine)]
        },

        // ------ BLOCK -------------------------------------------------------
        "blanks.p": {
            element: "p",
            content: [$.publiquiz.schemaInlineBlanks]
        },
        "pointing.p": {
            element: "p",
            content: [$.publiquiz.schemaInlinePointing]
        },

        "blanks.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "blanks.item"]]
        },
        "pointing.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "pointing.item"]]
        },
        "blanks.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockBlanks),
                      $.publiquiz.schemaInlineBlanks]
        },
        "pointing.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockPointing),
                      $.publiquiz.schemaInlinePointing]
        },

        "blanks.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "blanks.p", "blanks.list",
                       "blanks.speech", "attribution"]]
        },
        "pointing.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "pointing.p", "pointing.list",
                       "pointing.speech", "attribution"]]
        },

        "blanks.speech": {
            element: "speech",
            content: [["speaker", "stage", "blanks.p",
                       "blanks.blockquote"]]
        },
        "pointing.speech": {
            element: "speech",
            content: [["speaker", "stage", "pointing.p",
                       "pointing.blockquote"]]
        },

        // ------ INLINE ------------------------------------------------------
        blank: {
            content: [[".text"], ["s"]]
        },
        s: {
            content: [[".text"]]
        },
        point: {
            attributes: {
                ref: ["right", "cat1", "cat2", "cat3", "cat4", "cat5"] },
            content: [$.publidoc.schemaInline]
        }
    }
);


})(jQuery);
