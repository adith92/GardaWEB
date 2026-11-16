package org.foldview.cctv

import android.content.Context
import android.net.wifi.WifiManager
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.util.UUID

/**
 * WS-Discovery Probe for ONVIF cameras on the current LAN.
 * Only addresses from LAN devices are shown to the user. No automatic connection.
 * Not a replacement for ONVIF authentication/GetProfiles/GetStreamUri.
 */
object OnvifDiscovery {
    fun discover(context: Context): List<String> {
        val wifi = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as? WifiManager
        val lock = wifi?.createMulticastLock("foldview-discovery")
        val responses = linkedSetOf<String>()
        try {
            lock?.setReferenceCounted(false)
            lock?.acquire()
            DatagramSocket().use { socket ->
                socket.soTimeout = 650
                val msgId = UUID.randomUUID().toString()
                val probe = """
                    <?xml version="1.0" encoding="UTF-8"?>
                    <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                        xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing"
                        xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
                        xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
                      <s:Header>
                        <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</a:Action>
                        <a:MessageID>uuid:$msgId</a:MessageID>
                        <a:To s:mustUnderstand="1">urn:schemas-xmlsoap-org:ws:2005:04:discovery</a:To>
                      </s:Header>
                      <s:Body><d:Probe><d:Types>dn:NetworkVideoTransmitter</d:Types></d:Probe></s:Body>
                    </s:Envelope>
                """.trimIndent().toByteArray(Charsets.UTF_8)
                socket.send(DatagramPacket(probe, probe.size, InetAddress.getByName("239.255.255.250"), 3702))
                val until = System.currentTimeMillis() + 2500L
                while (System.currentTimeMillis() < until) {
                    val data = ByteArray(8192)
                    val packet = DatagramPacket(data, data.size)
                    try {
                        socket.receive(packet)
                        val xml = String(packet.data, 0, packet.length, Charsets.UTF_8)
                        val xaddrs = Regex("<(?:[A-Za-z0-9_]+:)?XAddrs[^>]*>([^<]+)</(?:[A-Za-z0-9_]+:)?XAddrs>", RegexOption.IGNORE_CASE)
                            .find(xml)?.groupValues?.getOrNull(1)
                        if (!xaddrs.isNullOrBlank()) {
                            xaddrs.split(Regex("\\s+")).take(4).forEach { address ->
                                if (address.startsWith("http://") || address.startsWith("https://")) responses.add(address)
                            }
                        } else {
                            responses.add(packet.address.hostAddress ?: "Unknown camera")
                        }
                    } catch (_: java.net.SocketTimeoutException) {
                        // Continue until discovery deadline.
                    }
                }
            }
        } catch (_: Exception) {
            // Empty response is normal on isolated VLANs, devices with ONVIF disabled, or denied local permission.
        } finally {
            if (lock?.isHeld == true) lock.release()
        }
        return responses.toList().take(50)
    }
}
