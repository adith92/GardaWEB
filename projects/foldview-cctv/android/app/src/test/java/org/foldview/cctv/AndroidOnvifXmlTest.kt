package org.foldview.cctv

import org.junit.Assert.*
import org.junit.Test

class AndroidOnvifXmlTest {
    @Test fun parsesNormalDeviceResponse() {
        val payload = """<?xml version="1.0" encoding="UTF-8"?>
            <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                        xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
                <s:Body><tds:GetCapabilitiesResponse/></s:Body>
            </s:Envelope>""".trimIndent()
        val doc = AndroidOnvifXml.parse(payload)
        assertEquals(1, doc.getElementsByTagNameNS("*", "GetCapabilitiesResponse").length)
    }

    @Test fun rejectsDoctypeAndEntityExpansion() {
        val xml = """<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
            <foo>&xxe;</foo>""".trimIndent()
        val error = runCatching { AndroidOnvifXml.parse(xml) }.exceptionOrNull()
        assertTrue(error is IllegalArgumentException)
    }

    @Test fun refusesOversizedResponse() {
        val huge = "<hello>" + "a".repeat(250_010) + "</hello>"
        val error = runCatching { AndroidOnvifXml.parse(huge) }.exceptionOrNull()
        assertTrue(error is IllegalArgumentException)
    }

    @Test fun acceptsBasicEscapedOnvifPayload() {
        val xml = "<s:Envelope xmlns:s=\"urn:test\"><s:Body> &amp; </s:Body></s:Envelope>"
        val doc = AndroidOnvifXml.parse(xml)
        assertEquals(" & ", doc.getElementsByTagNameNS("*", "Body").item(0).textContent)
    }
}
