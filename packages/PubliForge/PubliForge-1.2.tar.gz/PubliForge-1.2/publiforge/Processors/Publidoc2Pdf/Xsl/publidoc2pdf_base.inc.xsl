<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2pdf_base.inc.xsl ae7c00d5b084 2014/11/29 09:46:06 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str">

  <!--
      *************************************************************************
                                    DIVISION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      division mode corpus
      =========================================================================
  -->
  <xsl:template match="division" mode="corpus">
% Division
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
<xsl:if test="not(ancestor::division)">
\renewcommand{\headtitleodd}{<xsl:apply-templates select="head/title"/>}
</xsl:if>
\renewcommand{\topictitle}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
<xsl:choose>
  <xsl:when test="not(ancestor::division)">
\begin{titlepage}
\begin{center}
~\vspace{.20\textheight}\par
<xsl:call-template name="toc_title"/>
<xsl:if test="front">
\vfill
\begin{minipage}{.8\linewidth}
\fontfront <xsl:apply-templates select="front"/>
\end{minipage}
\vfill
</xsl:if>
\end{center}
\end{titlepage}
\newpage
  </xsl:when>
  <xsl:otherwise><xsl:call-template name="toc_title"/></xsl:otherwise>
</xsl:choose>
<xsl:apply-templates select="division|topic" mode="corpus"/>
  </xsl:template>


  <!--
      *************************************************************************
                                    COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      topic mode corpus
      =========================================================================
  -->
  <xsl:template match="topic" mode="corpus">
    <xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
    <xsl:choose>
      <xsl:when test="@type='title'">
% Title page
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
\renewcommand{\headtitleodd}{}
\renewcommand{\topictitle}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
\begin{titlepage}
\begin{center}
\setlength\parindent{0pt}
<xsl:if test="header">
{\fontsize{16}{20pt}\selectfont <xsl:apply-templates select="header"/>\vspace{2cm}}
</xsl:if>
~\par\vspace{3cm}
<xsl:if test="head/title">
{\fontsize{24}{28pt}\fontshape{sc}\selectfont <xsl:apply-templates select="head/title"/>\par\vspace{2cm}}
</xsl:if>
<xsl:if test="head/subtitle">
{\fontsize{20}{24pt}\selectfont <xsl:for-each select="head/subtitle"><xsl:apply-templates/>\par\vspace{1cm} </xsl:for-each>}
</xsl:if>
\vfill
<xsl:apply-templates select="section|footer"/>
\end{center}
\end{titlepage}
\newpage
      </xsl:when>

      <xsl:when test="@type='copyright'">
% Copyright
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
\renewcommand{\headtitleodd}{}
\renewcommand{\topictitle}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
~\vfill
{\setlength\parindent{0pt} <xsl:apply-templates select="section"/>}
\newpage
      </xsl:when>

      <xsl:when test="@type='dedication' or @type='inscription'">
% <xsl:value-of select="@type"/>
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
\renewcommand{\headtitleodd}{}
\renewcommand{\topictitle}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
~\vspace{2cm}
\begin{flushright}
\begin{minipage}{.5\linewidth}
\setlength\parindent{0pt}
<xsl:apply-templates select="section"/>
\end{minipage}
\end{flushright}
\newpage
      </xsl:when>

      <xsl:otherwise>
% Topic <xsl:value-of select="@type"/>
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<xsl:if test="not(ancestor::division)">
\renewcommand{\headtitleodd}{<xsl:apply-templates select="head/title"/>}
</xsl:if>
\renewcommand{\topictitle}{<xsl:apply-templates select="head/title" mode="link"/>\,}
\renewcommand{\header}{<xsl:apply-templates select="header"/>}
\renewcommand{\footer}{<xsl:apply-templates select="footer"/>}
\setcounter{topicfirstpage}{\thepage}
<xsl:call-template name="toc_title"/>
<xsl:apply-templates select="section"/>
<xsl:apply-templates select="bibliography"/>
\newpage
      </xsl:otherwise>
    </xsl:choose>
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
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
\pagebreak[3]
<xsl:choose>
  <!-- box -->
  <xsl:when test="@type='box'">
\noindent\fbox{\begin{minipage}{\linewidth}
<xsl:if test="head/title">
\begin{center}
{\Large\bfseries <xsl:apply-templates select="head/title"/>}\par
<xsl:if test="head/subtitle">
{\large\bfseries <xsl:for-each select="head/subtitle"><xsl:apply-templates/>\par </xsl:for-each>}
</xsl:if>
\smallskip
\end{center}
</xsl:if>
<xsl:call-template name="section_children"/>
\end{minipage}}
  </xsl:when>
  <!-- ex -->
  <xsl:when test="@type='ex'">
<xsl:call-template name="toc_title"/>
{\itshape <xsl:call-template name="section_children"/>}
  </xsl:when>
  <!-- sign -->
  <xsl:when test="@type='sign'">
<xsl:call-template name="toc_title"/>
\begin{flushright}
<xsl:call-template name="section_children"/>
\end{flushright}
  </xsl:when>
  <!-- others -->
  <xsl:otherwise>
<xsl:call-template name="toc_title"/>
<xsl:call-template name="section_children"/>
  </xsl:otherwise>
</xsl:choose>
\par\medskip
  </xsl:template>

  <xsl:template name="section_children">
    <xsl:apply-templates
        select="section|p|speech|list|blockquote|table|media"/>
  </xsl:template>

  <!--
      =========================================================================
      bibliography
      =========================================================================
  -->
  <xsl:template match="bibliography">
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\pagebreak[3]
<xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
<xsl:if test="../section">
\addcontentsline{toc}{chapter}{<xsl:value-of select="$i18n_bibliography"/>}
\bigskip{\noindent\fonttitleB <xsl:value-of select="$i18n_bibliography"/>\\[.6cm]}\nopagebreak
</xsl:if>
<xsl:apply-templates select="entry" mode="biblio"/>
\par\medskip
  </xsl:template>


  <!--
      *************************************************************************
                                       BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      p, p mode speech, p mode table, p mode link
      =========================================================================
  -->
  <xsl:template match="p">
    <xsl:apply-templates/>
    <xsl:if test="not(position()=last())">
      <xsl:text>\\
</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="p" mode="speech">
\noindent <xsl:apply-templates/><xsl:if test="not(position()=last())">\par </xsl:if>
  </xsl:template>

  <xsl:template match="p" mode="table">
    <xsl:apply-templates/>
    <xsl:if test="not(position()=last())">
      <xsl:choose>
        <xsl:when test="ancestor::*/@colspan"><xsl:text> </xsl:text></xsl:when>
        <xsl:otherwise>\par </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      speech
      =========================================================================
  -->
  <xsl:template match="speech">
    <xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
    <xsl:if test="speaker">
      <xsl:text>\noindent\textsc{</xsl:text>
      <xsl:apply-templates select="speaker"/>
      <xsl:text>}</xsl:text>
      <xsl:if test="stage"><xsl:value-of select="$str_stage_sep"/></xsl:if>
    </xsl:if>
    <xsl:apply-templates select="stage"/>
    <xsl:if test="speaker">\par\nopagebreak </xsl:if>
    <xsl:apply-templates select="p|blockquote" mode="speech"/>
    <xsl:text>\par\medskip
</xsl:text>
  </xsl:template>

  <xsl:template match="stage">
    <xsl:choose>
      <xsl:when test="not(../../speech)">
        <xsl:value-of select="$str_stage_open"/>
        <xsl:text>\textit{</xsl:text><xsl:apply-templates/><xsl:text>}</xsl:text>
        <xsl:value-of select="$str_stage_close"/>
      </xsl:when>
      <xsl:otherwise>\textit{<xsl:apply-templates/>}</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      list
      =========================================================================
  -->
  <xsl:template match="list">
    <xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
    <xsl:if test="head/title">
\noindent\textbf{<xsl:apply-templates select="head/title"/>}\par\nopagebreak
    </xsl:if>
    <xsl:if test="head/subtitle">
<xsl:for-each select="head/subtitle">\noindent\textit{<xsl:apply-templates/>}\par\nopagebreak </xsl:for-each>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@type='ordered'">
\begin{enumerate}
<xsl:apply-templates select="item"/>
\end{enumerate}
      </xsl:when>
      <xsl:when test="@type='glossary'">
\begin{list}{}{\setlength\leftmargin{0pt}}
<xsl:apply-templates select="item"/>
\end{list}
      </xsl:when>
      <xsl:otherwise>
\begin{list}{–}{\setlength\leftmargin{1.1em}}
<xsl:apply-templates select="item"/>
\end{list}
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="item">
\item <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="label">\textbf{<xsl:apply-templates/>}\par\nopagebreak </xsl:template>

  <!--
      =========================================================================
      blockquote
      =========================================================================
  -->
  <xsl:template match="blockquote">
    <xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
    <xsl:if test="head/title">
\noindent\textbf{<xsl:apply-templates select="head/title"/>}\par\nopagebreak
    </xsl:if>
    <xsl:if test="head/subtitle">
<xsl:for-each select="head/subtitle">\noindent\textit{<xsl:apply-templates/>}\par\nopagebreak </xsl:for-each>
    </xsl:if>
{\fontquote <xsl:apply-templates select="p|speech|list"/>}
<xsl:if test="attribution">
\begin{flushright}
<xsl:apply-templates select="attribution"/>
\end{flushright}
</xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      blockquote mode speech
      =========================================================================
  -->
  <xsl:template match="blockquote" mode="speech">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      table
      =========================================================================
  -->
  <xsl:template match="table">
    <xsl:if test="not(tgroup)">
<xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
\medskip\noindent
\begin{tabulary}{\linewidth}{|<xsl:for-each select="tr[1]/td|tr[1]/th|tbody/tr[1]/td|tbody/tr[1]/th">
<xsl:choose>
  <xsl:when test="@colspan">
    <xsl:call-template name="counter">
      <xsl:with-param name="xvalue"><xsl:value-of select="@colspan"/></xsl:with-param>
      <xsl:with-param name="insert">L|</xsl:with-param>
    </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>L|</xsl:otherwise>
</xsl:choose>
</xsl:for-each>}
<xsl:apply-templates select=".//tr"/>
\hline
\end{tabulary}
<xsl:if test="head/title">
\nopagebreak\noindent\textsc{<xsl:apply-templates select="head/title"/>}\par
</xsl:if>
<xsl:if test="head/subtitle">
  <xsl:for-each select="head/subtitle">\nopagebreak\noindent\textit{<xsl:apply-templates/>}\par </xsl:for-each>
</xsl:if>
\medskip
    </xsl:if>
  </xsl:template>

  <xsl:template match="tr">
\hline
    <xsl:for-each select="td|th">
      <xsl:if test="@colspan">\multicolumn{<xsl:value-of select="@colspan"/>}{<xsl:if test="position()=1">|</xsl:if>l|}{</xsl:if>
      <xsl:if test="name()='th'">\bfseries{</xsl:if>
      <xsl:apply-templates mode="table"/>
      <xsl:if test="name()='th'"><xsl:text>}</xsl:text></xsl:if>
      <xsl:if test="@colspan">}</xsl:if>
      <xsl:if test="position()!=last()"> &amp; </xsl:if>
    </xsl:for-each>
    <xsl:text>\tabularnewline </xsl:text>
  </xsl:template>

  <xsl:template name="counter">
    <xsl:param name="insert"/>
    <xsl:param name="xvalue"/>
    <xsl:value-of select="$insert"/>
    <xsl:if test="not($xvalue='1')">
      <xsl:call-template name="counter">
        <xsl:with-param name="xvalue"><xsl:value-of select="number($xvalue - 1)"/></xsl:with-param>
        <xsl:with-param name="insert"><xsl:value-of select="$insert"/></xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      media
      =========================================================================
  -->
  <xsl:template match="media">
    <xsl:if test="$img and image">
<xsl:apply-templates select="processing-instruction('tune')" mode="tune"/>
\medskip
      <xsl:apply-templates select="image" mode="media"/>
      <xsl:if test="head/title">
\nopagebreak\noindent\textsc{<xsl:apply-templates select="head/title"/>}\par\nopagebreak
      </xsl:if>
      <xsl:if test="head/subtitle">
        <xsl:for-each select="head/subtitle">\noindent\textit{<xsl:apply-templates/>}\par\nopagebreak </xsl:for-each>
      </xsl:if>
      <xsl:apply-templates select="caption"/>
\medskip
    </xsl:if>
  </xsl:template>

  <xsl:template match="caption">
\noindent{\small <xsl:apply-templates/>}\par
  </xsl:template>

  <!--
      =========================================================================
      image
      =========================================================================
  -->
  <xsl:template match="image">
    <xsl:if test="$img">
      <xsl:choose>
        <xsl:when test="ancestor::cover or ancestor::hotspot"/>
        <xsl:when test="ancestor::right or ancestor::wrong or ancestor::item">
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>\resizebox{1.5em}{!}{\includegraphics{</xsl:text>
          <xsl:value-of select="concat($img_dir, translate(@id, '_', '-'), '.pdf')"/>
          <xsl:text>}}</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="image" mode="media">
    <xsl:if test="$img">
      <xsl:choose>
        <xsl:when test="processing-instruction('tune')[
                        contains(., 'target=&quot;latex&quot;')
                        and contains(., 'size=')]">
          <xsl:text>\noindent\resizebox{</xsl:text>
          <xsl:apply-templates select="processing-instruction('tune')" mode="tune">
            <xsl:with-param name="argument">size</xsl:with-param>
          </xsl:apply-templates>
          <xsl:text>}{!}{\includegraphics{</xsl:text>
          <xsl:value-of select="concat($img_dir, translate(@id, '_', '-'), '.pdf')"/>
          <xsl:text>}}\par
          </xsl:text>
        </xsl:when>
        <xsl:when test="@type='thumbnail'">
          <xsl:text>\noindent\resizebox{.35\linewidth}{!}{\includegraphics{</xsl:text>
          <xsl:value-of select="concat($img_dir, translate(@id, '_', '-'), '.pdf')"/>
          <xsl:text>}}\par
          </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>\noindent\resizebox{\linewidth}{!}{\includegraphics{</xsl:text>
          <xsl:value-of select="concat($img_dir, translate(@id, '_', '-'), '.pdf')"/>
          <xsl:text>}}\par
          </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="copyright">
\noindent\textsf{\textit{\footnotesize <xsl:apply-templates select="copyright"/>}}\par
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      entry mode biblio
      =========================================================================
  -->
  <xsl:template match="entry" mode="biblio">
{\noindent
    <xsl:if test="contributors/contributor[role='author']">
      <xsl:text>\textbf{</xsl:text>
      <xsl:for-each select="contributors/contributor[role='author']">
        <xsl:apply-templates select="." mode="biblio"/>
      </xsl:for-each>
      <xsl:text>}. </xsl:text>
    </xsl:if>
    <xsl:text>\textit{</xsl:text><xsl:apply-templates select="title"/>
    <xsl:text>}. </xsl:text>
    <xsl:if test="contributors/contributor[role='publisher']">
      <xsl:for-each select="contributors/contributor[role='publisher']">
        <xsl:apply-templates select="." mode="biblio"/>
      </xsl:for-each>
      <xsl:if test="date">, </xsl:if>
    </xsl:if>
    <xsl:apply-templates select="date" mode="biblio"/>
    <xsl:if test="pages">
      <xsl:apply-templates select="pages"/>
      <xsl:text>~p. </xsl:text>
    </xsl:if>
    <xsl:if test="collection">
      <xsl:apply-templates select="collection"/>
      <xsl:text>. </xsl:text>
    </xsl:if>
    <xsl:if test="identifier">
      <xsl:text>EAN~</xsl:text>
      <xsl:value-of select="identifier"/>
    </xsl:if>
}\par\medskip
  </xsl:template>


  <!--
      *************************************************************************
                                      HEAD LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      contributor
      =========================================================================
  -->
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
      index
      =========================================================================
  -->
  <xsl:template match="index">
    <xsl:apply-templates select="w"/>
  </xsl:template>

  <xsl:template match="index" mode="link">
    <xsl:apply-templates select="w" mode="link"/>
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
  <xsl:template match="sup">\textsuperscript{<xsl:apply-templates/>}</xsl:template>

  <xsl:template match="sub">$_{\mathrm{<xsl:apply-templates/>}}$</xsl:template>

  <xsl:template match="sub|sup" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      var
      =========================================================================
  -->
  <xsl:template match="var">\textit{<xsl:apply-templates/>}</xsl:template>

  <xsl:template match="var" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      math
      =========================================================================
  -->
  <xsl:template match="math">
    <xsl:if test="@display and not(latex)">
\begin{center}
    </xsl:if>
    <xsl:choose>
      <xsl:when test="latex and latex/@plain='true'">
        <xsl:apply-templates select="latex"/>
      </xsl:when>
      <xsl:when test="latex">
        <xsl:if test="@display">$</xsl:if>
        <xsl:text>$</xsl:text>
        <xsl:apply-templates select="latex"/>
        <xsl:text>$</xsl:text>
        <xsl:if test="@display">$</xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="@display and not(latex)">
\end{center}
    </xsl:if>
  </xsl:template>

  <xsl:template match="math" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      number
      =========================================================================
  -->
  <xsl:template match="number" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      date
      =========================================================================
  -->
  <xsl:template match="date" mode="biblio">
    <xsl:value-of select="substring(@value, 1, 4)"/>
    <xsl:text>. </xsl:text>
  </xsl:template>

  <xsl:template match="date" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      note
      =========================================================================
  -->
  <xsl:template match="note">
    <xsl:choose>
      <xsl:when test="w">
        <xsl:apply-templates select="w"/>
        <xsl:text>\footnote{\fontnote </xsl:text>
        <xsl:apply-templates select="p"/>
        <xsl:text>}</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>\footnote{\fontnote </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="note" mode="link"/>

  <!--
      =========================================================================
      quote
      =========================================================================
  -->
  <xsl:template match="quote">
    <xsl:choose>
      <xsl:when test="phrase">
        <xsl:text>«~\textit{</xsl:text>
        <xsl:apply-templates select="phrase"/>
        <xsl:text>}~»</xsl:text>
        <xsl:text> (</xsl:text>
        <xsl:apply-templates select="attribution"/>
        <xsl:text>)</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>«~\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}~»</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="quote" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <!--
      =========================================================================
      initial
      =========================================================================
  -->
  <xsl:template match="initial">
    <xsl:text>{\lettrine{</xsl:text>
    <xsl:apply-templates select="c"/>
    <xsl:text>}{</xsl:text>
    <xsl:apply-templates select="w"/>
    <xsl:text>}}</xsl:text>
  </xsl:template>

  <xsl:template match="initial" mode="link">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      link
      =========================================================================
  -->
  <xsl:template match="link">
    <xsl:choose>
      <xsl:when test="@uri and (normalize-space() or node())">
        <xsl:value-of select="concat('\href{', @uri, '}{')"/>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
      </xsl:when>
      <xsl:when test="normalize-space() or node()">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:when test="@idref">
        <xsl:value-of select="str:replace(@idref, '_', '\_')"/>
      </xsl:when>
      <xsl:otherwise>\url{<xsl:value-of select="@uri"/>}</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      misc
      =========================================================================
  -->
  <xsl:template match="name">\textit{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="foreign">\textit{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="acronym">\textsc{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="term">\texttt{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="literal">\texttt{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="highlight">\textbf{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="emphasis">\textit{<xsl:apply-templates/>}</xsl:template>
  <xsl:template match="mentioned">\textit{<xsl:apply-templates/>}</xsl:template>

  <xsl:template match="name|foreign|acronym|term|literal|highlight|emphasis|mentioned" mode="link">
    <xsl:apply-templates select="."/>
  </xsl:template>

</xsl:stylesheet>
