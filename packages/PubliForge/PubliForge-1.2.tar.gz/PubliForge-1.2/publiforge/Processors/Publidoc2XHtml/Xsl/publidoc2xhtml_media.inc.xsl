<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_media.inc.xsl 96dceb006f15 2014/11/30 19:30:15 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <!--
      =========================================================================
      media
      =========================================================================
  -->
  <xsl:template match="media">
    <xsl:choose>
      <xsl:when test="($img and image) or ($aud and audio) or ($vid and video)">
        <div>
          <xsl:choose>
            <xsl:when test="@xml:id">
              <xsl:attribute name="id">
                <xsl:value-of select="@xml:id"/>
              </xsl:attribute>
            </xsl:when>
            <xsl:when test="head//index">
              <xsl:attribute name="id">
                <xsl:value-of select="concat('med', count(preceding::media))"/>
              </xsl:attribute>
            </xsl:when>
          </xsl:choose>
          <xsl:attribute name="class">
            <xsl:text>pdocMedia</xsl:text>
            <xsl:if test="@type"> pdocMedia-<xsl:value-of select="@type"/></xsl:if>
          </xsl:attribute>
          <xsl:choose>
            <xsl:when test="$vid and video">
              <xsl:apply-templates select="video" mode="media"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="image|audio" mode="media"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:if test="head/title or caption">
            <div class="pdocMediaText">
              <xsl:if test="head/title">
                <div class="pdocMediaTitle">
                  <xsl:call-template name="title"/>
                </div>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <div class="pdocMediaSubtitle">
                  <xsl:call-template name="subtitle"/>
                </div>
              </xsl:if>
              <xsl:apply-templates select="caption"/>
            </div>
          </xsl:if>
        </div>
      </xsl:when>
      <xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="caption">
    <xsl:choose>
      <xsl:when test="@x or @y">
        <div class="pdocMediaCaptionAbsolute">
          <xsl:attribute name="style">
            <xsl:if test="@x">left:<xsl:value-of select="@x"/>;</xsl:if>
            <xsl:if test="@y">top:<xsl:value-of select="@y"/>;</xsl:if>
          </xsl:attribute>
          <xsl:apply-templates/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <div class="pdocMediaCaption"><xsl:apply-templates/></div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      *************************************************************************
                                        IMAGE
      *************************************************************************
  -->
  <!--
      =========================================================================
      image
      =========================================================================
  -->
  <xsl:template match="image">
    <xsl:if test="$img">
      <xsl:call-template name="mid_image"/>
      <img>
        <xsl:attribute name="src">
          <xsl:value-of select="concat($img_dir, @id)"/>
          <xsl:call-template name="image_extension"/>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="@type='thumbnail' or ancestor::right or ancestor::wrong
                          or (ancestor::item and not(ancestor::list))">
            <xsl:attribute name="class">pdocThumbnail</xsl:attribute>
          </xsl:when>
          <xsl:when test="@type='icon' or
                          not(ancestor::media or ancestor::cover
                          or ancestor::hotspot or ancestor::pip or ancestor::dropzone)">
            <xsl:attribute name="class">pdocIcon</xsl:attribute>
          </xsl:when>
        </xsl:choose>
        <xsl:call-template name="image_alt"/>
      </img>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      image mode media
      =========================================================================
  -->
  <xsl:template match="image" mode="media">
    <xsl:if test="$img">
      <div>
        <xsl:attribute name="class">
          <xsl:text>pdocImage</xsl:text>
          <xsl:if test="@type"> pdocImage-<xsl:value-of select="@type"/></xsl:if>
          <xsl:if test="hotspot"> pdocImageHotspot</xsl:if>
          <xsl:if test="dropzone"> pdocImageDropzone</xsl:if>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="../link">
            <a>
              <xsl:apply-templates select="../link" mode="href"/>
              <xsl:call-template name="image_img"/>
            </a>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="image_img"/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:apply-templates select="hotspot|dropzone"/>
        <xsl:if test="copyright">
          <div class="pdocMediaCopyright">
            <xsl:apply-templates select="copyright"/>
          </div>
        </xsl:if>
      </div>
      <xsl:if test="hotspot or dropzone">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      image mode poster
      =========================================================================
  -->
  <xsl:template match="image" mode="poster">
    <xsl:if test="$img and $vid">
      <xsl:attribute name="poster">
        <xsl:value-of select="concat($img_dir, @id)"/>
        <xsl:call-template name="image_extension"/>
      </xsl:attribute>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      hotspot
      =========================================================================
  -->
  <xsl:template match="hotspot">
    <xsl:if test="@display='visible' or link or .//p
                  or ($img and .//image) or ($aud and .//audio)
                  or ($vid and .//video)">
      <!-- Hotspot -->
      <xsl:if test="link or p or ($img and image) or ($aud and audio)
                    or ($vid and video) or @display">
        <div>
          <xsl:attribute name="id">
            <xsl:choose>
              <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('hs', count(preceding::hotspot)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:attribute name="class">
            <xsl:text>pdocHotspot</xsl:text>
            <xsl:if test="@display">
              <xsl:value-of select="concat(' pdocHotspot-', @display)"/>
            </xsl:if>
            <xsl:if test="@type">
              <xsl:value-of select="concat(' pdocHotspot-', @type)"/>
            </xsl:if>
          </xsl:attribute>
          <xsl:attribute name="style">
            <xsl:text>position: absolute; </xsl:text>
            <xsl:value-of select="concat('left:', @x, '; top:', @y, ';')"/>
            <xsl:if test="@w and @w!='0%'">
              <xsl:value-of select="concat(' width:', @w, ';')"/>
            </xsl:if>
            <xsl:if test="@h and not(p or image or video)">
              <xsl:value-of select="concat(' height:', @h, ';')"/>
            </xsl:if>
          </xsl:attribute>

          <xsl:choose>
            <xsl:when test="link">
              <a style="width:100%; height:100%;">
                <xsl:apply-templates select="link" mode="href"/>
                <xsl:apply-templates select="link" mode="content"/>
              </a>
            </xsl:when>
            <xsl:when test="p|image">
              <xsl:apply-templates select="p|image"/>
            </xsl:when>
            <xsl:when test="audio">
              <xsl:call-template name="audio">
                <xsl:with-param name="id" select="audio/@id"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:when test="video">
              <xsl:call-template name="video">
                <xsl:with-param name="id" select="video/@id"/>
                <xsl:with-param name="width" select="$vid_width"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
          </xsl:choose>

          <xsl:if test="@display='pulse' and $js">
            <img class="pdocHotspotPulse" alt="pulse"
                 style="position: absolute; left: 0; top: 0; width: 100%;">
              <xsl:attribute name="src">
                <xsl:call-template name="pulse_gif"/>
              </xsl:attribute>
            </img>
          </xsl:if>

          <xsl:if test="not(link) and @display and $js and scenario/onclick">
            <span style="display: none;">
              <xsl:apply-templates select="scenario/onclick"/>
            </span>
          </xsl:if>
        </div>
      </xsl:if>

      <!-- Spot -->
      <xsl:if test="spot">
        <div>
          <xsl:attribute name="id">
            <xsl:choose>
              <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('hs', count(preceding::hotspot)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
            <xsl:text>s</xsl:text>
          </xsl:attribute>
          <xsl:attribute name="class">
            <xsl:text>pdocHotspotSpot</xsl:text>
            <xsl:if test="scenario/init[@action='hide'] and $js"> hidden</xsl:if>
            <xsl:if test="@display">
              <xsl:value-of select="concat(' pdocHotspotSpot-', @display)"/>
            </xsl:if>
            <xsl:if test="@type">
              <xsl:value-of select="concat(' pdocHotspotSpot-', @type)"/>
            </xsl:if>
          </xsl:attribute>
          <xsl:attribute name="style">
            <xsl:text>position: absolute; </xsl:text>
           <xsl:text>left:</xsl:text>
            <xsl:choose>
              <xsl:when test="spot/@dx">
                <xsl:value-of select="concat(translate(substring-before(@x, '%')
                                      +substring-before(spot/@dx, '%'), ',', '.'), '%')"/>
              </xsl:when>
              <xsl:otherwise><xsl:value-of select="@x"/></xsl:otherwise>
            </xsl:choose>
            <xsl:text>; top:</xsl:text>
            <xsl:choose>
              <xsl:when test="spot/@dy">
                <xsl:value-of select="concat(translate(substring-before(@y, '%')
                                      +substring-before(spot/@dy, '%'), ',', '.'), '%')"/>
              </xsl:when>
              <xsl:otherwise><xsl:value-of select="@y"/></xsl:otherwise>
            </xsl:choose>
            <xsl:if test="@w and @w!='0%' and not(spot/p)">
              <xsl:text>; width:</xsl:text>
              <xsl:choose>
                <xsl:when test="spot/@dw">
                  <xsl:value-of select="concat(translate(substring-before(@w, '%')
                                        +substring-before(spot/@dw, '%'), ',', '.'), '%')"/>
                </xsl:when>
                <xsl:otherwise><xsl:value-of select="@w"/></xsl:otherwise>
              </xsl:choose>
            </xsl:if>
            <xsl:text>;</xsl:text>
          </xsl:attribute>

          <xsl:choose>
            <xsl:when test="spot/audio">
              <xsl:call-template name="audio">
                <xsl:with-param name="id" select="spot/audio/@id"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:when test="spot/video">
              <xsl:call-template name="video">
                <xsl:with-param name="id" select="spot/video/@id"/>
                <xsl:with-param name="width" select="$vid_width"/>
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="spot"/>
            </xsl:otherwise>
          </xsl:choose>
        </div>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="scenario"/>

  <xsl:template match="onclick">
    <xsl:value-of select="@action"/><xsl:text>; </xsl:text>
  </xsl:template>

  <xsl:template name="pulse_gif">
    <xsl:value-of select="concat($img_dir, 'pulse.gif')"/>
  </xsl:template>


  <!--
      *************************************************************************
                                        AUDIO
      *************************************************************************
  -->
  <!--
      =========================================================================
      audio
      =========================================================================
  -->
  <xsl:template match="audio">
    <xsl:if test="$aud">
      <xsl:call-template name="audio"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="audio" mode="media">
    <xsl:if test="$aud">
      <xsl:choose>
        <xsl:when test="@type='background'">
          <xsl:call-template name="audio">
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="autoplay" select="1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise><xsl:call-template name="audio"/></xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="audio" mode="header">
    <xsl:if test="$aud and @type='background'">
      <xsl:call-template name="audio">
        <xsl:with-param name="controls" select="0"/>
        <xsl:with-param name="autoplay" select="1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                        VIDEO
      *************************************************************************
  -->
  <!--
      =========================================================================
      video
      =========================================================================
  -->
  <xsl:template match="video" mode="media">
    <xsl:if test="$vid">
      <xsl:call-template name="video">
        <!-- <xsl:with-param name="width" select="$vid_width"/> -->
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
