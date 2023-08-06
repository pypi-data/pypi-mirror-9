<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: publiquiz2epub3_opf.inc.xsl b662575e42a4 2015/02/02 12:25:15 Patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.idpf.org/2007/opf">

  <!--
      *************************************************************************
                                       MANIFEST
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template css_manifest
      =========================================================================
  -->
  <xsl:template name="css_manifest">
    <xsl:choose>
      <xsl:when test="$minify">
        <item id="c_styles" href="{$css_dir}styles.css" media-type="text/css"/>
      </xsl:when>
      <xsl:otherwise>
        <item id="c_publidoc" href="{$css_dir}publidoc.css" media-type="text/css"/>
        <item id="c_publidoc" href="{$css_dir}publiquiz.css" media-type="text/css"/>
        <item id="c_custom" href="{$css_dir}custom.css" media-type="text/css"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template js_manifest
      =========================================================================
  -->
  <xsl:template name="js_manifest">
    <xsl:choose>
      <xsl:when test="$minify">
        <item id="j_jquery" href="{$js_dir}jquery.js" media-type="application/javascript"/>
        <item id="j_scripts" href="{$js_dir}scripts.js" media-type="application/javascript"/>
      </xsl:when>
      <xsl:otherwise>
        <item id="j_jquery" href="{$js_dir}jquery.js" media-type="application/javascript"/>
        <item id="j_publidoc" href="{$js_dir}publidoc.js" media-type="application/javascript"/>
        <item id="j_publiquiz" href="{$js_dir}publiquiz.js" media-type="application/javascript"/>
        <item id="j_publiquiz_basics" href="{$js_dir}publiquiz_basics.js" media-type="application/javascript"/>
        <xsl:if test="$matching_link">
          <item id="j_publiquiz_matching_link" href="{$js_dir}publiquiz_matching_link.js" media-type="application/javascript"/>
        </xsl:if>
        <xsl:if test="$pip">
          <item id="j_publiquiz_pip" href="{$js_dir}publiquiz_pip.js" media-type="application/javascript"/>
        </xsl:if>
        <item id="j_publiquiz_loader" href="{$js_dir}publiquiz_loader.js" media-type="application/javascript"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      *************************************************************************
                                        SPINE
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template spine
      =========================================================================
  -->
  <xsl:template name="spine">
    <spine toc="ncx">
      <xsl:attribute name="page-progression-direction">
        <xsl:choose>
          <xsl:when test="$writing_mode='horizontal-rl'
                          or $writing_mode='vertical-rl'">rtl</xsl:when>
          <xsl:otherwise>ltr</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:if test="head/cover or ($cover and not($cover='='))">
        <itemref idref="h_{translate($fid, ' ', '_')}-cover" linear="no"/>
      </xsl:if>
      <!-- <itemref idref="h_{translate($fid, ' ', '_')}-nav" linear="no"/> -->
      <xsl:if test="$toc">
        <itemref idref="h_{translate($fid, ' ', '_')}-toc"/>
      </xsl:if>
      <xsl:apply-templates select="../topic|../quiz|division|topic|quiz"
                           mode="spine"/>
      <xsl:if test="$index and .//index">
        <itemref idref="h_{translate($fid, ' ', '_')}-index"/>
      </xsl:if>
      <xsl:if test=".//note">
        <itemref idref="h_{translate($fid, ' ', '_')}-not"/>  <!-- linear="no" -->
        <xsl:apply-templates select=".//note" mode="spine"/>
      </xsl:if>
    </spine>
  </xsl:template>

  <!--
      =========================================================================
      quiz
      =========================================================================
  -->
  <xsl:template match="quiz" mode="spine">
    <itemref idref="h_{translate($fid, ' ', '_')}-quz-{count(preceding::quiz)+1}"/>
  </xsl:template>

  
  <!--
      *************************************************************************
                                       GUIDE
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template guide
      =========================================================================
  -->
  <xsl:template name="guide">
    <guide>
      <xsl:if test="head/cover or ($cover and not($cover='='))">
        <reference type="cover" href="{$fid}-cover{$html_ext}" title="{$i18n_cover}"/>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="$toc">
          <reference type="toc" href="{$fid}-toc{$html_ext}" title="{$i18n_toc}"/>
        </xsl:when>
        <xsl:otherwise>
          <reference type="toc" href="{$fid}-nav{$html_ext}" title="{$i18n_toc}"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select=".//topic" mode="guide"/>
      <xsl:choose>
        <xsl:when test="../quiz or name(.//*[name()='topic' or name()='quiz'])='quiz'">
          <reference type="text" href="{$fid}-quz-1{$html_ext}" title="{$i18n_text}"/>
        </xsl:when>
        <xsl:otherwise>
          <reference type="text" href="{$fid}-tpc-1{$html_ext}" title="{$i18n_text}"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="$index and .//index">
        <reference type="index" href="{$fid}-index{$html_ext}" title="{$i18n_index}"/>
      </xsl:if>
    </guide>
  </xsl:template>

</xsl:stylesheet>
