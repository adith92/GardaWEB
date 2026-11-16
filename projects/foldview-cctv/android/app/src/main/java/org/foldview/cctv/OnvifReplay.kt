package org.foldview.cctv

import android.net.Uri
import org.w3c.dom.Element
import java.net.URI
import java.util.concurrent.ConcurrentHashMap

data class RemoteRecording(val token: String, val label: String)

/**
 * ONVIF Profile G Recording/Replay discovery. It does not provide V380 P2P
 * cloud playback, SD file download, or a full ONVIF recording search timeline.
 *
 * GetReplayUri RTSP stream may require ONVIF Replay RTSP time-range extensions
 * that Media3 ExoPlayer doesn't support. This is an experimental first step.
 */
object OnvifReplay {
    private data class Services(val recording: String, val replay: String)
    private val cache = ConcurrentHashMap<String, Services>()

    private fun parse(s: String): org.w3c.dom.Document = AndroidOnvifXml.parse(s)

    private fun childrenText(parent: Element, name: String): String? {
        val n = parent.getElementsByTagNameNS("*", name)
        return if (n.length > 0) n.item(0).textContent?.trim()?.takeIf { it.isNotEmpty() } else null
    }

    private fun endpoint(s: String): String {
        val address = URI(s)
        require(address.scheme.equals("http", true) || address.scheme.equals("https", true)) {
            "ONVIF service did not provide an HTTP endpoint"
        }
        return s
    }

    private fun services(camera: CameraInfo): Services {
        cache[camera.id]?.let { return it }
        check(camera.onvifUrl.isNotBlank()) { "Configure ONVIF Device Service URL first" }
        val response = OnvifPtz.soap(
            camera,
            endpoint(camera.onvifUrl),
            "<tds:GetServices><tds:IncludeCapability>false</tds:IncludeCapability></tds:GetServices>"
        )
        val document = parse(response)
        val nodes = document.getElementsByTagNameNS("*", "Service")
        var recording: String? = null
        var replay: String? = null
        for (i in 0 until nodes.length) {
            val element = nodes.item(i) as? Element ?: continue
            val namespace = childrenText(element, "Namespace").orEmpty()
            val xaddr = childrenText(element, "XAddr").orEmpty()
            if (namespace.endsWith("/recording/wsdl") && xaddr.isNotBlank()) recording = endpoint(xaddr)
            if (namespace.endsWith("/replay/wsdl") && xaddr.isNotBlank()) replay = endpoint(xaddr)
        }
        val pair = Services(
            recording ?: throw IllegalStateException("Camera does not expose ONVIF Profile G Recording service"),
            replay ?: throw IllegalStateException("Camera does not expose ONVIF Profile G Replay service")
        )
        cache[camera.id] = pair
        return pair
    }

    fun list(camera: CameraInfo): List<RemoteRecording> {
        val target = services(camera)
        val reply = OnvifPtz.soap(camera, target.recording, "<trc:GetRecordings/>")
        val document = parse(reply)
        val items = document.getElementsByTagNameNS("*", "GetRecordingsResponseItem")
        val found = linkedMapOf<String, RemoteRecording>()
        for (i in 0 until minOf(items.length, 200)) {
            val item = items.item(i) as? Element ?: continue
            val token = childrenText(item, "RecordingToken").orEmpty()
            if (token.isBlank() || token.length > 256) continue
            val title = childrenText(item, "Name")?.take(90)
                ?: "Camera recording " + (found.size + 1)
            found[token] = RemoteRecording(token, title)
        }
        return found.values.toList()
    }

    fun replayUri(camera: CameraInfo, token: String): Uri {
        require(token.isNotBlank() && token.length <= 256)
        val svc = services(camera)
        val safeToken = token.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")
        val body = """
            <trp:GetReplayUri>
              <trp:StreamSetup>
                <tt:Stream>RTP-Unicast</tt:Stream>
                <tt:Transport><tt:Protocol>RTSP</tt:Protocol></tt:Transport>
              </trp:StreamSetup>
              <trp:RecordingToken>$safeToken</trp:RecordingToken>
            </trp:GetReplayUri>
        """.trimIndent()
        val response = parse(OnvifPtz.soap(camera, svc.replay, body))
        val uri = response.getElementsByTagNameNS("*", "Uri")
        require(uri.length > 0) { "Camera did not provide a replay RTSP URL" }
        val url = uri.item(0).textContent?.trim().orEmpty()
        val link = URI(url)
        require(link.scheme.equals("rtsp", true) || link.scheme.equals("rtsps", true)) {
            "Camera did not return an RTSP replay URL"
        }
        require(link.host != null && link.host.isNotBlank()) { "Replay host missing" }
        // Do not send replay URLs to third-party analytics or logs.
        return Uri.parse(url)
    }
}
