<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2dtbook_template.inc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.daisy.org/z3986/2005/dtbook/">

  <!--
      =========================================================================
      Template head
      =========================================================================
  -->
  <xsl:template name="head">
    <head>
      <xsl:choose>
        <xsl:when test="@id"><meta name="dtb:uid" content="{@id}"/></xsl:when>
        <xsl:otherwise><meta name="dtb:uid" content="{$fid}"/></xsl:otherwise>
      </xsl:choose>
      <xsl:if test="head/title">
        <meta name="dc:Title" content="{normalize-space(head/title)}"/>
      </xsl:if>
      <xsl:if test="head/date">
        <meta name="dc:Date" content="{head/date/@value}" />
      </xsl:if>
      <meta name="dc:Language" content="{$lang}"/>
      <xsl:if test="head/identifier[@type='ean']">
        <meta name="dc:Identifier" content="{head/identifier[@type='ean'][1]}"/>
      </xsl:if>
      <xsl:apply-templates select="head/contributors/contributor" mode="head"/>
      <xsl:apply-templates select="head/subjectset/subject" mode="head"/>
      <xsl:if test="head/copyright">
        <meta name="dc:Rights" content="{normalize-space(head/copyright[1])}"/>
      </xsl:if>
    </head>
  </xsl:template>

  <!--
      =========================================================================
      Template frontmatter
      =========================================================================
  -->
  <xsl:template name="frontmatter">
    <xsl:if test="head/title or topic[@type='title']/head/title">
      <xsl:comment> ****************************************************************** </xsl:comment>
      <frontmatter>
        <doctitle>
          <xsl:choose>
            <xsl:when test="topic[@type='title']/head/title">
              <xsl:apply-templates select="topic[@type='title']/head/title"/>
              <xsl:call-template name="subtitle">
                <xsl:with-param name="nodes"
                                select="topic[@type='title']/head/subtitle"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="head/title"/>
              <xsl:call-template name="subtitle"/>
            </xsl:otherwise>
          </xsl:choose>
        </doctitle>

        <xsl:apply-templates select="head/contributors/contributor"
                             mode="frontmatter"/>

        <xsl:apply-templates select="topic[@type='title']" mode="corpus"/>
      </frontmatter>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template subtitle
      =========================================================================
  -->
  <xsl:template name="subtitle">
    <xsl:param name="nodes" select="head/subtitle"/>
    <xsl:for-each select="$nodes">
      <br/><xsl:apply-templates/>
    </xsl:for-each>
  </xsl:template>

  <!--
      =========================================================================
      Template id_attr
      =========================================================================
  -->
  <xsl:template name="id_attr">
    <xsl:if test="@xml:id or @id">
      <xsl:attribute name="id">
        <xsl:value-of select="@xml:id|@id"/>
      </xsl:attribute>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template class_attr
      =========================================================================
  -->
  <xsl:template name="class_attr">
    <xsl:if test="@type">
      <xsl:attribute name="class">
        <xsl:value-of select="@type"/>
      </xsl:attribute>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template level_attrs
      =========================================================================
  -->
  <xsl:template name="level_attrs">
    <xsl:call-template name="id_attr"/>

    <xsl:attribute name="class">
      <xsl:value-of select="name()"/>
      <xsl:if test="@type">
        <xsl:value-of select="concat('-', @type)"/>
      </xsl:if>
    </xsl:attribute>

    <xsl:copy-of select="@xml:lang"/>
  </xsl:template>

  <!--
      =========================================================================
      Template level_hd
      =========================================================================
  -->
  <xsl:template name="level_hd">
    <xsl:if test="head/title">
      <hd>
        <xsl:apply-templates select="head/title"/>
        <xsl:call-template name="subtitle"/>
      </hd>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template doctitle
      =========================================================================
  -->
  <xsl:template name="doctitle">
    <doctitle>
      <xsl:apply-templates select="head/title"/>
      <xsl:call-template name="subtitle"/>
    </doctitle>
  </xsl:template>

  <!--
      =========================================================================
      Template image_extension
      =========================================================================
  -->
  <xsl:template name="image_extension">
    <xsl:choose>
      <xsl:when test="processing-instruction('tune')[
                      contains(., 'target=&quot;html&quot;')
                      and contains(., 'format=')]">
        <xsl:text>.</xsl:text>
        <xsl:apply-templates select="processing-instruction('tune')"
                             mode="tune">
          <xsl:with-param name="argument">format</xsl:with-param>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$img_ext"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template image_alt
      =========================================================================
  -->
  <xsl:template name="image_alt">
    <xsl:attribute name="alt">
      <xsl:choose>
        <xsl:when test="@alt">
          <xsl:value-of select="@alt"/>
        </xsl:when>
        <xsl:when test="../head/title">
          <xsl:apply-templates select="../head/title" mode="text"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@id"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

</xsl:stylesheet>
