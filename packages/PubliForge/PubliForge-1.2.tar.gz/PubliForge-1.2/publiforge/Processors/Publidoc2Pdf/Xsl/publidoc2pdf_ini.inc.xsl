<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2pdf_ini.inc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      This XSL creates INI files for LePrisme module.

      Cf. publidoc2xhtml_ini.inc.xsl
      =========================================================================
  -->

  <!--
      *************************************************************************
                                          IMAGE
      *************************************************************************
  -->
  <!--
      =========================================================================
      image mode ini
      =========================================================================
  -->
  <xsl:template match="image" mode="ini">
    <xsl:if test="$img">
      <xsl:document
          href="{$path}{$fid}-img{format-number(count(preceding::image)+1, '0000')}-{count(ancestor::image)}~.ini"
          method="text" encoding="utf-8">
[Source]
type = image
id = <xsl:value-of select="@id"/>
search = <xsl:value-of select="$img_search"/>

[Target]
file = %(here)s/<xsl:value-of select="translate(concat($img_dir, @id, '.pdf'), '_', '-')"/>
dependencies = <xsl:call-template name="image_dependencies"/>
relations = <xsl:call-template name="image_relations"/>

[Transformation]
step.1 = nice convert "%(source)s" "%(target)s"

[Transformation:eps]
step.1 = nice inkscape -z -f "%(source)s" -A "%(target)s"

[Transformation:svg]
step.1 = nice inkscape -z -f "%(source)s" -A "%(target)s"
      </xsl:document>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template image_dependencies
      =========================================================================
  -->
  <xsl:template name="image_dependencies">%(source)s</xsl:template>

  <!--
      =========================================================================
      Template image_relations
      =========================================================================
  -->
  <xsl:template name="image_relations"/>


  <!--
      *************************************************************************
                                          POST
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template post_ini
      =========================================================================
  -->
  <xsl:template name="post_ini">
    <xsl:document href="{$path}{$fid}~.ini" method="text" encoding="utf-8">
[Transformation]
step.1 = nice lualatex --interaction=nonstopmode --halt-on-error
         <xsl:value-of select="$fid"/>.tmp.tex
<xsl:if test="$toc_depth!='-1'">
step.2 = nice lualatex --interaction=nonstopmode --halt-on-error
         <xsl:value-of select="$fid"/>.tmp.tex
step.3 = nice lualatex --interaction=nonstopmode --halt-on-error
         <xsl:value-of select="$fid"/>.tmp.tex
</xsl:if>
step.4 = mv <xsl:value-of select="$fid"/>.tmp.pdf %(target)s
    </xsl:document>
  </xsl:template>
</xsl:stylesheet>
