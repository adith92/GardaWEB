package org.foldview.cctv

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL

/**
 * Vendor-specific extensions for the user's custom FH8852V201 GARDA daemon.
 *
 * NOT standard ONVIF. Only show controls after an explicit /api/status check.
 * No shell, Telnet, binary PTZ or unrestricted URL entry.
 * The daemon may be unauthenticated: use only on a trusted isolated camera LAN.
 */
data class GardaTelemetry(
    val ip: String,
    val uptimeSeconds: Long,
    val freeRamKb: String,
    val dualLens: Boolean
)

enum class GardaAction(val path: String, val label: String) {
    LEFT("/api/ptz?dir=left", "Left"),
    RIGHT("/api/ptz?dir=right", "Right"),
    UP("/api/ptz?dir=up", "Up"),
    DOWN("/api/ptz?dir=down", "Down"),
    STOP("/api/ptz?dir=stop", "Stop"),
    CENTER("/api/ptz?dir=center", "Center"),
    IR_ON("/api/led?mode=ir_on", "IR on"),
    IR_OFF("/api/led?mode=ir_off", "IR off"),
    WHITE_ON("/api/led?mode=white_on", "White light on"),
    WHITE_OFF("/api/led?mode=white_off", "White light off"),
    IRCUT_DAY("/api/led?mode=ircut_day", "Day filter"),
    IRCUT_NIGHT("/api/led?mode=ircut_night", "Night filter")
}

object GardaNativeApi {
    private fun host(camera: CameraInfo): String {
        val uri = URI(camera.url)
        val ip = uri.host ?: throw IllegalArgumentException("No camera host")
        val bytes = ip.split('.').mapNotNull { it.toIntOrNull() }
        require(bytes.size == 4 && bytes.all { it in 0..255 }) { "Camera must be a private IPv4 device" }
        require(bytes[0] == 10 || (bytes[0] == 172 && bytes[1] in 16..31) ||
            (bytes[0] == 192 && bytes[1] == 168)) { "GARDA control is LAN only" }
        return ip
    }

    private fun request(ip: String, path: String, method: String): String {
        val conn = URL("http://" + ip + ":8899" + path).openConnection() as HttpURLConnection
        try {
            conn.requestMethod = method
            conn.connectTimeout = 1800
            conn.readTimeout = 1800
            conn.instanceFollowRedirects = false
            conn.useCaches = false
            if (method == "POST") {
                conn.doOutput = true
                conn.setFixedLengthStreamingMode(0)
                conn.outputStream.use { }
            }
            val code = conn.responseCode
            if (code !in 200..299) throw IllegalStateException("GARDA daemon HTTP " + code)
            val length = conn.contentLength
            if (length > 4096) throw IllegalStateException("Unexpected GARDA response size")
            conn.inputStream.use { input ->
                val buffer = ByteArray(4097)
                var total = 0
                while (total < buffer.size) {
                    val n = input.read(buffer, total, buffer.size - total)
                    if (n <= 0) break
                    total += n
                }
                if (total > 4096) throw IllegalStateException("GARDA response too large")
                return String(buffer, 0, total, Charsets.UTF_8)
            }
        } finally {
            conn.disconnect()
        }
    }

    fun status(camera: CameraInfo): GardaTelemetry {
        val ip = host(camera)
        val json = JSONObject(request(ip, "/api/status", "GET"))
        check(json.optString("status") == "online" && json.optBoolean("vlcview_running", false)) {
            "Not an online GARDA FH8852 camera"
        }
        return GardaTelemetry(
            ip = ip,
            uptimeSeconds = json.optLong("uptime_sec", 0L),
            freeRamKb = json.optString("free_ram_kb", "?"),
            dualLens = json.optBoolean("dual_lens", false)
        )
    }

    /** Send a bounded camera-side STOP even when a gesture is released mid-scroll. */
    fun stop(camera: CameraInfo) {
        val ip = host(camera)
        request(ip, GardaAction.STOP.path, "POST")
    }

    /** Returns an HTTP acknowledgement, not proof of physical motor/light movement. */
    fun command(camera: CameraInfo, action: GardaAction): String {
        val telemetry = status(camera) // Fail closed if this isn't a known GARDA daemon
        val body = request(telemetry.ip, action.path, "POST")
        if (body.trimStart().startsWith("{")) {
            val result = JSONObject(body)
            if (result.has("success") && !result.optBoolean("success")) {
                throw IllegalStateException("GARDA command rejected")
            }
            if (result.has("ok") && !result.optBoolean("ok")) {
                throw IllegalStateException("GARDA command rejected")
            }
            if (result.has("error") && !result.isNull("error")) {
                throw IllegalStateException("GARDA command reported an error")
            }
        }
        // The daemon handles hardware-specific motor steps. Stop as a second
        // explicit POST; never issue an unbounded repeat loop.
        if (action in listOf(GardaAction.LEFT, GardaAction.RIGHT, GardaAction.UP, GardaAction.DOWN)) {
            Thread.sleep(220L)
            try { request(telemetry.ip, GardaAction.STOP.path, "POST") }
            catch (_: Exception) { /* Daemon's own movement timeout remains essential. */ }
        }
        return action.label + " sent (verify camera movement)"
    }
}
