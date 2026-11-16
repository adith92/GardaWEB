package org.foldview.cctv

import org.w3c.dom.Document
import java.io.ByteArrayInputStream
import java.io.StringReader
import javax.xml.parsers.DocumentBuilderFactory
import org.xml.sax.InputSource

/**
 * Android-compatible ONVIF DOM parser.
 *
 * Android explicitly DOES NOT support XMLConstants.FEATURE_SECURE_PROCESSING on
 * DocumentBuilderFactory. Avoid the legacy parser exception and enforce a
 * no-DTD/no-entity policy before parsing. For portability, unsupported JAXP
 * hardening flags are best effort; an EntityResolver denies external entities.
 */
internal object AndroidOnvifXml {
    private val forbidden = Regex("<!\\s*(?:DOCTYPE|ENTITY)", RegexOption.IGNORE_CASE)

    fun parse(payload: String): Document {
        require(payload.length <= 250_000) { "ONVIF response exceeds safe size" }
        require(!forbidden.containsMatchIn(payload)) {
            "Unsafe ONVIF XML containing DTD or entity declarations"
        }
        val factory = DocumentBuilderFactory.newInstance()
        factory.isNamespaceAware = true
        factory.isExpandEntityReferences = false
        runCatching { factory.isXIncludeAware = false }
        // These features are not consistently implemented on Android versions.
        for ((feature, value) in listOf(
            "http://apache.org/xml/features/disallow-doctype-decl" to true,
            "http://xml.org/sax/features/external-general-entities" to false,
            "http://xml.org/sax/features/external-parameter-entities" to false,
            "http://apache.org/xml/features/nonvalidating/load-external-dtd" to false
        )) {
            runCatching { factory.setFeature(feature, value) }
        }
        val builder = factory.newDocumentBuilder()
        builder.setEntityResolver { _, _ -> InputSource(StringReader("")) }
        return builder.parse(ByteArrayInputStream(payload.toByteArray(Charsets.UTF_8)))
    }
}
