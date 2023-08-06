<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub3.xsl 237c275a0588 2015/02/04 20:29:27 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_media.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_ini.inc.xsl"/>
  <xsl:import href="publidoc2html5_template.inc.xsl"/>
  <xsl:import href="publidoc2html5_ini.inc.xsl"/>
  <xsl:import href="publidoc2epub2_template.inc.xsl"/>
  <xsl:import href="publidoc2epub2_i18n.inc.xsl"/>
  <xsl:import href="publidoc2epub2_base.inc.xsl"/>
  <xsl:import href="publidoc2epub2_ini.inc.xsl"/>
  <xsl:import href="publidoc2epub2_ncx.inc.xsl"/>
  <xsl:import href="publidoc2epub3_template.inc.xsl"/>
  <xsl:import href="publidoc2epub3_opf.inc.xsl"/>
  <xsl:import href="publidoc2epub3_nav.inc.xsl"/>
  <xsl:import href="publidoc2epub3_smil.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img" select="1"/>
  <xsl:param name="img_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="img_quality" select="92"/>
  <xsl:param name="img_optimize" select="4"/>
  <xsl:param name="img_ext">.jpg</xsl:param>
  <xsl:param name="img_ext_cover">.png</xsl:param>
  <xsl:param name="img_ext_icon">.png</xsl:param>
  <xsl:param name="img_size">640x480&gt;</xsl:param>
  <xsl:param name="img_size_cover">768x1024&gt;</xsl:param>
  <xsl:param name="img_size_header">x48&gt;</xsl:param>
  <xsl:param name="img_size_thumbnail">120x120&gt;</xsl:param>
  <xsl:param name="img_size_icon">x32&gt;</xsl:param>
  <!-- Processor audio parameters -->
  <xsl:param name="aud" select="0"/>
  <xsl:param name="aud_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="aud_ext1">.ogg</xsl:param>
  <xsl:param name="aud_ext2">.mp3</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="0"/>
  <xsl:param name="vid_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="vid_ext1">.ogv</xsl:param>
  <xsl:param name="vid_ext2">.mp4</xsl:param>
  <xsl:param name="vid_width">300</xsl:param>
  <!-- Processor string parameters -->
  <xsl:param name="str_sep"> – </xsl:param>
  <xsl:param name="str_notecall_open">(</xsl:param>
  <xsl:param name="str_notecall_close">)</xsl:param>
  <xsl:param name="str_stage_sep">, </xsl:param>
  <xsl:param name="str_stage_open">(</xsl:param>
  <xsl:param name="str_stage_close">)</xsl:param>
  <!-- Processor mathematical parameters -->
  <xsl:param name="math" select="1"/>
  <xsl:param name="math_mode">png</xsl:param>
  <xsl:param name="math_factor">0.60</xsl:param>
  <!-- Processor HTML 5 parameters -->
  <xsl:param name="writing_mode">horizontal-lr</xsl:param>
  <xsl:param name="toc" select="0"/>
  <xsl:param name="toc_division_depth" select="0"/>
  <xsl:param name="toc_section_depth" select="1"/>
  <xsl:param name="toc_with_abstract" select="0"/>
  <xsl:param name="subtoc" select="1"/>
  <xsl:param name="index" select="0"/>
  <xsl:param name="js" select="0"/>
  <xsl:param name="minify" select="1"/>
  <!-- Processor ePub 3 parameters -->
  <xsl:param name="ean"/>
  <xsl:param name="publisher_label"/>
  <xsl:param name="publisher_url"/>
  <xsl:param name="cover"/>
  <xsl:param name="extract_cover_ext">.jpg</xsl:param>
  <xsl:param name="extract_cover_size"/>

  <!-- Variables -->
  <xsl:variable name="path" select="concat($output, 'Container~/OEBPS/')"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Videos/</xsl:variable>
  <xsl:variable name="css_dir">Css/</xsl:variable>
  <xsl:variable name="js_dir">Js/</xsl:variable>
  <xsl:variable name="math_dir">Maths/</xsl:variable>
  <xsl:variable name="html_ext">.xhtml</xsl:variable>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="onefile" select="0"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="" doctype-system=""/>


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
    <xsl:apply-templates select="document|topic"/>

    <xsl:choose>
      <xsl:when test="$cover and not($cover='=')">
        <xsl:apply-templates select="//image[name(..)!='cover']" mode="ini"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="//image" mode="ini"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="$aud">
      <xsl:apply-templates select="//audio" mode="ini"/>
      <xsl:apply-templates select="//smil" mode="ini"/>
      <xsl:apply-templates select="//topic" mode="smil"/>
    </xsl:if>
    <xsl:if test="$vid"><xsl:apply-templates select="//video" mode="ini"/></xsl:if>
    <xsl:call-template name="minify_files"/>
    <xsl:call-template name="post_ini"/>

    <xsl:if test="$index and .//index">
      <xsl:call-template name="index_file"/>
    </xsl:if>
    <xsl:if test=".//note">
      <xsl:call-template name="html_file">
        <xsl:with-param name="name" select="concat($fid, '-not')"/>
        <xsl:with-param name="title" select="$i18n_notes"/>
        <xsl:with-param name="nojs" select="1"/>
        <xsl:with-param name="body">
          <body>
            <xsl:attribute name="class">
              <xsl:text>pdocDivision</xsl:text>
              <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
            </xsl:attribute>
            <h1><xsl:value-of select="$i18n_notes"/></h1>
          </body>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:call-template name="cover"/>
    <xsl:if test="$toc"><xsl:call-template name="toc"/></xsl:if>
    <xsl:call-template name="package_opf"/>
    <xsl:call-template name="nav_xhtml"/>
    <xsl:call-template name="toc_ncx"/>

    <xsl:apply-templates select=".//division|.//topic" mode="file"/>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="cover"/>
    <xsl:if test="$toc"><xsl:call-template name="toc"/></xsl:if>
    <xsl:call-template name="package_opf"/>
    <xsl:call-template name="nav_xhtml"/>
    <xsl:call-template name="toc_ncx"/>

    <xsl:call-template name="html_file">
      <xsl:with-param name="name" select="concat($fid, '-tpc-1')"/>
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body>
          <xsl:attribute name="class">
            <xsl:text>pdocTopic</xsl:text>
            <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
          </xsl:attribute>
          <xsl:apply-templates select="header"/>
          <xsl:call-template name="anchor_levels"/>
          <xsl:if test="head/title">
            <div class="h1"><xsl:apply-templates select="head/title"/></div>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <div class="h2">
              <xsl:call-template name="subtitle"/>
            </div>
          </xsl:if>
          <xsl:apply-templates select="." mode="corpus"/>
          <xsl:apply-templates select="footer"/>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>
