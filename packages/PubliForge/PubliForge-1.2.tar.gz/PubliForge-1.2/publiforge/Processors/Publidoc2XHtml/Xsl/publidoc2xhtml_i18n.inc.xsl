<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_i18n.inc.xsl 16ffbcb174f8 2014/12/16 16:22:03 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_type">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Type</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Tipo</xsl:when>
      <xsl:otherwise>Type</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_language">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Langue</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Idioma</xsl:when>
      <xsl:otherwise>Language</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_title">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Título</xsl:when>
      <xsl:otherwise>title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_shorttitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre court</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Título corto</xsl:when>
      <xsl:otherwise>Short title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subtitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sous-titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Subtítulo</xsl:when>
      <xsl:otherwise>Subtitle</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_identifier">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Identifiant</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Identificador</xsl:when>
      <xsl:otherwise>Identifier</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_copyright">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Copyright</xsl:when>
      <xsl:otherwise>Copyright</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_dedication">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Dédicace</xsl:when>
      <xsl:otherwise>Dedication</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_inscription">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Exergue</xsl:when>
      <xsl:otherwise>Inscription</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_collection">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Collection</xsl:when>
      <xsl:otherwise>Collection</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_contributors">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Contributeurs</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Contributors</xsl:when>
      <xsl:otherwise>Contributors</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_date">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Date</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Fecha</xsl:when>
      <xsl:otherwise>Date</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_place">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Lieu</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Lugar</xsl:when>
      <xsl:otherwise>Place</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_source">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Source</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Origen</xsl:when>
      <xsl:otherwise>Source</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subjects">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Thèmes</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Temas</xsl:when>
      <xsl:otherwise>Subjects</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_keywords">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Mots clés</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Palabras llaves</xsl:when>
      <xsl:otherwise>Keywords</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_abstract">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Résumé</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Resumen</xsl:when>
      <xsl:otherwise>Abstract</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_annotation">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Annotation</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Anotación</xsl:when>
      <xsl:otherwise>Annotation</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_cover">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Couverture</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Cobertura</xsl:when>
      <xsl:otherwise>Cover</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_toc">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sommaire</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Tabla de contenidos</xsl:when>
      <xsl:otherwise>Table of Contents</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_title_page">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Page de titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Página de título</xsl:when>
      <xsl:otherwise>Title Page</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_note">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Note</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Notas</xsl:when>
      <xsl:otherwise>Note</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_back">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Retour au texte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Volver al texto</xsl:when>
      <xsl:otherwise>Back to the text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_bibliography">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Bibliographie</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Bibliografía</xsl:when>
      <xsl:otherwise>Bibliography</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_index">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Index</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Índice</xsl:when>
      <xsl:otherwise>Index</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_noaudio">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Votre navigateur ne supporte pas la balise audio.</xsl:when>
      <xsl:otherwise>Your browser does not support the audio tag.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_novideo">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Votre navigateur ne supporte pas la vidéo HTML5.</xsl:when>
      <xsl:otherwise>Your browser does not support HTML5 video.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_listen">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Écoutez</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Escuche</xsl:when>
      <xsl:otherwise>Listen</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_nocanvas">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Balise &lt;canvas&gt; non supportée</xsl:when>
      <xsl:otherwise>&lt;canvas&gt; tag not supported</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
</xsl:stylesheet>
