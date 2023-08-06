<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiquiz_template.inc.xsl e21208adad20 2014/10/23 16:32:34 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                   CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template quiz_engine
      =========================================================================
  -->
  <xsl:template name="quiz_engine">
    <xsl:param name="node" select="."/>
    <xsl:choose>
      <xsl:when test="$node/choices-radio">choices-radio</xsl:when>
      <xsl:when test="$node/choices-check">choices-check</xsl:when>
      <xsl:when test="$node/blanks-fill">blanks-fill</xsl:when>
      <xsl:when test="$node/blanks-select">blanks-select</xsl:when>
      <xsl:when test="$node/blanks-char">blanks-char</xsl:when>
      <xsl:when test="$node/pointing">pointing</xsl:when>
      <xsl:when test="$node/pointing-categories">pointing-categories</xsl:when>
      <xsl:when test="$node/matching">matching</xsl:when>
      <xsl:when test="$node/sort">sort</xsl:when>
      <xsl:when test="$node/categories">categories</xsl:when>
      <xsl:when test="$node/pip">pip</xsl:when>
      <xsl:when test="$node/production">production</xsl:when>
      <xsl:when test="$node/composite">composite</xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
