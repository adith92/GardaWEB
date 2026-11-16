package org.foldview.cctv

import org.junit.Assert.*
import org.junit.Test

class GardaJoystickRecoveryTest {
    @Test fun leftRightUpDownMappingForGardaNative() {
        assertEquals(GardaAction.LEFT, GardaPtzStickDriver.nativeDirection(-1.0, 0.1))
        assertEquals(GardaAction.RIGHT, GardaPtzStickDriver.nativeDirection(0.8, -0.1))
        assertEquals(GardaAction.UP, GardaPtzStickDriver.nativeDirection(0.1, 1.0))
        assertEquals(GardaAction.DOWN, GardaPtzStickDriver.nativeDirection(0.1, -1.0))
    }

    @Test fun onvifSoapFault200IsNotSuccessfulMovement() {
        val xml = """
            <?xml version="1.0"?>
            <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
              <s:Body>
                <s:Fault>
                  <s:Code><s:Value>s:Sender</s:Value>
                    <s:Subcode><s:Value>ter:ActionNotSupported</s:Value></s:Subcode>
                  </s:Code>
                  <s:Reason><s:Text xml:lang="en">PTZ unavailable</s:Text></s:Reason>
                </s:Fault>
              </s:Body>
            </s:Envelope>
        """.trimIndent()
        val fault = OnvifPtz.parseFault(xml)
        assertNotNull(fault)
        assertTrue(fault!!.contains("ActionNotSupported"))
        assertTrue(fault.contains("PTZ unavailable"))
    }

    @Test fun normalSoapResponseIsNotFault() {
        val xml = """
            <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
              <s:Body><t:ContinuousMoveResponse xmlns:t="http://www.onvif.org/ver20/ptz/wsdl"/></s:Body>
            </s:Envelope>
        """.trimIndent()
        assertNull(OnvifPtz.parseFault(xml))
    }

    @Test fun joystickDeadzoneAndDiagonalMathStillValid() {
        assertEquals(0.0, GardaPtzMath.normalize(10f, 10f, 100f).first, 0.0001)
        val pair = GardaPtzMath.normalize(50f, -50f, 100f)
        assertTrue(pair.first > 0.0)
        assertTrue(pair.second > 0.0)
    }
}
