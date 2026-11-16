package org.foldview.cctv

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.net.InetSocketAddress
import java.net.Socket
import java.net.URI
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.security.SecureRandom
import kotlin.concurrent.thread
import kotlin.math.max
import kotlin.math.min

/**
 * Experimental ONVIF RTSP Profile T audio backchannel.
 * Supports G.711 PCMU/8000 (RTP-over-RTSP/TCP interleaved) only, when advertised
 * by a camera in a=sendonly SDP. Does not replicate V380 proprietary intercom.
 * Always request Android RECORD_AUDIO permission before start.
 */
class OnvifIntercom {
    @Volatile private var running = false
    private var socket: Socket? = null
    private var audio: AudioRecord? = null
    private val random = SecureRandom()

    @Synchronized fun start(camera: CameraInfo, onState: (Boolean, String) -> Unit) {
        if (running) return
        running = true
        thread(name = "foldview-onvif-intercom", isDaemon = true) {
            try {
                transmit(camera, onState)
            } catch (e: Exception) {
                if (running) onState(false, "Intercom unavailable: " + (e.message ?: "Unsupported camera"))
            } finally {
                stop()
                onState(false, "")
            }
        }
    }

    @Synchronized fun stop() {
        running = false
        try { audio?.stop() } catch (_: Exception) {}
        try { audio?.release() } catch (_: Exception) {}
        audio = null
        try { socket?.close() } catch (_: Exception) {}
        socket = null
    }

    private data class Reply(val status: Int, val headers: Map<String, String>, val body: String)

    private fun transmit(camera: CameraInfo, onState: (Boolean, String) -> Unit) {
        val uri = URI(camera.url)
        require(uri.scheme.equals("rtsp", ignoreCase = true) && uri.host != null) {
            "Only RTSP LAN cameras support this intercom method"
        }
        val userInfo = uri.userInfo.orEmpty().split(":", limit = 2)
        val username = userInfo.firstOrNull().orEmpty().ifEmpty { camera.onvifUser }
        val password = if (userInfo.size == 2) userInfo[1] else camera.onvifPassword
        val host = uri.host
        val port = if (uri.port > 0) uri.port else 554
        val connection = Socket()
        connection.connect(InetSocketAddress(host, port), 4500)
        connection.soTimeout = 4500
        socket = connection
        val input = BufferedInputStream(connection.getInputStream())
        val output = BufferedOutputStream(connection.getOutputStream())
        var cseq = 1
        var authorization: ((String, String) -> String)? = null

        fun request(method: String, url: String, headers: Map<String, String> = emptyMap()): Reply {
            fun send(auth: String?): Reply {
                val sb = StringBuilder()
                sb.append(method).append(" ").append(url).append(" RTSP/1.0\r\n")
                sb.append("CSeq: ").append(cseq++).append("\r\n")
                sb.append("User-Agent: FOLDVIEW/0.3 ONVIF Backchannel\r\n")
                sb.append("Accept: application/sdp\r\n")
                headers.forEach { (key, value) -> sb.append(key).append(": ").append(value).append("\r\n") }
                if (auth != null) sb.append("Authorization: ").append(auth).append("\r\n")
                sb.append("\r\n")
                output.write(sb.toString().toByteArray(StandardCharsets.US_ASCII))
                output.flush()
                val statusLine = line(input)
                if (!statusLine.startsWith("RTSP/1.")) throw IllegalStateException("Invalid RTSP server response")
                val code = statusLine.split(" ").getOrNull(1)?.toIntOrNull() ?: 0
                val parsed = linkedMapOf<String, String>()
                while (true) {
                    val l = line(input)
                    if (l.isEmpty()) break
                    val idx = l.indexOf(':')
                    if (idx > 0) parsed[l.substring(0, idx).lowercase()] = l.substring(idx + 1).trim()
                }
                val len = parsed["content-length"]?.toIntOrNull()?.coerceIn(0, 300_000) ?: 0
                val bytes = ByteArray(len)
                var off = 0
                while (off < len) {
                    val n = input.read(bytes, off, len - off)
                    if (n < 0) throw IllegalStateException("Truncated RTSP response")
                    off += n
                }
                return Reply(code, parsed, String(bytes, StandardCharsets.UTF_8))
            }
            var reply = send(authorization?.invoke(method, url))
            if (reply.status == 401 && username.isNotBlank()) {
                val challenge = reply.headers["www-authenticate"].orEmpty()
                authorization = parseChallenge(challenge, username, password)
                reply = send(authorization?.invoke(method, url))
            }
            if (reply.status != 200) {
                throw IllegalStateException("RTSP " + reply.status +
                    if (reply.status == 551) " (camera lacks ONVIF backchannel)" else " (check firmware/authentication)")
            }
            return reply
        }

        val rawUrl = camera.url.substringBefore("#")
        val controlUrl = URI(
            uri.scheme,
            null,
            uri.host,
            uri.port,
            uri.path.ifEmpty { "/" },
            uri.query,
            null
        ).toASCIIString()
        val required = mapOf("Require" to "www.onvif.org/ver20/backchannel")
        val describe = request("DESCRIBE", controlUrl, required)
        val track = parseSendOnlyPcmuTrack(describe.body)
            ?: throw IllegalStateException("Camera does not advertise G.711 PCMU audio backchannel")
        val trackUrl = if (track.startsWith("rtsp://")) track
            else URI(controlUrl).resolve(track).toString()
        val setup = request(
            "SETUP", trackUrl,
            required + mapOf("Transport" to "RTP/AVP/TCP;unicast;interleaved=0-1")
        )
        val session = setup.headers["session"]?.substringBefore(";")?.trim()
            ?: throw IllegalStateException("RTSP session absent")
        val channel = Regex("interleaved=(\\d+)-(\\d+)", RegexOption.IGNORE_CASE)
            .find(setup.headers["transport"].orEmpty())?.groupValues?.getOrNull(1)?.toIntOrNull() ?: 0
        val play = request("PLAY", controlUrl, required + mapOf("Session" to session))
        if (play.status != 200) throw IllegalStateException("Intercom rejected by camera")
        // No RTP is sent until PLAY 200 OK, as required by ONVIF.
        val minBytes = AudioRecord.getMinBufferSize(
            8000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT
        )
        require(minBytes > 0) { "8 kHz microphone capture unavailable on this phone" }
        val recorder = AudioRecord.Builder()
            .setAudioSource(MediaRecorder.AudioSource.MIC)
            .setAudioFormat(
                AudioFormat.Builder().setSampleRate(8000)
                    .setChannelMask(AudioFormat.CHANNEL_IN_MONO)
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT).build()
            )
            .setBufferSizeInBytes(max(3200, minBytes * 2))
            .build()
        audio = recorder
        check(recorder.state == AudioRecord.STATE_INITIALIZED) { "Android microphone initialization failed" }
        recorder.startRecording()
        onState(true, "Talk active (ONVIF G.711)")
        var seq = random.nextInt(65536)
        var timestamp = random.nextInt()
        val ssrc = random.nextInt()
        val frame = ShortArray(160)
        while (running && connection.isConnected && !connection.isClosed) {
            var have = 0
            while (have < frame.size && running) {
                val n = recorder.read(frame, have, frame.size - have, AudioRecord.READ_BLOCKING)
                if (n < 0) throw IllegalStateException("Microphone capture failed")
                if (n == 0) continue
                have += n
            }
            if (!running) break
            val rtp = ByteArray(12 + 160)
            rtp[0] = 0x80.toByte()
            rtp[1] = 0 // PCMU payload type 0
            rtp[2] = (seq shr 8).toByte()
            rtp[3] = seq.toByte()
            for (i in 0..3) {
                rtp[4 + i] = (timestamp ushr (24 - i * 8)).toByte()
                rtp[8 + i] = (ssrc ushr (24 - i * 8)).toByte()
            }
            for (i in frame.indices) rtp[12 + i] = g711u(frame[i])
            output.write(36) // '$' frame marker
            output.write(channel)
            output.write((rtp.size ushr 8) and 0xff)
            output.write(rtp.size and 0xff)
            output.write(rtp)
            output.flush()
            seq = (seq + 1) and 0xffff
            timestamp += 160
        }
        try {
            request("TEARDOWN", controlUrl, required + mapOf("Session" to session))
        } catch (_: Exception) { /* server may already have closed */ }
    }

    private fun parseSendOnlyPcmuTrack(sdp: String): String? {
        var control: String? = null
        var isAudio = false
        var sendOnly = false
        var pcmu = false
        fun finish(): String? {
            return if (isAudio && sendOnly && pcmu) control else null
        }
        for (line in sdp.lines()) {
            val l = line.trim()
            if (l.startsWith("m=")) {
                finish()?.let { return it }
                isAudio = l.startsWith("m=audio ")
                control = null
                sendOnly = false
                pcmu = isAudio && l.split(" ").contains("0")
            } else if (isAudio) {
                if (l.equals("a=sendonly", ignoreCase = true)) sendOnly = true
                if (l.startsWith("a=control:")) control = l.substringAfter(":").trim()
                if (Regex("a=rtpmap:0\\s+PCMU/8000", RegexOption.IGNORE_CASE).containsMatchIn(l) ||
                    l.startsWith("m=audio ") && l.split(" ").contains("0")) pcmu = true
            }
        }
        return finish()
    }

    private fun g711u(sample: Short): Byte {
        val input = sample.toInt()
        val sign = if (input < 0) 0x80 else 0
        val value = min(if (input < 0) -input else input, 32635) + 132
        var exponent = 7
        var mask = 0x4000
        while (exponent > 0 && (value and mask) == 0) {
            mask = mask shr 1
            exponent--
        }
        val mantissa = (value shr (exponent + 3)) and 0x0f
        return ((sign or (exponent shl 4) or mantissa) xor 0xff).toByte()
    }

    private fun parseChallenge(header: String, username: String, password: String): ((String, String) -> String)? {
        if (header.startsWith("Basic", ignoreCase = true)) {
            val s = android.util.Base64.encodeToString(
                (username + ":" + password).toByteArray(Charsets.UTF_8),
                android.util.Base64.NO_WRAP
            )
            return { _, _ -> "Basic " + s }
        }
        if (!header.startsWith("Digest", ignoreCase = true)) return null
        val realm = Regex("realm=\"([^\"]+)\"", RegexOption.IGNORE_CASE).find(header)?.groupValues?.getOrNull(1)
            ?: return null
        val nonce = Regex("nonce=\"([^\"]+)\"", RegexOption.IGNORE_CASE).find(header)?.groupValues?.getOrNull(1)
            ?: return null
        val qop = if (Regex("qop=\"?auth", RegexOption.IGNORE_CASE).containsMatchIn(header)) "auth" else null
        val opaque = Regex("opaque=\"([^\"]+)\"", RegexOption.IGNORE_CASE).find(header)?.groupValues?.getOrNull(1)
        val cnonce = random.nextLong().toULong().toString(16)
        var n = 0
        fun md5(s: String): String = MessageDigest.getInstance("MD5")
            .digest(s.toByteArray(StandardCharsets.ISO_8859_1))
            .joinToString("") { "%02x".format(it.toInt() and 0xff) }
        return { method, target ->
            n += 1
            val nc = "%08x".format(n)
            val ha1 = md5(username + ":" + realm + ":" + password)
            val ha2 = md5(method + ":" + target)
            val response = if (qop == "auth") md5(ha1 + ":" + nonce + ":" + nc + ":" + cnonce + ":auth:" + ha2)
                else md5(ha1 + ":" + nonce + ":" + ha2)
            "Digest username=\"" + username.replace("\"", "") + "\", realm=\"" + realm +
                "\", nonce=\"" + nonce + "\", uri=\"" + target +
                "\", response=\"" + response + "\"" +
                (if (qop != null) ", qop=auth, nc=" + nc + ", cnonce=\"" + cnonce + "\"" else "") +
                (if (opaque != null) ", opaque=\"" + opaque + "\"" else "")
        }
    }

    private fun line(input: BufferedInputStream): String {
        val bytes = java.io.ByteArrayOutputStream()
        while (bytes.size() < 8192) {
            val c = input.read()
            if (c < 0) throw IllegalStateException("RTSP server closed")
            if (c == 10) break
            if (c != 13) bytes.write(c)
        }
        return bytes.toString("UTF-8")
    }
}
