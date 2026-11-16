package org.foldview.cctv

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.Inet4Address
import java.net.InetSocketAddress
import java.net.Socket
import java.net.URI
import java.util.concurrent.Callable
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/** Observations only. An open port is NOT proof of ONVIF or root access. */
data class LanCamera(
    val ip: String,
    val rtspPorts: List<Int>,
    val onvifUrl: String?,
    val onvifCandidate: Boolean,
    val source: String
) {
    val summary: String
        get() = buildString {
            append(source)
            if (rtspPorts.isNotEmpty()) append("  · RTSP " + rtspPorts.joinToString(","))
            if (onvifUrl != null) append(" · ONVIF discovered")
            else if (onvifCandidate) append(" · ONVIF port open (unverified)")
        }
}

/**
 * User-triggered discovery on the active Wi-Fi subnet only.
 * - WS-Discovery multicast with existing multicast lock.
 * - TCP camera-port checks, max 20 concurrent workers, bounded timeout.
 * - No Telnet/SSH/auth guessing, no firmware changes, no data exfiltration.
 * - At most one local /24, even on a larger private subnet.
 */
object LanCameraScanner {
    private val CAMERA_PORTS = intArrayOf(554, 8554, 1234, 1235, 8899)

    fun scan(context: Context, status: (String) -> Unit): List<LanCamera> {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val active = cm.activeNetwork ?: throw IllegalStateException("Connect Fold7 to camera Wi-Fi")
        val caps = cm.getNetworkCapabilities(active)
        check(caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true ||
            caps?.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) == true) {
            "Connect to your camera Wi-Fi/LAN before scanning"
        }
        val props = cm.getLinkProperties(active)
            ?: throw IllegalStateException("Cannot read local Wi-Fi subnet")
        val link = props.linkAddresses.firstOrNull {
            it.address is Inet4Address && it.address.isSiteLocalAddress &&
                it.prefixLength in 16..30
        } ?: throw IllegalStateException("No private IPv4 LAN interface")
        val addr = link.address.address.map { it.toInt() and 255 }
        // Never extend beyond local /24: device discovery must remain bounded.
        val segment = "${addr[0]}.${addr[1]}.${addr[2]}"
        val prefix = maxOf(24, link.prefixLength)
        fun insideLocalSubnet(last: Int): Boolean {
            val ipValue = (addr[0].toLong() shl 24) or (addr[1].toLong() shl 16) or
                (addr[2].toLong() shl 8) or last.toLong()
            val ownValue = (addr[0].toLong() shl 24) or (addr[1].toLong() shl 16) or
                (addr[2].toLong() shl 8) or addr[3].toLong()
            val mask = (0xffffffffL shl (32-prefix)) and 0xffffffffL
            return (ipValue and mask) == (ownValue and mask)
        }
        val hosts = (1..254).filter { insideLocalSubnet(it) && it != addr[3] }
            .map { "$segment.$it" }
        val services = linkedMapOf<String, MutableSet<Int>>()
        val xaddrs = linkedMapOf<String, String>()
        status("Looking for ONVIF cameras (WS-Discovery)...")
        for (address in OnvifDiscovery.discover(context)) {
            try {
                val url = URI(address)
                val host = url.host ?: continue
                if (!host.startsWith("$segment.") || host !in hosts) continue
                if (url.scheme !in listOf("http", "https")) continue
                if (url.port !in -1..65535) continue
                xaddrs[host] = address
            } catch (_: Exception) {}
        }
        status("Checking camera ports on $segment.0/24 (limited scan)...")
        val workers = Executors.newFixedThreadPool(20)
        try {
            val tasks = hosts.map { ip ->
                Callable {
                    val ports = CAMERA_PORTS.filter { port ->
                        try {
                            Socket().use {
                                it.connect(InetSocketAddress(ip, port), 220)
                                true
                            }
                        } catch (_: Exception) { false }
                    }
                    ip to ports
                }
            }
            // Fails closed on excessive scan duration; no runaway background scan.
            val futures = workers.invokeAll(tasks, 28, TimeUnit.SECONDS)
            for (future in futures) {
                if (future.isCancelled) continue
                try {
                    val (ip, ports) = future.get()
                    if (ports.isNotEmpty()) services[ip] = ports.toMutableSet()
                } catch (_: Exception) {}
            }
        } finally { workers.shutdownNow() }
        val devices = mutableListOf<LanCamera>()
        val candidates = (services.keys + xaddrs.keys).distinct().sortedWith(
            compareBy { it.split('.').lastOrNull()?.toIntOrNull() ?: 999 }
        )
        for (ip in candidates) {
            val ports = services[ip].orEmpty()
            val rtsp = ports.filter { it in listOf(554, 8554, 1234, 1235) }.filter {
                rtspService(ip, it)
            }
            // Only present actual RTSP listeners or a genuine WS-Discovery XAddr.
            val onvif = xaddrs[ip]
            if (rtsp.isNotEmpty() || onvif != null) {
                devices += LanCamera(
                    ip = ip,
                    rtspPorts = rtsp,
                    onvifUrl = onvif,
                    onvifCandidate = onvif == null && 8899 in ports,
                    source = if (onvif != null) "ONVIF WS-Discovery" else "RTSP listener"
                )
            }
        }
        status("Detected ${devices.size} RTSP/ONVIF camera(s). Use Connect to negotiate playback.")
        return devices.take(64)
    }

    private fun rtspService(ip: String, port: Int): Boolean = try {
        Socket().use { socket ->
            socket.connect(InetSocketAddress(ip, port), 650)
            socket.soTimeout = 650
            val request = "OPTIONS rtsp://$ip:$port/ RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: FOLDVIEW\r\n\r\n"
            socket.getOutputStream().write(request.toByteArray(Charsets.US_ASCII))
            val line = BufferedReader(InputStreamReader(socket.getInputStream())).readLine() ?: ""
            line.startsWith("RTSP/1.")
        }
    } catch (_: Exception) { false }
}
