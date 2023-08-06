<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiquiz2html5_base.inc.xsl a580f30b6990 2015/02/17 17:17:11 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:date="http://exslt.org/dates-and-times"
                xmlns:pf="http://publiforge.org/functions"
                extension-element-prefixes="date pf">

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
    <xsl:if test="$toc">
      <h2><xsl:value-of select="$i18n_toc"/></h2>
      <div class="pdocOneFile pdocToc">
        <ul>
          <xsl:apply-templates select="division|topic|quiz" mode="onefiletoc"/>
        </ul>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="quiz" mode="onefiletoc">
    <xsl:if test="$toc and ancestor::document">
      <li>
        <a>
          <xsl:attribute name="href">
            <xsl:text>#</xsl:text>
            <xsl:choose>
              <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
              <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('quz', count(preceding::quiz)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:call-template name="quiz_toc_title"/>
        </a>
      </li>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode onefile
      =========================================================================
  -->
  <xsl:template match="quiz" mode="onefile">
    <div>
      <xsl:attribute name="id">
        <xsl:choose>
          <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
          <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat('quz', count(preceding::quiz)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="class">
        <xsl:text>pquizQuiz pquizQuizOneFile</xsl:text>
        <xsl:if test="@type"> pquizQuiz-<xsl:value-of select="@type"/></xsl:if>
        <xsl:if test="ancestor::division">
          <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:if test="head/title">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h2><xsl:apply-templates select="head/title"/></h2>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=1">
            <h3><xsl:apply-templates select="head/title"/></h3>
          </xsl:when>
          <xsl:otherwise>
            <h4><xsl:apply-templates select="head/title"/></h4>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h3><xsl:call-template name="subtitle"/></h3>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=1">
            <h4><xsl:call-template name="subtitle"/></h4>
          </xsl:when>
          <xsl:otherwise>
            <h5><xsl:call-template name="subtitle"/></h5>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:apply-templates select="." mode="corpus"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode toc
      =========================================================================
  -->
  <xsl:template match="quiz" mode="toc">
    <li id="quz{count(preceding::quiz)+1}">
      <a href="{$fid}-quz-{count(preceding::quiz)+1}{$html_ext}">
        <xsl:call-template name="quiz_toc_title"/>
      </a>
    </li>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode file
      =========================================================================
  -->
  <xsl:template match="quiz" mode="file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name"
                      select="concat($fid, '-quz-', count(preceding::quiz)+1)"/>

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
            <xsl:text>pquizQuiz</xsl:text>
            <xsl:if test="@type"> pquizQuiz-<xsl:value-of select="@type"/></xsl:if>
            <xsl:if test="ancestor::division">
              <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
              <xsl:for-each select="ancestor::division">
                <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
              </xsl:for-each>
            </xsl:if>
          </xsl:attribute>
          <xsl:call-template name="navigation"/>
          <xsl:call-template name="lead"/>
          <xsl:call-template name="anchor_levels"/>

          <xsl:if test="head/title">
            <h1><xsl:apply-templates select="head/title"/></h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2><xsl:call-template name="subtitle"/></h2>
          </xsl:if>
          <form action="#" method="post">
            <xsl:apply-templates select="." mode="corpus"/>
            <xsl:call-template name="quiz_messages"/>
            <xsl:call-template name="quiz_submit"/>
            <xsl:call-template name="quiz_configuration"/>
          </form>

          <xsl:call-template name="navigation">
            <xsl:with-param name="bottom" select="1"/>
          </xsl:call-template>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode corpus
      =========================================================================
  -->
  <xsl:template match="quiz" mode="corpus">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine"/>
    </xsl:variable>
    <xsl:variable name="engine_options">
      <xsl:call-template name="quiz_engine_options"/>
    </xsl:variable>

    <div class="publiquiz" data-quiz-id="{$quiz_id}" data-engine="{$engine}">
      <xsl:if test="$engine_options!=''">
        <xsl:attribute name="data-engine-options">
          <xsl:value-of select="normalize-space($engine_options)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="instructions"/>
      <xsl:apply-templates
          select="choices-radio|choices-check
                  |blanks-fill|blanks-select|blanks-char
                  |pointing|pointing-categories|matching|sort|categories|pip
                  |production|composite"/>
      <xsl:apply-templates select="help|answer"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      subquiz
      =========================================================================
  -->
  <xsl:template match="subquiz">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine"/>
    </xsl:variable>
    <xsl:variable name="engine_options">
      <xsl:call-template name="quiz_engine_options"/>
    </xsl:variable>

    <li class="pquizElement" data-quiz-id="{$quiz_id}" data-engine="{$engine}">
      <xsl:if test="$engine_options!=''">
        <xsl:attribute name="data-engine-options">
          <xsl:value-of select="normalize-space($engine_options)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="instructions"/>
      <xsl:apply-templates
          select="choices-radio|choices-check
                  |blanks-fill|blanks-select|blanks-char
                  |pointing|pointing-categories|matching|sort|categories|pip
                  |production"/>
      <xsl:apply-templates select="help|answer"/>
    </li>
  </xsl:template>


  <!--
      *************************************************************************
                                   SECTION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      instructions
      =========================================================================
  -->
  <xsl:template match="instructions">
    <div class="pquizInstructions">
      <xsl:if test="head/title">
        <div class="pquizInstructionsTitle">
          <xsl:apply-templates select="head/title"/>
        </div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pquizInstructionsSubtitle">
          <xsl:call-template name="subtitle"/>
        </div>
      </xsl:if>
      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>
      <xsl:apply-templates select="head/audio" mode="header"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      choices-radio & choices-check
      =========================================================================
  -->
  <xsl:template match="choices-radio|choices-check">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="right">
          <xsl:value-of select="format-number(count(preceding-sibling::right
                                |preceding-sibling::wrong)+1, '000')"/>
          <xsl:text>x</xsl:text>
          <xsl:if test="count(following-sibling::right)">::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:choose>
        <xsl:when test="$mode_choices_check='radio'">
          <xsl:call-template name="choices_check_mode_radio">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="choices_basic">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="choices_basic">
    <xsl:param name="quiz_id"/>
    <ul class="pquizChoices">
      <xsl:for-each select="right|wrong">
        <li id="{concat($quiz_id, '_', format-number(
                count(preceding-sibling::right|preceding-sibling::wrong)+1, '000'))}"
            class="pquizChoice">
          <input>
            <xsl:choose>
              <xsl:when test="name(..)='choices-radio'">
                <xsl:attribute name="name"><xsl:value-of select="$quiz_id"/></xsl:attribute>
                <xsl:attribute name="type">radio</xsl:attribute>
              </xsl:when>
              <xsl:when test="name(..)='choices-check'">
                <xsl:attribute name="type">checkbox</xsl:attribute>
              </xsl:when>
            </xsl:choose>
          </input>
          <xsl:text> </xsl:text>
          <xsl:choose>
            <xsl:when test="p">
              <xsl:apply-templates select="p/node()"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:apply-templates/>
              </xsl:otherwise>
            </xsl:choose>
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <xsl:template name="choices_check_mode_radio">
    <xsl:param name="quiz_id"/>
    <table>
      <tr>
        <th> </th>
        <th><xsl:value-of select="$i18n_true"/></th>
        <th><xsl:value-of select="$i18n_false"/></th>
      </tr>
      <xsl:for-each select="right|wrong">
        <tr>
          <td><xsl:apply-templates/></td>
          <td class="pquizChoice"
              data-group="{format-number(count(preceding-sibling::*)+1, '000')}"
              data-name="true">
            <input type="radio">
              <xsl:attribute name="name">
                <xsl:value-of select="concat($quiz_id, '-', count(preceding-sibling::*))"/>
              </xsl:attribute>
            </input>
          </td>
          <td class="pquizChoice"
              data-group="{format-number(count(preceding-sibling::*)+1, '000')}"
              data-name="false">
            <input type="radio">
              <xsl:attribute name="name">
                <xsl:value-of select="concat($quiz_id, '-', count(preceding-sibling::*))"/>
              </xsl:attribute>
            </input>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
      =========================================================================
      blanks-fill
      =========================================================================
  -->
  <xsl:template match="blanks-fill">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="s">
              <xsl:for-each select="s">
                <xsl:value-of select="normalize-space()"/>
                <xsl:if test="count(following-sibling::s)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="normalize-space()"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      blanks-select
      =========================================================================
  -->
  <xsl:template match="blanks-select">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank[not(ancestor::intruders)]">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="s">
              <xsl:for-each select="s">
                <xsl:call-template name="make_id">
                  <xsl:with-param name="item" select="."/>
                </xsl:call-template>
                <xsl:if test="count(following-sibling::s)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="make_id">
                <xsl:with-param name="item" select="."/>
              </xsl:call-template>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank[not(ancestor::intruders)]))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <div id="{$quiz_id}_items" class="pquizItems">
        <xsl:for-each select=".//blank|intruders/blank">
          <!-- <xsl:sort select="normalize-space()"/> -->
          <xsl:if test="not(ancestor::blanks-select[@multiple='true']) or
                        count(preceding::blank[normalize-space()=normalize-space(current())])
                        -count(ancestor::blanks-select/preceding::blank[normalize-space()=normalize-space(current())])=0">
            <span draggable="true" class="pquizItem">
              <xsl:attribute name="id">
                <xsl:value-of
                    select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
              </xsl:attribute>
              <xsl:attribute name="data-item-value">
                <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
              </xsl:attribute>
              <xsl:value-of select="normalize-space()"/>
              <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
            </span>
          </xsl:if>
        </xsl:for-each>
        <xsl:if test="not(.//blank)"><xsl:text> </xsl:text></xsl:if>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      blanks-char
      =========================================================================
  -->
  <xsl:template match="blanks-char">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank">
          <xsl:call-template name="blank_num"/>
          <xsl:value-of select="."/>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(.//blank)"><xsl:text> </xsl:text></xsl:if>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      pointing
      =========================================================================
  -->
  <xsl:template match="pointing">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//point[@ref]">
          <xsl:call-template name="point_num"/>
          <xsl:text>x</xsl:text>
          <xsl:call-template name="point_separator"/>
        </xsl:for-each>
        <xsl:if test="not(.//point[@ref])"><xsl:text> </xsl:text></xsl:if>
      </div>

      <div class="pquizText">
        <xsl:apply-templates/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      pointing-categories
      =========================================================================
  -->
  <xsl:template match="pointing-categories">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="preceding_point" select="count(preceding::point)"/>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//point">
          <xsl:value-of select="format-number(substring(@ref, 4), '000')"/>
          <xsl:value-of
              select="format-number(count(preceding::point)-$preceding_point+1,
                      '000')"/>
          <xsl:if test="count(following::point)
                        &gt; count(ancestor::pointing-categories/following::point)"
                  >::</xsl:if>
        </xsl:for-each>
        <xsl:if test="not(.//point)"><xsl:text> </xsl:text></xsl:if>
      </div>

      <div id="{$quiz_id}_categories" class="pquizCategories">
        <xsl:for-each select="categories/category">
          <span class="pquizCategory"
                data-category-id="{format-number(@id, '000')}">
            <xsl:apply-templates/>
            <span class="pquizCategoryColor pquizBgColor{@id}"> </span>
          </span>
        </xsl:for-each>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      matching
      =========================================================================
  -->
  <xsl:template match="matching">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="match">
          <xsl:sort select="normalize-space(item[2])"/>
          <xsl:value-of select="format-number(count(preceding-sibling::match)+1, '000')"/>
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="item[2]"/>
          </xsl:call-template>
          <xsl:if test="not(position()=last())">::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:choose>
        <!-- mode link -->
        <xsl:when test="(not(../processing-instruction('argument')) and $mode_matching='link')
                        or ../processing-instruction('argument')='link'
                        or contains(../../../processing-instruction('argument'), 'link')">
          <xsl:call-template name="matching_link">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode dragndrop -->
        <xsl:otherwise>
          <xsl:call-template name="matching_dragndrop">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="matching_dragndrop">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_items" class="pquizItems">
      <xsl:for-each select="intruders/item|match/item[2]">
        <xsl:sort select="normalize-space()"/>
        <xsl:if test="not(ancestor::matching[@multiple='true']) or
                      count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                           |preceding::item[image and image/@id=current()/image/@id])
                      -count(ancestor::matching/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                           |ancestor::matching/preceding::item[image and image/@id=current()/image/@id])=0">
          <span draggable="true" class="pquizItem">
            <xsl:attribute name="id">
              <xsl:value-of
                  select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
            </xsl:attribute>
            <xsl:attribute name="data-item-value">
              <xsl:call-template name="make_id">
                <xsl:with-param name="item" select="."/>
              </xsl:call-template>
              <xsl:if test="not(image or audio or video or normalize-space())">
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:attribute>
            <xsl:choose>
              <xsl:when test="not(image or audio or video)">
                <xsl:value-of select="normalize-space()"/>
                <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
              </xsl:when>
              <xsl:otherwise>
                <xsl:apply-templates/>
              </xsl:otherwise>
            </xsl:choose>
          </span>
        </xsl:if>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>

    <table class="pquizMatching">
      <xsl:choose>
        <xsl:when test="count(match) &gt; 10">
          <xsl:for-each select="match">
            <xsl:if test="position() mod 2=1">
              <tr>
                <td><xsl:apply-templates select="item[1]/node()"/></td>
                <td>  </td>
                <td id="{concat($quiz_id, '_',
                        format-number(count(preceding-sibling::match)+1, '000'))}"
                    class="pquizDrop">.................</td>
                <td>    </td>
                <td>
                  <xsl:if test="following-sibling::match">
                    <xsl:apply-templates select="following-sibling::match[1]/item[1]/node()"/>
                    </xsl:if>
                </td>
                <td>  </td>
                <td id="{concat($quiz_id, '_',
                        format-number(count(preceding-sibling::match)+2, '000'))}">
                    <xsl:if test="following-sibling::match">
                      <xsl:attribute name="class">pquizDrop</xsl:attribute>
                      <xsl:text>.................</xsl:text>
                    </xsl:if>
                </td>
              </tr>
            </xsl:if>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
            <xsl:for-each select="match">
              <tr>
                <td><xsl:apply-templates select="item[1]/node()"/></td>
                <td>  </td>
                <td id="{concat($quiz_id, '_',
                        format-number(count(preceding-sibling::match)+1, '000'))}"
                    class="pquizDrop">.................</td>
              </tr>
            </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </table>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="matching_link">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_items_left" class="pquizMatchingLinkItems">
      <xsl:for-each select="match">
        <span id="{concat($quiz_id, '_',
                  format-number(count(preceding-sibling::match)+1, '000'))}"
              class="pquizMatchingLinkItem">
          <xsl:apply-templates select="item[1]/node()"/>
        </span>
      </xsl:for-each>
    </div>

    <canvas id="{$quiz_id}_canvas" width="300">
      <xsl:value-of select="$i18n_nocanvas"/>
    </canvas>

    <div id="{$quiz_id}_items_right" class="pquizMatchingLinkItems">
      <xsl:for-each select="intruders/item|match/item[2]">
        <xsl:sort select="normalize-space()"/>
        <span class="pquizMatchingLinkItem">
          <xsl:attribute name="data-item-value">
            <xsl:call-template name="make_id">
              <xsl:with-param name="item" select="."/>
            </xsl:call-template>
          </xsl:attribute>
           <xsl:choose>
            <xsl:when test="not(image or audio or video)">
              <xsl:value-of select="normalize-space()"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates/>
            </xsl:otherwise>
          </xsl:choose>
        </span>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      sort
      =========================================================================
  -->
  <xsl:template match="sort">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="item">
          <xsl:value-of select="format-number(count(preceding-sibling::item)+1, '000')"/>
          <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
          <xsl:if test="count(following-sibling::item)">::</xsl:if>
       </xsl:for-each>
      </div>

      <div id="{$quiz_id}_items" class="pquizItems">
        <xsl:for-each select="item">
          <xsl:sort select="@shuffle"/>
          <span draggable="true" class="pquizItem">
            <xsl:attribute name="id">
              <xsl:value-of
                  select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
            </xsl:attribute>
            <xsl:attribute name="data-item-value">
              <xsl:call-template name="make_id">
                <xsl:with-param name="item" select="."/>
              </xsl:call-template>
              <xsl:if test="not(image or audio or video or normalize-space())">
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:attribute>
            <xsl:choose>
              <xsl:when test="not(image or audio or video)">
                <xsl:value-of select="normalize-space()"/>
                <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
              </xsl:when>
              <xsl:otherwise>
                <xsl:apply-templates/>
              </xsl:otherwise>
            </xsl:choose>
          </span>
        </xsl:for-each>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:for-each select="item">
          <span
              id="{concat($quiz_id, '_',
                  format-number(count(preceding-sibling::item)+1, '000'))}"
              class="pquizDrop">.................</span>
          <xsl:if test="../comparison and count(following-sibling::item)">
            <xsl:text> </xsl:text>
            <xsl:apply-templates select="../comparison"/>
          </xsl:if>
          <xsl:text> </xsl:text>
        </xsl:for-each>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      categories
      =========================================================================
  -->
  <xsl:template match="categories">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="category/item">
          <xsl:value-of
              select="format-number(count(ancestor::category/preceding-sibling::category)+1, '000')"/>
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="."/>
          </xsl:call-template>
          <xsl:if test="count(following-sibling::item|ancestor::category/following-sibling::category)"
                  >::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:choose>
        <xsl:when test="(not(../processing-instruction('argument')) and $mode_categories='color')
                        or ../processing-instruction('argument')='color'
                        or contains(../../../processing-instruction('argument'), 'color')">
          <xsl:call-template name="categories_color">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
       </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="categories_basket">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_color">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_categories" class="pquizCategories">
      <xsl:for-each select="category">
        <span class="pquizCategory"
              data-category-id="{format-number(count(preceding-sibling::category)+1, '000')}">
          <xsl:apply-templates select="head/title"/>
          <span class="pquizCategoryColor pquizBgColor{count(preceding-sibling::category)+1}"> </span>
        </span>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
    <ul class="pquizCategoriesChoices">
      <xsl:for-each select="category/item">
        <xsl:sort/>
        <xsl:if test="not(ancestor::categories[@multiple='true']) or
                      count(preceding::item[normalize-space()=normalize-space(current())])
                      -count(ancestor::categories/preceding::item[normalize-space()=normalize-space(current())])=0">
          <li class="pquizChoice">
            <xsl:attribute name="data-choice-value">
              <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
            </xsl:attribute>
            <xsl:apply-templates/>
          </li>
        </xsl:if>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_basket">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_items" class="pquizCategoriesItems">
      <xsl:for-each select="intruders/item|category/item">
        <xsl:sort/>
        <xsl:if test="not(ancestor::categories[@multiple='true']) or
                      count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                      |preceding::item[image and image/@id=current()/image/@id])
                      -count(ancestor::categories/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                      |ancestor::categories/preceding::item[image and image/@id=current()/image/@id])=0">
          <span draggable="true" class="pquizCategoryItem">
            <xsl:attribute name="id">
              <xsl:value-of
                  select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
            </xsl:attribute>
            <xsl:attribute name="data-item-value">
              <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
              <xsl:if test="not(image or audio or video or normalize-space())">
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:attribute>
            <xsl:apply-templates/>
          </span>
        </xsl:if>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
    <div class="pquizCategoriesDrops">
      <xsl:for-each select="category">
        <div class="pquizCategoriesBasket">
          <div class="legend"><xsl:apply-templates select="head/title"/></div>
          <div id="{$quiz_id}_{format-number(count(preceding-sibling::category)+1, '000')}"
               class="pquizCategoryDrop">
            <xsl:text> </xsl:text>
          </div>
        </div>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
  </xsl:template>

  <!--
      =========================================================================
      pip
      =========================================================================
  -->
  <xsl:template match="pip">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="image/dropzone">
          <xsl:value-of
              select="format-number(count(preceding-sibling::dropzone)+1, '000')"/>
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="."/>
          </xsl:call-template>
          <xsl:if test="count(following-sibling::dropzone)">::</xsl:if>
       </xsl:for-each>
      </div>

      <div id="{$quiz_id}_items" class="pquizItems">
        <xsl:for-each select="image/dropzone">
          <xsl:if test="image and (not(ancestor::pip[@multiple='true']) or
                        count(preceding-sibling::dropzone[image/@id=current()/image/@id])=0)">
            <span draggable="true" class="pquizItem">
              <xsl:attribute name="id">
                <xsl:value-of
                    select="concat($quiz_id, '_item',
                            format-number(count(preceding-sibling::dropzone)+1, '000'))"/>
               </xsl:attribute>
              <xsl:attribute name="data-item-value">
                <xsl:call-template name="make_id">
                  <xsl:with-param name="item" select="."/>
                </xsl:call-template>
              </xsl:attribute>
              <xsl:apply-templates/>
            </span>
          </xsl:if>
        </xsl:for-each>
        <xsl:if test="not(image/dropzone/*)">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pdocMedia">
        <div class="pdocImage pdocImageDropzone">
          <xsl:apply-templates select="image"/>
          <xsl:for-each select="image/dropzone">
            <div class="pquizDropzone pquizDropzone-visible pquizDrop"
                 id="{concat($quiz_id, '_',
                     format-number(count(preceding-sibling::dropzone)+1, '000'))}"
                 style="{concat('position: absolute; left:', @x, '; top:', @y,
                        '; width:', @w, '; height:', @h)}">
              <xsl:text> </xsl:text>
            </div>
          </xsl:for-each>
        </div>
        <div class="clear"><xsl:text> </xsl:text></div>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      production
      =========================================================================
  -->
  <xsl:template match="production">
    <div class="pquizEngine">
      <textarea cols="50" rows="5" class="pquizProduction">
        <xsl:text> </xsl:text>
      </textarea>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      composite
      =========================================================================
  -->
  <xsl:template match="composite">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <ol id="{$quiz_id}_engine" class="pquizElements">
      <xsl:apply-templates select="subquiz"/>
    </ol>
  </xsl:template>

  <!--
      =========================================================================
      help
      =========================================================================
  -->
  <xsl:template match="help">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div class="pquizHelpButton">
      <a href='#{$quiz_id}_help-slot' id="{$quiz_id}_help-link">
        <xsl:attribute name="class">
          <xsl:text>pquizButton</xsl:text>
          <xsl:apply-templates select="link" mode="class"/>
        </xsl:attribute>
        <xsl:value-of select="$i18n_help"/>
      </a>
    </div>
    <fieldset id="{$quiz_id}_help-slot" class="pquizHelpText">
      <legend> <xsl:value-of select="$i18n_help"/> </legend>
      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>
    </fieldset>
  </xsl:template>

  <xsl:template match="link" mode="include">
    <xsl:if test="@uri">
      <xsl:if test="//topic[@id=current()/@uri]/head/title">
        <h1><xsl:apply-templates select="//topic[@id=current()/@uri]/head/title"/></h1>
      </xsl:if>
      <xsl:apply-templates select="//topic[@id=current()/@uri]" mode="corpus"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      answer
      =========================================================================
  -->
  <xsl:template match="answer">
    <xsl:if test="not(ancestor::right|ancestor::wrong)">
      <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
      <fieldset id="{$quiz_id}_answer-slot" class="pquizAnswerText">
        <legend> <xsl:value-of select="$i18n_answer"/> </legend>
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </fieldset>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      dropzone
      =========================================================================
  -->
  <xsl:template match="dropzone">
    <div class="pquizDropzone">
      <xsl:attribute name="style">
        <xsl:value-of
            select="concat('position: absolute; left:', @x, '; top:', @y, ';')"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template note_file
      =========================================================================
  -->
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
              <xsl:when test="(name(//*/*)='topic' or name(//*/*)='quiz')
                              and not(contains($path, 'Container~/'))">
                <a href="{$fid}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:when test="ancestor::quiz">
                <a href="{$fid}-quz-{count(preceding::quiz)+1}{$html_ext}#n{count(preceding::note)+1}">
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

  <!--
      =========================================================================
      blank
      =========================================================================
  -->
  <xsl:template match="blank">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <xsl:choose>
      <xsl:when test="ancestor::blanks-fill">
        <input type="text" class="pquizChoice">
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="blank_num"/>
          </xsl:attribute>
        </input>
      </xsl:when>

      <xsl:when test="ancestor::blanks-select">
        <span class="pquizDrop">
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="blank_num"/>
          </xsl:attribute>
          <xsl:text>.................</xsl:text>
        </span>
      </xsl:when>

      <xsl:when test="ancestor::blanks-char and @function">
        <xsl:apply-templates/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      point
      =========================================================================
  -->
  <xsl:template match="point">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <span>
      <xsl:attribute name="class">
        <xsl:text>pquizPoint</xsl:text>
        <xsl:if test="image or audio or video"> pquizPointMedia</xsl:if>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="ancestor::pointing-categories">
          <xsl:attribute name="data-choice-id">
            <xsl:value-of
                select="format-number(count(preceding::point)
                        -count(ancestor::pointing-categories/preceding::point)+1,
                        '000')"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="point_num"/>
          </xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

</xsl:stylesheet>
