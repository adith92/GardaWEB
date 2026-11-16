# GARDA Mobile — Tactical Dual-Lens IP Camera Controller (Android App)
## Source Code Lengkap & Panduan Teknis untuk ChatGPT / Android Studio

Dokumen ini berisi seluruh arsitektur hardware kamera Fullhan FH8852V201, protokol komunikasi jaringan, serta 100% kode sumber (Source Code) lengkap proyek Android Studio untuk aplikasi **GARDA Mobile**.

Anda dapat langsung mengunggah file ini ke **ChatGPT** atau membuka foldernya di **Android Studio** untuk mengkompilasi menjadi file **APK**.

---

## 1. SPESIFIKASI TEKNIS & PROTOKOL KAMERA

- **Model Perangkat**: SriHome / V380 Pro Dual-Lens IP Camera
- **Hardware SoC**: Fullhan Microelectronics **FH8852V201** (ARMv7 Cortex-A7 @ 1.0 GHz)
- **Target IP Default**: `192.168.18.249` (atau `192.168.18.250` via DHCP LAN)
- **Video Stream Dual-Lens (RTSP over TCP)**:
  - **Lensa 1 (Utama / PTZ)**: `rtsp://<IP>:1234/` (1080p Full HD H.264 @ 15fps, AAC Audio)
  - **Lensa 2 (Wide-Angle Fixed)**: `rtsp://<IP>:1235/` (1080p Full HD H.264 @ 15fps)
  - *Catatan Penting*: Android Media3 ExoPlayer **wajib** dikonfigurasi dengan flag `setForceUseRtpTcp(true)` agar stream stabil tanpa packet loss UDP.
- **Daemon ONVIF & REST API (Port 8899 TCP)**:
  - `GET /api/status` $\rightarrow$ Respons JSON:
    ```json
    {"status":"online","ip":"192.168.18.250","uptime_sec":5392,"free_ram_kb":"3112","vlcview_running":true,"dual_lens":true}
    ```
  - `POST /api/ptz?dir=left|right|up|down|stop|center` $\rightarrow$ Menggerakkan motor stepper PTZ atau kembali ke posisi tengah (`x=515, y=70`).
  - `POST /api/led?mode=white_on|white_off` $\rightarrow$ Mengontrol lampu Spotlight Putih (PWM).
  - `POST /api/led?mode=ir_on|ir_off` $\rightarrow$ Mengontrol LED Inframerah Night Vision (GPIO 44).
  - `POST /api/led?mode=ircut_day|ircut_night` $\rightarrow$ Mengalihkan filter optik IR-Cut Siang (GPIO 39) & Malam (GPIO 40).
- **Protokol Native PTZ Binary (Port 7777 TCP)**:
  - Paket biner fixed 32-byte berawalan header magic `0xAA`.
  - Opcode arah: `0x40` (Kiri), `0x41` (Kanan), `0x42` (Bawah), `0x43` (Atas).
  - Opcode fitur: `0x44` (Kalibrasi / Reset Home), `0x47` (Patroli 360° Cruise), `0x48` (AI Human Auto-Tracking), `0x49` (Mode Manual).
  - Byte 2 & 3: Ukuran langkah (*Step size*) uint16 little-endian (10 - 100).
- **WS-Discovery Auto Scanner (UDP 3702)**:
  - Multicast probe SOAP ke `239.255.255.250:3702` untuk mendeteksi kamera otomatis di Wi-Fi lokal.

---

## 2. STRUKTUR PROYEK ANDROID STUDIO

```text
android/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── local.properties
└── app/
    ├── build.gradle.kts
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/garda/camera/
        │   ├── MainActivity.kt
        │   ├── CameraViewModel.kt
        │   ├── GardaApiClient.kt
        │   ├── GardaNativePtz.kt
        │   ├── OnvifDiscovery.kt
        │   └── RtspPlayerManager.kt
        └── res/
            ├── layout/
            │   └── activity_main.xml
            ├── values/
            │   ├── colors.xml
            │   ├── strings.xml
            │   └── themes.xml
            └── drawable/
                ├── bg_card.xml
                ├── bg_btn_ptz.xml
                ├── bg_btn_center.xml
                └── bg_badge.xml
```

---

## 3. CONFIGURATION & GRADLE BUILD SCRIPTS

### `settings.gradle.kts`
```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "GardaMobile"
include(":app")
```

### `build.gradle.kts` (Root Project)
```kotlin
plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
```

### `gradle.properties`
```properties
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
```

### `app/build.gradle.kts`
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.garda.camera"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.garda.camera"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")

    // AndroidX Media3 (ExoPlayer with native RTSP TCP support)
    implementation("androidx.media3:media3-exoplayer:1.2.1")
    implementation("androidx.media3:media3-exoplayer-rtsp:1.2.1")
    implementation("androidx.media3:media3-ui:1.2.1")

    // Networking & JSON
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("com.google.code.gson:gson:2.10.1")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

---

## 4. ANDROID MANIFEST

### `app/src/main/AndroidManifest.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_MULTICAST_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher"
        android:supportsRtl="true"
        android:theme="@style/Theme.GardaMobile"
        android:usesCleartextTraffic="true"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden"
            android:screenOrientation="unspecified">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

---

## 5. SOURCE CODE KOTLIN

### `GardaApiClient.kt`
```kotlin
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
```

### `GardaNativePtz.kt`
```kotlin
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
```

### `OnvifDiscovery.kt`
```kotlin
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
```

### `RtspPlayerManager.kt`
```kotlin
package com.garda.camera

import android.content.Context
import androidx.annotation.OptIn
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.rtsp.RtspMediaSource
import androidx.media3.ui.PlayerView

@OptIn(UnstableApi::class)
class RtspPlayerManager(private val context: Context) {
    private var player: ExoPlayer? = null

    fun startStream(playerView: PlayerView, rtspUrl: String, onStateChanged: ((Boolean) -> Unit)? = null) {
        release()
        try {
            val exoPlayer = ExoPlayer.Builder(context).build()
            val mediaItem = MediaItem.fromUri(rtspUrl)

            // Force TCP transport for RTSP to prevent UDP packet loss and screen distortion
            val mediaSource = RtspMediaSource.Factory()
                .setForceUseRtpTcp(true)
                .setTimeoutMs(4000)
                .createMediaSource(mediaItem)

            exoPlayer.setMediaSource(mediaSource)
            exoPlayer.prepare()
            exoPlayer.playWhenReady = true

            playerView.player = exoPlayer
            player = exoPlayer
            onStateChanged?.invoke(true)
        } catch (e: Exception) {
            onStateChanged?.invoke(false)
        }
    }

    fun stopStream() {
        player?.stop()
    }

    fun release() {
        player?.release()
        player = null
    }
}
```

### `CameraViewModel.kt`
```kotlin
package com.garda.camera

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class CameraViewModel : ViewModel() {
    private val apiClient = GardaApiClient()
    private val nativePtz = GardaNativePtz()
    private val discovery = OnvifDiscovery()

    private val _telemetry = MutableLiveData<TelemetryResponse?>()
    val telemetry: LiveData<TelemetryResponse?> = _telemetry

    private val _isOnline = MutableLiveData<Boolean>(false)
    val isOnline: LiveData<Boolean> = _isOnline

    private val _logMessage = MutableLiveData<String>()
    val logMessage: LiveData<String> = _logMessage

    private val _whiteLightOn = MutableLiveData<Boolean>(false)
    val whiteLightOn: LiveData<Boolean> = _whiteLightOn

    private val _irNightOn = MutableLiveData<Boolean>(false)
    val irNightOn: LiveData<Boolean> = _irNightOn

    private val _trackingOn = MutableLiveData<Boolean>(false)
    val trackingOn: LiveData<Boolean> = _trackingOn

    private val _cruiseOn = MutableLiveData<Boolean>(false)
    val cruiseOn: LiveData<Boolean> = _cruiseOn

    private var pollingJob: Job? = null

    fun startTelemetryPolling(ip: String) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            while (isActive) {
                val res = apiClient.getTelemetry(ip)
                if (res.isSuccess) {
                    val data = res.getOrNull()
                    _telemetry.postValue(data)
                    _isOnline.postValue(data?.status == "online")
                } else {
                    _isOnline.postValue(false)
                }
                delay(3000)
            }
        }
    }

    fun stopTelemetryPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    fun scanLan(onResult: (List<String>) -> Unit) {
        viewModelScope.launch {
            _logMessage.postValue("Scanning WS-Discovery (UDP 3702)...")
            val ips = discovery.discoverCameras()
            onResult(ips)
            if (ips.isNotEmpty()) {
                _logMessage.postValue("Ditemukan kamera: ${ips.joinToString(", ")}")
            } else {
                _logMessage.postValue("Scan selesai. Tidak ditemukan kamera baru.")
            }
        }
    }

    fun movePtz(ip: String, direction: String, step: Int) {
        viewModelScope.launch {
            val res = apiClient.sendPtz(ip, direction)
            if (res.isSuccess) {
                _logMessage.postValue("PTZ $direction: OK (REST)")
            } else {
                val opcode = when (direction) {
                    "left" -> GardaNativePtz.CMD_LEFT
                    "right" -> GardaNativePtz.CMD_RIGHT
                    "up" -> GardaNativePtz.CMD_UP
                    "down" -> GardaNativePtz.CMD_DOWN
                    else -> GardaNativePtz.CMD_RESET
                }
                val natRes = nativePtz.sendCommand(ip, opcode, step)
                if (natRes.isSuccess) {
                    _logMessage.postValue("PTZ $direction: OK (Native 7777)")
                } else {
                    _logMessage.postValue("PTZ $direction gagal: ${res.exceptionOrNull()?.message}")
                }
            }
        }
    }

    fun centerPtz(ip: String) {
        viewModelScope.launch {
            val res = apiClient.sendPtz(ip, "center")
            _logMessage.postValue("PTZ Center (x=515, y=70): ${if (res.isSuccess) "OK" else "Error"}")
        }
    }

    fun calibratePtz(ip: String) {
        viewModelScope.launch {
            val res = nativePtz.sendCommand(ip, GardaNativePtz.CMD_RESET, 0)
            _logMessage.postValue("Kalibrasi Motor PTZ: ${if (res.isSuccess) "OK" else "Error"}")
        }
    }

    fun toggleWhiteLight(ip: String) {
        val newState = !(_whiteLightOn.value ?: false)
        viewModelScope.launch {
            val mode = if (newState) "white_on" else "white_off"
            val res = apiClient.sendLed(ip, mode)
            if (res.isSuccess) {
                _whiteLightOn.postValue(newState)
                _logMessage.postValue("Spotlight: ${if (newState) "ON" else "OFF"}")
            }
        }
    }

    fun toggleNightIr(ip: String) {
        val newState = !(_irNightOn.value ?: false)
        viewModelScope.launch {
            val mode = if (newState) "ir_on" else "ir_off"
            val res = apiClient.sendLed(ip, mode)
            if (res.isSuccess) {
                _irNightOn.postValue(newState)
                _logMessage.postValue("Night IR (GPIO 44): ${if (newState) "ON" else "OFF"}")
            }
        }
    }

    fun setIrCutFilter(ip: String, nightMode: Boolean) {
        viewModelScope.launch {
            val mode = if (nightMode) "ircut_night" else "ircut_day"
            val res = apiClient.sendLed(ip, mode)
            _logMessage.postValue("IR-Cut Filter: ${if (nightMode) "Night Filter" else "Day Filter"} (${if (res.isSuccess) "OK" else "Error"})")
        }
    }

    fun toggleTracking(ip: String) {
        val newState = !(_trackingOn.value ?: false)
        viewModelScope.launch {
            val opcode = if (newState) GardaNativePtz.CMD_TRACKING else GardaNativePtz.CMD_MANUAL
            val res = nativePtz.sendCommand(ip, opcode, 0)
            if (res.isSuccess) {
                _trackingOn.postValue(newState)
                _logMessage.postValue("AI Human Tracking: ${if (newState) "AKTIF" else "NONAKTIF"}")
            }
        }
    }

    fun toggleCruise(ip: String) {
        val newState = !(_cruiseOn.value ?: false)
        viewModelScope.launch {
            val opcode = if (newState) GardaNativePtz.CMD_CRUISE else GardaNativePtz.CMD_MANUAL
            val res = nativePtz.sendCommand(ip, opcode, 0)
            if (res.isSuccess) {
                _cruiseOn.postValue(newState)
                _logMessage.postValue("Patroli 360°: ${if (newState) "AKTIF" else "BERHENTI"}")
            }
        }
    }
}
```

### `MainActivity.kt`
```kotlin
package com.garda.camera

import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.garda.camera.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: CameraViewModel by viewModels()

    private lateinit var playerLens1: RtspPlayerManager
    private lateinit var playerLens2: RtspPlayerManager

    private var isStreaming = false
    private var currentStep = 30

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        playerLens1 = RtspPlayerManager(this)
        playerLens2 = RtspPlayerManager(this)

        setupViewModeSpinner()
        setupListeners()
        setupObservers()

        val initialIp = binding.etCameraIp.text.toString().trim()
        if (initialIp.isNotEmpty()) {
            viewModel.startTelemetryPolling(initialIp)
        }
    }

    private fun setupViewModeSpinner() {
        val modes = arrayOf(
            getString(R.string.view_dual_vertical),
            getString(R.string.view_dual_horizontal),
            getString(R.string.view_lens1),
            getString(R.string.view_lens2)
        )
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, modes)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spnViewMode.adapter = adapter

        binding.spnViewMode.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                applyViewMode(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun applyViewMode(modeIndex: Int) {
        when (modeIndex) {
            0 -> { // Dual Vertical (Top - Bottom)
                binding.videoContainer.orientation = LinearLayout.VERTICAL
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
            1 -> { // Dual Horizontal (Left - Right)
                binding.videoContainer.orientation = LinearLayout.HORIZONTAL
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
            2 -> { // Lens 1 Only
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.GONE
            }
            3 -> { // Lens 2 Only
                binding.lens1Wrapper.visibility = View.GONE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
        }
    }

    private fun setupListeners() {
        binding.btnConnect.setOnClickListener {
            if (!isStreaming) {
                startCameraStream()
            } else {
                stopCameraStream()
            }
        }

        binding.btnScanLan.setOnClickListener {
            viewModel.scanLan { ips ->
                if (ips.isNotEmpty()) {
                    binding.etCameraIp.setText(ips[0])
                    viewModel.startTelemetryPolling(ips[0])
                    Toast.makeText(this, "Kamera ditemukan: ${ips[0]}", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Tidak ada kamera ditemukan di subnet ini", Toast.LENGTH_SHORT).show()
                }
            }
        }

        binding.sliderStep.addOnChangeListener { _, value, _ ->
            currentStep = value.toInt()
            binding.tvStepLabel.text = "Step: $currentStep"
        }

        val ipProvider = { binding.etCameraIp.text.toString().trim() }
        binding.btnPtzUp.setOnClickListener { viewModel.movePtz(ipProvider(), "up", currentStep) }
        binding.btnPtzDown.setOnClickListener { viewModel.movePtz(ipProvider(), "down", currentStep) }
        binding.btnPtzLeft.setOnClickListener { viewModel.movePtz(ipProvider(), "left", currentStep) }
        binding.btnPtzRight.setOnClickListener { viewModel.movePtz(ipProvider(), "right", currentStep) }

        binding.btnPtzUpLeft.setOnClickListener {
            viewModel.movePtz(ipProvider(), "up", currentStep)
            viewModel.movePtz(ipProvider(), "left", currentStep)
        }
        binding.btnPtzUpRight.setOnClickListener {
            viewModel.movePtz(ipProvider(), "up", currentStep)
            viewModel.movePtz(ipProvider(), "right", currentStep)
        }
        binding.btnPtzDownLeft.setOnClickListener {
            viewModel.movePtz(ipProvider(), "down", currentStep)
            viewModel.movePtz(ipProvider(), "left", currentStep)
        }
        binding.btnPtzDownRight.setOnClickListener {
            viewModel.movePtz(ipProvider(), "down", currentStep)
            viewModel.movePtz(ipProvider(), "right", currentStep)
        }

        binding.btnPtzCenter.setOnClickListener { viewModel.centerPtz(ipProvider()) }
        binding.btnPtzCalibrate.setOnClickListener { viewModel.calibratePtz(ipProvider()) }

        binding.btnToggleSpotlight.setOnClickListener { viewModel.toggleWhiteLight(ipProvider()) }
        binding.btnToggleNightIr.setOnClickListener { viewModel.toggleNightIr(ipProvider()) }
        binding.btnIrCutDay.setOnClickListener { viewModel.setIrCutFilter(ipProvider(), false) }
        binding.btnIrCutNight.setOnClickListener { viewModel.setIrCutFilter(ipProvider(), true) }

        binding.btnToggleTracking.setOnClickListener { viewModel.toggleTracking(ipProvider()) }
        binding.btnToggleCruise.setOnClickListener { viewModel.toggleCruise(ipProvider()) }
    }

    private fun setupObservers() {
        viewModel.isOnline.observe(this) { online ->
            if (online) {
                binding.tvOnvifBadge.text = "ONVIF :8899 ONLINE"
                binding.tvOnvifBadge.setTextColor(getColor(R.color.emerald_online))
            } else {
                binding.tvOnvifBadge.text = "ONVIF :8899 OFFLINE"
                binding.tvOnvifBadge.setTextColor(getColor(R.color.rose_alert))
            }
        }

        viewModel.telemetry.observe(this) { t ->
            if (t != null) {
                val upSec = t.uptimeSec?.toLong() ?: 0L
                val hrs = upSec / 3600
                val mins = (upSec % 3600) / 60
                val secs = upSec % 60
                binding.tvUptimeChip.text = "⏱️ Uptime: ${hrs}h ${mins}m ${secs}s"
                binding.tvRamChip.text = "🧠 Free RAM: ${t.freeRamKb ?: "-"} KB"
            }
        }

        viewModel.whiteLightOn.observe(this) { on ->
            binding.btnToggleSpotlight.text = if (on) getString(R.string.spotlight_on) else getString(R.string.spotlight_off)
            binding.btnToggleSpotlight.setBackgroundColor(getColor(if (on) R.color.amber_warning else R.color.border_primary))
            binding.btnToggleSpotlight.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.irNightOn.observe(this) { on ->
            binding.btnToggleNightIr.text = if (on) getString(R.string.ir_on) else getString(R.string.ir_off)
            binding.btnToggleNightIr.setBackgroundColor(getColor(if (on) R.color.purple_accent else R.color.border_primary))
            binding.btnToggleNightIr.setTextColor(if (on) 0xFFFFFFFF.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.trackingOn.observe(this) { on ->
            binding.btnToggleTracking.text = if (on) getString(R.string.tracking_on) else getString(R.string.tracking_off)
            binding.btnToggleTracking.setBackgroundColor(getColor(if (on) R.color.emerald_online else R.color.border_primary))
            binding.btnToggleTracking.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.cruiseOn.observe(this) { on ->
            binding.btnToggleCruise.text = if (on) getString(R.string.cruise_on) else getString(R.string.cruise_off)
            binding.btnToggleCruise.setBackgroundColor(getColor(if (on) R.color.cyan_accent else R.color.border_primary))
            binding.btnToggleCruise.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.logMessage.observe(this) { msg ->
            val prev = binding.tvLogConsole.text.toString()
            binding.tvLogConsole.text = "$prev> $msg\n"
        }
    }

    private fun startCameraStream() {
        val ip = binding.etCameraIp.text.toString().trim()
        if (ip.isEmpty()) {
            Toast.makeText(this, "Masukkan IP Kamera terlebih dahulu", Toast.LENGTH_SHORT).show()
            return
        }

        val rtspUrl1 = "rtsp://$ip:1234/"
        val rtspUrl2 = "rtsp://$ip:1235/"

        binding.tvStreamBadge.text = "CONNECTING..."
        binding.tvStreamBadge.setTextColor(getColor(R.color.amber_warning))

        playerLens1.startStream(binding.playerViewLens1, rtspUrl1) { ok1 ->
            if (ok1) {
                binding.tvStreamBadge.text = "DUAL LIVE 1080P"
                binding.tvStreamBadge.setTextColor(getColor(R.color.emerald_online))
            }
        }

        playerLens2.startStream(binding.playerViewLens2, rtspUrl2)

        isStreaming = true
        binding.btnConnect.text = getString(R.string.btn_disconnect)
        binding.btnConnect.setBackgroundColor(getColor(R.color.rose_alert))
        binding.btnConnect.setTextColor(0xFFFFFFFF.toInt())

        viewModel.startTelemetryPolling(ip)
    }

    private fun stopCameraStream() {
        playerLens1.stopStream()
        playerLens2.stopStream()

        isStreaming = false
        binding.tvStreamBadge.text = getString(R.string.status_standby)
        binding.tvStreamBadge.setTextColor(getColor(R.color.text_muted))

        binding.btnConnect.text = getString(R.string.btn_connect)
        binding.btnConnect.setBackgroundColor(getColor(R.color.cyan_accent))
        binding.btnConnect.setTextColor(0xFF000000.toInt())
    }

    override fun onDestroy() {
        super.onDestroy()
        playerLens1.release()
        playerLens2.release()
        viewModel.stopTelemetryPolling()
    }
}
```

---

## 6. XML LAYOUT & RESOURCES

### `activity_main.xml`
Lihat file [`activity_main.xml`](file:///C:/Users/adith/OneDrive/Desktop/CleanTV/GARDA%20Desktop/android/app/src/main/res/layout/activity_main.xml) di dalam proyek `app/src/main/res/layout/activity_main.xml`.

---

## 7. CARA MELANJUTKAN PEMBUATAN APK KE CHATGPT

Saat Anda mengunggah file ini ke ChatGPT, cukup berikan prompt seperti contoh di bawah:

> *"Halo ChatGPT, ini adalah source code lengkap proyek Android Studio untuk aplikasi **GARDA Mobile** (kamera IP Dual-Lens Fullhan FH8852V201). Tolong bantu saya [pilih salah satu opsi]:"*
> 1. *"Buatkan instruksi langkah demi langkah untuk compile file ini menjadi APK Release menggunakan Android Studio / Gradle."*
> 2. *"Tambahkan fitur tombol screenshot snapshot ke Gallery HP dan perekam video MP4 langsung di layar video."*
> 3. *"Ubah arsitektur stream menggunakan Jetpack Compose atau optimalkan latensi RTSP ExoPlayer ke ultra-low latency."*
