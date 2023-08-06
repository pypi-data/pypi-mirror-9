<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2html5.xsl 0dbbfbcef0d6 2015/02/01 08:38:54 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml.xsl"/>
  <xsl:import href="publidoc2html5_template.inc.xsl"/>
  <xsl:import href="publidoc2html5_ini.inc.xsl"/>

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
  <xsl:param name="aud" select="1"/>
  <xsl:param name="aud_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="aud_ext1">.ogg</xsl:param>
  <xsl:param name="aud_ext2">.mp3</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="1"/>
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
  <xsl:param name="math">1</xsl:param>
  <xsl:param name="math_mode">png</xsl:param>
  <xsl:param name="math_factor">0.50</xsl:param>
  <!-- Processor HTML 5 parameters -->
  <xsl:param name="onefile" select="0"/>
  <xsl:param name="toc" select="1"/>
  <xsl:param name="toc_division_depth" select="1"/>
  <xsl:param name="toc_section_depth" select="1"/>
  <xsl:param name="toc_with_abstract" select="1"/>
  <xsl:param name="subtoc" select="1"/>
  <xsl:param name="index" select="1"/>
  <xsl:param name="js" select="1"/>
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
              omit-xml-declaration="yes"
              doctype-public="" doctype-system=""/>

</xsl:stylesheet>
