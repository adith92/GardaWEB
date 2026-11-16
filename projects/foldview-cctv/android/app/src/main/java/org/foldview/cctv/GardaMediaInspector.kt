package org.foldview.cctv

import org.w3c.dom.Element
import java.net.URI

internal data class GardaStreamProfile(
    val token: String,
    val name: String,
    val width: Int?,
    val height: Int?,
    val rtspUrl: String?
) {
    val resolution: String
        get() = if (width != null && height != null) "$width × $height" else "Unknown"
}
internal data class GardaMediaReport(
    val streams: List<GardaStreamProfile>,
    val encoderOptions: List<String>
)

/** Query only. Never SetVideoEncoderConfiguration without explicit user approval. */
internal object GardaMediaInspector {
    private fun escape(s: String) = s.replace("&", "&amp;")
        .replace("<", "&lt;").replace(">", "&gt;")
        .replace("\"", "&quot;").replace("'", "&apos;")

    private fun nodes(element: Element, name: String): List<Element> {
        val result = element.getElementsByTagNameNS("*", name)
        return (0 until result.length).mapNotNull { result.item(it) as? Element }
    }
    private fun text(element: Element, name: String): String? =
        nodes(element, name).firstOrNull()?.textContent?.trim()
    private fun cameraHost(camera: CameraInfo): String =
        URI(camera.url).host ?: error("RTSP host missing")
    private fun validate(raw: String, camera: CameraInfo, schemes: Set<String>): URI {
        val uri = URI(raw.trim())
        require(uri.scheme?.lowercase() in schemes &&
            uri.host == cameraHost(camera) && uri.fragment == null && uri.userInfo == null) {
            "Camera returned an unsupported external stream/service URI"
        }
        return uri
    }
    fun inspect(camera: CameraInfo): GardaMediaReport {
        require(camera.onvifUrl.isNotBlank()) { "ONVIF Device Service is missing" }
        validate(camera.onvifUrl, camera, setOf("http", "https"))
        val capabilities = AndroidOnvifXml.parse(OnvifPtz.soap(
            camera, camera.onvifUrl,
            "<tds:GetCapabilities><tds:Category>Media</tds:Category></tds:GetCapabilities>"
        ))
        val media = nodes(capabilities.documentElement, "Media")
            .mapNotNull { text(it, "XAddr") }.firstOrNull()
            ?: error("ONVIF Media service is unavailable")
        validate(media, camera, setOf("http", "https"))
        val profiles = AndroidOnvifXml.parse(OnvifPtz.soap(
            camera, media, "<trt:GetProfiles/>"
        ))
        val streams = mutableListOf<GardaStreamProfile>()
        val resolutions = linkedSetOf<String>()
        var encoderToken: String? = null
        for (profile in nodes(profiles.documentElement, "Profiles").take(12)) {
            val token = profile.getAttribute("token").takeIf { it.isNotBlank() && it.length < 128 }
                ?: continue
            val encoder = nodes(profile, "VideoEncoderConfiguration").firstOrNull()
            val current = encoder?.let { nodes(it, "Resolution").firstOrNull() }
            val width = current?.let { text(it, "Width")?.toIntOrNull() }
            val height = current?.let { text(it, "Height")?.toIntOrNull() }
            if (width != null && height != null && width > 0 && height > 0)
                resolutions.add("$width × $height")
            if (encoderToken == null) encoderToken =
                encoder?.getAttribute("token")?.takeIf { it.isNotBlank() }
            val query = """
                <trt:GetStreamUri>
                  <trt:StreamSetup>
                    <tt:Stream>RTP-Unicast</tt:Stream>
                    <tt:Transport><tt:Protocol>RTSP</tt:Protocol></tt:Transport>
                  </trt:StreamSetup>
                  <trt:ProfileToken>${escape(token)}</trt:ProfileToken>
                </trt:GetStreamUri>
            """.trimIndent()
            var stream: String? = null
            try {
                val reply = AndroidOnvifXml.parse(OnvifPtz.soap(camera, media, query))
                val raw = text(reply.documentElement, "Uri")
                if (!raw.isNullOrBlank()) {
                    val uri = validate(raw, camera, setOf("rtsp", "rtsps"))
                    val existingUser = URI(camera.url).rawUserInfo
                    stream = if (!existingUser.isNullOrBlank()) {
                        URI(uri.scheme + "://" + existingUser + "@" +
                            uri.rawAuthority + uri.rawPath.orEmpty() +
                            (uri.rawQuery?.let { "?$it" } ?: "")).toASCIIString()
                    } else uri.toASCIIString()
                }
            } catch (_: Exception) { /* No valid stream URI for this profile */ }
            streams.add(GardaStreamProfile(
                token, text(profile, "Name")?.take(64) ?: token,
                width, height, stream
            ))
        }
        if (!encoderToken.isNullOrBlank()) {
            try {
                val req = "<trt:GetVideoEncoderConfigurationOptions>" +
                    "<trt:ConfigurationToken>${escape(encoderToken)}</trt:ConfigurationToken>" +
                    "</trt:GetVideoEncoderConfigurationOptions>"
                val options = AndroidOnvifXml.parse(OnvifPtz.soap(camera, media, req))
                for (r in nodes(options.documentElement, "ResolutionsAvailable")) {
                    val w = text(r, "Width")?.toIntOrNull()
                    val h = text(r, "Height")?.toIntOrNull()
                    if (w != null && h != null && w in 80..16384 && h in 80..16384)
                        resolutions.add("$w × $h")
                }
            } catch (_: Exception) { /* Optional capability */ }
        }
        return GardaMediaReport(streams, resolutions.toList().take(32))
    }
}
