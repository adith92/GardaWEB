package org.foldview.cctv

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import org.json.JSONObject

/** Per-host ONVIF/RTSP credentials; stored only when Remember is selected. */
data class CameraLogin(val username: String, val password: String) {
    init {
        require(username.length <= 128 && password.length <= 256)
    }
}

internal class CameraCredentialStore(context: Context) {
    private val preferences = context.getSharedPreferences("garda_onvif_login_v1", Context.MODE_PRIVATE)
    private val alias = "garda_onvif_login_keystore_v1"

    private fun key(): SecretKey {
        val ks = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (ks.getKey(alias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            .apply {
                init(
                    KeyGenParameterSpec.Builder(
                        alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                    )
                        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                        .setKeySize(256)
                        .build()
                )
            }.generateKey()
    }

    private fun hostKey(ip: String): String {
        require(Regex("(?:\\d{1,3}\\.){3}\\d{1,3}").matches(ip))
        return "host_$ip"
    }

    fun load(ip: String): CameraLogin? {
        val text = preferences.getString(hostKey(ip), null) ?: return null
        return try {
            val data = Base64.decode(text, Base64.NO_WRAP)
            if (data.size <= 12) return null
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(
                Cipher.DECRYPT_MODE, key(),
                GCMParameterSpec(128, data.copyOfRange(0, 12))
            )
            val obj = JSONObject(String(cipher.doFinal(data.copyOfRange(12, data.size)), Charsets.UTF_8))
            CameraLogin(obj.getString("username"), obj.getString("password"))
        } catch (_: Exception) {
            // No plaintext fallback if the Android Keystore key was invalidated.
            null
        }
    }

    fun remember(ip: String, login: CameraLogin) {
        val payload = JSONObject()
            .put("username", login.username)
            .put("password", login.password)
            .toString().toByteArray(Charsets.UTF_8)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val protected = cipher.iv + cipher.doFinal(payload)
        check(preferences.edit().putString(hostKey(ip), Base64.encodeToString(protected, Base64.NO_WRAP)).commit()) {
            "Could not securely save camera credentials"
        }
    }

    fun forget(ip: String) {
        preferences.edit().remove(hostKey(ip)).apply()
    }
}
