<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset4publidoc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str">

  <xsl:import href="publiset2publidoc.xsl"/>

  <!-- Processor meta data parameters -->
  <xsl:param name="id"/>
  <xsl:param name="lang">en</xsl:param>
  <xsl:param name="title"/>
  <xsl:param name="ean"/>
  <xsl:param name="copyright"/>
  <xsl:param name="collection"/>
  <xsl:param name="author_firstname"/>
  <xsl:param name="author_lastname"/>
  <xsl:param name="publisher_name"/>
  <xsl:param name="publisher_url"/>
  <xsl:param name="keywords"/>
  <xsl:param name="subjects"/>
  <xsl:param name="abstract"/>
  <xsl:param name="cover"/>
  <!-- Processor schema parameters -->
  <xsl:param name="div1_xslt"/>
  <xsl:param name="div1_xpath"/>
  <xsl:param name="div1_path">../../..</xsl:param>
  <xsl:param name="div1_head_transform"/>

  <!-- Variables -->
  <xsl:variable name="composition_id"><xsl:value-of select="$fid"/></xsl:variable>
  <xsl:variable name="composition_as">publidoc</xsl:variable>
  <xsl:variable name="composition_att">version=1.0</xsl:variable>
  <xsl:variable name="div1_as">document</xsl:variable>
  <xsl:variable name="div1_att">
    <xsl:text>id=</xsl:text><xsl:value-of select="$fid"/>
    <xsl:text> xml:lang=</xsl:text><xsl:value-of select="$lang"/>
  </xsl:variable>


  <!--
      =========================================================================
      publiforge
      =========================================================================
  -->
  <xsl:template match="publiforge">
    <xsl:apply-templates select="pack"/>
  </xsl:template>

  <!--
      =========================================================================
      pack
      =========================================================================
  -->
  <xsl:template match="pack">
    <publiset version="1.0">
      <composition id="{$composition_id}" xml:lang="{$lang}"
                   as="{$composition_as}" attributes="{$composition_att}">
        <division as="{$div1_as}" attributes="{$div1_att}">
          <xsl:choose>
            <xsl:when test="$div1_xslt">
              <xsl:attribute name="xslt">
                <xsl:value-of select="$div1_xslt"/>
              </xsl:attribute>
            </xsl:when>
            <xsl:when test="$div1_xpath">
              <xsl:attribute name="xpath">
                <xsl:value-of select="$div1_xpath"/>
              </xsl:attribute>
            </xsl:when>
          </xsl:choose>
          <xsl:if test="$div1_path">
            <xsl:attribute name="path">
              <xsl:value-of select="$div1_path"/>
            </xsl:attribute>
          </xsl:if>

          <xsl:call-template name="head"/>

          <xsl:comment> ================================================================ </xsl:comment>
          <xsl:apply-templates select="files/file"/>
        </division>
      </composition>
    </publiset>
  </xsl:template>

  <!--
      =========================================================================
      file
      =========================================================================
  -->
  <xsl:template match="file">
    <file><xsl:apply-templates/></file>
  </xsl:template>

  <!--
      =========================================================================
      Template head
      =========================================================================
  -->
  <xsl:template name="head">
    <head>
      <xsl:if test="$div1_head_transform">
        <xsl:attribute name="transform">
          <xsl:value-of select="$div1_head_transform"/>
        </xsl:attribute>
      </xsl:if>

      <title>
        <xsl:choose>
          <xsl:when test="$title">
            <xsl:value-of select="normalize-space($title)"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="label/node()"/>
          </xsl:otherwise>
        </xsl:choose>
      </title>

      <xsl:if test="$ean">
        <identifier type="ean"><xsl:value-of select="$ean"/></identifier>
      </xsl:if>

      <xsl:if test="$copyright">
        <copyright>
          <xsl:value-of select="normalize-space($copyright)"/>
        </copyright>
      </xsl:if>

      <xsl:if test="$collection">
        <collection>
          <xsl:value-of select="normalize-space($collection)"/>
        </collection>
      </xsl:if>

      <xsl:if test="$author_lastname or $publisher_name">
        <contributors>
          <xsl:if test="$author_lastname">
            <contributor>
              <xsl:if test="$author_firstname">
                <firstname><xsl:value-of select="$author_firstname"/></firstname>
              </xsl:if>
              <lastname><xsl:value-of select="$author_lastname"/></lastname>
              <role>author</role>
            </contributor>
          </xsl:if>
          <xsl:if test="$publisher_name">
            <contributor>
              <label><xsl:value-of select="$publisher_name"/></label>
              <xsl:if test="$publisher_url">
                <link uri="{$publisher_url}">
                  <xsl:value-of select="$publisher_name"/>
                </link>
              </xsl:if>
              <role>publisher</role>
            </contributor>
          </xsl:if>
        </contributors>
      </xsl:if>

      <xsl:if test="$keywords">
        <keywordset>
          <xsl:for-each select="str:split($keywords, ',')">
            <keyword><xsl:value-of select="normalize-space()"/></keyword>
          </xsl:for-each>
        </keywordset>
      </xsl:if>

      <xsl:if test="$subjects">
        <subjectset>
          <xsl:for-each select="str:split($subjects, ',')">
            <subject><xsl:value-of select="normalize-space()"/></subject>
          </xsl:for-each>
        </subjectset>
      </xsl:if>

      <xsl:if test="$abstract">
        <abstract>
          <p><xsl:value-of select="normalize-space($abstract)"/></p>
        </abstract>
      </xsl:if>

      <xsl:if test="$cover">
        <cover><image id="{$cover}"/></cover>
      </xsl:if>
    </head>
  </xsl:template>

</xsl:stylesheet>
