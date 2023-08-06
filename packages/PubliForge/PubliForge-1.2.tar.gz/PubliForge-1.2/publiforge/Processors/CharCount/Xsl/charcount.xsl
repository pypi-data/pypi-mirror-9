<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: charcount.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->


  <xsl:output method="text" encoding="utf-8"/>


  <!--
      =========================================================================
      /
      =========================================================================
  -->
  <xsl:template match="/">
    <xsl:variable name="num"
                  select="string-length(normalize-space())"/>
    <xsl:value-of
        select="concat(substring('          ', 1, 10-string-length($num)),
                $num, ' (', $fid, ')')"/>
  </xsl:template>
</xsl:stylesheet>
