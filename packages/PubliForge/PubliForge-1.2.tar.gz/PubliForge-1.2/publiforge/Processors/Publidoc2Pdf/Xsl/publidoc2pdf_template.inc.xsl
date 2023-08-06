<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2pdf_template.inc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                    CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template packages
      =========================================================================
  -->
  <xsl:template name="packages">
\usepackage[<xsl:value-of select="$paper_size"/>,
    layoutwidth=<xsl:value-of select="$layout_width"/>mm,
    layoutheight=<xsl:value-of select="$layout_height"/>mm,
    layoutoffset=<xsl:value-of select="$layout_offset"/>mm,
    width=<xsl:value-of select="$body_width"/>mm,
    height=<xsl:value-of select="$body_height"/>mm,
    left=<xsl:value-of select="$margin_left"/>mm,
    top=<xsl:value-of select="$margin_top"/>mm,
    bindingoffset=<xsl:value-of select="$bindingoffset"/>mm,
    headsep=<xsl:value-of select="$headsep"/>mm,
    footskip=<xsl:value-of select="$footskip"/>mm]{geometry}
\usepackage{fancyhdr}
\usepackage{fontspec}
\usepackage{libertine}
\usepackage{graphicx}
\usepackage{ifthen}
\usepackage{tabulary}
\usepackage{color}
\usepackage{epic}
\usepackage{lettrine}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue]{hyperref}
\usepackage[frenchb]{babel}
\usepackage{lipsum}
\urlstyle{same}
  </xsl:template>

  <!--
      =========================================================================
      Template font_families
      =========================================================================
  -->
  <xsl:template name="font_families">
% Font families
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newfontfeature{Microtype}{protrusion=default;expansion=default}
\setmainfont
    [Microtype, Ligatures=TeX]{Linux Libertine O}
\setsansfont
    [Microtype, Ligatures=TeX]{Linux Biolinum O}
\setmonofont
    [Microtype, Ligatures=TeX, Path=<xsl:value-of select="$font_dir"/>,
     Extension=.otf, UprightFont=*-Regular, BoldFont=*-Bold,
     ItalicFont=*-Italic, BoldItalicFont=*-BoldItalic]{Mono}

\newfontfamily\fontfamilySerif
    [Microtype, Ligatures=TeX]{Linux Libertine O}
\newfontfamily\fontfamilySans
    [Microtype, Ligatures=TeX]{Linux Biolinum O}
\newfontfamily\fontfamilyMono
    [Microtype, Ligatures=TeX, Path=<xsl:value-of select="$font_dir"/>,
     Extension=.otf, UprightFont=*-Regular, BoldFont=*-Bold,
     ItalicFont=*-Italic, BoldItalicFont=*-BoldItalic]{Mono}
\newfontfamily\fontfamilyScript
    [Microtype, Ligatures=TeX, Path=<xsl:value-of select="$font_dir"/>,
     Extension=.otf]{Script}
   </xsl:template>

   <!--
      =========================================================================
      Template fonts
      =========================================================================
  -->
  <xsl:template name="fonts">
% Fonts
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newcommand{\fontmain}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_main"/></xsl:call-template>\selectfont}
\newcommand{\fontheader}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_header"/></xsl:call-template>\selectfont}
\newcommand{\fontfolio}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_folio"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleA}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title1"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleB}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title2"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleC}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title3"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleD}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title4"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleE}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title5"/></xsl:call-template>\selectfont}
\newcommand{\fontnote}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_note"/></xsl:call-template>\selectfont}
\newcommand{\fontquote}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_quote"/></xsl:call-template>\selectfont}

\newcommand{\fontfront}{<xsl:call-template name="font"><xsl:with-param name="fnt">, /, ,</xsl:with-param><xsl:with-param name="dlt" select="2"/></xsl:call-template>\fontfamilySans\selectfont}
  </xsl:template>

  <!--
      =========================================================================
      Template font
      =========================================================================
  -->
  <xsl:template name="font">
    <xsl:param name="fnt"/>
    <xsl:param name="dlt" select="0"/>

    <xsl:text>\fontfamily</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before($fnt, ',')">
        <xsl:value-of select="substring-before($fnt, ',')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="substring-before($font_main, ',')"/>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:text>\fontsize{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before(substring-after($fnt, ', '), '/')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, ', '), '/') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="translate(substring-before(substring-after($font_main, ', '), '/') + $dlt, ',', '.')"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>}{</xsl:text>
    <xsl:choose>
      <xsl:when test="contains($fnt, '+') and substring-before(substring-after($fnt, '/'), '+')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, '/'), '+') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:when test="not(contains($fnt, '+')) and substring-before(substring-after($fnt, '/'), ',')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, '/'), ',') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:when test="contains($font_main, '+')">
        <xsl:value-of select="translate(substring-before(substring-after($font_main, '/'), '+') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="translate(substring-before(substring-after($font_main, '/'), ',') + $dlt, ',', '.')"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test="contains($fnt, '+') and substring-before(substring-after($fnt, '+'), ',')">
        <xsl:text>pt plus </xsl:text><xsl:value-of select="substring-before(substring-after($fnt, '+'), ',')"/>
      </xsl:when>
      <xsl:when test="contains($font_main, '+')">
        <xsl:text>pt plus </xsl:text><xsl:value-of select="substring-before(substring-after($font_main, '+'), ',')"/>
      </xsl:when>
    </xsl:choose>
    <xsl:text>pt}</xsl:text>

    <xsl:text>\fontseries{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before(substring-after(substring-after($fnt, ', '), ', '), ',')">
        <xsl:value-of select="substring-before(substring-after(substring-after($fnt, ', '), ', '), ',')"/>
      </xsl:when>
      <xsl:otherwise>m</xsl:otherwise>
    </xsl:choose>
    <xsl:text>}</xsl:text>

    <xsl:text>\fontshape{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-after(substring-after(substring-after($fnt, ', '), ', '), ', ')">
        <xsl:value-of select="substring-after(substring-after(substring-after($fnt, ', '), ', '), ', ')"/>
      </xsl:when>
      <xsl:otherwise>n</xsl:otherwise>
    </xsl:choose>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      Template variables_defines
      =========================================================================
  -->
  <xsl:template name="variables_defines">
% Variables and defines
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newcounter{topicfirstpage}
\newcommand{\topictitle}{}
\newcommand{\header}{}
\newcommand{\headtitleeven}{}
\newcommand{\headtitleodd}{}
\newcommand{\footer}{}

\setlength{\unitlength}{1mm}
\definecolor{gray}{gray}{0.5}
\setlength{\fboxsep}{4mm}
\renewcommand{\arraystretch}{1.4}

\sloppy
%\widowpenalty=8000
%\clubpenalty=8000
  </xsl:template>

  <!--
      =========================================================================
      Template layout
      =========================================================================
  -->
  <xsl:template name="layout">
% Layout
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<xsl:if test="not($web)">\geometry{showcrop}</xsl:if>
<xsl:if test="$debug">\geometry{showframe}</xsl:if>
\pagestyle{fancyplain}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[CE]{
    \ifthenelse{\equal{\topictitle}{} \or \equal{\thepage}{\thetopicfirstpage}}{}
        {\fontheader\headtitleeven}
}
\fancyhead[CO]{
    \ifthenelse{\equal{\topictitle}{} \or \equal{\thepage}{\thetopicfirstpage}}{}
        {\fontheader\headtitleodd}
}
\fancyfoot[LE]{
    \ifthenelse{\equal{\topictitle}{}}{}{\fontfolio\thepage}
}
\fancyfoot[RO]{
    \ifthenelse{\equal{\topictitle}{}}{}{\fontfolio\thepage}
}

\addto\captionsfrench{\def\partname{}}
\renewcommand{\thepart}{\empty{}}

\makeatletter
\long\def\@makefntextFB#1{%
    \noindent
    {\fontnote\color{gray}\@thefnmark.\,}#1%
}
\makeatother
  </xsl:template>

  <!--
      =========================================================================
      Template toc_title
      =========================================================================
  -->
  <xsl:template name="toc_title">
    <xsl:param name="title" select="head/title"/>
    <xsl:if test="$title">
      <xsl:variable name="depth"
                    select="count(ancestor::division|ancestor::topic|ancestor::section)"/>
      <xsl:choose>
        <xsl:when test="$depth=0">\addcontentsline{toc}{part}{</xsl:when>
        <xsl:when test="$depth=1">\addcontentsline{toc}{chapter}{</xsl:when>
        <xsl:when test="$depth=2">\addcontentsline{toc}{section}{</xsl:when>
        <xsl:when test="$depth=3">\addcontentsline{toc}{subsection}{</xsl:when>
        <xsl:otherwise>\addcontentsline{toc}{subsubsection}{</xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="$title" mode="link"/>
      <xsl:text>}</xsl:text>
      <xsl:choose>
        <xsl:when test="$depth=0">\bigskip{\noindent\fonttitleA <xsl:apply-templates select="$title"/>\par\vspace{.8cm}}</xsl:when>
        <xsl:when test="$depth=1">\medskip{\noindent\fonttitleB <xsl:apply-templates select="$title"/>\par\vspace{.6cm}}</xsl:when>
        <xsl:when test="$depth=2">\smallskip{\noindent\fonttitleC <xsl:apply-templates select="$title"/>\par\vspace{.5cm}}</xsl:when>
        <xsl:when test="$depth=3">{\noindent\fonttitleD <xsl:apply-templates select="$title"/>\par\vspace{.2cm}}</xsl:when>
        <xsl:otherwise>{\noindent\fonttitleE <xsl:apply-templates select="$title"/>\par}</xsl:otherwise>
      </xsl:choose>
      <xsl:text>\nopagebreak </xsl:text>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template title_page
      =========================================================================
  -->
  <xsl:template name="title_page">
<xsl:if test="$title_page and */head/title">
% Title page
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\begin{titlepage}
\begin{center}
~\par\vspace{3cm}
{\fontsize{24}{28pt}\fontshape{sc}\selectfont <xsl:apply-templates select="*/head/title"/>\\[2cm]}
<xsl:if test="*/head/subtitle">
<xsl:for-each select="*/head/subtitle">{\fontsize{20}{24pt}\selectfont <xsl:apply-templates/>\\[1cm]}</xsl:for-each>
</xsl:if>
\vfill
{\large \today}
\end{center}
\end{titlepage}
</xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template toc
      =========================================================================
  -->
  <xsl:template name="toc">
    <xsl:if test="$toc_depth!='-1'">
% Table of content
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
\renewcommand{\headtitleodd}{}
\renewcommand{\topictitle}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
\setcounter{tocdepth}{<xsl:value-of select="$toc_depth"/>}
\tableofcontents
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                PROCESSING INSTRUCTIONS
      *************************************************************************
  -->
  <!--
      =========================================================================
      PI tune
      =========================================================================
  -->
  <xsl:template match="processing-instruction('tune')" mode="tune">
    <xsl:param name="argument"/>
    <xsl:if test="contains(., 'target=&quot;latex&quot;')">
      <xsl:choose>
        <xsl:when test="$argument and contains(., concat($argument, '='))">
          <xsl:value-of
              select="substring-before(
                      substring-after(., concat($argument, '=&quot;')), '&quot;')"/>
        </xsl:when>
        <xsl:when test="contains(., 'action=&quot;newpage&quot;')">
\vfill\pagebreak
        </xsl:when>
        <xsl:when test="contains(., 'action=&quot;fontsize&quot;')">
\fontsize{<xsl:value-of select="substring-before(substring-after(., 'value=&quot;'), '/')"/>}%
         {<xsl:value-of select="substring-before(substring-after(., '/'), '&quot;')"/>}\selectfont
        </xsl:when>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      PI latex
      =========================================================================
  -->
  <xsl:template match="processing-instruction('latex')">
    <xsl:choose>
      <xsl:when test="ancestor::latex"><xsl:value-of select="."/></xsl:when>
      <xsl:when test=".='\'">{\textbackslash}</xsl:when>
      <xsl:when test=".='~'">\~{}</xsl:when>
      <xsl:when test=".='^'">^{}</xsl:when>
      <xsl:when test=".='['">{[}</xsl:when>
      <xsl:when test=".=']'">{]}</xsl:when>
      <xsl:when test=".='&amp;amp;'">\&amp;</xsl:when>
      <xsl:otherwise>\<xsl:value-of select="."/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
