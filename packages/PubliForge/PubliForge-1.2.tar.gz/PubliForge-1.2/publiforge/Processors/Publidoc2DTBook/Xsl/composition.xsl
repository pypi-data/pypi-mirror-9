<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: composition.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<!-- Publidoc2XHtml -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <!--
      =========================================================================
      Copy
      =========================================================================
  -->
  <xsl:template match="*|@*|text()|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates
          select="*|@*|text()|comment()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      publidoc, publiquiz
      =========================================================================
  -->
  <xsl:template match="publidoc|publiquiz">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      head
      =========================================================================
  -->
  <xsl:template match="head">
    <head>
      <xsl:choose>
        <xsl:when test="ancestor::publidoc">
          <xsl:apply-templates
              select="title|subtitle|contributors|date|place
                      |keywordset|subjectset|index|abstract|annotation"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </head>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:apply-templates
        select="*[name()!='head']|comment()|processing-instruction()"/>
  </xsl:template>

</xsl:stylesheet>
