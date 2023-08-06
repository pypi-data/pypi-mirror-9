<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_edit_base.inc.xsl 4650ee178855 2014/12/07 08:11:04 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                       GROUP
      *************************************************************************
  -->
  <!--
      =========================================================================
      group mode variables
      =========================================================================
  -->
  <xsl:template match="group" mode="variables">
    <xsl:param name="num"/>
    <xsl:param name="node"/>

    <group name="{@name}{$num}">
      <xsl:copy-of select="label"/>
      <xsl:apply-templates select="var" mode="variables">
        <xsl:with-param name="group" select="concat(@name, $num)"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:apply-templates>
    </group>
  </xsl:template>

  <!--
      =========================================================================
      group mode html_table
      =========================================================================
  -->
  <xsl:template match="group" mode="html_table">
    <xsl:param name="num"/>
    <xsl:param name="node"/>

    <table>
      <xsl:attribute name="class">
        <xsl:value-of
            select="concat('pdocMeta pdocMeta-', @name, ' tableToolTip')"/>
      </xsl:attribute>
      <xsl:apply-templates select="var" mode="html_table">
        <xsl:with-param name="group" select="concat(@name, $num)"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:apply-templates>
    </table>
  </xsl:template>

  <!--
      =========================================================================
      group mode html_div
      =========================================================================
  -->
  <xsl:template match="group" mode="html_div">
    <xsl:param name="num"/>
    <xsl:param name="node"/>

    <xsl:apply-templates select="var" mode="html_div">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
      <xsl:with-param name="node" select="$node"/>
    </xsl:apply-templates>
  </xsl:template>


  <!--
      *************************************************************************
                                         VAR
      *************************************************************************
  -->
  <!--
      =========================================================================
      var mode variables
      =========================================================================
  -->
  <xsl:template match="var" mode="variables">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:variable name="default">
      <xsl:call-template name="var_default">
        <xsl:with-param name="group" select="$group"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>

    <var name="{$group}{@name}">
      <xsl:copy-of select="@type|@class|@cast|@rows"/>
      <xsl:if test="string-length($default)">
        <default>
          <xsl:copy-of select="$default"/>
        </default>
      </xsl:if>
      <xsl:copy-of select="pattern|option|label"/>
    </var>
  </xsl:template>

  <!--
      =========================================================================
      var mode html_table
      =========================================================================
  -->
  <xsl:template match="var" mode="html_table">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <tr>
      <td>
        <xsl:call-template name="localized_label"/>
      </td>
      <td>
        <xsl:if test="not(description)">
          <xsl:attribute name="colspan">2</xsl:attribute>
        </xsl:if>
        <xsl:value-of select="concat('__', $group, @name, '__')"/>
      </td>
      <xsl:if test="description">
        <td class="pdocMetaToolTip">
          <input type="image" name="des!{../@name}:{@name}" class="toolTip"
                 src="{$main_route}Images/action_help_one.png" alt="tooltip"/>
        </td>
      </xsl:if>
    </tr>
  </xsl:template>

  <!--
      =========================================================================
      var mode html_div
      =========================================================================
  -->
  <xsl:template match="var" mode="html_div">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <div>
      <h3>
        <xsl:attribute name="class">
          <xsl:value-of select="concat('pdocVariable pdocVariable-', @name)"/>
        </xsl:attribute>
        <xsl:call-template name="localized_label"/>
      </h3>
      <xsl:value-of select="concat('__', $group, @name, '__')"/>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                   CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template var_default
      =========================================================================
  -->
  <xsl:template name="var_default">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:choose>
      <!-- Head attributes -->
      <xsl:when test="@name='id'">
        <xsl:value-of select="$node/@id"/>
      </xsl:when>
      <xsl:when test="@name='xml:id'">
        <xsl:value-of select="$node/@xml:id"/>
      </xsl:when>
      <xsl:when test="@name='type'">
        <xsl:value-of select="$node/@type"/>
      </xsl:when>
      <xsl:when test="@name='xml:lang'">
        <xsl:value-of select="$node/@xml:lang"/>
      </xsl:when>

      <!-- Head element -->
      <xsl:when test="@name='title'">
        <xsl:copy-of select="$node/head/title/node()"/>
      </xsl:when>
      <xsl:when test="@name='shorttitle'">
        <xsl:copy-of select="$node/head/shorttitle/node()"/>
      </xsl:when>
      <xsl:when test="@name='subtitle'">
        <xsl:copy-of select="$node/head/subtitle[1]/node()"/>
      </xsl:when>
      <xsl:when test="@name='identifier_ean'">
        <xsl:copy-of
            select="$node/head/identifier[@type='ean' and not(@for)]/node()"/>
      </xsl:when>
      <xsl:when test="@name='identifier_uri'">
        <xsl:copy-of select="$node/head/identifier[@type='uri']/node()"/>
      </xsl:when>
      <xsl:when test="@name='copyright'">
        <xsl:copy-of select="$node/head/copyright/node()"/>
      </xsl:when>
      <xsl:when test="@name='collection'">
        <xsl:copy-of select="$node/head/collection/node()"/>
      </xsl:when>
      <xsl:when test="@name='contributors'">
        <xsl:copy-of select="$node/head/contributors/node()"/>
      </xsl:when>
      <xsl:when test="@name='date'">
        <xsl:value-of select="$node/head/date/@value"/>
      </xsl:when>
      <xsl:when test="@name='place'">
        <xsl:copy-of select="$node/head/place/node()"/>
      </xsl:when>
      <xsl:when test="@name='source_book'">
        <xsl:copy-of select="$node/head/source[@type='book']/node()"/>
      </xsl:when>
      <xsl:when test="@name='source_file'">
        <xsl:copy-of select="$node/head/source[@type='file']/node()"/>
      </xsl:when>
      <xsl:when test="@name='keywordset'">
        <xsl:copy-of select="$node/head/keywordset/node()"/>
      </xsl:when>
      <xsl:when test="@name='subjectset'">
        <xsl:copy-of select="$node/head/subjectset/node()"/>
      </xsl:when>
      <xsl:when test="@name='abstract'">
        <xsl:copy-of select="$node/head/abstract/node()"/>
      </xsl:when>
      <xsl:when test="@name='cover'">
        <xsl:value-of select="$node/head/cover/image/@id"/>
      </xsl:when>
      <xsl:when test="@name='annotation'">
        <xsl:copy-of select="$node/head/annotation/node()"/>
      </xsl:when>

      <!-- Corpus -->
      <xsl:when test="@name='document' or @name='topic' or @name='quiz'">
        <xsl:copy-of
            select="$node/division|$node/topic|$node/quiz
                    |$node/header|$node/section|$node/bibliography|$node/footer
                    |$node/comment()|$node/processing-instruction()"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template localized_label
      =========================================================================
  -->
  <xsl:template name="localized_label">
    <xsl:param name="node" select="label"/>

    <xsl:choose>
      <xsl:when test="$node[@xml:lang=$lang]">
        <xsl:apply-templates select="$node[@xml:lang=$lang]"/>
      </xsl:when>
      <xsl:when test="$node[starts-with($lang, @xml:lang)]">
        <xsl:apply-templates select="$node[starts-with($lang, @xml:lang)][1]"/>
      </xsl:when>
      <xsl:when test="$node[@xml:lang='en']">
        <xsl:apply-templates select="$node[@xml:lang='en']"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="$node[1]"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
