package com.garda.camera

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException

class OnvifDiscovery {
    private val probeMessage = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>" +
        "<Envelope xmlns=\"http://www.w3.org/2003/05/soap-envelope\" " +
        "xmlns:wsa=\"http://schemas.xmlsoap.org/ws/2004/08/addressing\" " +
        "xmlns:wsd=\"http://schemas.xmlsoap.org/ws/2005/04/discovery\">" +
        "<Header>" +
        "<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>" +
        "<wsa:MessageID>urn:uuid:garda-android-probe-01</wsa:MessageID>" +
        "<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>" +
        "</Header>" +
        "<Body><wsd:Probe/></Body></Envelope>"
    ).toByteArray(Charsets.UTF_8)

    suspend fun discoverCameras(timeoutMs: Int = 1500): List<String> = withContext(Dispatchers.IO) {
        val foundIps = mutableListOf<String>()
        var socket: DatagramSocket? = null
        try {
            socket = DatagramSocket()
            socket.broadcast = true
            socket.soTimeout = 400

            val targets = listOf("239.255.255.250", "255.255.255.255")
            for (target in targets) {
                try {
                    val addr = InetAddress.getByName(target)
                    val packet = DatagramPacket(probeMessage, probeMessage.size, addr, 3702)
                    socket.send(packet)
                } catch (_: Exception) {}
            }

            val startTime = System.currentTimeMillis()
            val buf = ByteArray(4096)
            while (System.currentTimeMillis() - startTime < timeoutMs) {
                try {
                    val recvPacket = DatagramPacket(buf, buf.size)
                    socket.receive(recvPacket)
                    val ip = recvPacket.address.hostAddress
                    if (ip != null && !foundIps.contains(ip)) {
                        foundIps.add(ip)
                    }
                } catch (_: SocketTimeoutException) {
                    if (foundIps.isNotEmpty()) break
                }
            }
        } catch (_: Exception) {
        } finally {
            socket?.close()
        }
        foundIps
    }
}
