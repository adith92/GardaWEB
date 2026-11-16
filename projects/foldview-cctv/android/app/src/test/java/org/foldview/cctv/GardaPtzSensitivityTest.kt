package org.foldview.cctv

import org.junit.Assert.*
import org.junit.Test

class GardaPtzSensitivityTest {
    @Test fun highSensitivityActivatesSmallRealFingerMotion() {
        val radius = 76f
        val normal = GardaPtzMath.normalize(6f, 0f, radius)
        val boosted = GardaPtzMath.normalize(6f * 2.4f, 0f, radius)
        assertEquals(0.0, normal.first, 0.0001)
        assertTrue(boosted.first > 0.0)
    }

    @Test fun directionMappingPreservesAxisAndSign() {
        assertEquals(GardaAction.LEFT, GardaPtzStickDriver.nativeDirection(-.5, 0.0))
        assertEquals(GardaAction.RIGHT, GardaPtzStickDriver.nativeDirection(.5, 0.0))
        assertEquals(GardaAction.UP, GardaPtzStickDriver.nativeDirection(.0, .5))
        assertEquals(GardaAction.DOWN, GardaPtzStickDriver.nativeDirection(.0, -.5))
    }

    @Test fun actionablePtzErrorsExplainHardwareVsTouch() {
        assertTrue(PTZFeedback.safeMessage(
            IllegalStateException("ONVIF camera has no PTZConfiguration in its media profiles")
        ).contains("PTZ"))
        assertTrue(PTZFeedback.safeMessage(
            IllegalStateException("SOAP Fault: ter:ActionNotSupported")
        ).contains("menolak"))
    }

    @Test fun noCredentialsLeakedInSanitizedNetworkError() {
        val text = PTZFeedback.safeMessage(
            IllegalStateException("http://admin:secret@192.168.18.232:8899/onvif: offline")
        )
        assertFalse(text.contains("secret"))
        assertFalse(text.contains("admin:"))
    }

    @Test fun joystickMathStillCapsVelocity() {
        val p = GardaPtzMath.normalize(500f * 3.5f, -500f * 3.5f, 70f)
        assertTrue(kotlin.math.abs(p.first) <= 1.0)
        assertTrue(kotlin.math.abs(p.second) <= 1.0)
        assertEquals(1.0, kotlin.math.hypot(p.first, p.second), 0.0001)
    }
}
