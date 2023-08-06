<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2html5_ini.inc.xsl 3c9dd6aef086 2014/09/07 08:47:17 Patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      This XSL creates INI files for LePrisme module.

      Cf. publidoc2xhtml_ini.inc.xsl
      =========================================================================
  -->

  <!--
      *************************************************************************
                                        AUDIO
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template audio_ini
      =========================================================================
  -->
  <xsl:template name="audio_ini">
    <xsl:param name="id" select="@id"/>
    <xsl:document
        href="{$path}{$fid}-aud{format-number(count(preceding::audio)+count(preceding::smil)+1, '0000')}~.ini"
        method="text" encoding="utf-8">
[Source]
type = audio
id = <xsl:value-of select="$id"/>
search = <xsl:value-of select="$aud_search"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($aud_dir, $id, $aud_ext1)"/>
dependencies = <xsl:call-template name="audio_dependencies"/>
relations = <xsl:call-template name="audio_relations"/>

[Transformation]
<xsl:choose>
  <xsl:when test="$aud_ext1='.ogg'">
step.1 = nice avconv -i "%(source)s" -acodec libvorbis -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext1='.aac' or $aud_ext1='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -ab 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$aud_ext2!='-' and $aud_ext1!=$aud_ext2">
  <xsl:choose>
    <xsl:when test="$aud_ext2='.ogg'">
step.2 = nice avconv -i "%(source)s" -acodec libvorbis -ab 128k
         -y "%(targetpath)s/%(id)s.ogg"
    </xsl:when>
    <xsl:when test="$aud_ext2='.aac' or $aud_ext2='.m4a'">
step.2 = nice avconv -i "%(source)s" -strict experimental -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>

[Transformation:ogg]
<xsl:choose>
  <xsl:when test="$aud_ext1='.ogg'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext1='.aac' or $aud_ext1='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -ab 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$aud_ext2!='-' and $aud_ext1!=$aud_ext2">
  <xsl:choose>
    <xsl:when test="$aud_ext2='.ogg'">
step.2 = nice avconv -i "%(source)s" -acodec libvorbis -ab 128k
         -y "%(targetpath)s/%(id)s.ogg"
    </xsl:when>
    <xsl:when test="$aud_ext2='.aac' or $aud_ext2='.m4a'">
step.2 = nice avconv -i "%(source)s" -strict experimental -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>

[Transformation:aac]
<xsl:choose>
  <xsl:when test="$aud_ext1='.ogg'">
step.1 = nice avconv -i "%(source)s" -acodec libvorbis -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext1='.aac'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext1='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -ab 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$aud_ext2!='-' and $aud_ext1!=$aud_ext2">
  <xsl:choose>
    <xsl:when test="$aud_ext2='.ogg'">
step.2 = nice avconv -i "%(source)s" -acodec libvorbis -ab 128k
         -y "%(targetpath)s/%(id)s.ogg"
    </xsl:when>
    <xsl:when test="$aud_ext2='.aac' or $aud_ext2='.m4a'">
step.2 = nice avconv -i "%(source)s" -strict experimental -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -ab 128k
         -y "%(targetpath)s/%(id)s<xsl:value-of select="$aud_ext2"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>
    </xsl:document>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_relations
      =========================================================================
  -->
  <xsl:template name="audio_relations">
    <xsl:if test="$aud_ext2!='-' and $aud_ext1!=$aud_ext2">
      <xsl:value-of select="concat('%(targetpath)s/%(id)s', $aud_ext2)"/>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
