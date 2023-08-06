<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2xhtml.xsl 49f73360ef84 2015/01/30 08:44:35 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_media.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_ini.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img" select="1"/>
  <xsl:param name="img_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="img_quality" select="92"/>
  <xsl:param name="img_optimize" select="4"/>
  <xsl:param name="img_ext">.png</xsl:param>
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
  <xsl:param name="aud_ext">.ogg</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="0"/>
  <xsl:param name="vid_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="vid_ext">.ogv</xsl:param>
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
  <xsl:param name="math_factor">0.50</xsl:param>
  <!-- Processor XHTML parameters -->
  <xsl:param name="onefile" select="0"/>
  <xsl:param name="toc" select="1"/>
  <xsl:param name="toc_division_depth" select="1"/>
  <xsl:param name="toc_section_depth" select="1"/>
  <xsl:param name="toc_with_abstract" select="1"/>
  <xsl:param name="subtoc" select="1"/>
  <xsl:param name="index" select="1"/>
  <xsl:param name="js" select="0"/>
  <xsl:param name="minify" select="1"/>
  <xsl:param name="nonav" select="0"/>

  <!-- Variables -->
  <xsl:variable name="path" select="$output"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Videos/</xsl:variable>
  <xsl:variable name="css_dir">Css/</xsl:variable>
  <xsl:variable name="js_dir">Js/</xsl:variable>
  <xsl:variable name="math_dir">Maths/</xsl:variable>
  <xsl:variable name="html_ext">.html</xsl:variable>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="-//W3C//DTD XHTML 1.1//EN"
              doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:apply-templates select="selection"/>
  </xsl:template>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
    <xsl:if test="$img"><xsl:apply-templates select="//image" mode="ini"/></xsl:if>
    <xsl:if test="$aud"><xsl:apply-templates select="//audio" mode="ini"/></xsl:if>
    <xsl:if test="$vid"><xsl:apply-templates select="//video" mode="ini"/></xsl:if>
    <xsl:call-template name="minify_files"/>
    <xsl:call-template name="post_ini"/>
  </xsl:template>

  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection">
    <xsl:if test=".//link">
      <xsl:call-template name="html_frame">
        <xsl:with-param name="title">
          <xsl:value-of select="head/title"/>
        </xsl:with-param>
        <xsl:with-param name="body">
          <body class="pdocToc">
            <xsl:if test="head/title">
              <h1><xsl:call-template name="title"/></h1>
            </xsl:if>
            <xsl:if test="head/subtitle">
              <h2><xsl:call-template name="subtitle"/></h2>
            </xsl:if>
            <ul>
              <xsl:apply-templates select="division|link" mode="toc"/>
            </ul>
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
    <xsl:call-template name="html_frame">
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body>
          <xsl:choose>
            <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~ One file ~~~~~~~~~~~~~~~~~~~~~~~ -->
            <xsl:when test="$onefile">
              <xsl:attribute name="class">pdocDocument</xsl:attribute>
              <xsl:if test="head/title">
                <h1>
                  <xsl:call-template name="title"/>
                  <xsl:if test="head/subtitle">
                    <br/>
                    <span class="h2">
                      <xsl:call-template name="subtitle"/>
                    </span>
                  </xsl:if>
                </h1>
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
            </xsl:when>

            <!-- ~~~~~~~~~~~~~~~~~~~~~~~~ Multi files ~~~~~~~~~~~~~~~~~~~~~ -->
            <xsl:otherwise>
              <xsl:attribute name="class">pdocToc</xsl:attribute>
              <xsl:if test="head/title">
                <h1><xsl:call-template name="title"/></h1>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <h2><xsl:call-template name="subtitle"/></h2>
              </xsl:if>
              <ul>
                <xsl:apply-templates select="division|topic" mode="toc"/>
                <xsl:if test="$index and .//index">
                  <li>
                    <a href="{$fid}-index{$html_ext}">
                      <xsl:value-of select="$i18n_index"/>
                    </a>
                  </li>
                  <xsl:call-template name="index_file"/>
                </xsl:if>
              </ul>
              <xsl:apply-templates select=".//division|.//topic" mode="file"/>
            </xsl:otherwise>
          </xsl:choose>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="html_frame">
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
          <xsl:if test="head/title">
            <h1><xsl:call-template name="title"/></h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2><xsl:call-template name="subtitle"/></h2>
          </xsl:if>

          <xsl:if test="$onefile">
            <xsl:apply-templates select="." mode="onefiletoc"/>
          </xsl:if>

          <xsl:apply-templates select="." mode="corpus"/>

          <xsl:if test="$index and .//index">
            <div class="pdocIndex">
              <xsl:call-template name="index"/>
            </div>
          </xsl:if>
          <xsl:if test="$onefile and .//note">
            <div class="pdocNoteFooter">
              <xsl:apply-templates select=".//note" mode="footer"/>
            </div>
          </xsl:if>
          <xsl:apply-templates select="footer"/>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>
