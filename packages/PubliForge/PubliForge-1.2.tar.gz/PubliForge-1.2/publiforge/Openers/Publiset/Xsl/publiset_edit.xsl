<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_edit.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_edit_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->
  <xsl:param name="variables"/>   <!-- Full path to variable file -->
  <xsl:param name="mode"/>        <!-- variables or html -->

  <!-- Variables -->
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="variables_doc" select="document($variables)"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>


  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:choose>
      <xsl:when test="$mode='variables'">
        <publiforge version="1.0">
          <variables>
            <xsl:apply-templates select="composition|selection" mode="variables"/>
          </variables>
        </publiforge>
      </xsl:when>
      <xsl:when test="$mode='html'">
        <xsl:apply-templates select="composition|selection" mode="html"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


  <!--
      *************************************************************************
                                     COMPOSITION
      *************************************************************************
  -->
  <!--
      =========================================================================
      composition mode variables
      =========================================================================
  -->
  <xsl:template match="composition" mode="variables">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <group name="head{$num}">
      <label xml:lang="en">Head</label>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_head']/var"
          mode="variables">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='composition_head_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:if>
    </group>

    <xsl:choose>
      <xsl:when test="head or not(division)">
        <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                             mode="variables">
          <xsl:with-param name="num" select="$num"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="division" mode="variables_composition"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      division mode variables_composition
      =========================================================================
  -->
  <xsl:template match="division" mode="variables_composition">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <group name="head{$num}">
      <label xml:lang="en">Head <xsl:value-of select="$num"/></label>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_division_head']/var"
          mode="variables">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='composition_head_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:if>
    </group>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      composition mode html
      =========================================================================
  -->
  <xsl:template match="composition" mode="html">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <div class="pdocComposition">
      <h2>Composition</h2>
      <xsl:call-template name="title"/>
      <table class="pdocTransformAttributes tableToolTip">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='composition_head']/var"
            mode="html_table">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
        <xsl:if test="head">
          <xsl:apply-templates
              select="$variables_doc/*/*/group[@name='composition_head_head']/var"
              mode="html_table">
            <xsl:with-param name="group" select="concat('head', $num)"/>
            <xsl:with-param name="node" select="."/>
          </xsl:apply-templates>
        </xsl:if>
       </table>
       <xsl:if test="head">
         <table class="pdocMeta tableToolTip">
         <xsl:apply-templates
             select="$variables_doc/*/*/group[@name='common_head']/var"
             mode="html_table">
           <xsl:with-param name="group" select="concat('head', $num)"/>
           <xsl:with-param name="node" select="."/>
         </xsl:apply-templates>
         </table>
       </xsl:if>

       <xsl:choose>
         <xsl:when test="head or not(division)">
           <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                                mode="html_div">
             <xsl:with-param name="num" select="$num"/>
             <xsl:with-param name="node" select="."/>
           </xsl:apply-templates>
         </xsl:when>
         <xsl:otherwise>
           <xsl:apply-templates select="division" mode="html_composition"/>
         </xsl:otherwise>
       </xsl:choose>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      division mode html_composition
      =========================================================================
  -->
  <xsl:template match="division" mode="html_composition">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <xsl:call-template name="title"/>
    <table class="pdocTransformAttributes tableToolTip">
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_division_head']/var"
          mode="html_table">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='composition_head_head']/var"
            mode="html_table">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:if>
    </table>
    <xsl:if test="head">
      <table class="pdocMeta tableToolTip">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="html_table">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </table>
    </xsl:if>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                         mode="html_div">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>


  <!--
      *************************************************************************
                                      SELECTION
      *************************************************************************
  -->
  <!--
      =========================================================================
      selection mode variables
      =========================================================================
  -->
  <xsl:template match="selection" mode="variables">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <group name="head{$num}">
      <label xml:lang="en">Head</label>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_head']/var"
          mode="variables">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:if>
    </group>

    <xsl:choose>
      <xsl:when test="head or not(division)">
        <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                             mode="variables">
          <xsl:with-param name="num" select="$num"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="division" mode="variables_selection"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      division mode variables_selection
      =========================================================================
  -->
  <xsl:template match="division" mode="variables_selection">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <group name="head{$num}">
      <label xml:lang="en">Head <xsl:value-of select="$num"/></label>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_division_head']/var"
          mode="variables">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:if test="head">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="variables">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </xsl:if>
    </group>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                         mode="variables">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      selection mode html
      =========================================================================
  -->
  <xsl:template match="selection" mode="html">
    <xsl:variable name="num"
                  select="count(preceding::composition|preceding::selection)"/>

    <div class="pdocSelection">
      <h2>Selection</h2>
      <xsl:call-template name="title"/>
      <table class="pdocTransformAttributes tableToolTip">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='selection_head']/var"
            mode="html_table">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
       </table>
       <xsl:if test="head">
         <table class="pdocMeta tableToolTip">
         <xsl:apply-templates
             select="$variables_doc/*/*/group[@name='common_head']/var"
             mode="html_table">
           <xsl:with-param name="group" select="concat('head', $num)"/>
           <xsl:with-param name="node" select="."/>
         </xsl:apply-templates>
         </table>
       </xsl:if>

       <xsl:choose>
         <xsl:when test="head or not(division)">
           <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                                mode="html_div">
             <xsl:with-param name="num" select="$num"/>
             <xsl:with-param name="node" select="."/>
           </xsl:apply-templates>
         </xsl:when>
         <xsl:otherwise>
           <xsl:apply-templates select="division" mode="html_selection"/>
         </xsl:otherwise>
       </xsl:choose>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      division mode html_selection
      =========================================================================
  -->
  <xsl:template match="division" mode="html_selection">
    <xsl:variable name="num"
                  select="concat(count(preceding::composition|preceding::selection),
                          '.', count(preceding-sibling::division))"/>

    <xsl:call-template name="title"/>
    <table class="pdocTransformAttributes tableToolTip">
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_division_head']/var"
          mode="html_table">
        <xsl:with-param name="group" select="concat('head', $num)"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </table>
    <xsl:if test="head">
      <table class="pdocMeta tableToolTip">
        <xsl:apply-templates
            select="$variables_doc/*/*/group[@name='common_head']/var"
            mode="html_table">
          <xsl:with-param name="group" select="concat('head', $num)"/>
          <xsl:with-param name="node" select="."/>
        </xsl:apply-templates>
      </table>
    </xsl:if>

    <xsl:apply-templates select="$variables_doc/*/*/group[@name='corpus']"
                         mode="html_div">
      <xsl:with-param name="num" select="$num"/>
      <xsl:with-param name="node" select="."/>
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
        <xsl:when test="@name='pi-source'">
          <xsl:if test="$node/@pi-source='true'">true</xsl:if>
        </xsl:when>
        <xsl:when test="@name='path'">
          <xsl:value-of select="$node/@path"/>
        </xsl:when>
        <xsl:when test="@name='xpath'">
          <xsl:value-of select="$node/@xpath"/>
        </xsl:when>
        <xsl:when test="@name='xslt'">
          <xsl:value-of select="$node/@xslt"/>
        </xsl:when>
        <xsl:when test="@name='as'">
          <xsl:value-of select="$node/@as"/>
        </xsl:when>
        <xsl:when test="@name='attributes'">
          <xsl:value-of select="$node/@attributes"/>
        </xsl:when>
        <xsl:when test="@name='transform'">
          <xsl:value-of select="$node/@transform"/>
        </xsl:when>
        <xsl:when test="@name='head_as'">
          <xsl:value-of select="$node/head/@as"/>
        </xsl:when>
        <xsl:when test="@name='head_attributes'">
          <xsl:value-of select="$node/head/@attributes"/>
        </xsl:when>
        <xsl:when test="@name='head_transform'">
          <xsl:value-of select="$node/head/@transform"/>
        </xsl:when>
        <xsl:when test="@name='corpus'">
          <xsl:copy-of
              select="$node/division|$node/file|$node/link
                      |$node/comment()|$node/processing-instruction()"/>
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
      <xsl:copy-of select="@type|@class|@cast|@rows|@repeat"/>
      <xsl:if test="string-length($default)">
        <default>
          <xsl:copy-of select="$default"/>
        </default>
      </xsl:if>
      <xsl:copy-of select="pattern|option|label"/>
    </var>
  </xsl:template>


  <!--
      *************************************************************************
                                   CALLABLE TEMPLATE
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template title
      =========================================================================
  -->
  <xsl:template name="title">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/head/title">
      <xsl:choose>
        <xsl:when test="count($node/ancestor::division)=0
                        and not($node/ancestor::selection)">
          <div class="h1">
            <xsl:apply-templates select="$node/head/title"/>
            <xsl:for-each select="$node/head/subtitle">
              <div class="h2"><xsl:apply-templates/></div>
            </xsl:for-each>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <span class="pdocDivisionTitle">
            <xsl:apply-templates select="$node/head/title" mode="link"/>
            <xsl:for-each select="$node/head/subtitle">
              <xsl:value-of select="$str_sep"/>
              <xsl:apply-templates mode="link"/>
            </xsl:for-each>
          </span>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
