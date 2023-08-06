// $Id: publidoc_schema.js f2bacce83796 2014/12/23 07:59:31 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                                PUBLIDOC SCHEMA
// ****************************************************************************

if (!$.publidoc) $.publidoc = {};

$.publidoc.schemaBlock = [
    "p", "list", "blockquote", "speech", "table", "media"];

$.publidoc.schemaSimpleInline = [
    ".text", "sup", "sub", "var", "number", "acronym"];

$.publidoc.schemaInline = $.publidoc.schemaSimpleInline.concat([
    "highlight", "emphasis", "mentioned", "literal", "term", "stage", "name",
    "foreign", "date", "math", "quote", "initial", "note", "link", "anchor",
    "image", "audio", "smil"]);

$.publidoc.schemaAttLang = ["en", "fr", "es"];

$.publidoc.schema = {
    // ------ HEAD ------------------------------------------------------------
    "top.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "identifier",
                   "copyright", "collection", "contributors", "date", "place",
                   "source", "keywordset", "subjectset", "abstract", "cover",
                   "annotation"]]
    },
    "division.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "abstract", "annotation"]]
    },
    "component.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "contributors", "date",
                   "place", "keywordset", "subjectset", "abstract",
                   "annotation"]]
    },
    "section.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "keywordset",
                   "subjectset", "abstract", "audio", "annotation"]]
    },
    "block.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle"]]
    },

    title: {
        isFirst: true,
        content: [$.publidoc.schemaInline]
    },
    shorttitle: {
        content: [$.publidoc.schemaInline]
    },
    subtitle: {
        content: [$.publidoc.schemaInline]
    },

    identifier: {
        attributes: { type: ["ean", "uri"], for: null },
        content: [[".text"]]
    },
    "identifier.ean": {
        element: "identifier",
        attributes: { type: ["ean"], for: null },
        content: [[".text"]]
    },
    "identifier.uri": {
        element: "identifier",
        attributes: { type: ["uri"], for: null },
        content: [[".text"]]
    },

    copyright: {
        content: [$.publidoc.schemaSimpleInline]
    },

    ".contributors": {
        content: [["contributor"]]
    },
    contributors: {
        content: [["contributor"]]
    },
    contributor: {
        content: [["identifier.uri", "firstname", "lastname", "label",
                   "address", "link", "role"]]
    },
    firstname: {
        content: [$.publidoc.schemaSimpleInline]
    },
    lastname: {
        content: [$.publidoc.schemaSimpleInline]
    },
    label: {
        content: [$.publidoc.schemaSimpleInline]
    },
    address: {
        content: [$.publidoc.schemaSimpleInline]
    },
    role: {
        content: [[".text"]]
    },

    place: {
        content: [$.publidoc.schemaSimpleInline]
    },

    source: {
        attributes: { type: ["book", "file"] },
        content: [["identifier.uri", "annotation"],
                  ["identifier.ean", "title", "subtitle", "copyright",
                   "collection", "contributors", "date", "place", "folio",
                   "pages", "annotation"]]
    },
    folio: {
        content: [[".text"]]
    },
    pages: {
        content: [[".text"]]
    },

    ".keywordset": {
        content: [["keyword"]]
    },
    keywordset: {
        content: [["keyword"]]
    },
    keyword: {
        content: [$.publidoc.schemaSimpleInline]
    },
    ".subjectset": {
        content: [["subject"]]
    },
    subjectset: {
        content: [["subject"]]
    },
    subject: {
        content: [$.publidoc.schemaSimpleInline]
    },

    ".abstract": {
        content: [["p"]]
    },
    abstract: {
        content: [["p"]]
    },

    cover: {
        content: [["image"]]
    },

    annotation: {
        content: [$.publidoc.schemaInline]
    },

    // ------ DIVISION --------------------------------------------------------
    ".division": {
        content: [["division", "topic"]]
    },
    division: {
        attributes: { type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["division.head", "division", "topic"]]
    },

    // ------ COMPONENT -------------------------------------------------------
    document: {
        attributes: {
            id: null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["top.head", "division", "topic"]]
    },

    topic: {
        attributes: {
            id: null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["component.head", "section"]]
    },

    // ------ SECTION ---------------------------------------------------------
    ".section": {
        content: [["section"]]
    },
    section: {
        attributes: {
            "xml:id": null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["section.head", "section"],
                  ["section.head"].concat($.publidoc.schemaBlock)]
    },
    "special.section": {
        element: "section",
        attributes: {
            "xml:id": null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["section.head", "special.section"],
                  ["section.head", "special.p"]]
    },

    // ------ BLOCK -----------------------------------------------------------
    ".block": {
        content: [$.publidoc.schemaBlock]
    },

    p: {
        content: [$.publidoc.schemaInline]
    },
    "special.p": {
        element: "p",
        content: [$.publidoc.schemaInline]
    },

    list: {
        attributes: { type: ["ordered", "glossary"] },
        content: [["block.head", "item"]]
    },
    item: {
        content: [["label"].concat($.publidoc.schemaBlock),
                  $.publidoc.schemaInline]
    },

    blockquote: {
        attributes: { type: null },
        content: [["block.head", "p", "list", "speech", "attribution"]]
    },
    attribution: {
        content: [[".text", "sup", "number", "date", "name", "foreign",
                 "acronym", "term", "literal", "highlight", "emphasis",
                 "mentioned", "note"]]
    },

    speech: {
        content: [["speaker", "stage", "p", "blockquote"]]
    },
    speaker: {
        content: [$.publidoc.schemaInline]
    },

    table: {
        attributes: { type: null },
        content: [["block.head", "thead", "tbody", "caption"],
                  ["block.head", "tr", "caption"]]
    },
    thead: {
        content: [["tr"]]
    },
    tbody: {
        content: [["tr"]]
    },
    tr: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            type: null
        },
        content: [["th", "td"]]
    },
    th: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            colspan: null,
            rowspan: null,
            type: null
        },
        content: [$.publidoc.schemaBlock, $.publidoc.schemaInline]
    },
    td: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            colspan: null,
            rowspan: null,
            type: null
        },
        content: [$.publidoc.schemaBlock, $.publidoc.schemaInline]
    },
    caption: {
        content: [["p", "speech", "list", "blockquote"],
                  $.publidoc.schemaInline]
    },

    media: {
        captionElement: "caption",
        attributes: { "xml:id": null, type: null },
        content: [["block.head", "image", "audio", "video", "caption"]]
    },
    image: {
        attributes: {
            id: null,
            type: ["cover", "thumbnail", "icon", "animation"],
            alt: null },
        content: [["copyright"]]
    },
    audio: {
        attributes: {
            id: null,
            type: ["music", "voice", "background", "smil"] }
    },
    video: {
        attributes: { id: null }
    },

    // ------ INLINE ----------------------------------------------------------
    ".simple.inline": {
        content: [$.publidoc.schemaSimpleInline]
    },
    ".inline": {
        content: [$.publidoc.schemaInline]
    },

    sup: {
        content: [[".text"]]
    },
    sub: {
        content: [[".text"]]
    },
    var: {
        content: [[".text"]]
    },
    number: {
        attributes: { type: ["roman"] },
        content: [[".text", "sup"]]
    },
    acronym: {
        content: [[".text", "sup"]]
    },

    highlight: {
        content: [[".text", "sup", "sub", "emphasis"]]
    },
    emphasis: {
        content: [[".text", "sup", "sub", "highlight"]]
    },
    mentioned: {
        content: [[".text"]]
    },
    literal: {
        content: [$.publidoc.schemaInline]
    },
    term: {
        content: [[".text", "sup"]]
    },
    stage: {
        content: [[".text"]]
    },
    name: {
        attributes: {
            of: ["person", "company", "book", "newspaper", "party", "movie",
                 "painting"]
        },
        content: [[".text"]]
    },
    foreign: {
        attributes: { "xml:lang": null },
        content: [$.publidoc.schemaInline]
    },
    date: {
        attributes: { value: null, of: ["birth", "death"] },
        content: [[".text", "sup", "number"]]
    },
    math: {
        attributes: {
            "xml:id": null,
            display: ["wide", "numbered", "box", "numbered-box"]
        },
        content: [["latex"], [".text", "sup", "sub", "var"]]
    },
    latex: {
        attributes: { plain: ["true"] },
        content: [[".text"]]
    },
    quote: {
        content: [["phrase", "attribution"], $.publidoc.schemaInline]
    },
    phrase: {
        content: [$.publidoc.schemaInline]
    },

    initial: {
        content: [["c", "w"]]
    },
    c: {
        content: [[".text"]]
    },
    w: {
        content: [$.publidoc.schemaInline]
    },
    note: {
        attributes: { label: null },
        content: [$.publidoc.schemaBlock.concat(["w"]),
                  $.publidoc.schemaInline]
    },
    link: {
        attributes: { uri: null, idref: null },
        content: [$.publidoc.schemaSimpleInline]
    },
    anchor: {
        attributes: { "xml:id": null },
        content: [$.publidoc.schemaInline]
    },
    smil: {
        attributes: { begin: null, end: null, audio: null },
        content: [$.publidoc.schemaSimpleInline]
    }
};


})(jQuery);
