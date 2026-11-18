package id.garda.vision

import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray

/** GARDA Android client starter, not an APK or authenticated production integration.
 * Use HTTPS+mutual trust on a private VPN, not HTTP to public Internet.
 * Never bundle API tokens in APK; obtain scoped credentials from a real identity service.
 */
class GardaVisionClient(private val baseUrl: String, private val tokenProvider: () -> String) {
    suspend fun listCameras(): JSONArray = withContext(Dispatchers.IO) {
        val url = URL("${baseUrl.trimEnd('/')}/api/v1/cameras")
        val conn = (url.openConnection() as HttpURLConnection)
        try {
            conn.connectTimeout = 5000
            conn.readTimeout = 5000
            conn.setRequestProperty("Authorization", "Bearer ${tokenProvider()}")
            conn.setRequestProperty("Accept", "application/json")
            if (conn.responseCode != 200) error("Camera request failed: HTTP ${conn.responseCode}")
            JSONArray(conn.inputStream.bufferedReader().use { it.readText() })
        } finally { conn.disconnect() }
    }
}
