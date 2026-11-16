package org.foldview.cctv

import android.util.Base64
import org.w3c.dom.Element
import org.w3c.dom.Node
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.security.SecureRandom
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/**
 * ONVIF Profile S/T PTZ client using UsernameToken PasswordDigest SOAP.
 * Runs on a worker thread; no credentials or payloads are logged.
 * Requires a camera exposing the ONVIF Device, Media and PTZ services.
 *
 * No V380 proprietary UID/P2P support is implied by this implementation.
 */
object OnvifPtz {
    private val random = SecureRandom()
    private val cache = mutableMapOf<String, Pair<String, String>>()

    @Synchronized
    private fun endpoints(camera: CameraInfo): Pair<String, String> {
        cache[camera.id]?.let { return it }
        val deviceUrl = camera.onvifUrl.trim()
        require(deviceUrl.startsWith("http://") || deviceUrl.startsWith("https://")) {
            "Camera has no ONVIF service URL"
        }
        val capabilities = post(
            deviceUrl,
            camera,
            "<tds:GetCapabilities><tds:Category>All</tds:Category></tds:GetCapabilities>"
        )
        val doc = parse(capabilities)
        fun findXaddr(parentName: String): String? {
            val roots = doc.getElementsByTagNameNS("*", parentName)
            for (i in 0 until roots.length) {
                val n = roots.item(i)
                val children = (n as? Element)?.getElementsByTagNameNS("*", "XAddr") ?: continue
                if (children.length > 0) return children.item(0).textContent?.trim()
            }
            return null
        }
        val ptzUrl = findXaddr("PTZ") ?: throw IllegalStateException("PTZ service unavailable for camera")
        val mediaUrl = findXaddr("Media") ?: throw IllegalStateException("ONVIF Media service unavailable")
        val host = try { java.net.URI(camera.url).host } catch (_: Exception) { null }
        require(host != null)
        listOf(ptzUrl, mediaUrl).forEach { raw ->
            val service = java.net.URI(raw)
            require(service.host == host && service.scheme.lowercase() in listOf("http", "https")) {
                "ONVIF returned an unsupported external service URL"
            }
        }
        val profileDoc = parse(post(mediaUrl, camera, "<trt:GetProfiles/>"))
        val profiles = profileDoc.getElementsByTagNameNS("*", "Profiles")
        var token: String? = null
        for (i in 0 until profiles.length) {
            val e = profiles.item(i) as? Element ?: continue
            if (e.getElementsByTagNameNS("*", "PTZConfiguration").length > 0) {
                token = e.getAttribute("token").takeIf { it.isNotBlank() }
                if (token != null) break
            }
        }
        // Do not pretend a video-only profile has physical PTZ capability.
        val resolved = ptzUrl to (token?.takeIf { it.isNotBlank() }
            ?: throw IllegalStateException(
                "ONVIF camera has no PTZConfiguration in its media profiles"
            ))
        cache[camera.id] = resolved
        return resolved
    }

    /**
     * Brief movement only. Always try Stop, including after errors.
     * pan/tilt range is [-1.0,+1.0]; camera-specific scaling may differ.
     */
    fun pulse(camera: CameraInfo, pan: Double, tilt: Double) {
        require(pan in -1.0..1.0 && tilt in -1.0..1.0)
        val (service, token) = endpoints(camera)
        val safeToken = xml(token)
        val move = """
            <tptz:ContinuousMove>
              <tptz:ProfileToken>$safeToken</tptz:ProfileToken>
              <tptz:Velocity><tt:PanTilt x="$pan" y="$tilt"/></tptz:Velocity>
              <tptz:Timeout>PT0.35S</tptz:Timeout>
            </tptz:ContinuousMove>
        """.trimIndent()
        try {
            post(service, camera, move)
            Thread.sleep(280L)
        } finally {
            try {
                post(
                    service,
                    camera,
                    "<tptz:Stop><tptz:ProfileToken>$safeToken</tptz:ProfileToken><tptz:PanTilt>true</tptz:PanTilt><tptz:Zoom>true</tptz:Zoom></tptz:Stop>"
                )
            } catch (_: Exception) {
                // Some cameras reject Zoom Stop if PTZ is pan/tilt only.
            }
        }
    }

    /**
     * Real-time analog joystick PTZ: one short ContinuousMove request.
     * The camera itself stops at the timeout if the connection is lost.
     * Do not sleep or block the Compose input thread.
     */
    fun moveContinuous(camera: CameraInfo, pan: Double, tilt: Double) {
        require(pan in -1.0..1.0 && tilt in -1.0..1.0)
        val (service, token) = endpoints(camera)
        val body = """
            <tptz:ContinuousMove>
              <tptz:ProfileToken>${xml(token)}</tptz:ProfileToken>
              <tptz:Velocity><tt:PanTilt x="$pan" y="$tilt"/></tptz:Velocity>
              <tptz:Timeout>PT1S</tptz:Timeout>
            </tptz:ContinuousMove>
        """.trimIndent()
        post(service, camera, body)
    }

    /**
     * ONVIF RelativeMove for explicit one-shot diagnostic arrows.
     * Cameras may support relative but not continuous control (or vice versa).
     * Request is bounded; never send RelativeMove in a high-frequency loop.
     */
    fun relativeStep(camera: CameraInfo, pan: Double, tilt: Double) {
        require(pan in -1.0..1.0 && tilt in -1.0..1.0)
        require(pan != 0.0 || tilt != 0.0)
        val (service, token) = endpoints(camera)
        val body = """
            <tptz:RelativeMove>
                <tptz:ProfileToken>${xml(token)}</tptz:ProfileToken>
                <tptz:Translation>
                    <tt:PanTilt x="$pan" y="$tilt"/>
                </tptz:Translation>
            </tptz:RelativeMove>
        """.trimIndent()
        post(service, camera, body)
    }

    /** Explicit stop on finger lift/cancel/screen exit. */
    fun stopContinuous(camera: CameraInfo) {
        val (service, token) = endpoints(camera)
        post(service, camera, """
            <tptz:Stop>
              <tptz:ProfileToken>${xml(token)}</tptz:ProfileToken>
              <tptz:PanTilt>true</tptz:PanTilt>
              <tptz:Zoom>false</tptz:Zoom>
            </tptz:Stop>
        """.trimIndent())
    }

    /** Pre-resolve ONVIF endpoints on an IO worker to shorten first-drag latency. */
    fun warmup(camera: CameraInfo) {
        endpoints(camera)
    }

    /** Brief zoom movement. Requires a camera with a PTZ zoom space. */
    fun pulseZoom(camera: CameraInfo, zoom: Double) {
        require(zoom in -1.0..1.0 && zoom != 0.0)
        val (service, token) = endpoints(camera)
        val safeToken = xml(token)
        val body = """
            <tptz:ContinuousMove>
              <tptz:ProfileToken>$safeToken</tptz:ProfileToken>
              <tptz:Velocity><tt:Zoom x="$zoom"/></tptz:Velocity>
              <tptz:Timeout>PT0.35S</tptz:Timeout>
            </tptz:ContinuousMove>
        """.trimIndent()
        try {
            post(service, camera, body)
            Thread.sleep(280L)
        } finally {
            try {
                post(service, camera,
                    "<tptz:Stop><tptz:ProfileToken>$safeToken</tptz:ProfileToken><tptz:Zoom>true</tptz:Zoom></tptz:Stop>"
                )
            } catch (_: Exception) {}
        }
    }

    /** Shared SOAP transport and WS-Security for ONVIF Profile G requests. */
    internal fun soap(camera: CameraInfo, serviceUrl: String, body: String): String =
        post(serviceUrl, camera, body)

    private fun xml(v: String) = v.replace("&", "&amp;")
        .replace("<", "&lt;").replace(">", "&gt;")
        .replace("\"", "&quot;").replace("'", "&apos;")

    private fun security(camera: CameraInfo): String {
        if (camera.onvifUser.isEmpty()) return ""
        val nonce = ByteArray(20).also(random::nextBytes)
        val now = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).also {
            it.timeZone = TimeZone.getTimeZone("UTC")
        }.format(Date())
        val digest = MessageDigest.getInstance("SHA-1").digest(
            nonce + now.toByteArray(Charsets.UTF_8) + camera.onvifPassword.toByteArray(Charsets.UTF_8)
        )
        val b64Nonce = Base64.encodeToString(nonce, Base64.NO_WRAP)
        val b64Digest = Base64.encodeToString(digest, Base64.NO_WRAP)
        return """
            <wsse:Security s:mustUnderstand="1">
              <wsse:UsernameToken>
                <wsse:Username>${xml(camera.onvifUser)}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">$b64Digest</wsse:Password>
                <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">$b64Nonce</wsse:Nonce>
                <wsu:Created>$now</wsu:Created>
              </wsse:UsernameToken>
            </wsse:Security>
        """.trimIndent()
    }

    private fun post(url: String, camera: CameraInfo, body: String): String {
        val envelope = """
            <?xml version="1.0" encoding="UTF-8"?>
            <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
                xmlns:tds="http://www.onvif.org/ver10/device/wsdl"
                xmlns:trt="http://www.onvif.org/ver10/media/wsdl"
                xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl"
                xmlns:trc="http://www.onvif.org/ver10/recording/wsdl"
                xmlns:trp="http://www.onvif.org/ver10/replay/wsdl"
                xmlns:tt="http://www.onvif.org/ver10/schema">
                <s:Header>${security(camera)}</s:Header>
                <s:Body>$body</s:Body>
            </s:Envelope>
        """.trimIndent()
        val connection = (URL(url).openConnection() as HttpURLConnection)
        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = 2800
            connection.readTimeout = 2800
            connection.doOutput = true
            connection.instanceFollowRedirects = false
            connection.setRequestProperty("Content-Type", "application/soap+xml; charset=utf-8")
            connection.outputStream.use { it.write(envelope.toByteArray(Charsets.UTF_8)) }
            val code = connection.responseCode
            if (code == 401 || code == 403) {
                throw OnvifLoginRequired("Camera ONVIF login rejected (HTTP $code). Check credentials.")
            }
            val stream = if (code in 200..299) connection.inputStream
                else connection.errorStream
            val response = stream?.bufferedReader(Charsets.UTF_8)?.use { reader ->
                val result = StringBuilder()
                val chars = CharArray(4096)
                while (true) {
                    val n = reader.read(chars)
                    if (n < 0) break
                    if (result.length + n > 250_000)
                        throw IllegalStateException("ONVIF response too large")
                    result.append(chars, 0, n)
                }
                result.toString()
            }.orEmpty()
            // Many ONVIF firmware versions incorrectly reply HTTP 200 for SOAP faults.
            // The original client treated those as successful camera movement.
            val fault = parseFault(response)
            if (fault != null) throw IllegalStateException("ONVIF SOAP Fault: $fault")
            if (code !in 200..299) throw IllegalStateException("ONVIF HTTP $code")
            return response
        } finally {
            connection.disconnect()
        }
    }

    /**
     * Extract a sanitized SOAP fault identifier. Never surface an entire SOAP body,
     * camera credentials, or an untrusted URL in Android error messages.
     */
    internal fun parseFault(soap: String): String? {
        if (!soap.contains("Fault", ignoreCase = true)) return null
        val doc = runCatching { AndroidOnvifXml.parse(soap) }.getOrNull() ?: return null
        val faults = doc.getElementsByTagNameNS("*", "Fault")
        if (faults.length == 0) return null
        val root = faults.item(0) as? Element ?: return "unknown"
        fun safe(value: String): String = value
            .replace(Regex("[^a-zA-Z0-9_ :.-]"), " ")
            .trim().take(85)
        val code = root.getElementsByTagNameNS("*", "Subcode")
            .item(0)?.textContent?.trim()?.let(::safe)
        val reason = root.getElementsByTagNameNS("*", "Reason")
            .item(0)?.textContent?.trim()?.let(::safe)
        return listOfNotNull(code, reason)
            .filter { it.isNotBlank() }
            .joinToString(" / ").ifBlank { "unknown" }
    }

    private fun parse(xml: String): org.w3c.dom.Document = AndroidOnvifXml.parse(xml)
}
