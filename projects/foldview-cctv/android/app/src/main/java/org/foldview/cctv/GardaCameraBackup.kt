package org.foldview.cctv

import java.net.URI
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

/**
 * User-triggered portable camera registry, intentionally WITHOUT passwords.
 * CameraVault remains AES-GCM encrypted on-device.
 * A new app install can import device names, addresses and ONVIF endpoints,
 * but must request any protected RTSP/ONVIF credentials again.
 */
internal object GardaCameraBackup {
    private const val MAX_FILE = 128_000
    private const val MAX_CAMERAS = 128

    private fun withoutPassword(url: String, supported: Set<String>): String {
        val uri = URI(url.trim())
        require(uri.scheme?.lowercase() in supported && uri.host != null) {
            "Camera URL has an unsupported protocol or host"
        }
        require(uri.host.length <= 100 && url.length <= 1024)
        return URI(
            uri.scheme, null, uri.host, uri.port, uri.path,
            uri.query, null
        ).toASCIIString()
    }

    fun export(cameras: List<CameraInfo>): String {
        val entries = JSONArray()
        for (camera in cameras.take(MAX_CAMERAS)) {
            entries.put(JSONObject().apply {
                put("name", camera.name.take(90))
                put("rtspUrl", withoutPassword(camera.url, setOf("rtsp", "rtsps")))
                put("onvifUrl", camera.onvifUrl.takeIf { it.isNotBlank() }
                    ?.let { withoutPassword(it, setOf("http", "https")) } ?: "")
            })
        }
        return JSONObject().put("format", "garda-camera-list-v1")
            .put("passwordsExported", false)
            .put("cameras", entries).toString(2)
    }

    fun import(json: String): List<CameraInfo> {
        require(json.length in 1..MAX_FILE) { "Camera backup file is invalid or too large" }
        val payload = JSONObject(json)
        require(payload.optString("format") == "garda-camera-list-v1") {
            "Unsupported camera backup format"
        }
        val entries = payload.getJSONArray("cameras")
        require(entries.length() <= MAX_CAMERAS) { "Too many imported devices" }
        return (0 until entries.length()).map { i ->
            val item = entries.getJSONObject(i)
            val name = item.optString("name").take(90).ifBlank { "GARDA camera" }
            val video = withoutPassword(item.getString("rtspUrl"), setOf("rtsp", "rtsps"))
            val onvif = item.optString("onvifUrl").takeIf { it.isNotBlank() }
                ?.let { withoutPassword(it, setOf("http", "https")) }.orEmpty()
            CameraInfo(
                UUID.randomUUID().toString(), name, video, onvif,
                onvifUser = "", onvifPassword = ""
            )
        }
    }
}
