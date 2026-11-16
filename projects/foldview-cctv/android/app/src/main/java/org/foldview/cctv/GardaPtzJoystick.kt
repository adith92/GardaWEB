package org.foldview.cctv

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import java.util.concurrent.Executors
import kotlin.math.hypot
import kotlin.math.roundToInt

/** Pure analog-stick math, independently testable without camera hardware. */
internal object GardaPtzMath {
    fun normalize(dx: Float, dy: Float, radius: Float): Pair<Double, Double> {
        if (radius <= 0f) return 0.0 to 0.0
        val length = hypot(dx, dy)
        val scale = if (length > radius) radius / length else 1f
        val pan = dx * scale / radius
        val tilt = -dy * scale / radius
        return if (hypot(pan, tilt) < 0.16f) 0.0 to 0.0
        else pan.toDouble().coerceIn(-1.0, 1.0) to tilt.toDouble().coerceIn(-1.0, 1.0)
    }
}

/**
 * PTZ HTTP commands live on one worker. Drag coalesces into latest vector:
 * native GARDA uses short vendor pulses, standard ONVIF ContinuousMove uses Stop.
 * Never infer physical motor movement solely from a 200 response.
 */
internal class GardaPtzStickDriver(
    private val camera: CameraInfo,
    private val useGardaNative: Boolean,
    private val onError: (String) -> Unit,
    private val onInfo: (String) -> Unit
) {
    private val worker = Executors.newSingleThreadExecutor()
    @Volatile private var desired: Pair<Double, Double>? = null
    @Volatile private var firstQueued: Pair<Double, Double>? = null
    @Volatile private var working = false
    @Volatile private var disposed = false

    /**
     * Preserve the first movement even when a user releases before the worker starts.
     * Previous implementation discarded quick touches as soon as stop() cleared desired.
     */
    @Synchronized
    fun move(pan: Double, tilt: Double) {
        if (disposed) return
        val value = pan.coerceIn(-1.0, 1.0) to tilt.coerceIn(-1.0, 1.0)
        desired = value
        if (!working) {
            firstQueued = value
            working = true
            worker.execute { runLoop() }
        }
    }

    fun stop() { desired = null }

    /** Guaranteed bounded single step. Used by the on-screen arrow diagnostics. */
    fun nudge(pan: Double, tilt: Double) {
        if (disposed) return
        worker.execute {
            try {
                if (useGardaNative) {
                    GardaNativeApi.command(camera, nativeDirection(pan, tilt))
                } else {
                    // RelativeMove is a separate ONVIF capability. Do not infer it
                    // from an acknowledged ContinuousMove response.
                    OnvifPtz.relativeStep(camera, pan * 0.12, tilt * 0.12)
                }
                if (!disposed) onInfo("PTZ test command accepted; verify motor movement.")
            } catch (e: Exception) {
                if (!disposed) onError(PTZFeedback.safeMessage(e))
            }
        }
    }

    private fun runLoop() {
        var acceptedOnce = false
        try {
            while (!disposed) {
                // A rapid tap still issues one actual bounded command.
                val target = desired ?: firstQueued ?: break
                firstQueued = null
                if (useGardaNative) {
                    // Vendor daemon has a bounded ~220ms motor pulse and STOP.
                    GardaNativeApi.command(camera, nativeDirection(target.first, target.second))
                } else {
                    OnvifPtz.moveContinuous(camera, target.first, target.second)
                }
                if (!acceptedOnce) {
                    acceptedOnce = true
                    if (!disposed) onInfo(
                        if (useGardaNative) "GARDA command acknowledged; physical motion unverified."
                        else "ONVIF ContinuousMove acknowledged; physical motion unverified."
                    )
                }
                // Never cancel a successful short touch before the camera has time to act.
                // For held gestures re-send at a modest bounded rate.
                val held = desired != null
                Thread.sleep(if (held) 180L else 350L)
                if (!held && desired == null) break
            }
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
        } catch (e: Exception) {
            desired = null
            firstQueued = null
            if (!disposed) onError(PTZFeedback.safeMessage(e))
        } finally {
            try {
                if (useGardaNative) GardaNativeApi.stop(camera)
                else OnvifPtz.stopContinuous(camera)
            } catch (_: Exception) {
                if (!disposed) onError("PTZ Stop not confirmed; check physical camera.")
            }
            synchronized(this) {
                working = false
                if (!disposed && desired != null) {
                    firstQueued = desired
                    working = true
                    worker.execute { runLoop() }
                }
            }
        }
    }

    fun close() {
        disposed = true
        desired = null
        firstQueued = null
        worker.shutdown()
    }

    companion object {
        fun nativeDirection(pan: Double, tilt: Double): GardaAction =
            if (kotlin.math.abs(pan) >= kotlin.math.abs(tilt)) {
                if (pan < 0) GardaAction.LEFT else GardaAction.RIGHT
            } else {
                if (tilt >= 0) GardaAction.UP else GardaAction.DOWN
            }
    }
}

/** Safe messages never echo camera endpoint, credentials or XML payload. */
internal object PTZFeedback {
    fun safeMessage(error: Exception): String {
        val message = error.message.orEmpty()
        return when {
            message.contains("no PTZConfiguration", ignoreCase = true) ->
                "Kamera tidak mengiklankan PTZ pada profil ONVIF."
            message.contains("PTZ service unavailable", ignoreCase = true) ->
                "Firmware kamera tidak menyediakan ONVIF PTZ Service."
            message.contains("ActionNotSupported", ignoreCase = true) ->
                "Kamera menolak perintah PTZ (ActionNotSupported)."
            message.contains("login rejected", ignoreCase = true) ->
                "Login ONVIF ditolak; periksa akun PTZ."
            message.contains("timed out", ignoreCase = true) ->
                "Timeout ke kamera. Periksa jaringan dan server PTZ."
            message.contains("connection refused", ignoreCase = true) ->
                "Port PTZ kamera menolak koneksi."
            else -> "PTZ command failed: " + message
                .replace(Regex("(rtsp|https?)://\\S+"), "[camera-url]")
                .take(120)
        }
    }
}

/**
 * Analog dragpad: release or cancel issues a STOP, thumb snaps back gently.
 * Frame updates never block on HTTP. A short device-side timeout also limits runaway pan.
 */
@Composable
internal fun GardaPtzJoystick(
    camera: CameraInfo,
    useGardaNative: Boolean,
    onProblem: (String) -> Unit,
    onInfo: (String) -> Unit,
    modifier: Modifier = Modifier,
    sensitivity: Float = 2.4f,
    onTouchState: (Boolean) -> Unit = {}
) {
    val touchStateCallback by rememberUpdatedState(onTouchState)
    val liveSensitivity by rememberUpdatedState(sensitivity)
    val errorCallback by rememberUpdatedState(onProblem)
    val infoCallback by rememberUpdatedState(onInfo)
    val driver = remember(
        camera.id, camera.url, camera.onvifUrl, camera.onvifUser, useGardaNative
    ) {
        GardaPtzStickDriver(camera, useGardaNative,
            { errorCallback(it) }, { infoCallback(it) })
    }
    DisposableEffect(driver) {
        onDispose {
            driver.stop()
            driver.close()
        }
    }
    LaunchedEffect(driver) {
        if (!useGardaNative) {
            val result = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                runCatching { OnvifPtz.warmup(camera) }
            }
            result.onSuccess {
                infoCallback("ONVIF PTZ profile available; motor response not yet verified.")
            }.onFailure {
                errorCallback(PTZFeedback.safeMessage(it as? Exception ?: Exception("Unknown")))
            }
        }
    }

    var sidePx by remember { mutableFloatStateOf(1f) }
    var thumb by remember { mutableStateOf(Offset.Zero) }
    var active by remember { mutableStateOf(false) }
    val animatedX by animateFloatAsState(
        if (active) thumb.x else 0f, tween(100), label = "PTZ joystick pan"
    )
    val animatedY by animateFloatAsState(
        if (active) thumb.y else 0f, tween(100), label = "PTZ joystick tilt"
    )
    val red = MaterialTheme.colorScheme.primary
    val outline = MaterialTheme.colorScheme.outline
    val dark = MaterialTheme.colorScheme.surfaceVariant

    fun update(point: Offset) {
        val radius = sidePx * 0.34f
        if (radius <= 0f) return
        var px = point.x - sidePx / 2
        var py = point.y - sidePx / 2
        val length = hypot(px, py)
        if (length > radius) {
            px = px * radius / length
            py = py * radius / length
        }
        thumb = Offset(px, py)
        active = true
        // High sensitivity: 2.4x by default, adjustable without modifying camera firmware.
        val (pan, tilt) = GardaPtzMath.normalize(
            px * liveSensitivity.coerceIn(1f, 3.5f),
            py * liveSensitivity.coerceIn(1f, 3.5f),
            radius
        )
        if (pan == 0.0 && tilt == 0.0) driver.stop()
        else driver.move(pan, tilt)
    }

    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
    Box(
        modifier = Modifier.size(226.dp)
            .clip(CircleShape)
            .background(dark)
            .border(2.dp, red.copy(alpha = .45f), CircleShape)
            .onSizeChanged { sidePx = it.width.toFloat() }
            .pointerInput(driver) {
                // detectDragGestures waits for touch-slop. On a verticalScroll parent
                // the parent's scroll detector can win and the camera never moves.
                // Own the gesture immediately from ACTION_DOWN.
                awaitEachGesture {
                    val down = awaitFirstDown(
                        requireUnconsumed = false,
                        pass = PointerEventPass.Initial
                    )
                    down.consume()
                    touchStateCallback(true)
                    update(down.position)
                    try {
                        while (true) {
                            val event = awaitPointerEvent(PointerEventPass.Initial)
                            val change = event.changes.firstOrNull { it.id == down.id }
                                ?: break
                            if (!change.pressed || change.isConsumed) break
                            update(change.position)
                            change.consume()
                        }
                    } finally {
                        active = false
                        thumb = Offset.Zero
                        driver.stop()
                        touchStateCallback(false)
                    }
                }
            },
        contentAlignment = Alignment.Center
    ) {
        Canvas(Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2, size.height / 2)
            drawCircle(outline.copy(alpha = .2f), radius = size.width * .34f,
                center = center, style = Stroke(width = 2.dp.toPx()))
            drawCircle(outline.copy(alpha = .12f), radius = size.width * .22f,
                center = center, style = Stroke(width = 1.dp.toPx()))
            drawLine(outline.copy(alpha = .25f),
                Offset(center.x, size.height * .12f),
                Offset(center.x, size.height * .88f), 1.dp.toPx())
            drawLine(outline.copy(alpha = .25f),
                Offset(size.width * .12f, center.y),
                Offset(size.width * .88f, center.y), 1.dp.toPx())
        }
        Text("▲", Modifier.align(Alignment.TopCenter).padding(top = 6.dp),
            color = red, style = MaterialTheme.typography.labelLarge)
        Text("▼", Modifier.align(Alignment.BottomCenter).padding(bottom = 6.dp),
            color = red, style = MaterialTheme.typography.labelLarge)
        Text("◀", Modifier.align(Alignment.CenterStart).padding(start = 6.dp),
            color = red, style = MaterialTheme.typography.labelLarge)
        Text("▶", Modifier.align(Alignment.CenterEnd).padding(end = 6.dp),
            color = red, style = MaterialTheme.typography.labelLarge)
        Box(
            Modifier.offset {
                IntOffset(animatedX.roundToInt(), animatedY.roundToInt())
            }.size(55.dp).clip(CircleShape).background(red)
                .border(3.dp, Color.White.copy(alpha = .60f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text("✥", color = Color.White, fontWeight = FontWeight.ExtraBold,
                style = MaterialTheme.typography.headlineSmall)
        }
    }
    // Independent one-shot tests verify whether the camera accepts RelativeMove
    // or the native GARDA motor endpoint even if the finger gesture is blocked.
    Row(
        horizontalArrangement = Arrangement.spacedBy(5.dp),
        modifier = Modifier.horizontalScroll(androidx.compose.foundation.rememberScrollState())
    ) {
        GardaMotionButton("◀", { driver.nudge(-1.0, 0.0) }, filled = false)
        GardaMotionButton("▲", { driver.nudge(0.0, 1.0) }, filled = false)
        GardaMotionButton("▼", { driver.nudge(0.0, -1.0) }, filled = false)
        GardaMotionButton("▶", { driver.nudge(1.0, 0.0) }, filled = false)
    }
    }
}
