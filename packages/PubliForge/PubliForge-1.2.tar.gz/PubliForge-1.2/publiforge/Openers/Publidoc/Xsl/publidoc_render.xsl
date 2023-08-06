<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_render.xsl 0dbbfbcef0d6 2015/02/01 08:38:54 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_media.inc.xsl"/>
  <xsl:import href="publidoc2html5_template.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Processor image variables -->
  <xsl:variable name="img" select="1"/>
  <xsl:variable name="img_ext"></xsl:variable>
  <xsl:variable name="img_ext_cover"></xsl:variable>
  <xsl:variable name="img_ext_icon"></xsl:variable>
  <!-- Processor audio variables -->
  <xsl:variable name="aud" select="1"/>
  <xsl:variable name="aud_ext1"></xsl:variable>
  <xsl:variable name="aud_ext2"></xsl:variable>
  <!-- Processor video variables -->
  <xsl:variable name="vid" select="1"/>
  <xsl:variable name="vid_ext1"></xsl:variable>
  <xsl:variable name="vid_ext2"></xsl:variable>
  <xsl:variable name="vid_width">300</xsl:variable>
  <!-- Processor string variables -->
  <xsl:variable name="str_sep"> – </xsl:variable>
  <xsl:variable name="str_notecall_open">(</xsl:variable>
  <xsl:variable name="str_notecall_close">)</xsl:variable>
  <xsl:variable name="str_stage_sep">, </xsl:variable>
  <xsl:variable name="str_stage_open">(</xsl:variable>
  <xsl:variable name="str_stage_close">)</xsl:variable>
  <!-- Processor XHTML variables -->
  <xsl:variable name="onefile" select="1"/>
  <xsl:variable name="toc" select="1"/>
  <xsl:variable name="toc_division_depth" select="5"/>
  <xsl:variable name="toc_section_depth" select="1"/>
  <xsl:variable name="toc_with_abstract" select="1"/>
  <xsl:variable name="subtoc" select="0"/>
  <xsl:variable name="index" select="1"/>
  <xsl:variable name="js" select="1"/>

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>
  <xsl:variable name="aud_dir">/media/audios/</xsl:variable>
  <xsl:variable name="vid_dir">/media/videos/</xsl:variable>
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
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <div class="pdocDocument">
      <xsl:apply-templates select="head" mode="meta"/>
      <xsl:if test="head/title">
        <div class="h1">
          <xsl:apply-templates select="head/title"/>
          <xsl:if test="head/subtitle">
            <div class="h2">
              <xsl:call-template name="subtitle"/>
            </div>
          </xsl:if>
        </div>
      </xsl:if>
      <xsl:apply-templates select="head" mode="cover"/>
      <xsl:apply-templates select="." mode="onefiletoc"/>
      <xsl:apply-templates select="division|topic" mode="onefile"/>
      <xsl:if test="$index and .//index">
        <div class="pdocIndex">
          <xsl:call-template name="index"/>
        </div>
      </xsl:if>
      <xsl:if test=".//note">
        <div class="pdocNoteFooter">
          <xsl:apply-templates select=".//note" mode="footer"/>
        </div>
      </xsl:if>
      <xsl:call-template name="warnings"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocTopic</xsl:text>
        <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:apply-templates select="head" mode="meta"/>
      <xsl:apply-templates select="header"/>
      <xsl:if test="head/title">
        <h1><xsl:apply-templates select="head/title"/></h1>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <h2><xsl:call-template name="subtitle"/></h2>
      </xsl:if>
      <xsl:apply-templates select="." mode="onefiletoc"/>
      <xsl:apply-templates select="." mode="corpus"/>
      <xsl:if test="$index and .//index">
        <div class="pdocIndex">
          <xsl:call-template name="index"/>
        </div>
      </xsl:if>
      <xsl:if test=".//note">
        <div class="pdocNoteFooter">
          <xsl:apply-templates select=".//note" mode="footer"/>
        </div>
      </xsl:if>
      <xsl:apply-templates select="footer"/>
      <xsl:call-template name="warnings"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      warning
      =========================================================================
  -->
  <xsl:template match="warning">
    <xsl:variable name="count" select="count(preceding::warning)+1"/>
    <a href="#wc{$count}" id="w{$count}"
       class="pdocWarning"><xsl:apply-templates/></a>
  </xsl:template>

  <xsl:template match="warning" mode="call">
    <xsl:variable name="count" select="count(preceding::warning)+1"/>
    <a href="#w{$count}" id="wc{$count}">
      <span>(<xsl:value-of select="$count"/>) </span>
      <xsl:apply-templates/>
    </a>
    <xsl:if test="following::warning">
      <span> | </span>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template warnings
      =========================================================================
  -->
  <xsl:template name="warnings">
    <xsl:if test=".//warning">
      <div class="pdocWarnings">
        <label><xsl:value-of select="count(.//warning)"/> warning(s)</label>
        <xsl:apply-templates select=".//warning" mode="call"/>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template pulse_gif
      =========================================================================
  -->
  <xsl:template name="pulse_gif">
    <xsl:value-of select="concat($route, 'Images/pulse.gif')"/>
  </xsl:template>

  <!--
      =========================================================================
      Template image_extension
      =========================================================================
  -->
  <xsl:template name="image_extension"/>

  <!--
      =========================================================================
      audio mode header
      =========================================================================
  -->
  <xsl:template match="audio" mode="header">
    <xsl:if test="$aud and @type='background'
                  and count(preceding::audio[@type='background'])=0">
      <xsl:call-template name="audio">
        <xsl:with-param name="controls" select="0"/>
        <xsl:with-param name="autoplay" select="1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_symbol
      =========================================================================
  -->
  <xsl:template name="audio_symbol">
    <xsl:param name="id" select="@id"/>
    <img src="{$route}Images/audio.png" alt="{$id}"/>
  </xsl:template>

  <!--
      =========================================================================
      Template math
      =========================================================================
  -->
  <xsl:template name="math">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      PI hold
      =========================================================================
  -->
  <xsl:template match="processing-instruction('hold')">
    <xsl:text> </xsl:text>
  </xsl:template>

</xsl:stylesheet>
