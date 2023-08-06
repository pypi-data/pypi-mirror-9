<?xml version="1.0"?>
<xsl:stylesheet version="3.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:stream href="books.xml">
            <xsl:iterate select="/books/book">
                <xsl:result-document href="{concat('book', position(),'.xml')}">
                    <xsl:copy-of select="."/>
                </xsl:result-document>
                <xsl:next-iteration/>
            </xsl:iterate>
        </xsl:stream>
    </xsl:template>
</xsl:stylesheet>
