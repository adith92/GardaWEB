package org.foldview.cctv

import org.w3c.dom.Element
import java.net.URI

data class ResolvedCamera(
    val url: String,
    val onvifUrl: String,
    val method: String,
    val secondaryUrl: String? = null
)

/**
 * Actual ONVIF GetCapabilities -> Media GetProfiles -> GetStreamUri negotiation.
 * A WS-Discovery answer or open 8899 port alone is NOT sufficient for connection.
 * Requests are unauthenticated until the user supplies per-camera credentials.
 */
object CameraQuickConnect {
    fun resolve(
        candidate: LanCamera,
        login: CameraLogin? = null,
        manualRtsp: String = ""
    ): ResolvedCamera {
        val target = candidate.ip
        require(isPrivateIpv4(target)) { "Camera target must be private IPv4" }
        val service = candidate.onvifUrl
            ?: if (candidate.onvifCandidate) "http://$target:8899/onvif/device_service" else null
        val override = manualRtsp.trim()
        if (override.isNotBlank()) {
            requireSameHost(override, target, setOf("rtsp", "rtsps"))
            return ResolvedCamera(
                withRtspCredentials(override, login), service.orEmpty(),
                "User-entered RTSP endpoint (verify playback)"
            )
        }
        var error: String? = null
        if (service != null) {
            try {
                requireSameHost(service, target, setOf("http", "https"))
                val profile = CameraInfo(
                    id = "discovered-$target", name = "Camera $target",
                    url = "rtsp://$target/", onvifUrl = service,
                    onvifUser = login?.username.orEmpty(),
                    onvifPassword = login?.password.orEmpty()
                )
                val capsXml = OnvifPtz.soap(
                    profile, service,
                    "<tds:GetCapabilities><tds:Category>All</tds:Category></tds:GetCapabilities>"
                )
                val caps = parse(capsXml)
                val list = caps.getElementsByTagNameNS("*", "Media")
                var media: String? = null
                for (i in 0 until list.length) {
                    val node = list.item(i) as? Element ?: continue
                    val xaddr = node.getElementsByTagNameNS("*", "XAddr")
                    if (xaddr.length > 0) {
                        media = xaddr.item(0).textContent?.trim()
                        if (media != null) break
                    }
                }
                val mediaUrl = media ?: throw IllegalStateException("ONVIF Media service missing")
                requireSameHost(mediaUrl, target, setOf("http", "https"))
                val profilesDoc = parse(OnvifPtz.soap(profile, mediaUrl, "<trt:GetProfiles/>"))
                val profiles = profilesDoc.getElementsByTagNameNS("*", "Profiles")
                var token: String? = null
                for (i in 0 until profiles.length) {
                    val element = profiles.item(i) as? Element ?: continue
                    val candidateToken = element.getAttribute("token").takeIf { it.isNotEmpty() }
                    if (candidateToken != null) { token = candidateToken; break }
                }
                val safeToken = token?.let(::escapeXml)
                    ?: throw IllegalStateException("ONVIF Media profiles missing")
                val body = """
                    <trt:GetStreamUri>
                      <trt:StreamSetup>
                        <tt:Stream>RTP-Unicast</tt:Stream>
                        <tt:Transport><tt:Protocol>RTSP</tt:Protocol></tt:Transport>
                      </trt:StreamSetup>
                      <trt:ProfileToken>$safeToken</trt:ProfileToken>
                    </trt:GetStreamUri>
                """.trimIndent()
                val streamDoc = parse(OnvifPtz.soap(profile, mediaUrl, body))
                val uriElements = streamDoc.getElementsByTagNameNS("*", "Uri")
                if (uriElements.length == 0) throw IllegalStateException("ONVIF stream URI missing")
                val rtsp = uriElements.item(0).textContent.trim()
                requireSameHost(rtsp, target, setOf("rtsp", "rtsps"))
                // Dual-lens GARDA: verified distinct RTSP listeners on ports 1234/1235.
                val alternate = if (1234 in candidate.rtspPorts && 1235 in candidate.rtspPorts) {
                    if (URI(rtsp).port == 1235) "rtsp://$target:1234/" else "rtsp://$target:1235/"
                } else null
                return ResolvedCamera(
                    withRtspCredentials(rtsp, login),
                    service,
                    "ONVIF GetStreamUri",
                    alternate?.let { withRtspCredentials(it, login) }
                )
            } catch (e: OnvifLoginRequired) {
                // Never fall back to a guessed anonymous stream on a protected device.
                throw e
            } catch (e: Exception) {
                error = "ONVIF negotiation unavailable. Enter camera login and retry, or supply RTSP path."
            }
        }
        // Fullhan on 1234/1235 advertises a bare '/' path. Other vendors
        // generally need an authenticated ONVIF URI or a user-entered RTSP path.
        val known = if (1234 in candidate.rtspPorts) 1234
            else if (1235 in candidate.rtspPorts) 1235 else null
        if (known != null) {
            val alternate = if (1234 in candidate.rtspPorts && 1235 in candidate.rtspPorts) {
                if (known == 1234) "rtsp://$target:1235/" else "rtsp://$target:1234/"
            } else null
            return ResolvedCamera(
                withRtspCredentials("rtsp://$target:$known/", login),
                service.orEmpty(),
                "RTSP listener (ONVIF: ${error ?: "not detected"})",
                alternate?.let { withRtspCredentials(it, login) }
            )
        }
        throw OnvifLoginRequired(
            if (service != null) "ONVIF detected. Check camera username/password or enter RTSP path."
            else "RTSP found. Enter the camera's username/password and full RTSP stream path."
        )
    }

    private fun escapeXml(value: String): String =
        value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")

    private fun parse(xml: String): org.w3c.dom.Document =
        AndroidOnvifXml.parse(xml)

    /** Media3 RTSP supports Basic/Digest credentials supplied as URI user-info. */
    private fun withRtspCredentials(raw: String, login: CameraLogin?): String {
        if (login == null || login.username.isBlank()) return raw
        val uri = URI(raw)
        // URI's multi-argument ctor escapes usernames/passwords containing @/#/spaces.
        val encoded = URI(
            uri.scheme, "${login.username}:${login.password}",
            uri.host, uri.port, uri.rawPath ?: "/", uri.rawQuery, uri.rawFragment
        )
        return encoded.toASCIIString()
    }

    private fun isPrivateIpv4(ip: String): Boolean {
        val x = ip.split(".").mapNotNull { it.toIntOrNull() }
        if (x.size != 4 || x.any { it !in 0..255 }) return false
        return x[0] == 10 || (x[0] == 172 && x[1] in 16..31) ||
            (x[0] == 192 && x[1] == 168)
    }

    private fun requireSameHost(raw: String, ip: String, schemes: Set<String>) {
        val url = URI(raw)
        require(url.scheme?.lowercase() in schemes && url.host == ip) {
            "Camera advertised a non-local endpoint or unsupported protocol"
        }
    }
}

/** Trigger credentials dialog without exposing the camera's SOAP response. */
internal class OnvifLoginRequired(message: String) : IllegalStateException(message)
