package com.garda.camera

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.InputStream
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.Socket

class GardaNativePtz {
    companion object {
        const val CMD_LEFT = 0x40
        const val CMD_RIGHT = 0x41
        const val CMD_DOWN = 0x42
        const val CMD_UP = 0x43
        const val CMD_RESET = 0x44
        const val CMD_CRUISE = 0x47
        const val CMD_TRACKING = 0x48
        const val CMD_MANUAL = 0x49
    }

    suspend fun sendCommand(ip: String, opcode: Int, step: Int = 30, port: Int = 7777): Result<Boolean> = withContext(Dispatchers.IO) {
        var socket: Socket? = null
        try {
            socket = Socket()
            socket.connect(InetSocketAddress(ip, port), 1500)
            socket.soTimeout = 1500

            val pkt = ByteArray(32)
            pkt[0] = 0xAA.toByte()
            pkt[1] = (opcode and 0xFF).toByte()
            pkt[2] = (step and 0xFF).toByte()
            pkt[3] = ((step shr 8) and 0xFF).toByte()

            val out: OutputStream = socket.getOutputStream()
            out.write(pkt)
            out.flush()

            val `in`: InputStream = socket.getInputStream()
            val ack = ByteArray(32)
            val read = `in`.read(ack)

            val success = read > 0 && ack[0] == 0xBB.toByte()
            Result.success(success)
        } catch (e: Exception) {
            Result.failure(e)
        } finally {
            try {
                socket?.close()
            } catch (_: Exception) {}
        }
    }
}
