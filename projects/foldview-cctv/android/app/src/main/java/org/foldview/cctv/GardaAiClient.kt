package org.foldview.cctv

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import org.json.JSONObject
import org.json.JSONArray

/**
 * Private GARDA AI event catalog. No camera passwords, biometric templates or
 * RTSP streams are transmitted by this client. HTTPS is mandatory off-loopback.
 */
internal data class GardaAiEvent(
    val id: String, val camera: String, val kind: String, val whenUtc: String,
    val plate: String, val faceLabel: String, val confidence: Double
)

internal class GardaAiClient(context: Context) {
    private val prefs = context.getSharedPreferences("garda_ai_endpoint_v1", Context.MODE_PRIVATE)
    private val alias = "garda_ai_server_api_key_v1"

    private fun key(): SecretKey {
        val ks = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (ks.getKey(alias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            .apply {
                init(KeyGenParameterSpec.Builder(alias,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setKeySize(256).build())
            }.generateKey()
    }

    private fun origin(raw: String): String {
        val u = URI(raw.trim())
        val scheme = u.scheme?.lowercase()
        require(u.host != null && u.userInfo == null && u.query == null &&
            u.fragment == null && (u.path.isNullOrEmpty() || u.path == "/")) {
            "Enter the GARDA AI HTTPS server root URL without credentials or path"
        }
        val loopback = u.host == "localhost" || u.host == "127.0.0.1" || u.host == "::1"
        require(scheme == "https" || (scheme == "http" && loopback)) {
            "GARDA AI requires HTTPS from another device. Use Tailscale/VPN TLS proxy."
        }
        return URI(scheme, null, u.host, u.port, null, null, null).toASCIIString()
    }

    fun savedUrl(): String = prefs.getString("url", "") ?: ""

    fun savedKey(): String {
        val value = prefs.getString("secret", null) ?: return ""
        return runCatching {
            val encrypted = Base64.decode(value, Base64.NO_WRAP)
            require(encrypted.size > 12)
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, key(),
                GCMParameterSpec(128, encrypted.copyOfRange(0, 12)))
            String(cipher.doFinal(encrypted.copyOfRange(12, encrypted.size)), Charsets.UTF_8)
        }.getOrDefault("")
    }

    fun remember(url: String, secret: String) {
        val target = origin(url)
        require(secret.length >= 24) { "API key must contain at least 24 characters" }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val encrypted = cipher.iv + cipher.doFinal(secret.toByteArray(Charsets.UTF_8))
        check(prefs.edit()
            .putString("url", target)
            .putString("secret", Base64.encodeToString(encrypted, Base64.NO_WRAP))
            .commit()) { "Failed to save GARDA AI connection securely" }
    }

    fun forget() { prefs.edit().clear().apply() }

    private fun get(path: String): JSONObject {
        val url = origin(savedUrl()) + path
        val secret = savedKey()
        require(secret.length >= 24) { "GARDA AI key is not configured" }
        val connection = URL(url).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "GET"
            connection.connectTimeout = 4500
            connection.readTimeout = 4500
            connection.instanceFollowRedirects = false
            connection.setRequestProperty("X-GARDA-KEY", secret)
            connection.setRequestProperty("Accept", "application/json")
            val code = connection.responseCode
            if (code !in 200..299) error("GARDA AI returned HTTP $code")
            val body = connection.inputStream.bufferedReader().use { reader ->
                val output = StringBuilder()
                val chars = CharArray(4096)
                while (true) {
                    val len = reader.read(chars)
                    if (len < 0) break
                    require(output.length + len <= 250_000) { "AI response too large" }
                    output.append(chars, 0, len)
                }
                output.toString()
            }
            return JSONObject(body)
        } finally {
            connection.disconnect()
        }
    }

    fun stats(): JSONObject = get("/api/stats")
    fun events(kind: String = ""): List<GardaAiEvent> {
        require(kind.isEmpty() || kind in listOf("plate", "face", "motion"))
        val suffix = if (kind.isEmpty()) "" else "&kind=$kind"
        val items: JSONArray = get("/api/events?limit=30$suffix").getJSONArray("events")
        return (0 until items.length()).map { index ->
            val item = items.getJSONObject(index)
            GardaAiEvent(
                id = item.getString("id"),
                camera = item.optString("camera_id"),
                kind = item.optString("kind"),
                whenUtc = item.optString("observed_at"),
                plate = item.optString("plate_text").takeUnless { it == "null" } ?: "",
                faceLabel = item.optString("face_label").takeUnless { it == "null" } ?: "",
                confidence = item.optDouble("confidence", 0.0)
            )
        }
    }
    fun photoIds(eventId: String): List<String> {
        require(Regex("[a-f0-9]{32}").matches(eventId))
        val items = get("/api/events/$eventId/photos").getJSONArray("photos")
        return (0 until items.length()).map { items.getJSONObject(it).getString("id") }
    }
    fun photo(eventId: String, photoId: String): ByteArray {
        require(Regex("[a-f0-9]{32}").matches(eventId) &&
            Regex("[a-f0-9]{32}").matches(photoId))
        val url = origin(savedUrl()) + "/api/events/$eventId/photos/$photoId"
        val con = URL(url).openConnection() as HttpURLConnection
        try {
            con.connectTimeout = 4500
            con.readTimeout = 6000
            con.instanceFollowRedirects = false
            con.setRequestProperty("X-GARDA-KEY", savedKey())
            require(con.responseCode == 200) { "Evidence could not be opened" }
            con.inputStream.use { input ->
                val output = java.io.ByteArrayOutputStream()
                val chunk = ByteArray(8192)
                while (true) {
                    val n = input.read(chunk)
                    if (n < 0) break
                    require(output.size() + n <= 4 * 1024 * 1024) { "Image exceeds safe size" }
                    output.write(chunk, 0, n)
                }
                return output.toByteArray()
            }
        } finally { con.disconnect() }
    }
}
