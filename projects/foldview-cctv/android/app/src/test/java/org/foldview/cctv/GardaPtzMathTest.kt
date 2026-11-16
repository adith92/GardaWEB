package org.foldview.cctv

import org.junit.Assert.assertEquals
import org.junit.Test

class GardaPtzMathTest {
    @Test fun centerNoMove() {
        assertEquals(0.0, GardaPtzMath.normalize(0f, 0f, 100f).first, 0.0001)
        assertEquals(0.0, GardaPtzMath.normalize(10f, 10f, 100f).second, 0.0001)
    }
    @Test fun rightAndUp() {
        val right = GardaPtzMath.normalize(200f, 0f, 100f)
        assertEquals(1.0, right.first, 0.0001)
        assertEquals(0.0, right.second, 0.0001)
        val up = GardaPtzMath.normalize(0f, -60f, 100f)
        assertEquals(0.0, up.first, 0.0001)
        assertEquals(0.6, up.second, 0.0001)
    }
    @Test fun diagonalStaysWithinUnitRadius() {
        val dir = GardaPtzMath.normalize(1000f, -1000f, 100f)
        val length = kotlin.math.hypot(dir.first, dir.second)
        assertEquals(1.0, length, 0.001)
    }
}
