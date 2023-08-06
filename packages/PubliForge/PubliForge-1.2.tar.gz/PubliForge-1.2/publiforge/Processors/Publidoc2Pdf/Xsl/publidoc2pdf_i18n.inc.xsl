<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2pdf_i18n.inc.xsl 66c4a347e805 2013/04/07 15:05:09 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_bibliography">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Bibliographie</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Bibliografía</xsl:when>
      <xsl:otherwise>Bibliography</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
</xsl:stylesheet>
