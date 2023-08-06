<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_base.inc.xsl 3a627ba12869 2015/02/13 14:16:32 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">


  <!--
      *************************************************************************
                                      HEAD LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      head mode cover
      =========================================================================
  -->
  <xsl:template match="head" mode="cover">
    <xsl:if test="cover/image">
      <div class="pdocCover">
        <img src="{$img_dir}{cover/image/@id}{$img_ext_cover}"
             alt="{$i18n_cover}"/>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      head mode meta
      =========================================================================
  -->
  <xsl:template match="head" mode="meta">
    <table class="pdocMeta">
      <xsl:if test="(../@id or ../../@id) and
                    (name(..)='document' or name(..)='topic' or name(..)='quiz')">
        <tr>
          <td>ID</td>
          <td>
            <xsl:choose>
              <xsl:when test="../@id"><xsl:value-of select="../@id"/></xsl:when>
              <xsl:when test="../../@id"><xsl:value-of select="../../@id"/></xsl:when>
            </xsl:choose>
          </td>
        </tr>
      </xsl:if>
      <xsl:if test="../@type or ../../@type">
        <tr>
          <td><xsl:value-of select="$i18n_type"/></td>
          <td>
            <xsl:choose>
              <xsl:when test="../@type"><xsl:value-of select="../@type"/></xsl:when>
              <xsl:when test="../../@type"><xsl:value-of select="../../@type"/></xsl:when>
            </xsl:choose>
          </td>
        </tr>
      </xsl:if>
      <xsl:if test="../@xml:lang or ../../@xml:lang">
        <tr>
          <td><xsl:value-of select="$i18n_language"/></td>
          <td>
            <xsl:choose>
              <xsl:when test="../@xml:lang"><xsl:value-of select="../@xml:lang"/></xsl:when>
              <xsl:when test="../../@xml:lang"><xsl:value-of select="../../@xml:lang"/></xsl:when>
            </xsl:choose>
          </td>
        </tr>
      </xsl:if>
      <xsl:apply-templates
          select="title|shorttitle|subtitle|identifier|copyright|collection
                  |contributors|date|place|source|keywordset|subjectset
                  |abstract|cover|annotation"
          mode="meta"/>
      </table>
  </xsl:template>

  <xsl:template match="*" mode="meta">
    <tr>
      <td>
        <xsl:choose>
          <xsl:when test="name()='title'"><xsl:value-of select="$i18n_title"/></xsl:when>
          <xsl:when test="name()='shorttitle'"><xsl:value-of select="$i18n_shorttitle"/></xsl:when>
          <xsl:when test="name()='subtitle'"><xsl:value-of select="$i18n_subtitle"/></xsl:when>
          <xsl:when test="name()='identifier'">
            <xsl:value-of select="concat($i18n_identifier, ' ', @type)"/>
            <xsl:if test="@for"><xsl:value-of select="concat(' ', @for)"/></xsl:if>
          </xsl:when>
          <xsl:when test="name()='copyright'"><xsl:value-of select="$i18n_copyright"/></xsl:when>
          <xsl:when test="name()='collection'"><xsl:value-of select="$i18n_collection"/></xsl:when>
          <xsl:when test="name()='contributors'"><xsl:value-of select="$i18n_contributors"/></xsl:when>
          <xsl:when test="name()='date'"><xsl:value-of select="$i18n_date"/></xsl:when>
          <xsl:when test="name()='place'"><xsl:value-of select="$i18n_place"/></xsl:when>
          <xsl:when test="name()='source'"><xsl:value-of select="$i18n_source"/></xsl:when>
          <xsl:when test="name()='keywordset'"><xsl:value-of select="$i18n_keywords"/></xsl:when>
          <xsl:when test="name()='subjectset'"><xsl:value-of select="$i18n_subjects"/></xsl:when>
          <xsl:when test="name()='abstract'"><xsl:value-of select="$i18n_abstract"/></xsl:when>
          <xsl:when test="name()='cover'"><xsl:value-of select="$i18n_cover"/></xsl:when>
          <xsl:when test="name()='annotation'"><xsl:value-of select="$i18n_annotation"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="name()"/></xsl:otherwise>
      </xsl:choose>
      </td>
      <td>
        <xsl:apply-templates select="."/>
      </td>
    </tr>
  </xsl:template>

  <!--
      =========================================================================
      contributor
      =========================================================================
  -->
  <xsl:template match="contributor">
    <div>
      <xsl:apply-templates select="firstname"/><xsl:text> </xsl:text>
      <xsl:apply-templates select="lastname|label"/>
      <xsl:if test="link">
        <xsl:text> (</xsl:text>
        <xsl:apply-templates select="link"/>
        <xsl:text>)</xsl:text>
      </xsl:if>
      <xsl:text>, </xsl:text>
      <xsl:for-each select="role">
        <xsl:if test="position()&gt;1"> / </xsl:if>
        <xsl:apply-templates/>
      </xsl:for-each>
    </div>
  </xsl:template>

  <xsl:template match="contributor" mode="biblio">
    <xsl:if test="position()&gt;1"> ; </xsl:if>
    <xsl:apply-templates select="lastname|label" mode="biblio"/>
    <xsl:if test="firstname">
      <xsl:text>, </xsl:text>
      <xsl:apply-templates select="firstname" mode="biblio"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      source
      =========================================================================
  -->
  <xsl:template match="source">
    <xsl:value-of select="concat('[', @type, '] ')"/>
    <xsl:apply-templates select="title"/>
    <xsl:if test="title and identifier">, </xsl:if>
    <xsl:apply-templates select="identifier"/>
    <xsl:if test="pages">
      <xsl:text>, </xsl:text>
      <xsl:apply-templates select="pages"/>
      <xsl:text> pages</xsl:text>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      keyword, subject
      =========================================================================
  -->
  <xsl:template match="keyword|subject">
    <xsl:if test="count(preceding-sibling::keyword|preceding-sibling::subject)&gt;0">
      <xsl:text> / </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      index
      =========================================================================
  -->
  <xsl:template match="index">
    <xsl:if test="not(ancestor::indexset)">
      <a id="{concat('idx', count(preceding::index))}">
        <xsl:apply-templates select="w"/>
        <xsl:if test="not(w)"><xsl:text> </xsl:text></xsl:if>
      </a>
    </xsl:if>
  </xsl:template>

  <xsl:template match="index" mode="text">
    <xsl:apply-templates select="w" mode="text"/>
  </xsl:template>
  <xsl:template match="index" mode="link">
    <xsl:apply-templates select="w" mode="link"/>
  </xsl:template>

  <!--
      =========================================================================
      index mode ref
      =========================================================================
  -->
  <xsl:template match="index" mode="ref">
    <xsl:param name="position"/>
    <xsl:variable name="parent">
      <xsl:choose>
        <xsl:when test="ancestor::quiz">-quz-</xsl:when>
        <xsl:otherwise>-tpc-</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <a>
      <xsl:attribute name="href">
        <xsl:choose>
          <!-- in text -->
          <xsl:when test="not(ancestor::indexset) and $onefile">
            <xsl:value-of select="concat('#idx', count(preceding::index))"/>
          </xsl:when>
          <xsl:when test="not(ancestor::indexset)">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#idx',
                                  count(preceding::index))"/>
          </xsl:when>

          <!-- $onefile and head with ../@xml:id -->
          <xsl:when test="ancestor::head/../@id and $onefile">
            <xsl:value-of select="concat('#', ancestor::head/../@id)"/>
          </xsl:when>
          <xsl:when test="ancestor::head/../@xml:id and $onefile">
            <xsl:value-of select="concat('#', ancestor::head/../@xml:id)"/>
          </xsl:when>

          <!-- division -->
          <xsl:when test="name(ancestor::head/..)='division' and $onefile">
            <xsl:value-of select="concat('#div',
                                  count(preceding::division|ancestor::division))"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='division'
                          and $toc_division_depth&gt;count(ancestor::division)-1">
            <xsl:value-of select="concat($fid, '-div-',
                                  count(preceding::division|ancestor::division), $html_ext)"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='division'">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#div',
                                  count(preceding::division|ancestor::division))"/>
          </xsl:when>

          <!-- topic -->
          <xsl:when test="name(ancestor::head/..)='topic' and $onefile">
            <xsl:value-of select="concat('#tpc', count(preceding::topic)+1)"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='topic'">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext)"/>
          </xsl:when>

          <!-- head with ../@xml:id -->
          <xsl:when test="ancestor::head/../@xml:id">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#',
                                  ancestor::head/../@xml:id)"/>
          </xsl:when>

          <!-- section -->
          <xsl:when test="name(ancestor::head/..)='section' and $onefile">
            <xsl:value-of select="concat('#sect',
                                  count(preceding::section|ancestor::section)-1)"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='section'">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#sect',
                                  count(preceding::section|ancestor::section)-1)"/>
          </xsl:when>

          <!-- table -->
          <xsl:when test="name(ancestor::head/..)='table' and $onefile">
            <xsl:value-of select="concat('#tbl', count(preceding::table))"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='table'">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#tbl',
                                  count(preceding::table))"/>
          </xsl:when>

          <!-- media -->
          <xsl:when test="name(ancestor::head/..)='media' and $onefile">
            <xsl:value-of select="concat('#med', count(preceding::media))"/>
          </xsl:when>
          <xsl:when test="name(ancestor::head/..)='media'">
            <xsl:value-of select="concat($fid, $parent,
                                  count(preceding::topic)+1, $html_ext, '#med',
                                  count(preceding::media))"/>
          </xsl:when>

          <xsl:otherwise>#</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>

      <xsl:call-template name="index_symbol">
        <xsl:with-param name="position" select="$position"/>
      </xsl:call-template>
    </a>
  </xsl:template>

  <!--
      =========================================================================
      cover
      =========================================================================
  -->
  <xsl:template match="cover">
    <xsl:value-of select="image/@id"/>
  </xsl:template>


  <!--
      *************************************************************************
                                     DIVISION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      division mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="division" mode="onefiletoc">
    <xsl:choose>
      <xsl:when test="$toc_division_depth&gt;count(ancestor::division)
                      and (head/title or ($toc_with_abstract and head/abstract))">
        <xsl:variable name="has_children">
          <xsl:call-template name="has_toc_children"/>
        </xsl:variable>
        <li>
          <a href="#div{count(preceding::division|ancestor::division)+1}">
            <xsl:call-template name="division_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates mode="onefiletoc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>

      <xsl:when test="head/title or ($toc_with_abstract and head/abstract)">
        <xsl:variable name="has_children">
          <xsl:call-template name="has_toc_children"/>
        </xsl:variable>
        <li>
          <span>
            <xsl:choose>
              <xsl:when test="head/shorttitle">
                <xsl:apply-templates select="head/shorttitle"/>
              </xsl:when>
              <xsl:when test="head/title">
                <xsl:apply-templates select="head/title"/>
              </xsl:when>
            </xsl:choose>
            <xsl:for-each select="head/subtitle">
              <xsl:value-of select="$str_sep"/>
              <xsl:apply-templates/>
            </xsl:for-each>
          </span>
          <xsl:if test="$toc_with_abstract and head/abstract">
            <div class="pdocAbstract">
              <xsl:apply-templates select="head/abstract"/>
            </div>
          </xsl:if>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates mode="onefiletoc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>

      <xsl:otherwise>
        <xsl:apply-templates mode="onefiletoc"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="head|file|front" mode="onefiletoc"/>

  <!--
      =========================================================================
      division mode onefile
      =========================================================================
  -->
  <xsl:template match="division" mode="onefile">
    <div id="div{count(preceding::division|ancestor::division)+1}">
      <xsl:attribute name="class">
        <xsl:text>pdocDivision</xsl:text>
        <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:if test="head/title">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h2 class="pdocTitle"><xsl:call-template name="title"/></h2>
          </xsl:when>
          <xsl:otherwise>
            <h3 class="pdocTitle"><xsl:call-template name="title"/></h3>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle">
          <xsl:choose>
            <xsl:when test="count(ancestor::division)=0">
              <h3 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h3>
            </xsl:when>
            <xsl:otherwise>
              <h4 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h4>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </xsl:if>
      <xsl:if test="head/abstract">
        <div class="pdocAbstract">
          <xsl:apply-templates select="head/abstract"/>
        </div>
      </xsl:if>
      <xsl:apply-templates mode="onefile"/>
    </div>
  </xsl:template>

  <xsl:template match="head|file|link" mode="onefile"/>

  <!--
      =========================================================================
      division mode toc
      =========================================================================
  -->
  <xsl:template match="division" mode="toc">
    <xsl:choose>
      <xsl:when test="$toc_division_depth&gt;count(ancestor::division)
                      and (head/title or ($toc_with_abstract and head/abstract))">
        <xsl:variable name="has_children">
          <xsl:call-template name="has_toc_children"/>
        </xsl:variable>
        <li>
          <a href="{$fid}-div-{count(preceding::division|ancestor::division)+1}{$html_ext}">
            <xsl:call-template name="division_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates mode="toc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>

      <xsl:when test="head/title or ($toc_with_abstract and head/abstract)">
        <xsl:variable name="has_children">
          <xsl:call-template name="has_toc_children"/>
        </xsl:variable>
        <li>
          <span>
            <xsl:choose>
              <xsl:when test="head/shorttitle">
                <xsl:apply-templates select="head/shorttitle"/>
              </xsl:when>
              <xsl:when test="head/title">
                <xsl:apply-templates select="head/title"/>
              </xsl:when>
            </xsl:choose>
            <xsl:for-each select="head/subtitle">
              <xsl:value-of select="$str_sep"/>
              <xsl:apply-templates/>
            </xsl:for-each>
          </span>
          <xsl:if test="$toc_with_abstract and head/abstract">
            <div class="pdocAbstract">
              <xsl:apply-templates select="head/abstract"/>
            </div>
          </xsl:if>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates mode="toc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>

      <xsl:otherwise>
        <xsl:apply-templates mode="toc"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="head|file|front" mode="toc"/>

  <!--
      =========================================================================
      division mode file
      =========================================================================
  -->
  <xsl:template match="division" mode="file">
    <xsl:if test="$toc_division_depth&gt;count(ancestor::division)">
      <xsl:variable name="has_children">
        <xsl:call-template name="has_toc_children"/>
      </xsl:variable>

      <xsl:call-template name="html_file">
        <xsl:with-param name="name"
                        select="concat($fid, '-div-',
                                count(preceding::division|ancestor::division)+1)"/>

        <xsl:with-param name="title">
          <xsl:if test="/*/*/head/title">
            <xsl:apply-templates select="/*/*/head/title" mode="text"/>
          </xsl:if>
          <xsl:if test="head/title">
            <xsl:if test="/*/*/head/title"><xsl:value-of select="$str_sep"/></xsl:if>
            <xsl:apply-templates select="head/title" mode="text"/>
          </xsl:if>
        </xsl:with-param>

        <xsl:with-param name="nojs" select="1"/>

        <xsl:with-param name="body">
          <body>
            <xsl:attribute name="class">
              <xsl:text>pdocToc pdocDivision</xsl:text>
              <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
            </xsl:attribute>
            <xsl:call-template name="navigation"/>
            <xsl:if test="head/title or ancestor::division/head/title">
              <h1 class="pdocTitle">
                <xsl:for-each select="ancestor-or-self::division">
                  <xsl:if test="head/title">
                    <span class="pdocTitle{count(ancestor::division)+1}">
                      <xsl:call-template name="title"/>
                    </span><br/>
                  </xsl:if>
                </xsl:for-each>
              </h1>
            </xsl:if>
            <xsl:if test="head/subtitle">
              <h2 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h2>
            </xsl:if>
            <xsl:apply-templates select="front"/>
            <xsl:if test="$has_children='1' and $subtoc">
              <ul>
                <xsl:apply-templates mode="toc"/>
              </ul>
            </xsl:if>
            <xsl:call-template name="navigation">
              <xsl:with-param name="bottom" select="1"/>
            </xsl:call-template>
          </body>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      division mode lead
      =========================================================================
  -->
  <xsl:template match="division" mode="lead">
    <div>
      <xsl:if test="head/indexset/index">
        <xsl:attribute name="id">
          <xsl:value-of select="concat('div',
                                count(preceding::division|ancestor::division)+1)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:attribute name="class">
        <xsl:value-of select="concat('pdocLead',
                              count(ancestor::division|ancestor::division)+1)"/>
        <xsl:if test="@type"> pdocLead-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:if test="head/title">
        <div class="pdocDivisionTitle">
          <xsl:call-template name="title"/>
        </div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pdocDivisionSubtitle">
          <xsl:call-template name="subtitle"/>
        </div>
      </xsl:if>
      <xsl:apply-templates select="front"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      link mode toc
      =========================================================================
  -->
  <xsl:template match="link" mode="toc">
    <li><xsl:apply-templates select="."/></li>
  </xsl:template>

  <!--
      =========================================================================
      front mode onefile
      =========================================================================
  -->
  <xsl:template match="front" mode="onefile">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      front
      =========================================================================
  -->
  <xsl:template match="front">
    <div class="pdocFront">
      <xsl:apply-templates select="section"/>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                     COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      document mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="document" mode="onefiletoc">
    <xsl:variable name="has_children">
      <xsl:call-template name="has_toc_children"/>
    </xsl:variable>

    <xsl:if test="$toc and $has_children='1'">
      <h2><xsl:value-of select="$i18n_toc"/></h2>
      <div class="pdocOneFile pdocToc">
        <ul>
          <xsl:apply-templates select="division|topic" mode="onefiletoc"/>
        </ul>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      topic mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="topic" mode="onefiletoc">
    <xsl:variable name="has_children">
      <xsl:call-template name="has_toc_children"/>
    </xsl:variable>

    <xsl:choose>
      <xsl:when
          test="$toc and ancestor::document
                and (head/title or @type='title' or @type='copyright'
                or @type='dedication' or @type='inscription'
                or ($toc_with_abstract and head/abstract))">
        <li>
          <a>
            <xsl:attribute name="href">
              <xsl:text>#</xsl:text>
              <xsl:choose>
                <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
                <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="concat('tpc', count(preceding::topic)+1)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <xsl:call-template name="topic_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates select="section" mode="onefiletoc"/>
              <xsl:apply-templates select="bibliography" mode="onefiletoc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>

      <xsl:when test="$toc and ancestor::document and $has_children='1'">
        <xsl:apply-templates select="section" mode="onefiletoc"/>
        <xsl:apply-templates select="bibliography" mode="onefiletoc"/>
      </xsl:when>

      <xsl:when test="$toc and $has_children='1'">
        <h2><xsl:value-of select="$i18n_toc"/></h2>
        <div class="pdocOneFile pdocToc">
          <ul>
            <xsl:apply-templates select="section" mode="onefiletoc"/>
            <xsl:apply-templates select="bibliography" mode="onefiletoc"/>
          </ul>
        </div>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      topic mode onefile
      =========================================================================
  -->
  <xsl:template match="topic" mode="onefile">
    <div>
      <xsl:attribute name="id">
        <xsl:choose>
          <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
          <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat('tpc', count(preceding::topic)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="class">
        <xsl:text>pdocTopic pdocTopicOneFile</xsl:text>
        <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
        <xsl:if test="ancestor::division">
          <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates select="header"/>
      <xsl:if test="head/title">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h2 class="pdocTitle"><xsl:call-template name="title"/></h2>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=1">
            <h3 class="pdocTitle"><xsl:call-template name="title"/></h3>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=2">
            <h4 class="pdocTitle"><xsl:call-template name="title"/></h4>
          </xsl:when>
           <xsl:otherwise>
            <h5 class="pdocTitle"><xsl:call-template name="title"/></h5>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle">
          <xsl:choose>
            <xsl:when test="count(ancestor::division)=0">
              <h3 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h3>
            </xsl:when>
            <xsl:when test="count(ancestor::division)=1">
              <h4 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h4>
            </xsl:when>
            <xsl:when test="count(ancestor::division)=2">
              <h5 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h5>
            </xsl:when>
            <xsl:otherwise>
              <h6 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h6>
            </xsl:otherwise>
        </xsl:choose>
        </xsl:if>
      </xsl:if>
      <xsl:apply-templates select="." mode="corpus"/>
      <xsl:apply-templates select="footer"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      topic mode toc
      =========================================================================
  -->
  <xsl:template match="topic" mode="toc">
    <xsl:variable name="has_children">
      <xsl:call-template name="has_toc_children"/>
    </xsl:variable>

    <xsl:choose>
      <xsl:when
          test="head/title or @type='title' or @type='copyright'
                or @type='dedication' or @type='inscription'
                or ($toc_with_abstract and head/abstract)">
        <li id="tpc{count(preceding::topic)+1}">
          <a href="{$fid}-tpc-{count(preceding::topic)+1}{$html_ext}">
            <xsl:call-template name="topic_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates select="section" mode="toc"/>
              <xsl:apply-templates select="bibliography" mode="toc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>
      <xsl:when test="$has_children='1'">
        <xsl:apply-templates select="section" mode="toc"/>
        <xsl:apply-templates select="bibliography" mode="toc"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      topic mode file
      =========================================================================
  -->
  <xsl:template match="topic" mode="file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name"
                      select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>

      <xsl:with-param name="title">
        <xsl:if test="/*/*/head/title">
          <xsl:apply-templates select="/*/*/head/title" mode="text"/>
        </xsl:if>
        <xsl:if test="head/title">
          <xsl:if test="/*/*/head/title"> – </xsl:if>
          <xsl:apply-templates select="head/title" mode="text"/>
        </xsl:if>
      </xsl:with-param>

      <xsl:with-param name="body">
        <body>
          <xsl:attribute name="class">
            <xsl:text>pdocTopic</xsl:text>
            <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
            <xsl:if test="ancestor::division">
              <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
              <xsl:for-each select="ancestor::division">
                <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
              </xsl:for-each>
            </xsl:if>
          </xsl:attribute>
          <xsl:call-template name="navigation"/>
          <xsl:call-template name="lead"/>
          <xsl:apply-templates select="header"/>

          <xsl:if test="head/title">
            <h1 class="pdocTitle"><xsl:call-template name="title"/></h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2 class="pdocSubtitle"><xsl:call-template name="subtitle"/></h2>
          </xsl:if>
          <xsl:apply-templates select="." mode="corpus"/>

          <xsl:apply-templates select="footer"/>
          <xsl:call-template name="navigation">
            <xsl:with-param name="bottom" select="1"/>
          </xsl:call-template>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      topic mode corpus
      =========================================================================
  -->
  <xsl:template match="topic" mode="corpus">
    <xsl:apply-templates select="section"/>
    <xsl:apply-templates select="bibliography"/>
  </xsl:template>


  <!--
      *************************************************************************
                                      SECTION LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      header
      ========================================================================
  -->
  <xsl:template match="header">
    <div class="pdocHeader">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      section mode onefiletoc
      ========================================================================
  -->
  <xsl:template match="section" mode="onefiletoc">
    <xsl:variable name="has_children">
      <xsl:call-template name="has_toc_children"/>
    </xsl:variable>

    <xsl:choose>
      <xsl:when test="head/title">
        <li>
          <a>
            <xsl:attribute name="href">
              <xsl:text>#</xsl:text>
              <xsl:choose>
                <xsl:when test="@xml:id">
                  <xsl:value-of select="@xml:id"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of
                      select="concat('sect',
                              count(preceding::section|ancestor::section))"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <xsl:call-template name="section_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates select="section" mode="onefiletoc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>
      <xsl:when test="$toc_section_depth &gt; count(ancestor::section)+1">
        <xsl:apply-templates select="section" mode="onefiletoc"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      ========================================================================
      section mode toc
      ========================================================================
  -->
  <xsl:template match="section" mode="toc">
    <xsl:variable name="has_children">
      <xsl:call-template name="has_toc_children"/>
    </xsl:variable>

     <xsl:choose>
      <xsl:when test="head/title">
        <li>
          <a>
            <xsl:attribute name="href">
              <xsl:value-of
                  select="concat($fid, '-tpc-',
                          count(preceding::topic)+1, $html_ext, '#')"/>
              <xsl:choose>
                <xsl:when test="@xml:id">
                  <xsl:value-of select="@xml:id"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of
                      select="concat('sect',
                              count(preceding::section|ancestor::section))"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <xsl:call-template name="section_toc_title"/>
          </a>
          <xsl:if test="$has_children='1'">
            <ul>
              <xsl:apply-templates select="section" mode="toc"/>
            </ul>
          </xsl:if>
        </li>
      </xsl:when>
      <xsl:when test="$toc_section_depth &gt; count(ancestor::section)+1">
        <xsl:apply-templates select="section" mode="toc"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      ========================================================================
      section
      ========================================================================
  -->
  <xsl:template match="section">
    <div>
      <xsl:choose>
        <xsl:when test="@xml:id">
          <xsl:attribute name="id">
            <xsl:value-of select="@xml:id"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:when test="$toc_section_depth &gt;= count(ancestor::section)
                        or head/indexset/index">
          <xsl:attribute name="id">
            <xsl:value-of
                select="concat('sect',
                        count(preceding::section|ancestor::section))"/>
          </xsl:attribute>
        </xsl:when>
      </xsl:choose>
      <xsl:attribute name="class">
        <xsl:value-of select="concat('pdocSection', count(ancestor::section)+1)"/>
        <xsl:if test="@type"> pdocSection-<xsl:value-of select="@type"/></xsl:if>
        <xsl:if test="count(preceding-sibling::section)=0
                      and count(ancestor::section/preceding-sibling::section)=0">
          <xsl:text> first</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:call-template name="mid_section"/>

      <xsl:if test="head/title">
        <div class="pdocSectionTitle"><xsl:call-template name="title"/></div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pdocSectionSubtitle"><xsl:call-template name="subtitle"/></div>
      </xsl:if>

      <xsl:apply-templates
          select="section|p|list|blockquote|speech|table|media"/>

      <xsl:apply-templates select="head/audio" mode="header"/>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      bibliography mode onefiletoc
      ========================================================================
  -->
  <xsl:template match="bibliography" mode="onefiletoc">
    <li>
      <a href="#biblio">
        <xsl:value-of select="$i18n_bibliography"/>
      </a>
    </li>
  </xsl:template>

  <!--
      ========================================================================
      bibliography mode toc
      ========================================================================
  -->
  <xsl:template match="bibliography" mode="toc">
    <li>
      <a href="{$fid}-tpc-{count(preceding::topic)+1}{$html_ext}#biblio">
        <xsl:value-of select="$i18n_bibliography"/>
      </a>
    </li>
  </xsl:template>

  <!--
      ========================================================================
      bibliography
      ========================================================================
  -->
  <xsl:template match="bibliography">
    <div id="biblio" class="pdocBiblio">
      <xsl:if test="../section">
        <div class="pdocSectionTitle">
          <xsl:value-of select="$i18n_bibliography"/>
        </div>
      </xsl:if>
      <xsl:apply-templates select="entry" mode="biblio"/>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      footer
      ========================================================================
  -->
  <xsl:template match="footer">
    <div class="pdocFooter">
      <xsl:apply-templates/>
    </div>
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
    <p>
      <xsl:attribute name="class">
        <xsl:text>pdocP</xsl:text>
        <xsl:if test="initial"> initial</xsl:if>
        <xsl:if test="position()=1"> first</xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="p" mode="text">
    <xsl:apply-templates mode="text"/><xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template match="p" mode="link">
    <xsl:apply-templates mode="link"/><br/>
  </xsl:template>

  <!--
      =========================================================================
      speech
      =========================================================================
  -->
  <xsl:template match="speech">
    <div class="pdocSpeech"><xsl:apply-templates/></div>
  </xsl:template>

  <xsl:template match="speaker">
    <strong class="pdocSpeechSpeaker"><xsl:apply-templates/></strong>
    <xsl:if test="../stage"><xsl:value-of select="$str_stage_sep"/></xsl:if>
  </xsl:template>

  <xsl:template match="stage">
    <xsl:choose>
      <xsl:when test="not(../../speech)">
        <xsl:value-of select="$str_stage_open"/>
        <em class="pdocStage"><xsl:apply-templates/></em>
        <xsl:value-of select="$str_stage_close"/>
      </xsl:when>
      <xsl:otherwise>
        <em class="pdocStage"><xsl:apply-templates/></em>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      list
      =========================================================================
  -->
  <xsl:template match="list">
    <xsl:if test="head/title">
      <div class="pdocListTitle"><xsl:call-template name="title"/></div>
    </xsl:if>
    <xsl:if test="head/subtitle">
      <div class="pdocListSubtitle"><xsl:call-template name="subtitle"/></div>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@type='ordered'">
        <ol class="pdocList">
          <xsl:apply-templates select="item"/>
        </ol>
      </xsl:when>
      <xsl:when test="@type='glossary'">
        <ul class="pdocListGlossary">
          <xsl:apply-templates select="item"/>
        </ul>
      </xsl:when>
      <xsl:otherwise>
        <ul class="pdocList">
          <xsl:apply-templates select="item"/>
        </ul>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="item">
    <li><xsl:apply-templates/></li>
  </xsl:template>

  <xsl:template match="label">
    <strong class="pdocLabel"><xsl:apply-templates/></strong>
  </xsl:template>

  <!--
      =========================================================================
      blockquote
      =========================================================================
  -->
  <xsl:template match="blockquote">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocQuote</xsl:text>
        <xsl:if test="@type"> pdocQuote-<xsl:value-of select="@type"/></xsl:if>
        <xsl:if test="count(preceding-sibling::p)=0"> first</xsl:if>
      </xsl:attribute>
      <xsl:if test="head/title">
        <div class="pdocQuoteTitle"><xsl:call-template name="title"/></div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pdocQuoteSubtitle"><xsl:call-template name="subtitle"/></div>
      </xsl:if>
      <xsl:apply-templates select="p|speech|list"/>
      <xsl:if test="attribution">
        <div class="pdocQuoteAttribution">
          <xsl:apply-templates select="attribution"/>
        </div>
      </xsl:if>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      table
      =========================================================================
  -->
  <xsl:template match="table">
    <div>
      <xsl:if test="head/indexset/index">
        <xsl:attribute name="id">
          <xsl:value-of select="concat('tbl', count(preceding::table))"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:attribute name="class">
        <xsl:text>pdocTable</xsl:text>
        <xsl:if test="@type"> pdocTable-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <table>
        <xsl:apply-templates select="thead|tbody|tr|tgroup"/>
      </table>
      <xsl:if test="head/title or caption">
        <div class="pdocTableText">
          <xsl:if test="head/title">
            <div class="pdocTableTitle"><xsl:call-template name="title"/></div>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <div class="pdocTableSubtitle"><xsl:call-template name="subtitle"/></div>
          </xsl:if>
          <xsl:if test="caption">
            <div class="pdocTableCaption">
            <xsl:apply-templates select="caption"/>
            </div>
          </xsl:if>
        </div>
      </xsl:if>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      table> thead, tbody
      =========================================================================
  -->
  <xsl:template match="thead">
    <thead>
      <xsl:apply-templates select="tr"/>
    </thead>
  </xsl:template>

  <xsl:template match="tbody">
    <tbody>
      <xsl:apply-templates select="tr"/>
    </tbody>
  </xsl:template>

  <!--
      =========================================================================
      table> tr
      =========================================================================
  -->
  <xsl:template match="tr">
    <tr>
      <xsl:if test="@type">
        <xsl:attribute name="class">
          <xsl:value-of select="concat('pdocCell-', @type)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="th|td"/>
    </tr>
  </xsl:template>

  <!--
      =========================================================================
      table> th, td
      =========================================================================
  -->
  <xsl:template match="th|td">
    <xsl:call-template name="cell">
      <xsl:with-param name="tag"><xsl:value-of select="name()"/></xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      table> tgroup
      =========================================================================
  -->
  <xsl:template match="tgroup">
    <xsl:apply-templates select="thead/row"/>
    <xsl:apply-templates select="tbody/row"/>
  </xsl:template>

  <!--
      =========================================================================
      table> row
      =========================================================================
  -->
  <xsl:template match="row">
    <tr>
      <xsl:apply-templates select="entry"/>
    </tr>
  </xsl:template>

  <!--
      =========================================================================
      table> entry
      =========================================================================
  -->
  <xsl:template match="thead/row/entry">
    <xsl:call-template name="cell">
      <xsl:with-param name="tag">th</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tbody/row/entry">
    <xsl:call-template name="cell"/>
  </xsl:template>

  <!--
      =========================================================================
      Template cell
      =========================================================================
  -->
  <xsl:template name="cell">
    <xsl:param name="tag">td</xsl:param>
    <xsl:element name="{$tag}">
      <xsl:copy-of select="@colspan|@rowspan"/>

      <xsl:if test="@align or ../@align or @valign or ../@valign">
        <xsl:attribute name="style">
          <!-- align -->
          <xsl:choose>
            <xsl:when test="@align">
              <xsl:value-of select="concat('text-align:', @align, ';')"/>
            </xsl:when>
            <xsl:when test="../@align">
              <xsl:value-of select="concat('text-align:', ../@align, ';')"/>
            </xsl:when>
          </xsl:choose>
          <!-- valign -->
          <xsl:choose>
            <xsl:when test="@valign">
              <xsl:value-of select="concat('vertical-align:', @valign, ';')"/>
            </xsl:when>
            <xsl:when test="../@valign">
              <xsl:value-of select="concat('vertical-align:', ../@valign, ';')"/>
            </xsl:when>
          </xsl:choose>
        </xsl:attribute>
      </xsl:if>

      <xsl:if test="@type">
        <xsl:attribute name="class">
          <xsl:value-of select="concat('pdocCell-', @type)"/>
        </xsl:attribute>
      </xsl:if>

      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!--
      =========================================================================
      entry mode biblio
      =========================================================================
  -->
  <xsl:template match="entry" mode="biblio">
    <div class="pdocBiblioEntry">
      <xsl:if test="contributors/contributor[role='author']">
        <strong class="pdocBiblioEntryAuthor">
          <xsl:for-each select="contributors/contributor[role='author']">
            <xsl:apply-templates select="." mode="biblio"/>
          </xsl:for-each>
        </strong>
        <xsl:text>. </xsl:text>
      </xsl:if>
      <em class="pdocBiblioTitle"><xsl:apply-templates select="title"/></em>
      <xsl:text>. </xsl:text>
      <xsl:if test="contributors/contributor[role='publisher']">
        <span class="pdocBiblioEntryPublisher">
          <xsl:for-each select="contributors/contributor[role='publisher']">
            <xsl:apply-templates select="." mode="biblio"/>
          </xsl:for-each>
        </span>
        <xsl:if test="date">, </xsl:if>
      </xsl:if>
      <xsl:apply-templates select="date" mode="biblio"/>
      <xsl:if test="pages">
        <xsl:apply-templates select="pages"/>
        <xsl:text> p. </xsl:text>
      </xsl:if>
      <xsl:if test="collection">
        <xsl:apply-templates select="collection"/>
        <xsl:text>. </xsl:text>
      </xsl:if>
      <xsl:if test="identifier">
        <xsl:text>EAN </xsl:text>
        <xsl:value-of select="identifier"/>
      </xsl:if>
    </div>
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

  <xsl:template match="sup" mode="link">
    <sup><xsl:apply-templates mode="link"/></sup>
  </xsl:template>
  <xsl:template match="sub" mode="link">
    <sub><xsl:apply-templates mode="link"/></sub>
  </xsl:template>

  <!--
      =========================================================================
      var
      =========================================================================
  -->
  <xsl:template match="var">
    <em class="pdocVar"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="var" mode="link">
    <em class="pdocVar"><xsl:apply-templates mode="link"/></em>
  </xsl:template>

  <!--
      =========================================================================
      number
      =========================================================================
  -->
  <xsl:template match="number">
    <xsl:choose>
      <xsl:when test="@type='roman'">
        <span class="pdocNumberRoman"><xsl:value-of select="."/></span>
      </xsl:when>
      <xsl:otherwise>
        <span class="pdocNumber"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="number" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      math
      =========================================================================
  -->
  <xsl:template match="math">
    <xsl:choose>
      <xsl:when test="starts-with(@display, 'numbered')">
        <span class="pdocMathDiv">
          <xsl:if test="@xml:id">
            <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
          </xsl:if>
          <span class="pdocMathNumber">
            <xsl:text> (</xsl:text>
            <xsl:apply-templates select="." mode="number"/>
            <xsl:text>)</xsl:text>
          </span>
          <span>
            <xsl:apply-templates select="." mode="formula"/>
          </span>
        </span>
      </xsl:when>
      <xsl:otherwise>
        <span>
          <xsl:if test="@xml:id">
            <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="." mode="formula"/>
        </span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="math" mode="number">
    <xsl:value-of
        select="count(preceding::math[starts-with(@display, 'numbered')])+1"/>
  </xsl:template>

  <xsl:template match="math" mode="formula">
    <xsl:attribute name="class">
      <xsl:text>pdocMath</xsl:text>
      <xsl:if test="@display"> pdocMathDisplay</xsl:if>
      <xsl:if test="contains(@display, 'box')"> pdocMathBox</xsl:if>
      <xsl:if test="latex"> pdocMathLatex</xsl:if>
    </xsl:attribute>
    <xsl:call-template name="math"/>
  </xsl:template>

  <xsl:template match="math" mode="link">
    <span class="pdocMath"><xsl:apply-templates/></span>
  </xsl:template>

  <!--
      =========================================================================
      date
      =========================================================================
  -->
  <xsl:template match="date">
    <xsl:choose>
      <xsl:when test="not(text())">
        <xsl:choose>
          <xsl:when test="string-length(@value)=4">
            <xsl:value-of select="@value"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=7">
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=10">
            <xsl:value-of select="substring(@value, 9, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="date" mode="biblio">
    <xsl:value-of select="substring(@value, 1, 4)"/>
    <xsl:text>. </xsl:text>
  </xsl:template>

  <xsl:template match="date" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      name
      =========================================================================
  -->
  <xsl:template match="name">
    <em class="pdocName">
      <xsl:attribute name="class">
        <xsl:text>pdocName</xsl:text>
        <xsl:if test="@of">
          <xsl:value-of select="concat(' pdocName-', @of)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </em>
  </xsl:template>

  <xsl:template match="name" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      initial
      =========================================================================
  -->
  <xsl:template match="initial">
    <span class="pdocInitialCap"><xsl:apply-templates select="c"/></span>
    <xsl:if test="w">
      <span class="pdocInitialWords"><xsl:apply-templates select="w"/></span>
    </xsl:if>
  </xsl:template>

  <xsl:template match="initial" mode="link">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      quote
      =========================================================================
  -->
  <xsl:template match="quote">
    <xsl:choose>
      <xsl:when test="phrase">
        <xsl:text>« </xsl:text>
        <em class="pdocQuote"><xsl:apply-templates select="phrase"/></em>
        <xsl:text> »</xsl:text>
        <xsl:text> (</xsl:text>
        <xsl:apply-templates select="attribution"/>
        <xsl:text>)</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>« </xsl:text>
        <em class="pdocQuote"><xsl:apply-templates/></em>
        <xsl:text> »</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="quote" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      note
      =========================================================================
  -->
  <xsl:template match="note">
    <xsl:choose>
      <xsl:when test="$onefile">
        <a href="#n{count(preceding::note)+1}" id="nc{count(preceding::note)+1}">
          <xsl:apply-templates select="." mode="call"/>
        </a>
      </xsl:when>
      <xsl:otherwise>
        <a href="{$fid}-not-{count(preceding::note)+1}{$html_ext}" id="n{count(preceding::note)+1}">
          <xsl:apply-templates select="." mode="call"/>
        </a>
        <xsl:call-template name="note_file"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="note" mode="call">
    <xsl:choose>
      <xsl:when test="w">
        <xsl:attribute name="class">pdocNoteLink</xsl:attribute>
        <xsl:attribute name="title">
          <xsl:for-each select="p">
            <xsl:value-of select="normalize-space()"/><xsl:text> </xsl:text>
          </xsl:for-each>
        </xsl:attribute>
        <xsl:apply-templates select="w"/>
      </xsl:when>
      <xsl:when test="@label">
        <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
        <xsl:attribute name="title"><xsl:value-of select="normalize-space()"/></xsl:attribute>
        <sup><xsl:value-of select="concat($str_notecall_open, @label, $str_notecall_close)"/></sup>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
        <xsl:attribute name="title"><xsl:value-of select="normalize-space()"/></xsl:attribute>
        <sup>
          <xsl:value-of select="concat($str_notecall_open,
                                count(preceding::note[not(@label) and not(w)])+1,
                                $str_notecall_close)"/>
        </sup>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="note" mode="title">
    <xsl:choose>
      <xsl:when test="w">
        <xsl:apply-templates select="w" mode="text"/>
      </xsl:when>
      <xsl:when test="@label">
        <xsl:value-of select="concat($i18n_note, ' ', @label)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat($i18n_note, ' ',
                              count(preceding::note[not(@label) and not(w)])+1)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="note" mode="footer">
    <div>
      <p class="pdocP">
        <a href="#nc{count(preceding::note)+1}" id="n{count(preceding::note)+1}">
          <xsl:apply-templates select="." mode="title"/>
        </a>
      </p>
      <xsl:apply-templates select="*[name()!='w']|text()"/>
    </div>
  </xsl:template>

  <xsl:template name="note_file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name">
        <xsl:value-of select="concat($fid, '-not-', count(preceding::note)+1)"/>
      </xsl:with-param>
      <xsl:with-param name="title">
        <xsl:apply-templates select="." mode="title"/>
      </xsl:with-param>
      <xsl:with-param name="nojs" select="1"/>
      <xsl:with-param name="body">
        <body class="pdocNote">
          <h1><xsl:apply-templates select="." mode="title"/></h1>
          <div class="pdocNoteText">
            <xsl:apply-templates select="*[name()!='w']|text()"/>
          </div>
          <div class="pdocNoteBack">
            <xsl:choose>
              <xsl:when test="$toc_division_depth&gt;count(ancestor::division)-1
                              and (ancestor::front or name(../../..)='division')">
                <a href="{$fid}-div-{count(preceding::division|ancestor::division)}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:when test="name(//*/*)='topic'
                              and not(contains($path, 'Container~/'))">
                <a href="{$fid}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:otherwise>
                <a href="{$fid}-tpc-{count(preceding::topic)+1}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:otherwise>
            </xsl:choose>
          </div>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="note" mode="link"/>
  <xsl:template match="note" mode="text"/>

  <!--
      =========================================================================
      link
      =========================================================================
  -->
  <xsl:template match="link">
    <a class="pdocLink">
      <xsl:apply-templates select="." mode="href"/>
      <xsl:apply-templates select="." mode="content"/>
    </a>
  </xsl:template>

  <xsl:template match="link" mode="href">
    <xsl:attribute name="href">
      <xsl:choose>
        <xsl:when test="@idref">
          <xsl:call-template name="link_idref">
            <xsl:with-param name="target" select="id(@idref)"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

  <xsl:template name="link_idref">
    <xsl:param name="target"/>
    <xsl:choose>
      <xsl:when test="not($onefile) and name($target)='topic'">
        <xsl:value-of
            select="concat($fid, '-tpc-', count($target/preceding::topic)+1,
                    $html_ext)"/>
      </xsl:when>
      <xsl:when test="$onefile or
                      (count(preceding::topic)=count($target/preceding::topic)
                      and not(ancestor::note))">
        <xsl:value-of select="concat('#', $target/@xml:id)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of
            select="concat($fid, '-tpc-', count($target/preceding::topic)+1,
                    $html_ext, '#', $target/@xml:id)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="link" mode="content">
    <xsl:choose>
      <xsl:when test="normalize-space() or node()"><xsl:apply-templates/></xsl:when>
      <xsl:when test="ancestor::hotspot"><xsl:text> </xsl:text></xsl:when>
      <xsl:when test="@idref"><xsl:value-of select="@idref"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="link" mode="link">
    <xsl:apply-templates select="." mode="content"/>
  </xsl:template>

  <!--
      =========================================================================
      anchor
      =========================================================================
  -->
  <xsl:template match="anchor">
    <a id="{@xml:id}" class="pdocAnchor">
      <xsl:choose>
        <xsl:when test=".//text()"><xsl:apply-templates/></xsl:when>
        <xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
      </xsl:choose>
    </a>
  </xsl:template>

  <xsl:template match="anchor" mode="link">
    <xsl:apply-templates mode="link"/>
  </xsl:template>

  <!--
      =========================================================================
      smil
      =========================================================================
  -->
  <xsl:template match="smil">
    <span id="s{count(preceding::smil)+1}" class="pdocSmil">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <xsl:template match="smil" mode="link">
    <xsl:apply-templates mode="link"/>
  </xsl:template>

  <!--
      =========================================================================
      Miscellaneous
      =========================================================================
  -->
  <xsl:template match="acronym">
    <span class="pdocAcronym"><xsl:apply-templates/></span>
  </xsl:template>
  <xsl:template match="acronym" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <xsl:template match="term">
    <em class="pdocTerm"><xsl:apply-templates/></em>
  </xsl:template>
  <xsl:template match="term" mode="link">
    <em class="pdocTerm"><xsl:apply-templates mode="link"/></em>
  </xsl:template>

  <xsl:template match="foreign">
    <em class="pdocForeign"><xsl:apply-templates/></em>
  </xsl:template>
  <xsl:template match="foreign" mode="link">
    <em class="pdocForeign"><xsl:apply-templates mode="link"/></em>
  </xsl:template>

  <xsl:template match="literal">
    <span class="pdocLiteral"><xsl:apply-templates/></span>
  </xsl:template>
  <xsl:template match="literal" mode="link">
    <span class="pdocLiteral"><xsl:apply-templates mode="link"/></span>
  </xsl:template>

  <xsl:template match="highlight">
    <strong class="pdocHighlight"><xsl:apply-templates/></strong>
  </xsl:template>
  <xsl:template match="highlight" mode="link">
    <strong class="pdocHighlight"><xsl:apply-templates mode="link"/></strong>
  </xsl:template>

  <xsl:template match="emphasis">
    <em class="pdocEmphasis"><xsl:apply-templates/></em>
  </xsl:template>
  <xsl:template match="emphasis" mode="link">
    <em class="pdocEmphasis"><xsl:apply-templates mode="link"/></em>
  </xsl:template>

  <xsl:template match="mentioned">
    <em class="pdocMentioned"><xsl:apply-templates/></em>
  </xsl:template>
  <xsl:template match="mentioned" mode="link">
    <em class="pdocMentioned"><xsl:apply-templates mode="link"/></em>
  </xsl:template>

  <xsl:template match="warning">
    <span id="w{count(preceding::warning)+1}"
          class="pdocWarning"><xsl:apply-templates/></span>
  </xsl:template>
  <xsl:template match="warning" mode="link">
    <xsl:apply-templates mode="link"/>
  </xsl:template>

</xsl:stylesheet>
