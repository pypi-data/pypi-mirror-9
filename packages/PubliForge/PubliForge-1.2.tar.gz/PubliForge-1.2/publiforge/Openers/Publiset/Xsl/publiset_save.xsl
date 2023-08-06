<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_save.xsl 58cf3969a6d8 2014/12/09 16:16:25 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_save_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="variables"/>   <!-- Full path to variable file -->

  <!-- Variables -->
  <xsl:variable name="variables_doc" select="document($variables)"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:strip-space elements="*"/>


  <!--
      *************************************************************************
                                     COMPOSITION
      *************************************************************************
  -->
  <!--
      =========================================================================
      composition
      =========================================================================
  -->
  <xsl:template match="composition">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <xsl:copy>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_head']/var"
          mode="head">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <head>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='composition_head_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='common_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates select="head/source[@type='file']|head/index"/>
        </head>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="head or not(division)">
          <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                               mode="corpus">
            <xsl:with-param name="num" select="$num"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates
              select="comment()|processing-instruction()|division"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      division
      =========================================================================
  -->
  <xsl:template match="division">
    <xsl:choose>
      <xsl:when test="ancestor::composition">
        <xsl:apply-templates select="." mode="composition"/>
      </xsl:when>
      <xsl:when test="ancestor::selection">
        <xsl:apply-templates select="." mode="selection"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      division mode composition
      =========================================================================
  -->
  <xsl:template match="division" mode="composition">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <xsl:copy>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_division_head']/var"
          mode="head">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <head>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='composition_head_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='common_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates select="head/source[@type='file']|head/index"/>
        </head>
      </xsl:if>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>


  <!--
      *************************************************************************
                                        SELECTION
      *************************************************************************
  -->
  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <xsl:copy>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_head']/var"
          mode="head">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <head>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='common_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates select="head/source[@type='file']|head/index"/>
        </head>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="head or not(division)">
          <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                               mode="corpus">
            <xsl:with-param name="num" select="$num"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates
              select="comment()|processing-instruction()|division"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      division mode selection
      =========================================================================
  -->
  <xsl:template match="division" mode="selection">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <xsl:copy>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_division_head']/var"
          mode="head">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <head>
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='common_head']/var"
              mode="head">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
          <xsl:apply-templates select="head/source[@type='file']|head/index"/>
        </head>
      </xsl:if>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>


  <!--
      *************************************************************************
                                          VAR
      *************************************************************************
  -->
  <!--
      =========================================================================
      var mode head
      =========================================================================
  -->
  <xsl:template match="var" mode="head">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:choose>
      <xsl:when test="@name='head_as'">
        <xsl:attribute name="as">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:when test="@name='head_attributes'">
        <xsl:attribute name="attributes">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:when test="@name='head_transform'">
        <xsl:attribute name="transform">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="var_head">
          <xsl:with-param name="group" select="$group"/>
          <xsl:with-param name="node" select="$node"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
