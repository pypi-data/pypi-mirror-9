<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2dtbook_base.inc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.daisy.org/z3986/2005/dtbook/">

  <!--
      *************************************************************************
                                      HEAD LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      contributor mode head
      =========================================================================
  -->
  <xsl:template match="contributor" mode="head">
    <xsl:if test="role='author'">
      <meta name="dc:Creator">
        <xsl:attribute name="content">
          <xsl:value-of select="normalize-space(firstname)"/>
          <xsl:if test="firstname"><xsl:text> </xsl:text></xsl:if>
          <xsl:value-of select="normalize-space(lastname|label)"/>
        </xsl:attribute>
      </meta>
    </xsl:if>
    <xsl:if test="role='publisher'">
      <meta name="dc:Publisher" content="{normalize-space(label)}"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      contributor mode frontmatter
      =========================================================================
  -->
  <xsl:template match="contributor" mode="frontmatter">
    <xsl:if test="role='author'">
      <docauthor>
        <xsl:apply-templates select="firstname"/>
        <xsl:if test="firstname"><xsl:text> </xsl:text></xsl:if>
        <xsl:apply-templates select="lastname|label"/>
      </docauthor>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      subject mode head
      =========================================================================
  -->
  <xsl:template match="subject" mode="head">
    <meta name="dc:Subject" content="{normalize-space()}"/>
  </xsl:template>


  <!--
      *************************************************************************
                                    DIVISION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      division mode onefile
      =========================================================================
  -->
  <xsl:template match="division" mode="onefile">
    <xsl:choose>
      <xsl:when test="count(ancestor::division)=0">
        <xsl:comment> ================================================================ </xsl:comment>
      </xsl:when>
      <xsl:when test="count(ancestor::division)=1">
        <xsl:comment> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ </xsl:comment>
      </xsl:when>
    </xsl:choose>
    <level>
      <xsl:call-template name="level_attrs"/>
      <xsl:call-template name="level_hd"/>
      <xsl:apply-templates select="division|front|topic" mode="onefile"/>
    </level>
  </xsl:template>


  <!--
      *************************************************************************
                                    COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      front mode onefile
      =========================================================================
  -->
  <xsl:template match="front" mode="onefile">
    <level class="front">
      <xsl:apply-templates select="section"/>
    </level>
  </xsl:template>

  <!--
      =========================================================================
      topic mode onefile
      =========================================================================
  -->
  <xsl:template match="topic" mode="onefile">
    <xsl:choose>
      <xsl:when test="count(ancestor::division)=0">
        <xsl:comment> ================================================================ </xsl:comment>
      </xsl:when>
      <xsl:when test="count(ancestor::division)=1">
        <xsl:comment> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ </xsl:comment>
      </xsl:when>
      <xsl:when test="count(ancestor::division)=2">
        <xsl:comment> ............................................................ </xsl:comment>
      </xsl:when>
    </xsl:choose>
    <level>
      <xsl:call-template name="level_attrs"/>
      <xsl:call-template name="level_hd"/>
      <xsl:apply-templates select="." mode="corpus"/>
    </level>
  </xsl:template>

  <!--
      =========================================================================
      topic mode corpus
      =========================================================================
  -->
  <xsl:template match="topic" mode="corpus">
    <xsl:apply-templates select="section"/>
    <!-- <xsl:apply-templates select="bibliography"/> -->
  </xsl:template>


  <!--
      *************************************************************************
                                     SECTION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      section
      =========================================================================
  -->
  <xsl:template match="section">
    <level>
      <xsl:call-template name="level_attrs"/>
      <xsl:call-template name="level_hd"/>
      <xsl:apply-templates
          select="section|p|list|blockquote|speech|table|media"/>
      <xsl:apply-templates
          select="p//note|list//note|blockquote//note|speech//note
                  |table//note|media//note"
          mode="note"/>
    </level>
  </xsl:template>


  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      p
      =========================================================================
  -->
  <xsl:template match="p">
    <p><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="p" mode="speech">
    <line><xsl:apply-templates/></line>
  </xsl:template>

  <!--
      =========================================================================
      list
      =========================================================================
  -->
  <xsl:template match="list">
    <list>
      <xsl:attribute name="type">
        <xsl:choose>
          <xsl:when test="@type='ordered'">ol</xsl:when>
          <xsl:when test="@type='glossary'">pl</xsl:when>
          <xsl:otherwise>ul</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:call-template name="level_hd"/>
      <xsl:apply-templates select="item"/>
    </list>
  </xsl:template>

  <xsl:template match="item">
    <li>
      <xsl:choose>
        <xsl:when test="label">
          <p class="label"><xsl:apply-templates select="label"/></p>
          <xsl:apply-templates select="*[name()!='label']"/>
        </xsl:when>
        <xsl:when test="p|list|blockquote|speech|table|media">
          <xsl:apply-templates select="*"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </li>
  </xsl:template>

  <!--
      =========================================================================
      blockquote
      =========================================================================
  -->
  <xsl:template match="blockquote">
    <blockquote>
      <xsl:call-template name="class_attr"/>
      <xsl:choose>
        <xsl:when test="head/title">
          <div>
            <doctitle>
              <xsl:apply-templates select="head/title"/>
              <xsl:call-template name="subtitle"/>
            </doctitle>
            <xsl:apply-templates select="p|speech|list|attribution"/>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="p|speech|list|attribution"/>
        </xsl:otherwise>
      </xsl:choose>
    </blockquote>
  </xsl:template>

  <xsl:template match="blockquote" mode="speech">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <xsl:template match="attribution">
    <xsl:choose>
      <xsl:when test="ancestor::blockquote">
        <p class="attribution"><xsl:apply-templates/></p>
      </xsl:when>
      <xsl:otherwise>
        <span class="attribution"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      speech
      =========================================================================
  -->
  <xsl:template match="speech">
    <linegroup>
      <xsl:if test="speaker">
        <byline><xsl:apply-templates select="speaker"/></byline>
      </xsl:if>
      <xsl:apply-templates select="stage" mode="speech"/>
      <xsl:apply-templates select="p|blockquote" mode="speech"/>
    </linegroup>
  </xsl:template>

  <!--
      =========================================================================
      table
      =========================================================================
  -->
  <xsl:template match="table">
    <xsl:choose>
      <xsl:when test="head/title">
        <div>
          <xsl:call-template name="doctitle"/>
          <xsl:call-template name="table"/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="table"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="table">
    <xsl:choose>
      <xsl:when test="tgroup">
        <xsl:apply-templates select="tgroup"/>
      </xsl:when>
      <xsl:otherwise>
        <table>
          <xsl:call-template name="class_attr"/>
          <xsl:apply-templates select="caption"/>
          <xsl:apply-templates select="thead|tbody|tr"/>
        </table>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="tgroup">
    <table>
      <xsl:if test="../@type">
        <xsl:attribute name="class">
          <xsl:value-of select="../@type"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="../caption"/>
      <xsl:apply-templates select="thead|tbody"/>
    </table>
  </xsl:template>

  <xsl:template match="thead">
    <thead><xsl:apply-templates select="row|tr"/></thead>
  </xsl:template>

  <xsl:template match="tbody">
    <tbody><xsl:apply-templates select="row|tr"/></tbody>
  </xsl:template>

  <xsl:template match="row">
    <tr>
      <xsl:copy-of select="@valign"/>
      <xsl:apply-templates select="entry" mode="td"/>
    </tr>
  </xsl:template>

  <xsl:template match="tr">
    <tr>
      <xsl:copy-of select="@align|@valign"/>
      <xsl:call-template name="class_attr"/>
      <xsl:apply-templates select="th|td"/>
    </tr>
  </xsl:template>

  <xsl:template match="entry" mode="td">
    <xsl:choose>
      <xsl:when test="ancestor::thead">
        <th>
          <xsl:copy-of select="@align|@valign"/>
          <xsl:apply-templates/>
        </th>
      </xsl:when>
      <xsl:otherwise>
        <td>
          <xsl:copy-of select="@align|@valign"/>
          <xsl:apply-templates/>
        </td>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="th">
    <th>
      <xsl:copy-of select="@align|@valign|@colspan|@rowspan"/>
      <xsl:call-template name="class_attr"/>
      <xsl:apply-templates/>
    </th>
  </xsl:template>

  <xsl:template match="td">
    <td>
      <xsl:copy-of select="@align|@valign|@colspan|@rowspan"/>
      <xsl:call-template name="class_attr"/>
      <xsl:apply-templates/>
    </td>
  </xsl:template>

  <!--
      =========================================================================
      caption
      =========================================================================
  -->
  <xsl:template match="caption">
    <caption><xsl:apply-templates/></caption>
  </xsl:template>

  <!--
      =========================================================================
      media
      =========================================================================
  -->
  <xsl:template match="media">
    <xsl:choose>
      <xsl:when test="head/title">
        <div>
          <xsl:call-template name="doctitle"/>
          <xsl:call-template name="media"/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="media"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="media">
    <xsl:choose>
      <xsl:when test="link">
        <a href="{link/@uri|link/@href}">
          <imggroup>
            <xsl:call-template name="id_attr"/>
            <xsl:call-template name="class_attr"/>
            <xsl:apply-templates select="image|audio|video" mode="media"/>
            <xsl:apply-templates select="caption"/>
          </imggroup>
        </a>
      </xsl:when>
      <xsl:otherwise>
        <imggroup>
          <xsl:call-template name="id_attr"/>
          <xsl:call-template name="class_attr"/>
          <xsl:apply-templates select="image|audio|video" mode="media"/>
          <xsl:apply-templates select="caption"/>
        </imggroup>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      image
      =========================================================================
  -->
  <xsl:template match="image">
    <img>
      <xsl:attribute name="src">
        <xsl:value-of select="concat($img_dir, @id)"/>
        <xsl:call-template name="image_extension"/>
      </xsl:attribute>
      <xsl:call-template name="image_alt"/>
      <xsl:attribute name="class">
        <xsl:choose>
          <xsl:when test="@type">
            <xsl:value-of select="@type"/>
          </xsl:when>
          <xsl:otherwise>icon</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
    </img>
  </xsl:template>

  <!--
      =========================================================================
      image mode media
      =========================================================================
  -->
  <xsl:template match="image" mode="media">
    <img>
      <xsl:attribute name="src">
        <xsl:value-of select="concat($img_dir, @id)"/>
        <xsl:call-template name="image_extension"/>
      </xsl:attribute>
      <xsl:call-template name="image_alt"/>
      <xsl:call-template name="class_attr"/>
    </img>
  </xsl:template>

  <!--
      =========================================================================
      audio mode media
      =========================================================================
  -->
  <xsl:template match="audio" mode="media">
    <xsl:if test="not(../image)">
      <img id="{@id}" src="{$img_dir}noaudio{$img_ext}" alt="{@id}"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      video mode media
      =========================================================================
  -->
  <xsl:template match="video" mode="media">
    <xsl:if test="not(../image)">
      <img id="{@id}" src="{$img_dir}novideo{$img_ext}" alt="{@id}"/>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      sup, sub
      =========================================================================
  -->
  <xsl:template match="sup"><sup><xsl:apply-templates/></sup></xsl:template>
  <xsl:template match="sub"><sub><xsl:apply-templates/></sub></xsl:template>

  <!--
      =========================================================================
      Template var
      =========================================================================
  -->
  <xsl:template name="var">
    <em class="var"><xsl:apply-templates/></em>
  </xsl:template>

  <!--
      =========================================================================
      number
      =========================================================================
  -->
  <xsl:template match="number">
    <xsl:choose>
      <xsl:when test="@type='roman'">
        <span class="roman"><xsl:value-of select="."/></span>
      </xsl:when>
      <xsl:otherwise>
        <span class="number"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      math
      =========================================================================
  -->
  <xsl:template match="math">
    <span>
      <xsl:attribute name="class">
        <xsl:text>math</xsl:text>
        <xsl:if test="@display">
          <xsl:value-of select="concat('-', @display)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:call-template name="id_attr"/>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      date
      =========================================================================
  -->
  <xsl:template match="date">
    <span>
      <xsl:attribute name="class">
        <xsl:text>date</xsl:text>
        <xsl:if test="@of">
          <xsl:value-of select="concat('-of-', @of)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      name
      =========================================================================
  -->
  <xsl:template match="name">
    <span>
      <xsl:attribute name="class">
        <xsl:text>name</xsl:text>
        <xsl:if test="@of">
          <xsl:value-of select="concat('-of-', @of)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      acronym
      =========================================================================
  -->
  <xsl:template match="acronym">
    <acronym><xsl:apply-templates/></acronym>
  </xsl:template>

  <!--
      =========================================================================
      term
      =========================================================================
  -->
  <xsl:template match="term">
    <span class="term"><xsl:apply-templates/></span>
  </xsl:template>

  <!--
      =========================================================================
      literal
      =========================================================================
  -->
  <xsl:template match="literal">
    <span class="literal"><xsl:apply-templates/></span>
  </xsl:template>

  <!--
      =========================================================================
      foreign
      =========================================================================
  -->
  <xsl:template match="foreign">
    <span class="foreign">
      <xsl:copy-of select="@xml:lang"/>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      highlight
      =========================================================================
  -->
  <xsl:template match="highlight">
    <strong><xsl:apply-templates/></strong>
  </xsl:template>

  <!--
      =========================================================================
      emphasis
      =========================================================================
  -->
  <xsl:template match="emphasis">
    <em><xsl:apply-templates/></em>
  </xsl:template>

  <!--
      =========================================================================
      mentioned
      =========================================================================
  -->
  <xsl:template match="mentioned">
    <em class="mentioned"><xsl:apply-templates/></em>
  </xsl:template>

  <!--
      =========================================================================
      stage
      =========================================================================
  -->
  <xsl:template match="stage">
    <span class="stage"><xsl:apply-templates/></span>
  </xsl:template>

  <xsl:template match="stage" mode="speech">
    <line class="stage"><xsl:apply-templates/></line>
  </xsl:template>

  <!--
      =========================================================================
      initial
      =========================================================================
  -->
  <xsl:template match="initial">
    <span class="initial">
      <w class="dropcap"><xsl:apply-templates select="c"/></w>
      <xsl:apply-templates select="w" mode="initial"/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      quote
      =========================================================================
  -->
  <xsl:template match="quote">
    <q>
      <xsl:choose>
        <xsl:when test="phrase">
          <sent><xsl:apply-templates select="phrase"/></sent>
          <xsl:text> </xsl:text>
          <xsl:apply-templates select="attribution"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </q>
  </xsl:template>

  <!--
      =========================================================================
      note
      =========================================================================
  -->
  <xsl:template match="note">
    <xsl:choose>
      <xsl:when test="w">
        <noteref idref="#note{count(preceding::note)}">
          <xsl:apply-templates select="w" mode="note"/>
        </noteref>
      </xsl:when>
      <xsl:when test="@label">
        <noteref idref="#note{count(preceding::note)}">
          <xsl:value-of select="@label"/>
        </noteref>
      </xsl:when>
      <xsl:otherwise>
        <noteref idref="#note{count(preceding::note)}">
          <xsl:value-of select="count(preceding::note)+1"/>
        </noteref>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      note mode note
      =========================================================================
  -->
  <xsl:template match="note" mode="note">
    <note id="note{count(preceding::note)}">
      <xsl:choose>
        <xsl:when test="p|list|blockquote|speech|table|media">
          <xsl:apply-templates select="p|list|blockquote|speech|table|media"/>
        </xsl:when>
        <xsl:otherwise>
          <p><xsl:apply-templates/></p>
        </xsl:otherwise>
      </xsl:choose>
    </note>
  </xsl:template>

  <!--
      =========================================================================
      link
      =========================================================================
  -->
  <xsl:template match="link">
    <a>
      <xsl:attribute name="href">
        <xsl:choose>
          <xsl:when test="@idref">
            <xsl:value-of select="concat('#', @idref)"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@uri"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:apply-templates/>
    </a>
  </xsl:template>

  <!--
      =========================================================================
      anchor
      =========================================================================
  -->
  <xsl:template match="anchor">
    <span class="anchor">
      <xsl:call-template name="id_attr"/>
      <xsl:apply-templates/>
   </span>
  </xsl:template>

  <!--
      =========================================================================
      index
      =========================================================================
  -->
  <xsl:template match="index">
    <xsl:apply-templates select="w" mode="index"/>
  </xsl:template>

  <!--
      =========================================================================
      w
      =========================================================================
  -->
  <xsl:template match="w" mode="note">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="w" mode="initial">
    <w><xsl:apply-templates/></w>
  </xsl:template>

  <xsl:template match="w" mode="index">
    <w class="index"><xsl:apply-templates/></w>
  </xsl:template>

</xsl:stylesheet>
