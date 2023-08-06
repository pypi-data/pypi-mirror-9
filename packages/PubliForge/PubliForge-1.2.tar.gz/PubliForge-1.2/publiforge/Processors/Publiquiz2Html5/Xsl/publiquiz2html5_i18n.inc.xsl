<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiquiz2html5_i18n.inc.xsl ee9da323210e 2015/02/13 16:10:39 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_help">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Aide</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ayuda</xsl:when>
      <xsl:otherwise>Help</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_answer">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Réponse</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Respuesta</xsl:when>
      <xsl:otherwise>Answer</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_user_answer">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Voir la réponse donnée</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ver la respuesta dada</xsl:when>
      <xsl:otherwise>Display the user answer</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_right_answer">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Voir la réponse correcte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ver la respuesta correcta</xsl:when>
      <xsl:otherwise>Display the right answer</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_retry">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Recommencer</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Reintentar</xsl:when>
      <xsl:otherwise>Retry</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_validate">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Valider</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Validar</xsl:when>
      <xsl:otherwise>Validate</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_true">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">VRAI</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">VERDA</xsl:when>
      <xsl:otherwise>TRUE</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_false">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">FAUX</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">FALSO</xsl:when>
      <xsl:otherwise>FALSE</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_congratulate1">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">[100-100]Bravo !|Félicitations !|Parfait !</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">[100-100]¡Bien Hecho!|¡Felicitaciones!|¡Qué bueno!</xsl:when>
      <xsl:otherwise>[100-100]Well done!|Congratulations!|Great!</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_congratulate2">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">[91-99]Très peu d'erreurs.</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">[91-99]Muy poco errores.</xsl:when>
      <xsl:otherwise>[91-99]Very few errors.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_congratulate3">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">[51-90]Quelques erreurs.</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">[51-90]Algunos errores.</xsl:when>
      <xsl:otherwise>[51-90]Some errors.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_congratulate4">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">[1-50]Trop d'erreurs.</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">[1-50]Demasiados errores.</xsl:when>
      <xsl:otherwise>[1-50]Too many errors.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_congratulate5"/>
  <xsl:variable name="i18n_congratulate6"/>

</xsl:stylesheet>
