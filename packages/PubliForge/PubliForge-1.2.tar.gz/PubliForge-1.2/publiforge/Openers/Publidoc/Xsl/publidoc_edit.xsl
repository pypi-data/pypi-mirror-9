<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_edit.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_edit_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->
  <xsl:param name="variables"/>   <!-- Full path to variable file -->
  <xsl:param name="mode"/>        <!-- variables or html -->

  <!-- Variables -->
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="variables_doc" select="document($variables)"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>


  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:choose>
      <xsl:when test="$mode='variables'">
        <publiforge version="1.0">
          <variables>
            <xsl:apply-templates select="document|topic" mode="variables"/>
          </variables>
        </publiforge>
      </xsl:when>
      <xsl:when test="$mode='html'">
        <xsl:apply-templates select="document|topic" mode="html"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      document mode variables
      =========================================================================
  -->
  <xsl:template match="document" mode="variables">
    <xsl:variable name="num" select="0"/>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
    <xsl:apply-templates select="$variables_doc/*/*/group[@name='document']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      document mode html
      =========================================================================
  -->
  <xsl:template match="document|topic" mode="html">
    <xsl:variable name="num" select="0"/>

    <div class="pdocDocument">
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="html_table">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='document']"
                           mode="html_div">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      topic mode variables
      =========================================================================
  -->
  <xsl:template match="topic" mode="variables">
    <xsl:variable name="num" select="0"/>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
    <xsl:apply-templates select="$variables_doc/*/*/group[@name='topic']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      topic mode html
      =========================================================================
  -->
  <xsl:template match="topic" mode="html">
    <xsl:variable name="num" select="0"/>

    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocTopic</xsl:text>
        <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>

      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="html_table">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='topic']"
                           mode="html_div">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </div>
  </xsl:template>

</xsl:stylesheet>
