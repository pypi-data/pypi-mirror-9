<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_save_base.inc.xsl 4650ee178855 2014/12/07 08:11:04 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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
      <xsl:apply-templates select="$node/head/indexset"/>
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

    <xsl:apply-templates select="var" mode="corpus">
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
      var mode head
      =========================================================================
  -->
  <xsl:template match="var" mode="head">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:call-template name="var_head">
      <xsl:with-param name="group" select="$group"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      var mode corpus
      =========================================================================
  -->
  <xsl:template match="var" mode="corpus">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:value-of select="concat('__', $group, @name, '__')"/>
    <xsl:text> </xsl:text>
  </xsl:template>


  <!--
      *************************************************************************
                                  CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template var_head
      =========================================================================
  -->
  <xsl:template name="var_head">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:choose>
      <xsl:when test="@name='subtitle'">
        <subtitle>
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </subtitle>
        <xsl:apply-templates
            select="$node/head/subtitle[preceding-sibling::subtitle]"/>
      </xsl:when>
      <xsl:when test="@name='identifier_ean'">
        <identifier type="ean">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </identifier>
        <xsl:apply-templates
            select="$node/head/identifier[@type='ean' and @for]"/>
      </xsl:when>
      <xsl:when test="@name='identifier_uri'">
        <identifier type="uri">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </identifier>
      </xsl:when>
      <xsl:when test="@name='date'">
        <date value="__{$group}{@name}__"/>
      </xsl:when>
      <xsl:when test="@name='source_book'">
        <source type="book">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </source>
      </xsl:when>
      <xsl:when test="@name='source_file'">
        <source type="file">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </source>
      </xsl:when>
      <xsl:when test="@name='cover'">
        <cover>
          <image id="__{$group}{@name}__"/>
        </cover>
      </xsl:when>

      <xsl:when test="@cast='attribute' and @type='boolean'">
        <xsl:attribute name="{@name}">
          <xsl:value-of select="concat('BOOL__', $group, @name, '__')"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:when test="@cast='attribute'">
        <xsl:attribute name="{@name}">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:attribute>
      </xsl:when>

      <xsl:otherwise>
        <xsl:element name="{@name}">
          <xsl:value-of select="concat('__', $group, @name, '__')"/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
