<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiquiz_edit.xsl be4bc702f956 2014/12/03 16:50:19 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_edit.xsl"/>
  <xsl:import href="publiquiz_template.inc.xsl"/>

  <!--
      =========================================================================
      publiquiz
      =========================================================================
  -->
  <xsl:template match="publiquiz">
    <xsl:choose>
      <xsl:when test="$mode='variables'">
        <publiforge version="1.0">
          <variables>
            <xsl:apply-templates
                select="document|topic|quiz" mode="variables"/>
          </variables>
        </publiforge>
      </xsl:when>
      <xsl:when test="$mode='html'">
        <xsl:apply-templates select="document|topic|quiz" mode="html"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode variables
      =========================================================================
  -->
  <xsl:template match="quiz" mode="variables">
    <xsl:variable name="num" select="count(preceding::quiz)"/>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
    <xsl:apply-templates select="$variables_doc/*/*/group[@name='quiz']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode html
      =========================================================================
  -->
  <xsl:template match="quiz" mode="html">
    <xsl:variable name="num" select="count(preceding::quiz)"/>

    <div class="pquizQuiz">
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="html_table">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='quiz']"
                           mode="html_div_quiz">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                       GROUP
      *************************************************************************
  -->
  <!--
      =========================================================================
      group mode html_div_quiz
      =========================================================================
  -->
  <xsl:template match="group" mode="html_div_quiz">
    <xsl:param name="num"/>
    <xsl:param name="node"/>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>

    <xsl:apply-templates select="var[@name='instructions']" mode="html_div">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
    </xsl:apply-templates>

    <xsl:apply-templates select="var[@name=$engine]" mode="html_div">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
    </xsl:apply-templates>

    <xsl:apply-templates
        select="var[@name='help' or @name='answer']" mode="html_div">
      <xsl:with-param name="group" select="concat(@name, $num)"/>
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
      <xsl:choose>
        <xsl:when test="@name='instructions'">
          <xsl:copy-of select="$node/instructions/node()"/>
        </xsl:when>

        <xsl:when test="@name='choices-radio'">
          <xsl:copy-of select="$node/choices-radio"/>
        </xsl:when>
        <xsl:when test="@name='choices-check'">
          <xsl:copy-of select="$node/choices-check"/>
        </xsl:when>

        <xsl:when test="@name='blanks-fill'">
          <xsl:copy-of select="$node/blanks-fill"/>
        </xsl:when>
        <xsl:when test="@name='blanks-select'">
          <xsl:copy-of select="$node/blanks-select"/>
        </xsl:when>

        <xsl:when test="@name='pointing'">
          <xsl:copy-of select="$node/pointing"/>
        </xsl:when>
        <xsl:when test="@name='pointing-categories'">
          <xsl:copy-of select="$node/pointing-categories"/>
        </xsl:when>

        <xsl:when test="@name='matching'">
          <xsl:copy-of select="$node/matching"/>
        </xsl:when>

        <xsl:when test="@name='sort'">
          <xsl:copy-of select="$node/sort"/>
        </xsl:when>

        <xsl:when test="@name='categories'">
          <xsl:copy-of select="$node/categories"/>
        </xsl:when>

        <xsl:when test="@name='pip'">
          <xsl:copy-of select="$node/pip"/>
        </xsl:when>

        <xsl:when test="@name='composite'">
          <xsl:copy-of select="$node/composite"/>
        </xsl:when>

        <xsl:when test="@name='help'">
          <xsl:copy-of select="$node/help/node()"/>
        </xsl:when>
        
        <xsl:when test="@name='answer'">
          <xsl:copy-of select="$node/answer/node()"/>
        </xsl:when>

        <xsl:otherwise>
          <xsl:call-template name="var_default">
            <xsl:with-param name="group" select="$group"/>
            <xsl:with-param name="node" select="$node"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
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

</xsl:stylesheet>
