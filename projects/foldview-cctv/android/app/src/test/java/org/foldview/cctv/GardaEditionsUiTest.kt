package org.foldview.cctv

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow

class GardaEditionsUiTest {
    @Test fun foldUsesRailOnlyAtExpandedWidth() {
        assertFalse(GardaLayoutRules.useNavigationRail(true, 390f))
        assertFalse(GardaLayoutRules.useNavigationRail(true, 679f))
        assertTrue(GardaLayoutRules.useNavigationRail(true, 680f))
        assertTrue(GardaLayoutRules.useNavigationRail(true, 850f))
    }

    @Test fun standardNeverUsesRailEvenOnLandscapeOrTablet() {
        assertFalse(GardaLayoutRules.useNavigationRail(false, 360f))
        assertFalse(GardaLayoutRules.useNavigationRail(false, 750f))
        assertFalse(GardaLayoutRules.useNavigationRail(false, 1200f))
    }

    @Test fun compactDashboardAvoidsThreeSideBySideCards() {
        assertTrue(GardaLayoutRules.compactMetrics(320f))
        assertTrue(GardaLayoutRules.compactMetrics(400f))
        assertFalse(GardaLayoutRules.compactMetrics(540f))
    }

    @Test fun dualVisionAndVideoWallsRespectWidth() {
        assertEquals(1, GardaLayoutRules.videoColumns(2, false))
        assertEquals(2, GardaLayoutRules.videoColumns(2, true))
        assertEquals(2, GardaLayoutRules.videoColumns(4, false))
        assertEquals(3, GardaLayoutRules.videoColumns(9, true))
    }

    private fun luminance(hex: Int): Double {
        fun channel(shift: Int): Double {
            val value = ((hex shr shift) and 0xFF) / 255.0
            return if (value <= 0.04045) value / 12.92
            else ((value + 0.055) / 1.055).pow(2.4)
        }
        return .2126 * channel(16) + .7152 * channel(8) + .0722 * channel(0)
    }

    private fun contrast(a: Int, b: Int): Double {
        val la = luminance(a)
        val lb = luminance(b)
        return (max(la, lb) + .05) / (min(la, lb) + .05)
    }

    @Test fun criticalDarkAndLightTypographyMeetsWcagAA() {
        // Filled dark button, body text on dark surface, light red on white.
        assertTrue(contrast(0xFF26030C.toInt(), 0xFFFF556C.toInt()) >= 4.5)
        assertTrue(contrast(0xFFCDD0DA.toInt(), 0xFF171A22.toInt()) >= 4.5)
        assertTrue(contrast(0xFFFFFFFF.toInt(), 0xFFC51A36.toInt()) >= 4.5)
        assertTrue(contrast(0xFF555D6B.toInt(), 0xFFFFFFFF.toInt()) >= 4.5)
    }
}
