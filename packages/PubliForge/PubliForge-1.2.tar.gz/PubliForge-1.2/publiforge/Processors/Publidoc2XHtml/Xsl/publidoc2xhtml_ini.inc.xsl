<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_ini.inc.xsl 842d5adb3a8c 2015/02/03 18:17:00 Patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      This XSL creates INI files for LePrisme module.

      For post processing section is:

      * [Transformation]

      with special strings:

      * %(here)s = full path to INI file
      * %(bin)s = full path to PubliForge binaries
      * %(output)s = full path to the output directory
      * %(processor)s = full path to the processor directory
      * %(donetag)s = tag to mark the used files
      * %(lang)s = language of the current user
      * %(target)s = full path to target file

      For media (image, audio, video) processing, sections are:

      * [Source]
      * [Target]
      * [Transformation]
      * [Transformation:<source_extension>]

      with additional special strings:

      * %(stgpath)s = full path to the storage root directory
      * %(filepath)s = full path to the processed file directory
      * %(ext)s = one of possible extensions for the source file
      * %(id)s = source ID
      * %(source)s = full path to source file
      * %(sourcepath)s = full path to source directory
      * %(targetpath)s = full path to target directory
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
    <xsl:if test="$img or name(..)='cover'">
      <xsl:call-template name="image_ini">
        <xsl:with-param name="size">
          <xsl:call-template name="image_size"/>
        </xsl:with-param>
        <xsl:with-param name="ext">
          <xsl:call-template name="image_extension"/>
        </xsl:with-param>
      </xsl:call-template>
      <xsl:call-template name="image_extra"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="image_extra"/>

  <!--
      =========================================================================
      Template image_ini
      =========================================================================
  -->
  <xsl:template name="image_ini">
    <xsl:param name="id" select="@id"/>
    <xsl:param name="size"/>
    <xsl:param name="ext" select="$img_ext"/>
    <xsl:param name="ext2" select="substring-after($img_ext, '+')"/>
    <xsl:param name="idx" select="count(ancestor::image)"/>
    <xsl:param name="target"
               select="concat('%(here)s/', $img_dir, $id, $ext)"/>
    <xsl:document
        href="{$path}{$fid}-img{format-number(count(preceding::image)+1, '0000')}-{$idx}~.ini"
        method="text" encoding="utf-8">
[Source]
type = image
id = <xsl:value-of select="$id"/>
search = <xsl:value-of select="$img_search"/>

[Target]
file = <xsl:value-of select="$target"/>
dependencies = <xsl:call-template name="image_dependencies">
                 <xsl:with-param name="ext" select="$ext"/>
                 <xsl:with-param name="ext2" select="$ext2"/>
               </xsl:call-template>
relations = <xsl:call-template name="image_relations">
              <xsl:with-param name="ext" select="$ext"/>
              <xsl:with-param name="ext2" select="$ext2"/>
            </xsl:call-template>

[Transformation]
<xsl:choose>
<xsl:when test="$ext='.png'">
step.1 = nice convert "%(source)s" -strip -quality 100
         -geometry <xsl:value-of select="$size"/> "%(target)s"
<xsl:if test="$img_optimize">
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> "%(target)s"
step.3 = nice advpng -z -q -4 "%(target)s"
</xsl:if>
</xsl:when>
<xsl:when test="$ext='.jpg' or $ext='.jpeg'">
step.1 = nice convert "%(source)s" -strip
         -quality <xsl:value-of select="$img_quality"/>
         -geometry <xsl:value-of select="$size"/> "%(target)s"
<xsl:if test="$img_optimize">
step.2 = nice jpegoptim -q "%(target)s"
</xsl:if>
</xsl:when>
<xsl:when test="$ext='.svg' and $ext2">
step.1 = %(bin)s/pfimage2svg "%(source)s" "%(target)s" --lang %(lang)s
         --size <xsl:value-of select="$size"/>
         --bitmap <xsl:value-of select="substring($ext2, 2)"/>
</xsl:when>
<xsl:when test="$ext='.svg'">
step.1 = %(bin)s/pfimage2svg "%(source)s" "%(target)s" --lang %(lang)s
         --size <xsl:value-of select="$size"/>
</xsl:when>
<xsl:otherwise>
step.1 = nice convert "%(source)s" -strip
         -geometry <xsl:value-of select="$size"/> "%(target)s"
</xsl:otherwise>
</xsl:choose>

[Transformation:eps]
step.1 = nice convert -density 300 "%(source)s" -colorspace RGB -strip
         -geometry <xsl:value-of select="$size"/> "%(target)s"
<xsl:if test="$ext='.png' and $img_optimize">
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> "%(target)s"
step.3 = nice advpng -z -q -4 "%(target)s"
</xsl:if>
<xsl:if test="$ext='.jpg' and $img_optimize">
step.2 = nice jpegoptim -q "%(target)s"
</xsl:if>

   </xsl:document>
  </xsl:template>

  <!--
      =========================================================================
      Template image_dependencies
      =========================================================================
  -->
  <xsl:template name="image_dependencies">
    <xsl:param name="ext" select="$img_ext"/>
    <xsl:param name="ext2" select="substring-after($img_ext, '+')"/>
    <xsl:choose>
      <xsl:when test="$ext='.svg' and $ext2">
        <xsl:text>%(sourcepath)s/%(id)s*</xsl:text>
      </xsl:when>
      <xsl:otherwise>%(source)s</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template image_relations
      =========================================================================
  -->
  <xsl:template name="image_relations">
    <xsl:param name="ext" select="$img_ext"/>
    <xsl:param name="ext2" select="substring-after($img_ext, '+')"/>
    <xsl:choose>
      <xsl:when test="$ext='.svg' and $ext2='.png'">
        <xsl:text>%(targetpath)s/%(id)s.svg.png</xsl:text>
      </xsl:when>
      <xsl:when test="$ext='.svg' and $ext2='.jpg'">
        <xsl:text>%(targetpath)s/%(id)s.svg.jpg</xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


  <!--
      *************************************************************************
                                        AUDIO
      *************************************************************************
  -->
  <!--
      =========================================================================
      audio mode ini
      =========================================================================
  -->
  <xsl:template match="audio" mode="ini">
    <xsl:if test="$aud">
      <xsl:call-template name="audio_ini"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      smil mode ini
      =========================================================================
  -->
  <xsl:template match="smil" mode="ini">
    <xsl:if test="$aud and @audio">
      <xsl:call-template name="audio_ini">
        <xsl:with-param name="id" select="@audio"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_ini
      =========================================================================
  -->
  <xsl:template name="audio_ini">
    <xsl:param name="id" select="@id"/>
    <xsl:document
        href="{$path}{$fid}-aud{format-number(count(preceding::audio|preceding::smil)+1, '0000')}~.ini"
        method="text" encoding="utf-8">
[Source]
type = audio
id = <xsl:value-of select="$id"/>
search = <xsl:value-of select="$aud_search"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($aud_dir, $id, $aud_ext)"/>
dependencies = <xsl:call-template name="audio_dependencies"/>
relations = <xsl:call-template name="audio_relations"/>

[Transformation]
<xsl:choose>
  <xsl:when test="$aud_ext='.ogg'">
step.1 = nice avconv -i "%(source)s" -codec:a libvorbis -b:a 128k -y "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext='.aac' or $aud_ext='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -b:a 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -b:a 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>

[Transformation:ogg]
<xsl:choose>
  <xsl:when test="$aud_ext='.ogg'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext='.aac' or $aud_ext='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -b:a 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -b:a 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>

[Transformation:aac]
<xsl:choose>
  <xsl:when test="$aud_ext='.ogg'">
step.1 = nice avconv -i "%(source)s" -codec:a libvorbis -b:a 128k -y "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext='.aac'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext='.m4a'">
step.1 = nice avconv -i "%(source)s" -strict experimental -b:a 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -b:a 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>

    </xsl:document>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_dependencies
      =========================================================================
  -->
  <xsl:template name="audio_dependencies">%(source)s</xsl:template>

  <!--
      =========================================================================
      Template audio_relations
      =========================================================================
  -->
  <xsl:template name="audio_relations"/>


  <!--
      *************************************************************************
                                        VIDEO
      *************************************************************************
  -->
  <!--
      =========================================================================
      video mode ini
      =========================================================================
  -->
  <xsl:template match="video" mode="ini">
    <xsl:if test="$vid">
      <xsl:call-template name="video_ini"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template video_ini
      =========================================================================
  -->
  <xsl:template name="video_ini">
    <xsl:param name="id" select="@id"/>
    <xsl:document
        href="{$path}{$fid}-vid{format-number(count(preceding::video)+1, '0000')}~.ini"
        method="text" encoding="utf-8">
[Source]
type = video
id = <xsl:value-of select="$id"/>
search = <xsl:value-of select="$vid_search"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($vid_dir, $id, $vid_ext1)"/>
dependencies = <xsl:call-template name="video_dependencies"/>
relations = <xsl:call-template name="video_relations"/>

[Transformation]
<xsl:choose>
  <xsl:when test="$vid_ext1='.mp4'">
step.1 = nice avconv -i "%(source)s" -q:v 1 -y "%(target)s"
  </xsl:when>
  <xsl:when test="$vid_ext1='.ogv'">
step.1 = nice avconv -i "%(source)s" -codec:a libvorbis -q:v 10 -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$vid_ext2!='-' and $vid_ext1!=$vid_ext2">
  <xsl:choose>
    <xsl:when test="$vid_ext2='.mp4'">
step.2 = nice avconv -i "%(source)s" -q:v 1 -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:when test="$vid_ext2='.ogv'">
step.2 = nice avconv -i "%(source)s" -codec:a libvorbis -q:v 10 -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -y "%(target)s"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>

[Transformation:mp4]
<xsl:choose>
  <xsl:when test="$vid_ext1='.mp4'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:when test="$vid_ext1='.ogv'">
step.1 = nice avconv -i "%(source)s" -codec:a libvorbis -q:v 10 -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$vid_ext2!='-' and $vid_ext1!=$vid_ext2">
  <xsl:choose>
    <xsl:when test="$vid_ext2='.mp4'">
step.2 = nice cp "%(source)s"
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:when test="$vid_ext2='.ogv'">
step.2 = nice avconv -i "%(source)s" -codec:a libvorbis -q:v 10 -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>

[Transformation:ogv]
<xsl:choose>
  <xsl:when test="$vid_ext1='.mp4'">
step.1 = nice avconv -i "%(source)s" -q:v 1 -y "%(target)s"
  </xsl:when>
  <xsl:when test="$vid_ext1='.ogv'">
step.1 = nice cp "%(source)s" "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice avconv -i "%(source)s" -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>
<xsl:if test="$vid_ext2!='-' and $vid_ext1!=$vid_ext2">
  <xsl:choose>
    <xsl:when test="$vid_ext2='.mp4'">
step.2 = nice avconv -i "%(source)s" -q:v 1 -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:when test="$vid_ext2='.ogv'">
step.2 = nice cp "%(source)s"
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice avconv -i "%(source)s" -y
         "%(targetpath)s/%(id)s<xsl:value-of select="$vid_ext2"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>
    </xsl:document>
  </xsl:template>

  <!--
      =========================================================================
      Template video_dependencies
      =========================================================================
  -->
  <xsl:template name="video_dependencies">%(source)s</xsl:template>

  <!--
      =========================================================================
      Template audio_relations
      =========================================================================
  -->
  <xsl:template name="video_relations">
    <xsl:if test="$vid_ext2!='-' and $vid_ext1!=$vid_ext2">
      <xsl:value-of select="concat('%(targetpath)s/%(id)s', $vid_ext2)"/>
    </xsl:if>
  </xsl:template>


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
    <xsl:if test=".//math/latex or $minify">
      <xsl:document href="{$output}{$fid}~.ini" method="text" encoding="utf-8">
[Transformation]
<xsl:if test=".//math/latex">
step.1 = %(bin)s/pftexmath <xsl:value-of select="$fid"/>
         <xsl:value-of select="concat(' ', $path)"/>
         --output <xsl:value-of select="concat($path, $math_dir)"/>
         --mode <xsl:value-of select="$math_mode"/>
         --factor <xsl:value-of select="$math_factor"/>
         --done-tag %(donetag)s_
         --lang %(lang)s
</xsl:if>
<xsl:if test="$minify">
step.2 = %(bin)s/pfminify
         <xsl:value-of select="concat($path, $css_dir, 'styles.css')"/>
         <xsl:if test="$js">
           <xsl:text>
         </xsl:text>
           <xsl:value-of select="concat($path, $js_dir, 'scripts.js')"/>
         </xsl:if>
         --lang %(lang)s
</xsl:if>
      </xsl:document>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
