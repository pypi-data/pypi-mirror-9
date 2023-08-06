<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiquiz_save.xsl 301c3ebaab06 2014/12/09 10:21:56 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_save.xsl"/>
  <xsl:import href="publiquiz_template.inc.xsl"/>

  <!--
      =========================================================================
      quiz
      =========================================================================
  -->
  <xsl:template match="quiz">
    <xsl:variable name="num" select="count(preceding::quiz)"/>

    <xsl:copy>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="head">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='quiz']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>


  <!--
      *************************************************************************
                                         GROUP
      *************************************************************************
  -->
  <!--
      =========================================================================
      group mode head
      =========================================================================
  -->
  <xsl:template match="group" mode="head">
    <xsl:param name="num"/>
    <xsl:param name="node"/>

    <xsl:apply-templates select="var[@cast='attribute']" mode="head">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>
    <head>
      <xsl:apply-templates select="var[not(@cast) or @cast!='attribute']"
                           mode="head">
        <xsl:with-param name="group" select="concat(@name, $num)"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:apply-templates>
      <xsl:apply-templates
          select="$node/head/identifier|$node/head/collection
                  |$node/head/date|$node/head/place|$node/head/source
                  |$node/head/indexset|$node/head/abstract|$node/head/cover"/>
    </head>
  </xsl:template>

  <!--
      =========================================================================
      group mode corpus
      =========================================================================
  -->
  <xsl:template match="group" mode="corpus">
    <xsl:param name="num"/>
    <xsl:param name="node"/>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>

    <xsl:apply-templates select="var[@name='instructions']" mode="corpus">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>

    <xsl:if test="$node/production"><production>[?hold?]</production></xsl:if>
    <xsl:apply-templates select="var[@name=$engine]" mode="corpus">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>

    <xsl:apply-templates select="var[@name='help']" mode="corpus">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="var[@name='answer']" mode="corpus">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>
  </xsl:template>


  <!--
      *************************************************************************
                                          VAR
      *************************************************************************
  -->
  <!--
      =========================================================================
      var mode corpus
      =========================================================================
  -->
  <xsl:template match="var" mode="corpus">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:choose>
      <xsl:when test="@name='instructions' or @name='help' or @name='answer'">
        <xsl:element name="{@name}">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat('__', $group, @name, '__')"/>
        <xsl:text> </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
