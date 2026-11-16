package org.foldview.cctv

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import org.json.JSONArray
import org.json.JSONObject
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

data class CameraInfo(
    val id: String,
    val name: String,
    val url: String,
    val onvifUrl: String = "",
    val onvifUser: String = "",
    val onvifPassword: String = ""
)

/**
 * Encrypted local camera profiles. Android Keystore never exports the key.
 * Never log camera URLs, username/password or server responses.
 */
class CameraVault(context: Context) {
    private val prefs = context.getSharedPreferences("foldview_vault", Context.MODE_PRIVATE)
    private val alias = "foldview_camera_key_v1"

    private fun key(): SecretKey {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val existing = store.getKey(alias, null) as? SecretKey
        if (existing != null) return existing
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                alias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            ).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
             .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
             .setKeySize(256)
             .build()
        )
        return generator.generateKey()
    }

    fun read(): List<CameraInfo> {
        val encrypted = prefs.getString("cameras", null) ?: return emptyList()
        return try {
            val allBytes = Base64.decode(encrypted, Base64.NO_WRAP)
            if (allBytes.size < 13) return emptyList()
            val iv = allBytes.copyOfRange(0, 12)
            val ciphertext = allBytes.copyOfRange(12, allBytes.size)
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, iv))
            val array = JSONArray(String(cipher.doFinal(ciphertext), Charsets.UTF_8))
            (0 until array.length()).map { i ->
                val o = array.getJSONObject(i)
                CameraInfo(
                    id = o.getString("id"),
                    name = o.getString("name"),
                    url = o.getString("url"),
                    onvifUrl = o.optString("onvifUrl"),
                    onvifUser = o.optString("onvifUser"),
                    onvifPassword = o.optString("onvifPassword")
                )
            }
        } catch (_: Exception) {
            // If Keystore key is reset, encrypted camera data is unavailable.
            emptyList()
        }
    }

    fun write(cameras: List<CameraInfo>) {
        val data = JSONArray().apply {
            cameras.forEach { c ->
                put(
                    JSONObject().put("id", c.id).put("name", c.name).put("url", c.url)
                        .put("onvifUrl", c.onvifUrl)
                        .put("onvifUser", c.onvifUser)
                        .put("onvifPassword", c.onvifPassword)
                )
            }
        }.toString().toByteArray(Charsets.UTF_8)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val combined = cipher.iv + cipher.doFinal(data)
        prefs.edit().putString("cameras", Base64.encodeToString(combined, Base64.NO_WRAP)).apply()
    }
}
