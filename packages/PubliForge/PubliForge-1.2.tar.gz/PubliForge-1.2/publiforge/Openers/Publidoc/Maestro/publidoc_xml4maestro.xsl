<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_xml4maestro.xsl 53a93cee8900 2014/08/05 17:48:10 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <!--
      =========================================================================
      Copy
      =========================================================================
  -->
  <xsl:template match="*|@*|text()|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates select="*|@*|text()|comment()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>

  <!--
      ========================================================================
      section
      ========================================================================
  -->
  <xsl:template match="section">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:if test="not(ancestor::section)">
       <xsl:attribute name="mid">
         <xsl:value-of select="concat('section', count(preceding::section))"/>
       </xsl:attribute>
     </xsl:if>
     <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!--
      ========================================================================
      image
      ========================================================================
  -->
  <xsl:template match="image">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:if test="not(ancestor::image) and not(ancestor::media and ../link)">
       <xsl:attribute name="mid">
         <xsl:value-of select="concat('image', count(preceding::image))"/>
       </xsl:attribute>
     </xsl:if>
     <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
