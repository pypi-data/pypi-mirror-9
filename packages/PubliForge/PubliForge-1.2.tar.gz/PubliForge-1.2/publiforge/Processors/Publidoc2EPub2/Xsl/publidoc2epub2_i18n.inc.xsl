<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2epub2_i18n.inc.xsl 191291cfed6e 2014/03/30 18:01:09 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_guide">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Guide</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Guía</xsl:when>
      <xsl:otherwise>Guide</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_notes">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Notes</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Notas</xsl:when>
      <xsl:otherwise>Notes</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_text">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Texte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Texto</xsl:when>
      <xsl:otherwise>Text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_corpus">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Corpus</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Corpus</xsl:when>
      <xsl:otherwise>Corpus</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
