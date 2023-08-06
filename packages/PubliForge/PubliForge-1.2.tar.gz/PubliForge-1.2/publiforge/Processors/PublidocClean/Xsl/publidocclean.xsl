<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidocclean.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Processor suppression parameters -->
  <xsl:param name="sup_warning" select="1"/>
  <xsl:param name="sup_annotation" select="0"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:strip-space elements="*"/>


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
      warning
      =========================================================================
  -->
  <xsl:template match="warning">
    <xsl:choose>
      <xsl:when test="$sup_warning">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates select="*|@*|text()|comment()|processing-instruction()"/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      annotation
      =========================================================================
  -->
  <xsl:template match="annotation">
    <xsl:choose>
      <xsl:when test="$sup_annotation"/>
      <xsl:otherwise>
        <xsl:copy><xsl:apply-templates/></xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
