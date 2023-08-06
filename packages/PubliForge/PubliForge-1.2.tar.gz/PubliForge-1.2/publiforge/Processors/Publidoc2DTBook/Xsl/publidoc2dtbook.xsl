<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2dtbook.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.daisy.org/z3986/2005/dtbook/">

  <xsl:import href="publidoc2dtbook_template.inc.xsl"/>
  <xsl:import href="publidoc2dtbook_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img_dir">Images/</xsl:param>
  <xsl:param name="img_ext">.png</xsl:param>

  <!-- Variables -->
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset"/>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <dtbook version="2005-3" xml:lang="{$lang}">
      <xsl:apply-templates select="document|topic"/>
    </dtbook>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:call-template name="head"/>
    <book>
      <xsl:call-template name="frontmatter"/>
      <xsl:comment> ****************************************************************** </xsl:comment>
      <bodymatter>
        <xsl:apply-templates
            select="division|topic[not(@type) or @type!='title']"
            mode="onefile"/>
      </bodymatter>
    </book>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="head"/>
    <book>
      <xsl:call-template name="frontmatter"/>
      <xsl:comment> ****************************************************************** </xsl:comment>
      <bodymatter>
        <xsl:apply-templates select="." mode="corpus"/>
      </bodymatter>
    </book>
  </xsl:template>

</xsl:stylesheet>
