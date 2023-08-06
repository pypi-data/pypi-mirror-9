<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns="http://www.w3.org/1999/xhtml" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:imdi="http://www.mpi.nl/IMDI/Schema/IMDI" xmlns:folia="http://ilk.uvt.nl/folia">

<xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" indent="yes" />

<!-- FoLiA v0.11 -->

<xsl:template match="/folia:FoLiA">
  <html>
  <head>
        <meta http-equiv="content-type" content="application/xhtml+xml; charset=utf-8"/>
        <meta name="generator" content="folia2html.xsl" />
        <xsl:choose>
            <xsl:when test="folia:metadata/folia:meta[@id='title']">
                <title><xsl:value-of select="folia:metadata/folia:meta[@id='title']" /></title>
            </xsl:when>
            <xsl:when test="folia:metadata[@type='imdi']//imdi:Session/imdi:Title">
                <title><xsl:value-of select="folia:metadata[@type='imdi']//imdi:Session/imdi:Title" /></title>
            </xsl:when>
            <xsl:otherwise>
                <title><xsl:value-of select="@xml:id" /></title>
            </xsl:otherwise>
        </xsl:choose>
        <style type="text/css">
 				body {
					/*background: #222222;*/
					background: #b7c8c7;
					font-family: sans-serif;
					font-size: 12px;
					margin-bottom:240px;
				}

				div.text {
					width: 700px;
					margin-top: 50px;
					margin-left: auto;
					margin-right: auto;
					padding: 10px;
					padding-left: 50px;
					padding-right: 50px;
					text-align: left;
					background: white;
					border: 2px solid black;
				}

				div.div {
					padding-left: 0px;
					padding-top: 10px;
					padding-bottom: 10px;
				}

				#metadata {
					font-family: sans-serif;
					width: 700px;
					font-size: 90%;
					margin-left: auto;
					margin-right: auto;
					margin-top: 5px;
					margin-bottom: 5px;
					background: #b4d4d1; /*#FCFFD0;*/
					border: 1px solid #628f8b;
					width: 40%;
					padding: 5px;
				}
				#metadata table {
					text-align: left;
				}

				#text {
					border: 1px solid #628f8b;
					width: 60%;
					max-width: 1024px;
					background: white;
					padding: 20px;
					padding-right: 100px;
					margin-top: 5px;
					margin-left: auto;
					margin-right: auto;
					color: #222;
				}
				.s {
					background: white;
					display: inline;
					border-left: 1px white solid;
					border-right: 1px white solid;
				}
				.s:hover {
					background: #e7e8f8;
					border-left: 1px blue solid;
					border-right: 1px blue solid;
				}
				.word {
					display: inline;
					color: black;
					position: relative;
					text-decoration: none;
					z-index: 24;
                }
                .sh { 
                    background: #f4f9ca;
                }
                .cor {
                    background: #f9caca;
                }
                .s:hover .sh { 
					background: #cfd0ed;
                }
                .s:hover .cor { 
					background: #cfd0ed;
                }

				#text {
					border: 1px solid #628f8b;
					width: 60%;
					max-width: 1024px;
					background: white;
					padding: 20px;
					padding-right: 100px;
					margin-top: 5px;
					margin-left: auto;
					margin-right: auto;
					color: #222;
				}

				.word {
					display: inline;
					color: black;
					position: relative;
					text-decoration: none;
					z-index: 24;
				}

				.t {
					display: inline;
					text-decoration: none;
					z-index: 24;
				}

				.word .attributes { display: none; font-size: 12px; font-weight: normal; }
				.word:hover {
					/*text-decoration: underline;*/
					z-index: 25;
				}
				.word:hover .t {
					background: #bfc0ed;
					text-decoration: underline;
				}

				.word:hover .attributes {
					display: block;
					position: absolute;
					width: 340px;
					font-size: 12px;
					left: 2em;
					top: 2em;
					background: #b4d4d1; /*#FCFFD0;*/
					opacity: 0.9; filter: alpha(opacity = 90);
					border: 1px solid #628f8b;
					padding: 5px;
					text-decoration: none !important;
                    text-align: left;
				}
				.attributes dt {
					color: #254643;
					font-weight: bold;
				}
				.attributes dd {
					color: black;
					font-family: monospace;
				}
				.attributes .wordid {
					display: inline-block:
					width: 100%;
					font-size: 75%;
					color: #555;
					font-family: monospace;
					text-align: center;
				}
				.event {
					padding: 10px;
					border: 1px solid #4f7d87;
				}
                pre.gap {
                    width: 90%;
					padding: 5px;
                    border: 1px dashed #ddd;
                    white-space: pre-wrap;
				}
				span.attrlabel {
					display: inline-block;
					color: #254643;
					font-weight: bold;
					width: 110px;
				}
				span.attrvalue {
					font-weight: 12px;
					font-family: monospace;
                }
                span.spanclass {
                    color: #990000;
                    text-weight: bold;
                }
                span.morpheme {
                    font-style: italic;
                }
                span.details {
                    font-style: normal;
                    font-size: 80%;
                }

                div.caption {
                    text-align: center;
                    style: italic;
                }


				div#iewarning {
					width: 90%;
					padding: 10px;
					color: red;
					font-size: 16px;
					font-weight: bold;
					text-align: center;
				}
                td {
                 border: 1px solid #ddd;
                }
                thead {
                font-weight: bold;
                background: #ddd;
                }
        </style>
  </head>
    <body>
    	<xsl:comment><![CDATA[[if lte IE 10]>
		<div id="iewarning">
			The FoLiA viewer does not work properly with Internet Explorer, please consider upgrading to Mozilla Firefox or Google Chrome instead.
		</div>
		<![endif]]]></xsl:comment>
        <xsl:apply-templates />
    </body>
  </html>
</xsl:template>

<xsl:template match="folia:meta">
    <!-- ignore -->
</xsl:template>

<xsl:template match="folia:t">
    <!-- ignore -->
</xsl:template>

<xsl:template match="folia:text">
 <div class="text">
 	<xsl:apply-templates />
 </div>
</xsl:template>

<xsl:template match="folia:div">
 <div class="div">
   <xsl:apply-templates />
 </div>
</xsl:template>

<xsl:template match="folia:p">
 <p id="{@xml:id}">    
        <xsl:choose>
        <xsl:when test=".//folia:s or .//folia:w">
            <xsl:apply-templates />
        </xsl:when>
        <xsl:when test=".//folia:t[not(@class) and not(ancestor::folia:original) and not(ancestor::folia:suggestion) and not(ancestor::folia:alternative) and not(ancestor-or-self::*/auth)]">
            <xsl:call-template name="textcontent" />
        </xsl:when>
        </xsl:choose>
 </p>
</xsl:template>


<xsl:template match="folia:gap">
 <pre class="gap">
  <xsl:value-of select="folia:content" />
 </pre>
</xsl:template>


<xsl:template match="folia:head">
<xsl:choose>
 <xsl:when test="count(ancestor::folia:div) = 1">
    <h1>
        <xsl:call-template name="headinternal" />
    </h1>
 </xsl:when>
 <xsl:when test="count(ancestor::folia:div) = 2">
    <h2>
        <xsl:call-template name="headinternal" />
    </h2>
 </xsl:when>
 <xsl:when test="count(ancestor::folia:div) = 3">
    <h3>
        <xsl:call-template name="headinternal" />
    </h3>
 </xsl:when>
 <xsl:when test="count(ancestor::folia:div) = 4">
    <h4>
        <xsl:call-template name="headinternal" />
    </h4>
 </xsl:when>
 <xsl:when test="count(ancestor::folia:div) = 5">
    <h5>
        <xsl:call-template name="headinternal" />
    </h5>
 </xsl:when>
 <xsl:otherwise>
    <h6>
        <xsl:call-template name="headinternal" />
    </h6>
 </xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template name="headinternal">
    <span id="{@xml:id}" class="head">
        <xsl:choose>
        <xsl:when test=".//folia:s">
            <xsl:apply-templates select=".//folia:s|folia:whitespace|folia:br" />
        </xsl:when>
        <xsl:when test=".//folia:w">
            <xsl:apply-templates select=".//folia:w|folia:whitespace|folia:br" />
        </xsl:when>
        <xsl:when test=".//folia:t[not(@class) and not(ancestor::folia:original) and not(ancestor::folia:suggestion) and not(ancestor::folia:alternative) and not(ancestor-or-self::*/auth) and not(ancestor::folia:str)]">
            <xsl:call-template name="textcontent" />
        </xsl:when>
        </xsl:choose>
    </span>
</xsl:template>


<xsl:template match="folia:list">
<ul>
    <xsl:apply-templates />
</ul>
</xsl:template>

<xsl:template match="folia:listitem">
<li><xsl:apply-templates /></li>
</xsl:template>




<xsl:template match="folia:s">
    <span id="{@xml:id}" class="s">
        <xsl:choose>
        <xsl:when test=".//folia:w">
            <xsl:apply-templates select=".//folia:w|folia:whitespace|folia:br" />
        </xsl:when>
        <xsl:when test=".//folia:t[not(@class) and not(ancestor::folia:original) and not(ancestor::folia:suggestion) and not(ancestor::folia:alternative) and not(ancestor-or-self::*/auth)]">
            <xsl:call-template name="textcontent" />
        </xsl:when>
        </xsl:choose>
    </span>
</xsl:template>

<xsl:template match="folia:w">
    <xsl:variable name="wid" select="@xml:id" />
    <xsl:if test="not(ancestor::folia:original) and not(ancestor::folia:suggestion) and not(ancestor::folia:alternative) and not(ancestor-or-self::*/auth)">
        <span id="{@xml:id}"><xsl:attribute name="class">word<xsl:if test="//folia:wref[@id=$wid and not(ancestor::folia:altlayers)]"> sh</xsl:if><xsl:if test=".//folia:correction or .//folia:errordetection"> cor</xsl:if></xsl:attribute><xsl:call-template name="textcontent" /><xsl:call-template name="tokenannotations" /></span>
    <xsl:choose>
       <xsl:when test="@space = 'no'"></xsl:when>
       <xsl:otherwise>
        <xsl:text> </xsl:text>
       </xsl:otherwise>
    </xsl:choose>
    </xsl:if>
</xsl:template>

<xsl:template name="textcontent">
    <span class="t"><xsl:value-of select="string(.//folia:t[not(ancestor-or-self::*/@auth)
        and not(ancestor::folia:morpheme) and not(ancestor::folia:str) and not(@class)])"/></span>
</xsl:template>

<xsl:template name="tokenannotation_text">
    <xsl:if test="folia:t">
            <xsl:for-each select="folia:t">
                <span class="attrlabel">Text
                <xsl:if test="count(../folia:t) &gt; 1">
                    (<xsl:value-of select="@class" />)
                  </xsl:if>
                </span><span class="attrvalue"><xsl:value-of select=".//text()" /></span><br />
            </xsl:for-each>
      </xsl:if>
</xsl:template>

<xsl:template name="tokenannotations">
 <span class="attributes">
     <span class="attrlabel">ID</span><span class="attrvalue"><xsl:value-of select="@xml:id" /></span><br />
        <xsl:call-template name="tokenannotation_text" />
        <xsl:if test=".//folia:phon">
            <xsl:for-each select=".//folia:phon[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
                <span class="attrlabel">Phonetics</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:pos">
            <xsl:for-each select=".//folia:pos[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
            	<span class="attrlabel">PoS</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:lemma">
            <xsl:for-each select=".//folia:lemma[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
			    <span class="attrlabel">Lemma</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:sense">
            <xsl:for-each select=".//folia:sense[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
			    <span class="attrlabel">Sense</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:subjectivity[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
            <xsl:for-each select=".//folia:subjectivity">
			    <span class="attrlabel">Subjectivity</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:metric">
            <xsl:for-each select=".//folia:metric[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
                <span class="attrlabel">Metric <xsl:value-of select="@class" /></span><span class="attrvalue"><xsl:value-of select="@value" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//folia:errordetection">
            <xsl:for-each select=".//folia:errordetection[not(ancestor-or-self::*/@auth) and not(ancestor-or-self::*/morpheme)]">
                <span class="attrlabel">Error detected</span><span class="attrvalue"><xsl:value-of select="@class" /></span><br />
            </xsl:for-each>
        </xsl:if>
        <xsl:if test="folia:correction">
            <!-- TODO: Expand to support all token annotations -->
            <xsl:if test="folia:correction/folia:suggestion/folia:t">
            	<span class="attrlabel">Suggestion(s) for text correction</span><span class="attrvalue"><xsl:for-each select="folia:correction/folia:suggestion/folia:t">
                    <em><xsl:value-of select="." /></em><xsl:text> </xsl:text>
                </xsl:for-each></span><br />
            </xsl:if>
            <xsl:if test="folia:correction/folia:original/folia:t">
            	<span class="attrlabel">Original pre-corrected text</span>
            	<span class="attrvalue">
                <xsl:for-each select="folia:correction/folia:original/folia:t">
                    <em><xsl:value-of select="." /></em><xsl:text> </xsl:text>
                </xsl:for-each>
                </span><br />
            </xsl:if>
        </xsl:if>
        <xsl:if test=".//folia:morphology">
            <xsl:for-each select=".//folia:morphology[not(ancestor-or-self::*/@auth)]">
                <span class="attrlabel">Morphology</span> 
                <span class="attrvalue">
                    <xsl:for-each select="folia:morpheme">
                        <span class="morpheme">
                            <xsl:value-of select="./folia:t[not(@class) or @class='current']" />
                            <xsl:if test="@class">
                                <span class="details">(<xsl:value-of select="@class" />)</span>
                            </xsl:if>
                            <xsl:if test="@function">
                                <span class="details">[<xsl:value-of select="@function" />]</span>
                                </xsl:if>
                            <xsl:text> </xsl:text>
                        </span>
                    </xsl:for-each>
                </span><br />
            </xsl:for-each>
        </xsl:if>
        <span class="spanannotations">
            <xsl:call-template name="spanannotations">
                <xsl:with-param name="id" select="@xml:id" />
            </xsl:call-template>
        </span>
 </span>
</xsl:template>


<xsl:template name="span">
    <xsl:param name="id" />
    <xsl:text> </xsl:text>
    <span class="span">
        <xsl:for-each select=".//folia:wref">
            <xsl:variable name="wrefid" select="@id" />
            <xsl:choose>
                <xsl:when test="@t">
                    <xsl:value-of select="@t" />
                    <xsl:text> </xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:if test="//folia:w[@xml:id=$wrefid]">
                        <xsl:value-of select="//folia:w[@xml:id=$wrefid]/folia:t[not(ancestor::folia:original) and not(ancestor::folia:suggestion) and not(ancestor::folia:alternative) and not(ancestor-or-self::*/auth)]"/>
                    </xsl:if>
                    <xsl:text> </xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </span>
</xsl:template>

<xsl:template name="spanannotations">
    <xsl:param name="id" />

    <xsl:variable name="entities" select="ancestor::*"></xsl:variable>
    <xsl:for-each select="$entities">
        <xsl:for-each select="folia:entities">
            <xsl:for-each select="folia:entity">
                <xsl:if test=".//folia:wref[@id=$id]">
                    <span class="attrlabel">Entity</span>
                    <span class="attrvalue">
                        <span class="spanclass"><xsl:value-of select="@class" /></span>
                        <xsl:call-template name="span">
                            <xsl:with-param name="id" select="$id" />
                        </xsl:call-template>
                    </span><br />
                </xsl:if>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:for-each>


    <xsl:variable name="ancestors" select="ancestor::*"></xsl:variable>
    <xsl:for-each select="$ancestors">
    <xsl:for-each select="folia:chunking">
        <xsl:for-each select="folia:chunk">
            <xsl:if test=".//folia:wref[@id=$id]">
                <span class="attrlabel">Chunk</span>
                <span class="attrvalue">
                    <span class="spanclass"><xsl:value-of select="@class" /></span>
                        <xsl:call-template name="span">
                            <xsl:with-param name="id" select="$id" />
                        </xsl:call-template>
                </span><br/>
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </xsl:for-each>

    <xsl:for-each select="$ancestors">
    <xsl:for-each select="folia:syntax">
        <xsl:for-each select="//folia:su">
            <xsl:if test=".//folia:wref[@id=$id]">
                <span class="attrlabel">Syntactic Unit</span>
                <span class="attrvalue">
                    <span class="spanclass"><xsl:value-of select="@class" /></span>
                        <xsl:call-template name="span">
                            <xsl:with-param name="id" select="$id" />
                        </xsl:call-template>
                </span><br/>
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </xsl:for-each>


    <xsl:for-each select="$ancestors">
    <xsl:for-each select="folia:semroles">
        <xsl:for-each select="folia:semrole">
            <xsl:if test=".//folia:wref[@id=$id]">
                <span class="attrlabel">Semantic Role</span>
                <span class="attrvalue">
                    <span class="spanclass"><xsl:value-of select="@class" /></span>
                        <xsl:call-template name="span">
                            <xsl:with-param name="id" select="$id" />
                        </xsl:call-template>
                </span><br />
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </xsl:for-each>


    <xsl:for-each select="$ancestors">
    <xsl:for-each select="folia:coreferences">
        <xsl:for-each select="folia:coreferencechain">
            <xsl:if test=".//folia:wref[@id=$id]">
                <span class="attrlabel">Coreference Chain</span>
                <span class="attrvalue">
                    <span class="spanclass"><xsl:value-of select="@class" /></span>
                    <xsl:for-each select="folia:coreferencelink">
                        <xsl:call-template name="span">
                            <xsl:with-param name="id" select="$id" />
                        </xsl:call-template>
                        <xsl:text> - </xsl:text>
                    </xsl:for-each>
                    <br />
                </span><br/>
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </xsl:for-each>

    <xsl:for-each select="$ancestors">
    <xsl:for-each select="folia:dependencies">
        <xsl:for-each select="folia:dependency">
            <xsl:if test=".//folia:wref[@id=$id]">
                <span class="attrlabel">Dependency</span>
                <span class="attrvalue">
                    <span class="spanclass"><xsl:value-of select="@class" /></span><xsl:text> </xsl:text>
                        <xsl:for-each select="folia:hd">
                            <strong>Head:</strong>
                            <xsl:call-template name="span">
                                <xsl:with-param name="id" select="$id" />
                            </xsl:call-template>
                        </xsl:for-each>
                        <xsl:for-each select="folia:dep">
                            <strong>Dep:</strong>
                            <xsl:call-template name="span">
                                <xsl:with-param name="id" select="$id" />
                            </xsl:call-template>
                        </xsl:for-each>
                </span><br />
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </xsl:for-each>

</xsl:template>


<xsl:template match="folia:whitespace">
 <br /><br />
</xsl:template>

<xsl:template match="folia:br">
 <br />
</xsl:template>

<xsl:template match="folia:figure">
 <div class="figure">
  <img>
      <xsl:attribute name="src">
        <xsl:value-of select="@src" />
      </xsl:attribute>
      <xsl:attribute name="alt">
        <xsl:value-of select="folia:desc" />
      </xsl:attribute>
  </img>
  <xsl:if test="folia:caption">
   <div class="caption">
     <xsl:apply-templates select="folia:caption/*" />
   </div>
  </xsl:if>
 </div>
</xsl:template>

<xsl:template match="folia:table">
    <table>
      <xsl:apply-templates select="folia:tablehead" />
      <tbody>
        <xsl:apply-templates select="folia:row" />
      </tbody>
    </table>
</xsl:template>



<xsl:template match="folia:tablehead">
  <thead>
        <xsl:apply-templates select="folia:row" />
  </thead>
</xsl:template>


<xsl:template match="folia:row">
  <tr>
        <xsl:apply-templates select="folia:cell" />
 </tr>
</xsl:template>

<xsl:template match="folia:cell">
  <td>
    <xsl:apply-templates select="folia:p|folia:s|folia:w" />
  </td>
</xsl:template>

</xsl:stylesheet>

