<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_render4maestro.xsl c064a7b90674 2014/09/12 17:21:50 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc_render.xsl"/>

  <!-- Variables -->
  <xsl:variable name="img_dir">Static/Images/notfound.jpg#</xsl:variable>
  <xsl:variable name="aud_dir">Media/Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Media/Videos/</xsl:variable>

  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="-//W3C//DTD XHTML 1.1//EN"
              doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <html>
      <xsl:attribute name="xml:lang"><xsl:value-of select="$lang"/></xsl:attribute>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta http-equiv="Content-Language">
          <xsl:attribute name="content"><xsl:value-of select="$lang"/></xsl:attribute>
        </meta>
        <title><xsl:apply-templates select="*/head/title" mode="text"/></title>
        <link rel="StyleSheet" href="Css/reset.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/publidoc.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/custom.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/opener.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/maestro.css" type="text/css"/>
      </head>
      <body>
        <div id="content">
          <xsl:apply-templates select="document|topic"/>
        </div>
      </body>
    </html>
  </xsl:template>

  <!--
      =========================================================================
      Template pulse_gif
      =========================================================================
  -->
  <xsl:template name="pulse_gif">
    <xsl:text>Static/Images/pulse.gif</xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_symbol
      =========================================================================
  -->
  <xsl:template name="audio_symbol">
    <xsl:param name="id" select="@id"/>
    <img src="Static/Images/audio.png" alt="{$id}"/>
  </xsl:template>

  <!--
      =========================================================================
      Templates mid
      =========================================================================
  -->
  <xsl:template name="mid_section">
    <xsl:if test="not(ancestor::section)">
      <a id="section{count(preceding::section)}" class="mid">
        <xsl:text> </xsl:text>
      </a>
    </xsl:if>
  </xsl:template>

  <xsl:template name="mid_image">
    <xsl:if test="not(ancestor::image) and not(ancestor::media and ../link)">
      <a id="image{count(preceding::image)}" class="mid">
        <xsl:text> </xsl:text>
      </a>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
