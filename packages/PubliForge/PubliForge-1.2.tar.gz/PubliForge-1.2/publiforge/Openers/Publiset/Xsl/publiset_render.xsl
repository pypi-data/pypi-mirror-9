<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_render.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Processor image variables -->
  <xsl:variable name="img" select="1"/>
  <xsl:variable name="img_ext"></xsl:variable>
  <xsl:variable name="img_ext_cover"></xsl:variable>
  <!-- Processor string variables -->
  <xsl:variable name="str_sep"> – </xsl:variable>

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:apply-templates select="composition|selection"/>
  </xsl:template>

  <!--
      =========================================================================
      composition
      =========================================================================
  -->
  <xsl:template match="composition">
    <div class="pdocComposition">
      <h2>Composition</h2>
      <xsl:call-template name="title"/>
      <xsl:call-template name="attributes"/>
      <xsl:apply-templates select="head" mode="meta"/>
      <xsl:apply-templates select="head" mode="cover"/>
      <ul>
        <xsl:apply-templates select="division|file"/>
      </ul>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection">
    <div class="pdocSelection">
      <h2>Selection</h2>
      <xsl:call-template name="title"/>
      <xsl:call-template name="attributes"/>
      <xsl:apply-templates select="head" mode="meta"/>
      <xsl:apply-templates select="head" mode="cover"/>
      <ul>
        <xsl:apply-templates select="division|file"/>
      </ul>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      division
      =========================================================================
  -->
  <xsl:template match="division">
    <li class="pdocDivision">
      <xsl:call-template name="title"/>
      <xsl:call-template name="attributes"/>
      <xsl:apply-templates select="head" mode="meta"/>
      <xsl:apply-templates select="head" mode="cover"/>
      <xsl:if test="division|file">
        <ul>
          <xsl:apply-templates select="division|file"/>
        </ul>
      </xsl:if>
    </li>
  </xsl:template>

  <!--
      =========================================================================
      head mode meta
      =========================================================================
  -->
  <xsl:template match="head" mode="meta">
    <xsl:if test="shorttitle or identifier or copyright or collection
                  or contributors or date or place or source or keywordset
                  or subjectset or abstract or cover or annotation">
      <table class="pdocMeta">
        <xsl:apply-templates
            select="shorttitle|identifier|copyright|collection
                    |contributors|date|place|source|keywordset|subjectset
                    |abstract|cover|annotation"
            mode="meta"/>
      </table>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      file
      =========================================================================
  -->
  <xsl:template match="file">
    <li>
      <span class="pdocFile">
        <xsl:apply-templates/>
        <xsl:if test="@path or @xpath or @xslt or @argument">
          <strong> | </strong>
          <span>
            <xsl:if test="@path">
              <xsl:text>path="</xsl:text>
              <xsl:value-of select="@path"/>
              <xsl:text>"</xsl:text>
            </xsl:if>
            <xsl:if test="@xpath">
              <xsl:if test="@path">, </xsl:if>
              <xsl:text>xpath="</xsl:text>
              <xsl:value-of select="@xpath"/>
              <xsl:text>"</xsl:text>
            </xsl:if>
            <xsl:if test="@xslt">
              <xsl:if test="@path or @xpath">, </xsl:if>
              <xsl:text>xslt="</xsl:text>
              <xsl:value-of select="@xslt"/>
              <xsl:text>"</xsl:text>
            </xsl:if>
            <xsl:if test="@argument">
              <xsl:if test="@path or @xpath or @xslt">, </xsl:if>
              <xsl:text>argument="</xsl:text>
              <xsl:value-of select="@argument"/>
              <xsl:text>"</xsl:text>
             </xsl:if>
          </span>
        </xsl:if>
      </span>
    </li>
  </xsl:template>


  <!--
      *************************************************************************
                                   CALLABLE TEMPLATE
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template title
      =========================================================================
  -->
  <xsl:template name="title">
    <xsl:if test="head/title">
      <xsl:choose>
        <xsl:when test="count(ancestor::division)=0 and not(ancestor::selection)">
          <div class="h1">
            <xsl:apply-templates select="head/title"/>
            <xsl:for-each select="head/subtitle">
              <div class="h2"><xsl:apply-templates/></div>
            </xsl:for-each>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <span class="pdocDivisionTitle">
            <xsl:apply-templates select="head/title" mode="link"/>
            <xsl:for-each select="head/subtitle">
              <xsl:value-of select="$str_sep"/>
              <xsl:apply-templates mode="link"/>
            </xsl:for-each>
          </span>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template attributes
      =========================================================================
  -->
  <xsl:template name="attributes">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/@id or $node/@xml:lang or $node/@pi-source
                  or $node/@path or $node/@xpath or $node/@xslt
                  or $node/@as or $node/@attributes or $node/@transform
                  or $node/head/@as or $node/head/@attributes
                  or $node/head/@transform">
      <table class="pdocTransformAttributes">
        <xsl:if test="$node/@id">
          <tr>
            <td>ID</td><td> = </td>
            <td><xsl:value-of select="$node/@id"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@xml:lang">
          <tr>
            <td>xml:lang</td><td> = </td>
            <td><xsl:value-of select="$node/@xml:lang"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@path">
          <tr>
            <td>path</td><td> = </td>
            <td><xsl:value-of select="$node/@path"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@pi-source">
          <tr>
            <td>PI source</td><td> = </td>
            <td><xsl:value-of select="$node/@pi-source"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@xpath">
          <tr>
            <td>xpath</td><td> = </td>
            <td><xsl:value-of select="$node/@xpath"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@xslt">
          <tr>
            <td>xslt</td><td> = </td>
            <td><xsl:value-of select="$node/@xslt"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@as">
          <tr>
            <td>as</td><td> = </td>
            <td><xsl:value-of select="$node/@as"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@attributes">
          <tr>
            <td>attributes</td><td> = </td>
            <td><xsl:value-of select="$node/@attributes"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/@transform">
          <tr>
            <td>transform</td><td> = </td>
            <td><xsl:value-of select="$node/@transform"/></td>
          </tr>
        </xsl:if>

        <xsl:if test="$node/head/@as">
          <tr>
            <td>head/as</td><td> = </td>
            <td><xsl:value-of select="$node/head/@as"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/head/@attributes">
          <tr>
            <td>head/attributes</td><td> = </td>
            <td><xsl:value-of select="$node/head/@attributes"/></td>
          </tr>
        </xsl:if>
        <xsl:if test="$node/head/@transform">
          <tr>
            <td>head/transform</td><td> = </td>
            <td><xsl:value-of select="$node/head/@transform"/></td>
          </tr>
        </xsl:if>
      </table>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
