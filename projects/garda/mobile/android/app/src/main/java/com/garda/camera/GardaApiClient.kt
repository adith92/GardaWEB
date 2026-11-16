package com.garda.camera

import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

data class TelemetryResponse(
    @SerializedName("status") val status: String? = null,
    @SerializedName("ip") val ip: String? = null,
    @SerializedName("uptime_sec") val uptimeSec: Double? = null,
    @SerializedName("free_ram_kb") val freeRamKb: String? = null,
    @SerializedName("vlcview_running") val vlcviewRunning: Boolean? = null,
    @SerializedName("dual_lens") val dualLens: Boolean? = null
)

class GardaApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(2, TimeUnit.SECONDS)
        .readTimeout(2, TimeUnit.SECONDS)
        .writeTimeout(2, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val emptyBody = "".toRequestBody("application/json".toMediaType())

    suspend fun getTelemetry(ip: String, port: Int = 8899): Result<TelemetryResponse> = withContext(Dispatchers.IO) {
        try {
            val url = "http://$ip:$port/api/status"
            val request = Request.Builder().url(url).get().build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext Result.failure(Exception("HTTP ${response.code}"))
                }
                val body = response.body?.string() ?: ""
                val telemetry = gson.fromJson(body, TelemetryResponse::class.java)
                Result.success(telemetry)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendPtz(ip: String, direction: String, port: Int = 8899): Result<String> = withContext(Dispatchers.IO) {
        try {
            val url = "http://$ip:$port/api/ptz?dir=$direction"
            val request = Request.Builder().url(url).post(emptyBody).build()
            client.newCall(request).execute().use { response ->
                Result.success(response.body?.string() ?: "OK")
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendLed(ip: String, mode: String, port: Int = 8899): Result<String> = withContext(Dispatchers.IO) {
        try {
            val url = "http://$ip:$port/api/led?mode=$mode"
            val request = Request.Builder().url(url).post(emptyBody).build()
            client.newCall(request).execute().use { response ->
                Result.success(response.body?.string() ?: "OK")
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
