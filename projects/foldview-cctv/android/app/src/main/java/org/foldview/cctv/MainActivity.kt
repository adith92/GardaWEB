package org.foldview.cctv

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.content.ContentValues
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.view.PixelCopy
import android.view.SurfaceView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.*
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.graphicsLayer
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.rtsp.RtspMediaSource
import androidx.media3.ui.AspectRatioFrameLayout
import androidx.media3.ui.PlayerView
import java.util.UUID
import kotlin.concurrent.thread

private val Bg: Color
    @Composable get() = MaterialTheme.colorScheme.background
private val Panel: Color
    @Composable get() = MaterialTheme.colorScheme.surface
private val Mint: Color
    @Composable get() = MaterialTheme.colorScheme.primary
private val Muted: Color
    @Composable get() = MaterialTheme.colorScheme.onSurfaceVariant

class MainActivity : ComponentActivity() {
    private val intercomEngine = OnvifIntercom()

    override fun onStop() {
        // Privacy: never leave the phone microphone streaming in the background.
        intercomEngine.stop()
        super.onStop()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = android.graphics.Color.rgb(9, 16, 25)
        window.navigationBarColor = android.graphics.Color.rgb(9, 16, 25)
        setContent {
            val context = LocalContext.current
            val scope = rememberCoroutineScope()
            val themePrefs = remember { context.getSharedPreferences("garda_ui", android.content.Context.MODE_PRIVATE) }
            var darkMode by rememberSaveable { mutableStateOf(themePrefs.getBoolean("dark_mode", true)) }
            var language by rememberSaveable { mutableStateOf(themePrefs.getString("language", "id") ?: "id") }
            val vault = remember { CameraVault(applicationContext) }
            val loginVault = remember { CameraCredentialStore(applicationContext) }
            val sessionOnlyIds = remember { mutableStateListOf<String>() }
            var loginTarget by remember { mutableStateOf<LanCamera?>(null) }
            var loginDraft by remember { mutableStateOf<CameraLogin?>(null) }
            val cameras = remember { mutableStateListOf<CameraInfo>().apply { addAll(vault.read()) } }
            val found = remember { mutableStateListOf<LanCamera>() }
            var scanning by remember { mutableStateOf(false) }
            var connectingIp by remember { mutableStateOf("") }
            var waitingForScanPermission by remember { mutableStateOf(false) }
            var autoJoinOnScan by remember { mutableStateOf(false) }
            var selectedId by rememberSaveable { mutableStateOf("") }
            var grid by rememberSaveable { mutableIntStateOf(1) }
            var tab by rememberSaveable { mutableStateOf("Live") }
            var addDialog by remember { mutableStateOf(false) }
            var audio by rememberSaveable { mutableStateOf(false) }
            var focusedSurface by remember { mutableStateOf<SurfaceView?>(null) }
            var scanMessage by remember { mutableStateOf("Tap Scan ONVIF to discover local cameras.") }
            var recording by rememberSaveable { mutableStateOf(false) }
            var talking by remember { mutableStateOf(false) }
            var talkStarting by remember { mutableStateOf(false) }
            val intercom = remember { this@MainActivity.intercomEngine }
            DisposableEffect(intercom) { onDispose { intercom.stop() } }

            val recordings = remember { mutableStateListOf<LocalClip>() }
            LaunchedEffect(Unit) {
                val clips = withContext(Dispatchers.IO) {
                    runCatching { RecordingLibrary.list(context) }.getOrDefault(emptyList())
                }
                recordings.clear()
                recordings.addAll(clips)
            }
            var playingClip by remember { mutableStateOf<LocalClip?>(null) }
            var storageLabel by remember { mutableStateOf(RecordingStorage.label(context)) }
            var storageExternal by remember { mutableStateOf(RecordingStorage.isExternal(context)) }
            val externalPicker = rememberLauncherForActivityResult(
                ActivityResultContracts.OpenDocumentTree()
            ) { uri ->
                if (uri != null) {
                    try {
                        RecordingStorage.selectFolder(context, uri)
                        storageLabel = RecordingStorage.label(context)
                        storageExternal = true
                        scope.launch {
                            val clips = withContext(Dispatchers.IO) {
                                runCatching { RecordingLibrary.list(context) }.getOrDefault(emptyList())
                            }
                            recordings.clear()
                            recordings.addAll(clips)
                        }
                        Toast.makeText(context, "External recording folder selected", Toast.LENGTH_SHORT).show()
                    } catch (e: Exception) {
                        Toast.makeText(context, "Folder access failed: " + (e.message ?: "Unsupported provider"), Toast.LENGTH_LONG).show()
                    }
                }
            }
            val usePhone = {
                RecordingStorage.selectPhone(context)
                storageLabel = RecordingStorage.label(context)
                storageExternal = false
                Unit
            }
            val chooseExternal = { externalPicker.launch(null) }
            val selected = cameras.firstOrNull { it.id == selectedId } ?: cameras.firstOrNull()
            var gardaTelemetry by remember { mutableStateOf<GardaTelemetry?>(null) }
            var gardaVerifiedId by remember { mutableStateOf("") }
            var gardaBusy by remember { mutableStateOf(false) }
            var gardaMessage by remember { mutableStateOf("") }
            LaunchedEffect(selected?.id, selected?.url) {
                gardaVerifiedId = ""
                gardaTelemetry = null
                val camera = selected
                if (camera != null) {
                    thread(name = "foldview-garda-status", isDaemon = true) {
                        try {
                            val telemetry = GardaNativeApi.status(camera)
                            runOnUiThread {
                                val currentId = selectedId.ifBlank { cameras.firstOrNull()?.id ?: "" }
                                if (camera.id == currentId) {
                                    gardaTelemetry = telemetry
                                    gardaVerifiedId = camera.id
                                    gardaMessage = "GARDA native service detected"
                                }
                            }
                        } catch (_: Exception) {
                            // No GARDA API is normal for ordinary ONVIF cameras.
                        }
                    }
                }
            }
            var mediaReport by remember { mutableStateOf<GardaMediaReport?>(null) }
            var mediaBusy by remember { mutableStateOf(false) }
            var mediaMessage by remember { mutableStateOf("") }
            var joystickProblem by remember { mutableStateOf("") }
            var joystickInfo by remember { mutableStateOf("") }
            LaunchedEffect(selected?.id) {
                mediaReport = null
                mediaMessage = ""
                joystickProblem = ""
                joystickInfo = ""
            }
            val cameraRecordings = remember { mutableStateListOf<RemoteRecording>() }
            var remoteBusy by remember { mutableStateOf(false) }
            var remoteMessage by remember { mutableStateOf("Requires ONVIF Profile G Recording + Replay services. V380 microSD/P2P may not support this.") }
            val findRemote = {
                val camera = selected
                if (camera == null || camera.onvifUrl.isBlank()) {
                    remoteMessage = "Select a camera with an ONVIF Device service URL."
                } else if (!remoteBusy) {
                    remoteBusy = true
                    cameraRecordings.clear()
                    remoteMessage = "Querying ONVIF Profile G Recording service..."
                    thread(name = "foldview-onvif-replay-list", isDaemon = true) {
                        try {
                            val records = OnvifReplay.list(camera)
                            runOnUiThread {
                                cameraRecordings.addAll(records)
                                remoteMessage = if (records.isEmpty()) "No Profile G recordings returned."
                                    else "Camera exposed " + records.size + " recording track(s). Replay time seeking may require a more advanced RTSP client."
                                remoteBusy = false
                            }
                        } catch (e: Exception) {
                            runOnUiThread {
                                remoteMessage = "Profile G unavailable: " + (e.message ?: "Camera rejected request")
                                remoteBusy = false
                            }
                        }
                    }
                }
                Unit
            }
            val openRemote: (RemoteRecording) -> Unit = { track ->
                val camera = selected
                if (camera != null && !remoteBusy) {
                    remoteBusy = true
                    remoteMessage = "Requesting camera RTSP replay endpoint..."
                    thread(name = "foldview-onvif-replay-start", isDaemon = true) {
                        try {
                            val url = OnvifReplay.replayUri(camera, track.token)
                            runOnUiThread {
                                playingClip = LocalClip(
                                    id = -(track.token.hashCode().toLong() and 0x7fffffffL) - 1,
                                    name = track.label + " · ONVIF Profile G",
                                    uri = url,
                                    dateSeconds = System.currentTimeMillis() / 1000,
                                    durationMs = 0
                                )
                                remoteMessage = "Playing camera-provided RTSP replay URI. Time seeking may be unsupported."
                                remoteBusy = false
                            }
                        } catch (e: Exception) {
                            runOnUiThread {
                                remoteMessage = "Replay unavailable: " + (e.message ?: "Unsupported firmware")
                                remoteBusy = false
                            }
                        }
                    }
                }
            }
            fun stripRtspUserinfo(raw: String): String = try {
                val uri = java.net.URI(raw)
                java.net.URI(uri.scheme, null, uri.host, uri.port, uri.path, uri.query, uri.fragment)
                    .toASCIIString()
            } catch (_: Exception) { raw }
            fun saveAll() = vault.write(cameras.map { camera ->
                if (camera.id in sessionOnlyIds) camera.copy(
                    url = stripRtspUserinfo(camera.url), onvifUser = "", onvifPassword = ""
                ) else camera
            })
            fun registerResolved(
                candidate: LanCamera,
                resolved: ResolvedCamera,
                login: CameraLogin? = null,
                rememberLogin: Boolean = true
            ): Pair<CameraInfo, Int> {
                val urls = listOfNotNull(resolved.url, resolved.secondaryUrl).distinct()
                var first: CameraInfo? = null
                var added = 0
                for (url in urls) {
                    val currentUri = try { java.net.URI(url) } catch (_: Exception) { continue }
                    val existingIndex = cameras.indexOfFirst {
                        try {
                            val old = java.net.URI(it.url)
                            old.host == currentUri.host && old.port == currentUri.port &&
                                old.scheme.equals(currentUri.scheme, true)
                        } catch (_: Exception) { false }
                    }
                    val entry = if (existingIndex >= 0) {
                        val previous = cameras[existingIndex]
                        previous.copy(
                            url = url,
                            onvifUrl = resolved.onvifUrl.ifBlank { previous.onvifUrl },
                            onvifUser = login?.username ?: previous.onvifUser,
                            onvifPassword = login?.password ?: previous.onvifPassword
                        ).also { cameras[existingIndex] = it }
                    } else {
                        val name = when (currentUri.port) {
                            1234 -> "GARDA " + candidate.ip + " PTZ"
                            1235 -> "GARDA " + candidate.ip + " Wide"
                            else -> "LAN " + candidate.ip
                        }
                        CameraInfo(
                            UUID.randomUUID().toString(), name, url, resolved.onvifUrl,
                            login?.username.orEmpty(), login?.password.orEmpty()
                        ).also {
                            cameras.add(it)
                            added++
                        }
                    }
                    if (login != null) {
                        if (rememberLogin) sessionOnlyIds.remove(entry.id)
                        else if (entry.id !in sessionOnlyIds) sessionOnlyIds.add(entry.id)
                    }
                    if (first == null) first = entry
                }
                if (login != null) {
                    if (rememberLogin) loginVault.remember(candidate.ip, login)
                    else loginVault.forget(candidate.ip)
                }
                saveAll()
                return (first ?: throw IllegalStateException("No usable video URI")) to added
            }
            val backupExportLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.CreateDocument("application/json")
            ) { target ->
                if (target != null) {
                    scope.launch {
                        val ok = withContext(Dispatchers.IO) {
                            runCatching {
                                val safeJson = GardaCameraBackup.export(cameras.toList())
                                context.contentResolver.openOutputStream(target)?.use {
                                    it.write(safeJson.toByteArray(Charsets.UTF_8))
                                } ?: error("File unavailable")
                            }.isSuccess
                        }
                        Toast.makeText(context,
                            if (ok) "📁 Camera list exported (without passwords)"
                            else "Backup failed", Toast.LENGTH_LONG).show()
                    }
                }
            }
            val backupImportLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.OpenDocument()
            ) { source ->
                if (source != null) {
                    scope.launch {
                        val imported = withContext(Dispatchers.IO) {
                            runCatching {
                                context.contentResolver.openInputStream(source)?.use { input ->
                                    val content = input.bufferedReader().readText()
                                    GardaCameraBackup.import(content)
                                } ?: error("File unavailable")
                            }
                        }
                        imported.onSuccess { restored ->
                            var added = 0
                            restored.forEach { c ->
                                val known = cameras.any { it.url == c.url && it.onvifUrl == c.onvifUrl }
                                if (!known) { cameras.add(c); added++ }
                            }
                            saveAll()
                            Toast.makeText(context,
                                "📹 $added camera(s) restored. Re-enter protected camera logins.",
                                Toast.LENGTH_LONG).show()
                        }.onFailure {
                            Toast.makeText(context, "Camera backup invalid or unreadable",
                                Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
            val exportCameras = { backupExportLauncher.launch("GARDA-camera-list.json") }
            val importCameras = { backupImportLauncher.launch(arrayOf("application/json", "text/plain")) }
            val inspectMedia = {
                val camera = selected
                if (camera != null && camera.onvifUrl.isNotBlank() && !mediaBusy) {
                    mediaBusy = true
                    mediaReport = null
                    mediaMessage = "Inspecting camera profiles…"
                    thread(name = "garda-onvif-media-inspect", isDaemon = true) {
                        val result = runCatching { GardaMediaInspector.inspect(camera) }
                        runOnUiThread {
                            if (selected?.id == camera.id) {
                                result.onSuccess { report ->
                                    mediaReport = report
                                    mediaMessage = "Read-only media capabilities loaded."
                                }.onFailure {
                                    mediaMessage = "Media information unavailable: " +
                                        (it.message?.take(110) ?: "unsupported camera")
                                }
                            }
                            mediaBusy = false
                        }
                    }
                }
                Unit
            }
            val chooseStream: (GardaStreamProfile) -> Unit = { profile ->
                val camera = selected
                val newUri = profile.rtspUrl
                if (camera != null && newUri != null) {
                    val valid = runCatching {
                        java.net.URI(newUri).host == java.net.URI(camera.url).host
                    }.getOrDefault(false)
                    if (valid) {
                        val index = cameras.indexOfFirst { it.id == camera.id }
                        if (index >= 0) {
                            cameras[index] = camera.copy(url = newUri)
                            saveAll()
                            mediaMessage = "📹 " + profile.name + " · " + profile.resolution
                        }
                    }
                }
            }
            fun startDiscovery(connectNow: Boolean) {
                if (scanning) return
                scanning = true
                found.clear()
                scanMessage = "Scanning local Wi-Fi for RTSP and ONVIF cameras..."
                thread(name = "foldview-lan-scan", isDaemon = true) {
                    try {
                        val results = LanCameraScanner.scan(applicationContext) { status ->
                            runOnUiThread { scanMessage = status }
                        }
                        val needsLogin = mutableListOf<LanCamera>()
                        val ready = if (connectNow) results.take(16).mapNotNull { candidate ->
                            val saved = loginVault.load(candidate.ip)
                            if (candidate.onvifUrl != null && saved == null) {
                                needsLogin.add(candidate)
                                null
                            } else {
                                try { Triple(candidate, CameraQuickConnect.resolve(candidate, saved), saved) }
                                catch (_: OnvifLoginRequired) {
                                    needsLogin.add(candidate)
                                    null
                                } catch (_: Exception) { null }
                            }
                        } else emptyList()
                        runOnUiThread {
                            found.addAll(results)
                            var connected = 0
                            var firstReady: CameraInfo? = null
                            for ((candidate, resolved, login) in ready) {
                                val (camera, count) = registerResolved(candidate, resolved, login)
                                if (firstReady == null) firstReady = camera
                                connected += count
                            }
                            if (firstReady != null) {
                                selectedId = firstReady.id
                                grid = if (cameras.size > 1) 2 else 1
                                tab = "Live"
                            }
                            scanMessage = "Detected ${results.size} camera(s); added $connected stream(s)." +
                                (if (needsLogin.isNotEmpty()) " Camera login required for ONVIF/RTSP." else "")
                            scanning = false
                            if (needsLogin.isNotEmpty()) loginTarget = needsLogin.first()
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            scanMessage = "LAN scan failed: " + (e.message ?: "Check Wi-Fi and permission")
                            scanning = false
                        }
                    }
                }
            }
            val permissionLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestPermission()
            ) { granted ->
                if (granted && waitingForScanPermission) startDiscovery(autoJoinOnScan)
                else if (!granted) scanMessage = "Allow Nearby devices / Local network to scan cameras."
                waitingForScanPermission = false
            }
            fun requestDiscovery(autoConnect: Boolean) {
                autoJoinOnScan = autoConnect
                if (Build.VERSION.SDK_INT >= 37 &&
                    checkSelfPermission("android.permission.ACCESS_LOCAL_NETWORK") != PackageManager.PERMISSION_GRANTED
                ) {
                    waitingForScanPermission = true
                    permissionLauncher.launch("android.permission.ACCESS_LOCAL_NETWORK")
                } else startDiscovery(autoConnect)
            }
            val requestScan = { requestDiscovery(false) }
            val requestScanAuto = { requestDiscovery(true) }
            fun connectWithLogin(
                candidate: LanCamera,
                login: CameraLogin?,
                rememberLogin: Boolean,
                manualRtsp: String = ""
            ) {
                if (connectingIp.isNotBlank()) return
                connectingIp = candidate.ip
                scanMessage = "Connecting to ${candidate.ip}..."
                thread(name = "garda-camera-login", isDaemon = true) {
                    try {
                        val resolved = CameraQuickConnect.resolve(candidate, login, manualRtsp)
                        runOnUiThread {
                            try {
                                val (camera, added) = registerResolved(
                                    candidate, resolved, login, rememberLogin
                                )
                                intercom.stop()
                                talking = false
                                selectedId = camera.id
                                grid = if (resolved.secondaryUrl != null) 2 else 1
                                tab = "Live"
                                scanMessage = "Camera ${candidate.ip} added ($added stream(s))." +
                                    (if (rememberLogin && login != null) " Login securely remembered." else "")
                                loginTarget = null
                                loginDraft = null
                            } catch (_: Exception) {
                                scanMessage = "Connected, but could not save camera profile securely."
                                Toast.makeText(context, scanMessage, Toast.LENGTH_LONG).show()
                            } finally {
                                connectingIp = ""
                            }
                        }
                    } catch (error: Exception) {
                        runOnUiThread {
                            connectingIp = ""
                            scanMessage = if (error is OnvifLoginRequired)
                                "${candidate.ip}: Check ONVIF credentials or RTSP path."
                            else "${candidate.ip}: Cannot negotiate ONVIF/RTSP. Check camera login and path."
                            loginTarget = candidate
                            Toast.makeText(context, scanMessage, Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
            val connectCamera: (LanCamera) -> Unit = { candidate ->
                val remembered = loginVault.load(candidate.ip)
                if (remembered == null && candidate.onvifUrl != null) {
                    loginDraft = null
                    loginTarget = candidate
                } else {
                    connectWithLogin(candidate, remembered, rememberLogin = remembered != null)
                }
            }
            val onGardaAction: (GardaAction) -> Unit = { action ->
                val camera = selected
                if (camera != null && camera.id == gardaVerifiedId &&
                    gardaTelemetry != null && !gardaBusy) {
                    gardaBusy = true
                    thread(name = "foldview-garda-control", isDaemon = true) {
                        val response = try {
                            GardaNativeApi.command(camera, action)
                        } catch (e: Exception) {
                            "GARDA control failed: " + (e.message ?: "no response")
                        }
                        runOnUiThread {
                            gardaBusy = false
                            gardaMessage = response
                            Toast.makeText(context, response, Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            }
            val projectionManager = remember { getSystemService(MediaProjectionManager::class.java) }
            val captureLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.StartActivityForResult()
            ) { result ->
                if (result.resultCode == Activity.RESULT_OK && result.data != null) {
                    try {
                        startForegroundService(
                            Intent(this, RecordingService::class.java).setAction(RecordingService.START)
                                .putExtra(RecordingService.RESULT, result.resultCode)
                                .putExtra(RecordingService.DATA, result.data)
                        )
                        recording = true
                        Toast.makeText(context, "Screen recording requested. Stop from Live or notification.", Toast.LENGTH_LONG).show()
                    } catch (_: Exception) {
                        recording = false
                        Toast.makeText(context, "Could not start recording service.", Toast.LENGTH_LONG).show()
                    }
                } else recording = false
            }
            fun startTalk() {
                val cam = selected ?: return
                if (talking || talkStarting) return
                talkStarting = true
                intercom.start(cam) { active, message ->
                    runOnUiThread {
                        talking = active
                        talkStarting = false
                        if (message.isNotBlank()) Toast.makeText(context, message, Toast.LENGTH_LONG).show()
                    }
                }
            }
            val micLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestPermission()
            ) { approved ->
                if (approved) startTalk()
                else Toast.makeText(context, "Microphone permission required for camera intercom.", Toast.LENGTH_SHORT).show()
            }
            val onTalkClick = {
                if (talking || talkStarting) {
                    intercom.stop()
                    talking = false
                    talkStarting = false
                } else if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    micLauncher.launch(Manifest.permission.RECORD_AUDIO)
                } else startTalk()
            }
            val requestRecord = {
                if (!recording) captureLauncher.launch(projectionManager.createScreenCaptureIntent())
            }
            val stopRecord = {
                startService(Intent(this, RecordingService::class.java).setAction(RecordingService.STOP))
                recording = false
            }
            val refreshRecordings = {
                scope.launch {
                    val clips = withContext(Dispatchers.IO) {
                        runCatching { RecordingLibrary.list(context) }.getOrDefault(emptyList())
                    }
                    recordings.clear()
                    recordings.addAll(clips)
                }
                Unit
            }
            val ptzControl: (Double, Double) -> Unit = { pan, tilt ->
                val camera = selected
                if (camera == null || camera.onvifUrl.isBlank()) {
                    Toast.makeText(context, "Configure ONVIF camera service first.", Toast.LENGTH_LONG).show()
                } else {
                    thread(name = "foldview-onvif-ptz", isDaemon = true) {
                        try {
                            OnvifPtz.pulse(camera, pan, tilt)
                        } catch (e: Exception) {
                            runOnUiThread {
                                Toast.makeText(context, "PTZ unavailable: " + (e.message ?: "Camera refused"), Toast.LENGTH_LONG).show()
                            }
                        }
                    }
                }
            }
            val stopPtz: () -> Unit = {
                val camera = selected
                if (camera != null && camera.onvifUrl.isNotBlank()) {
                    thread(name = "garda-ptz-emergency-stop", isDaemon = true) {
                        runCatching { OnvifPtz.stopContinuous(camera) }
                    }
                }
            }
            val zoomControl: (Double) -> Unit = { speed ->
                val camera = selected
                if (camera == null || camera.onvifUrl.isBlank()) {
                    Toast.makeText(context, "Configure ONVIF camera service first.", Toast.LENGTH_LONG).show()
                } else {
                    thread(name = "foldview-onvif-zoom", isDaemon = true) {
                        try {
                            OnvifPtz.pulseZoom(camera, speed)
                        } catch (e: Exception) {
                            runOnUiThread {
                                Toast.makeText(context, "Zoom unavailable: " + (e.message ?: "Camera refused"), Toast.LENGTH_LONG).show()
                            }
                        }
                    }
                }
            }
            CompositionLocalProvider(LocalGardaLanguage provides language) {
            MaterialTheme(colorScheme = gardaScheme(darkMode)) {
                SideEffect {
                    // System Back / Home / Recents remain readable on either palette.
                    window.statusBarColor = if (darkMode) android.graphics.Color.rgb(9, 11, 16)
                        else android.graphics.Color.rgb(247, 248, 250)
                    window.navigationBarColor = if (darkMode) android.graphics.Color.rgb(9, 11, 16)
                        else android.graphics.Color.rgb(247, 248, 250)
                    val appearance = android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS or
                        android.view.WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS
                    window.insetsController?.setSystemBarsAppearance(if (darkMode) 0 else appearance, appearance)
                }
                BoxWithConstraints(Modifier.fillMaxSize().background(Bg).safeDrawingPadding()) {
                    val wide = GardaLayoutRules.useNavigationRail(BuildConfig.IS_FOLD_EDITION, maxWidth.value)
                    val menu = @Composable {
                        AppNavigation(tab = tab, onChoose = { tab = it; if (it == "Recordings") refreshRecordings() }, vertical = wide)
                    }
                    if (wide) {
                        Row(Modifier.fillMaxSize()) {
                            menu()
                            VerticalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = .33f))
                            MainPane(
                                modifier = Modifier.weight(1f),
                                tab = tab,
                                cameras = cameras.toList(),
                                selected = selected,
                                grid = grid,
                                audio = audio,
                                foldWide = wide,
                                darkMode = darkMode,
                                onToggleTheme = {
                                    darkMode = !darkMode
                                    themePrefs.edit().putBoolean("dark_mode", darkMode).apply()
                                },
                                language = language,
                                onLanguageChange = {
                                    language = it
                                    themePrefs.edit().putString("language", it).apply()
                                },
                                scanMessage = scanMessage,
                                scanResults = found.toList(),
                                scanning = scanning,
                                connectingIp = connectingIp,
                                gardaTelemetry = if (selected?.id == gardaVerifiedId) gardaTelemetry else null,
                                gardaBusy = gardaBusy,
                                gardaMessage = gardaMessage,
                                onGardaAction = onGardaAction,
                                onJoystickProblem = { message ->
                                    runOnUiThread { joystickProblem = message }
                                },
                                onJoystickInfo = { message ->
                                    runOnUiThread { joystickInfo = message }
                                },
                                joystickProblem = joystickProblem,
                                joystickInfo = joystickInfo,
                                mediaReport = mediaReport,
                                mediaBusy = mediaBusy,
                                mediaMessage = mediaMessage,
                                onInspectMedia = inspectMedia,
                                onChooseMediaStream = chooseStream,
                                onQuickConnect = connectCamera,
                                onScanAndConnect = requestScanAuto,
                                recording = recording,
                                talking = talking,
                                clips = recordings.toList(),
                                storageLabel = storageLabel,
                                storageExternal = storageExternal,
                                onUsePhone = usePhone,
                                onChooseExternal = chooseExternal,
                                remote = cameraRecordings.toList(),
                                remoteMessage = remoteMessage,
                                remoteBusy = remoteBusy,
                                onFindRemote = findRemote,
                                onOpenRemote = openRemote,
                                onRecord = requestRecord,
                                onStopRecord = stopRecord,
                                onPtz = ptzControl,
                                onZoom = zoomControl,
                                onStopPtz = stopPtz,
                                onRefreshRecordings = refreshRecordings,
                                onPlayRecording = { playingClip = it },
                                onIntercom = onTalkClick,
                                onGrid = { grid = it },
                                onAudio = { audio = !audio },
                                onChoose = {
                                    intercom.stop()
                                    talking = false
                                    talkStarting = false
                                    selectedId = it
                                    grid = 1
                                    tab = "Live"
                                    if (Build.VERSION.SDK_INT >= 37 &&
                                        checkSelfPermission("android.permission.ACCESS_LOCAL_NETWORK") != PackageManager.PERMISSION_GRANTED
                                    ) permissionLauncher.launch("android.permission.ACCESS_LOCAL_NETWORK")
                                },
                                onAdd = { addDialog = true },
                                onRemove = { id ->
                                    cameras.removeAll { it.id == id }
                                    if (selectedId == id) selectedId = ""
                                    saveAll()
                                },
                                onScan = requestScan,
                                onExportCameras = exportCameras,
                                onImportCameras = importCameras,
                                onSurface = { focusedSurface = it },
                                onSnapshot = {
                                    val surface = focusedSurface
                                    if (surface == null || !surface.holder.surface.isValid) {
                                        Toast.makeText(context, "Select an active camera first.", Toast.LENGTH_SHORT).show()
                                    } else saveSnapshot(surface)
                                }
                            )
                        }
                    } else {
                        Column(Modifier.fillMaxSize()) {
                            MainPane(
                                modifier = Modifier.weight(1f),
                                tab = tab,
                                cameras = cameras.toList(),
                                selected = selected,
                                grid = grid,
                                audio = audio,
                                foldWide = wide,
                                darkMode = darkMode,
                                onToggleTheme = {
                                    darkMode = !darkMode
                                    themePrefs.edit().putBoolean("dark_mode", darkMode).apply()
                                },
                                language = language,
                                onLanguageChange = {
                                    language = it
                                    themePrefs.edit().putString("language", it).apply()
                                },
                                scanMessage = scanMessage,
                                scanResults = found.toList(),
                                scanning = scanning,
                                connectingIp = connectingIp,
                                gardaTelemetry = if (selected?.id == gardaVerifiedId) gardaTelemetry else null,
                                gardaBusy = gardaBusy,
                                gardaMessage = gardaMessage,
                                onGardaAction = onGardaAction,
                                onJoystickProblem = { message ->
                                    runOnUiThread { joystickProblem = message }
                                },
                                onJoystickInfo = { message ->
                                    runOnUiThread { joystickInfo = message }
                                },
                                joystickProblem = joystickProblem,
                                joystickInfo = joystickInfo,
                                mediaReport = mediaReport,
                                mediaBusy = mediaBusy,
                                mediaMessage = mediaMessage,
                                onInspectMedia = inspectMedia,
                                onChooseMediaStream = chooseStream,
                                onQuickConnect = connectCamera,
                                onScanAndConnect = requestScanAuto,
                                recording = recording,
                                talking = talking,
                                clips = recordings.toList(),
                                storageLabel = storageLabel,
                                storageExternal = storageExternal,
                                onUsePhone = usePhone,
                                onChooseExternal = chooseExternal,
                                remote = cameraRecordings.toList(),
                                remoteMessage = remoteMessage,
                                remoteBusy = remoteBusy,
                                onFindRemote = findRemote,
                                onOpenRemote = openRemote,
                                onRecord = requestRecord,
                                onStopRecord = stopRecord,
                                onPtz = ptzControl,
                                onZoom = zoomControl,
                                onStopPtz = stopPtz,
                                onRefreshRecordings = refreshRecordings,
                                onPlayRecording = { playingClip = it },
                                onIntercom = onTalkClick,
                                onGrid = { grid = it },
                                onAudio = { audio = !audio },
                                onChoose = {
                                    intercom.stop()
                                    talking = false
                                    talkStarting = false
                                    selectedId = it
                                    grid = 1
                                    tab = "Live"
                                    if (Build.VERSION.SDK_INT >= 37 &&
                                        checkSelfPermission("android.permission.ACCESS_LOCAL_NETWORK") != PackageManager.PERMISSION_GRANTED
                                    ) permissionLauncher.launch("android.permission.ACCESS_LOCAL_NETWORK")
                                },
                                onAdd = { addDialog = true },
                                onRemove = { id ->
                                    cameras.removeAll { it.id == id }
                                    if (selectedId == id) selectedId = ""
                                    saveAll()
                                },
                                onScan = requestScan,
                                onExportCameras = exportCameras,
                                onImportCameras = importCameras,
                                onSurface = { focusedSurface = it },
                                onSnapshot = {
                                    val surface = focusedSurface
                                    if (surface == null || !surface.holder.surface.isValid) {
                                        Toast.makeText(context, "Select an active camera first.", Toast.LENGTH_SHORT).show()
                                    } else saveSnapshot(surface)
                                }
                            )
                            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = .33f))
                            menu()
                        }
                    }
                }
                playingClip?.let { LocalClipPlayer(it) { playingClip = null } }
                loginTarget?.let { camera ->
                    CameraLoginDialog(
                        camera = camera,
                        remembered = loginDraft ?: loginVault.load(camera.ip),
                        onDismiss = { loginTarget = null },
                        onConnect = { login, rememberLogin, manualRtsp ->
                            loginDraft = login
                            loginTarget = null
                            connectWithLogin(camera, login, rememberLogin, manualRtsp)
                        },
                        onAnonymous = {
                            loginDraft = null
                            loginTarget = null
                            connectWithLogin(camera, null, false)
                        }
                    )
                }
                if (addDialog) {
                    AddCameraDialog(
                        onDismiss = { addDialog = false },
                        onSave = { name, url, onvifEndpoint, onvifUsername, onvifPassword ->
                            val camera = CameraInfo(UUID.randomUUID().toString(), name, url, onvifEndpoint, onvifUsername, onvifPassword)
                            cameras.add(camera)
                            selectedId = camera.id
                            grid = 1
                            tab = "Live"
                            saveAll()
                            addDialog = false
                            if (Build.VERSION.SDK_INT >= 37 &&
                                checkSelfPermission("android.permission.ACCESS_LOCAL_NETWORK") != PackageManager.PERMISSION_GRANTED
                            ) permissionLauncher.launch("android.permission.ACCESS_LOCAL_NETWORK")
                        }
                    )
                }
            }
            }
        }
    }

    private fun saveSnapshot(view: SurfaceView) {
        val width = view.width
        val height = view.height
        if (width < 1 || height < 1) return
        val bmp = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        PixelCopy.request(view, bmp, { result ->
            if (result == PixelCopy.SUCCESS) {
                try {
                    val values = ContentValues().apply {
                        put(MediaStore.Images.Media.DISPLAY_NAME, "GARDA_FOLD_" + System.currentTimeMillis() + ".png")
                        put(MediaStore.Images.Media.MIME_TYPE, "image/png")
                        put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/GARDA_CCTV")
                    }
                    val uri = contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
                    uri?.let { contentResolver.openOutputStream(it)?.use { stream ->
                        bmp.compress(Bitmap.CompressFormat.PNG, 100, stream)
                    } }
                    Toast.makeText(this, "Snapshot saved to Pictures/GARDA_CCTV", Toast.LENGTH_SHORT).show()
                } catch (_: Exception) {
                    Toast.makeText(this, "Snapshot save failed", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Snapshot unavailable for this stream", Toast.LENGTH_SHORT).show()
            }
            bmp.recycle()
        }, Handler(Looper.getMainLooper()))
    }
}

@Composable
private fun AppNavigation(tab: String, onChoose: (String) -> Unit, vertical: Boolean) {
    val tabs = listOf("Live", "Recordings", "Cameras", "Settings")
    val icons = listOf("◉", "▤", "▦", "⚙")
    if (vertical) {
        Column(
            Modifier.width(98.dp).fillMaxHeight().background(Panel).padding(8.dp),
            verticalArrangement = Arrangement.spacedBy(9.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(Modifier.height(6.dp))
            GardaLogo()
            Text("GARDA", color = Mint, style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Black)
            Spacer(Modifier.height(13.dp))
            tabs.forEachIndexed { index, label ->
                GardaNavItem(
                    label = when (label) {
                        "Recordings" -> gText("Klip", "Clips")
                        "Cameras" -> gText("Kamera", "Devices")
                        "Settings" -> gText("Setelan", "Settings")
                        else -> gText("Live", "Live")
                    },
                    symbol = icons[index], active = tab == label,
                    modifier = Modifier.fillMaxWidth().height(69.dp),
                    onClick = { onChoose(label) }
                )
            }
            Spacer(Modifier.weight(1f))
            Text("FOLD", color = Muted, style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold)
        }
    } else {
        Row(
            Modifier.fillMaxWidth().height(69.dp).background(Panel)
                .padding(horizontal = 6.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            tabs.forEachIndexed { index, label ->
                GardaNavItem(
                    label = when (label) {
                        "Recordings" -> gText("Klip", "Clips")
                        "Cameras" -> gText("Kamera", "Devices")
                        "Settings" -> gText("Setelan", "Settings")
                        else -> gText("Live", "Live")
                    },
                    symbol = icons[index], active = tab == label,
                    modifier = Modifier.weight(1f).fillMaxHeight(),
                    onClick = { onChoose(label) }
                )
            }
        }
    }
}

@Composable
private fun GardaNavItem(
    label: String,
    symbol: String,
    active: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val source = remember { MutableInteractionSource() }
    val pressed by source.collectIsPressedAsState()
    val scale by animateFloatAsState(if (pressed) .93f else 1f, animationSpec = tween(120), label = "nav press")
    val fill by animateColorAsState(
        if (active) MaterialTheme.colorScheme.primaryContainer else Color.Transparent,
        animationSpec = tween(210), label = "nav color"
    )
    Column(
        modifier.graphicsLayer { scaleX = scale; scaleY = scale }
            .clip(RoundedCornerShape(14.dp)).background(fill)
            .clickable(interactionSource = source, indication = null, onClick = onClick)
            .padding(horizontal = 3.dp, vertical = 4.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(symbol, color = if (active) Mint else Muted,
            style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        Text(label, color = if (active) MaterialTheme.colorScheme.onSurface else Muted,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = if (active) FontWeight.Bold else FontWeight.Medium,
            maxLines = 1)
    }
}

@Composable
private fun MainPane(
    modifier: Modifier,
    tab: String,
    cameras: List<CameraInfo>,
    selected: CameraInfo?,
    grid: Int,
    audio: Boolean,
    foldWide: Boolean,
    darkMode: Boolean,
    onToggleTheme: () -> Unit,
    language: String,
    onLanguageChange: (String) -> Unit,
    scanMessage: String,
    scanResults: List<LanCamera>,
    scanning: Boolean,
    connectingIp: String,
    gardaTelemetry: GardaTelemetry?,
    gardaBusy: Boolean,
    gardaMessage: String,
    onGardaAction: (GardaAction) -> Unit,
    onJoystickProblem: (String) -> Unit,
    onJoystickInfo: (String) -> Unit,
    joystickProblem: String,
    joystickInfo: String,
    mediaReport: GardaMediaReport?,
    mediaBusy: Boolean,
    mediaMessage: String,
    onInspectMedia: () -> Unit,
    onChooseMediaStream: (GardaStreamProfile) -> Unit,
    onQuickConnect: (LanCamera) -> Unit,
    onScanAndConnect: () -> Unit,
    recording: Boolean,
    talking: Boolean,
    clips: List<LocalClip>,
    storageLabel: String,
    storageExternal: Boolean,
    onUsePhone: () -> Unit,
    onChooseExternal: () -> Unit,
    remote: List<RemoteRecording>,
    remoteMessage: String,
    remoteBusy: Boolean,
    onFindRemote: () -> Unit,
    onOpenRemote: (RemoteRecording) -> Unit,
    onRecord: () -> Unit,
    onStopRecord: () -> Unit,
    onPtz: (Double, Double) -> Unit,
    onZoom: (Double) -> Unit,
    onStopPtz: () -> Unit,
    onRefreshRecordings: () -> Unit,
    onPlayRecording: (LocalClip) -> Unit,
    onIntercom: () -> Unit,
    onGrid: (Int) -> Unit,
    onAudio: () -> Unit,
    onChoose: (String) -> Unit,
    onAdd: () -> Unit,
    onRemove: (String) -> Unit,
    onScan: () -> Unit,
    onExportCameras: () -> Unit,
    onImportCameras: () -> Unit,
    onSurface: (SurfaceView?) -> Unit,
    onSnapshot: () -> Unit
) {
    Column(modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        GardaHeader("GARDA CCTV",
            if (BuildConfig.IS_FOLD_EDITION)
                gText("FOLD edition · Pemantauan lokal", "FOLD edition · Local monitoring")
            else
                gText("Standard edition · Pemantauan lokal", "Standard edition · Local monitoring"),
            cameras.size
        )
        when (tab) {
            "Live" -> {
                Column(
                    Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(gText("Pusat Kontrol", "Command Deck"), style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.ExtraBold)
                            Text(gText("Pemantauan langsung · Dua lensa", "Live monitoring · Dual Vision ready"),
                                color = Muted, style = MaterialTheme.typography.bodySmall)
                        }
                        Surface(
                            color = MaterialTheme.colorScheme.primaryContainer,
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("● LOCAL LIVE", modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
                                color = MaterialTheme.colorScheme.onPrimaryContainer,
                                style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                        }
                    }
                    GardaDashboardMetrics(cameras.size, grid, gardaTelemetry != null)
                    if (cameras.isEmpty()) {
                        Surface(
                            color = Panel, shape = RoundedCornerShape(20.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                Modifier.fillMaxWidth().padding(20.dp),
                                verticalArrangement = Arrangement.spacedBy(12.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                GardaEmptyCameraArtwork()
                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    GardaProtocolChip("📷", "RTSP")
                                    GardaProtocolChip("📡", "ONVIF")
                                }
                                Text(gText("Hubungkan kamera pertama", "Connect your first camera"), fontWeight = FontWeight.Bold,
                                    style = MaterialTheme.typography.titleMedium)
                                Text(gText("Cari kamera ONVIF/RTSP di jaringan sendiri. Tanpa login cloud.",
                        "Search your authorized local network for ONVIF and RTSP. No cloud login."),
                                    color = Muted, style = MaterialTheme.typography.bodyMedium)
                                GardaMotionButton(
                                    title = if (scanning) gText("Memindai LAN…", "Scanning LAN…")
                                    else gText("📡 Cari & hubungkan", "📡 Scan & connect"),
                                    onClick = onScanAndConnect, enabled = !scanning
                                )
                            }
                        }
                        if (scanning) GardaScanSkeleton()
                    } else {
                        GardaSectionHeading(gText("Video langsung", "Live feeds"),
                            if (cameras.size == 2) gText("DUA LENSA", "DUAL LENS") else "CAMERA WALL")
                        val slots: List<CameraInfo?> = if (grid == 1) listOf(selected) else
                            (0 until grid).map { cameras.getOrNull(it) }
                        val columns = GardaLayoutRules.videoColumns(grid, foldWide)
                        for ((rowIndex, row) in slots.chunked(columns).withIndex()) {
                            Row(
                                Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                row.forEachIndexed { inRow, camera ->
                                    val index = rowIndex * columns + inRow
                                    val focused = camera?.id == selected?.id
                                    VideoTile(
                                        camera = camera,
                                        enabled = index < 4 && camera != null,
                                        muted = !(grid == 1 && audio && focused),
                                        selected = focused,
                                        onClick = { if (camera != null) onChoose(camera.id) },
                                        onSurface = { surface ->
                                            if (focused && grid == 1) onSurface(surface)
                                        },
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                                repeat(columns - row.size) { Spacer(Modifier.weight(1f)) }
                            }
                        }
                        if (scanning) {
                            Text("Searching your LAN in the background…", color = Muted,
                                style = MaterialTheme.typography.bodySmall)
                            GardaScanSkeleton()
                        }
                    }
                    GardaFoldSection(
                        gText("Tampilan & aksi cepat", "Display & quick actions"), "⚡"
                    ) {
                        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                            listOf(1, 2, 4, 9).forEach { size ->
                                GardaMotionButton(
                                    title = when (size) {
                                        1 -> gText("Fokus", "Focus")
                                        2 -> gText("Dua lensa", "Dual")
                                        else -> "$size " + gText("kotak", "tiles")
                                    },
                                    onClick = { onGrid(size) },
                                    filled = grid == size
                                )
                            }
                            GardaMotionButton(gText("Tambah", "Add camera"), onAdd, filled = false)
                            GardaMotionButton(gText("Cari LAN", "Discover"), onScanAndConnect,
                                filled = false, enabled = !scanning)
                        }
                        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                            GardaMotionButton(if (audio) gText("Suara ON", "Audio ON")
                                else gText("Aktifkan audio", "Unmute"), onAudio, filled = false)
                            GardaMotionButton("📸 " + gText("Foto", "Snapshot"),
                                onSnapshot, filled = false, enabled = selected != null && grid == 1)
                            if (recording) GardaMotionButton(gText("Stop rekam", "Stop recording"), onStopRecord)
                            else GardaMotionButton(gText("Rekam MP4", "Record MP4"), onRecord,
                                enabled = selected != null)
                            GardaMotionButton(if (talking) gText("Stop bicara", "Stop talk")
                                else gText("Interkom", "Talk"), onIntercom, filled = false,
                                enabled = selected != null)
                        }
                    }
                    if (selected != null) {
                        val hasOnvifPtz = selected.onvifUrl.isNotBlank()
                        val hasGardaPtz = gardaTelemetry != null
                        if (hasOnvifPtz || hasGardaPtz) {
                            var useGardaNative by remember(selected.id, gardaTelemetry?.ip) {
                                mutableStateOf(hasGardaPtz)
                            }
                            var ptzSensitivity by rememberSaveable(selected.id) {
                                mutableFloatStateOf(2.4f)
                            }
                            var ptzTouchActive by remember(selected.id) {
                                mutableStateOf(false)
                            }
                            GardaFoldSection(
                                gText("Joystick PTZ analog", "Analog PTZ joystick"), "🎮",
                                expandedByDefault = true
                            ) {
                                if (hasOnvifPtz && hasGardaPtz) {
                                    Row(Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        GardaMotionButton(
                                            "📡 ONVIF", onClick = { useGardaNative = false },
                                            filled = !useGardaNative, modifier = Modifier.weight(1f)
                                        )
                                        GardaMotionButton(
                                            "🎛 GARDA", onClick = { useGardaNative = true },
                                            filled = useGardaNative, modifier = Modifier.weight(1f)
                                        )
                                    }
                                }
                                Text(
                                    if (useGardaNative) "GARDA native PTZ · bounded vendor pulses"
                                    else "ONVIF PTZ · ContinuousMove + Stop",
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    style = MaterialTheme.typography.labelMedium
                                )
                                Text(
                                    "🎚 " + gText("Sensitivitas", "Sensitivity") +
                                        " ×" + String.format(java.util.Locale.US, "%.1f", ptzSensitivity),
                                    style = MaterialTheme.typography.labelMedium
                                )
                                Slider(
                                    value = ptzSensitivity,
                                    onValueChange = { ptzSensitivity = it },
                                    valueRange = 1.0f..3.5f,
                                    steps = 9,
                                    modifier = Modifier.fillMaxWidth()
                                )
                                Row(Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.Center) {
                                    GardaPtzJoystick(
                                        camera = selected,
                                        useGardaNative = useGardaNative,
                                        onProblem = onJoystickProblem,
                                        onInfo = onJoystickInfo,
                                        sensitivity = ptzSensitivity,
                                        onTouchState = { ptzTouchActive = it }
                                    )
                                }
                                Text(
                                    if (ptzTouchActive)
                                        "● " + gText("Sentuhan joystick terbaca", "Joystick touch detected")
                                    else gText(
                                        "Sentuh lingkaran atau gunakan empat tombol arah untuk uji PTZ.",
                                        "Touch the circle or use four direction buttons to test PTZ."
                                    ),
                                    color = if (ptzTouchActive) MaterialTheme.colorScheme.primary
                                    else MaterialTheme.colorScheme.onSurfaceVariant,
                                    style = MaterialTheme.typography.labelMedium
                                )
                                Text(gText(
                                    "Sentuh dan geser dari area lingkaran; lepas jari untuk STOP. " +
                                        "Jika tidak bergerak, coba mode ONVIF/GARDA dan cek pesan status. " +
                                        "Respons HTTP bukan bukti motor bergerak.",
                                    "Touch and drag inside the circle; release to STOP. " +
                                        "If the camera does not move, try ONVIF/GARDA mode and read the status. " +
                                        "HTTP acknowledgement does not prove motor movement."
                                ), color = Muted, style = MaterialTheme.typography.bodySmall)
                                Row(Modifier.horizontalScroll(rememberScrollState()),
                                    horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                                    if (hasOnvifPtz) {
                                        GardaMotionButton("🔎 −", { onZoom(-.45) }, filled = false)
                                        GardaMotionButton("🔎 +", { onZoom(.45) }, filled = false)
                                    }
                                    GardaMotionButton(
                                        "⏹ STOP",
                                        onClick = {
                                            // For native GARDA, the same REST STOP is used as joystick.
                                            onStopPtz()
                                            if (hasGardaPtz) onGardaAction(GardaAction.STOP)
                                        },
                                        filled = false
                                    )
                                }
                                if (joystickInfo.isNotBlank()) Text(
                                    joystickInfo, color = MaterialTheme.colorScheme.primary,
                                    style = MaterialTheme.typography.bodySmall
                                )
                                if (joystickProblem.isNotBlank()) Text(
                                    joystickProblem, color = MaterialTheme.colorScheme.error,
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }
                        if (gardaTelemetry != null) {
                            GardaFoldSection(
                                gText("Lampu & kontrol GARDA", "GARDA lighting & controls"), "💡"
                            ) {
                                Text("GARDA native · ${gardaTelemetry.ip}:8899",
                                    color = Mint, style = MaterialTheme.typography.labelMedium)
                                Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                                    horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    listOf(GardaAction.CENTER, GardaAction.STOP,
                                        GardaAction.IR_ON, GardaAction.IR_OFF,
                                        GardaAction.WHITE_ON, GardaAction.WHITE_OFF,
                                        GardaAction.IRCUT_DAY, GardaAction.IRCUT_NIGHT
                                    ).forEach { action ->
                                        GardaMotionButton(action.label, { onGardaAction(action) },
                                            filled = false, enabled = !gardaBusy)
                                    }
                                }
                                if (gardaMessage.isNotBlank()) Text(gardaMessage,
                                    color = Muted, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                        GardaMediaAndCardPanel(
                            camera = selected,
                            report = mediaReport,
                            checking = mediaBusy,
                            message = mediaMessage,
                            onCheck = onInspectMedia,
                            onSelectStream = onChooseMediaStream,
                            remoteTracks = remote,
                            remoteBusy = remoteBusy,
                            remoteStatus = remoteMessage,
                            onScanCard = onFindRemote,
                            onPlayCard = onOpenRemote
                        )
                    }
                    if (recording) Text("Recording screen to $storageLabel. Stop recording to finalize MP4.",
                        color = Mint, style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(10.dp))
                }
            }
            "Recordings" -> {
                RecordingsScreen(
                    clips, recording, onRefreshRecordings, onPlayRecording,
                    storageLabel, storageExternal, onUsePhone, onChooseExternal,
                    remote, remoteMessage, remoteBusy, onFindRemote, onOpenRemote
                )
            }
            "Cameras" -> {
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Text(gText("Kamera tersimpan", "Saved devices"), modifier = Modifier.weight(1f),
                        style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    GardaMotionButton(gText("Tambah RTSP", "Add RTSP"), onAdd)
                }
                Column(Modifier.weight(1f).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    cameras.forEach { camera ->
                        GardaSavedCameraCard(
                            camera = camera,
                            onView = { onChoose(camera.id) },
                            onDelete = { onRemove(camera.id) }
                        )
                    }
                    if (cameras.isEmpty()) Text(gText("Belum ada kamera tersimpan.", "No saved devices yet."), color = Muted)
                    Spacer(Modifier.height(10.dp))
                    GardaFoldSection(
                        gText("Backup daftar kamera", "Camera list backup"), "📁"
                    ) {
                        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            GardaMotionButton(gText("Ekspor", "Export"), onExportCameras, filled = false)
                            GardaMotionButton(gText("Pulihkan", "Restore"), onImportCameras, filled = false)
                        }
                        Text(gText(
                            "Ekspor hanya alamat dan nama kamera, tanpa password. Impor kembali " +
                                "setelah instal ulang dan isi password bila diperlukan.",
                            "Exports only camera names and addresses, without passwords. " +
                                "Import after reinstall; protected cameras require login again."
                        ), style = MaterialTheme.typography.bodySmall)
                    }
                    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        GardaMotionButton(
                            title = if (scanning) gText("Memindai…", "Scanning…") else "📡 Scan LAN",
                            onClick = onScan, modifier = Modifier.fillMaxWidth(),
                            filled = false, enabled = !scanning
                        )
                        GardaMotionButton(
                            title = "🔗 " + gText("Scan + Hubungkan", "Scan + Connect"),
                            onClick = onScanAndConnect, modifier = Modifier.fillMaxWidth(),
                            enabled = !scanning
                        )
                    }
                    Text(scanMessage, color = Muted, style = MaterialTheme.typography.bodySmall)
                    if (scanning) GardaScanSkeleton()
                    scanResults.forEach { camera ->
                        Card(colors = CardDefaults.cardColors(containerColor = Panel)) {
                            Column(Modifier.fillMaxWidth().padding(10.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Column(Modifier.weight(1f)) {
                                        Text(camera.ip, fontWeight = FontWeight.SemiBold)
                                        Text(camera.summary, color = Muted, style = MaterialTheme.typography.bodySmall)
                                    }
                                    Button(
                                        onClick = { onQuickConnect(camera) },
                                        enabled = !scanning && connectingIp.isBlank()
                                    ) {
                                        Text(if (connectingIp == camera.ip) gText("Menghubungkan…", "Connecting…")
                                            else gText("Hubungkan", "Connect"))
                                    }
                                }
                                if (camera.onvifCandidate) {
                                    Text("ONVIF port presence unverified; Connect negotiates capabilities and stream URI.",
                                        color = Muted, style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
            }
            else -> {
                Column(
                    Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    GardaFoldSection(gText("Bahasa / Language", "Language / Bahasa"), "🌐",
                        expandedByDefault = true) {
                        Row(horizontalArrangement = Arrangement.spacedBy(9.dp)) {
                            GardaMotionButton("🇮🇩 Indonesia", {
                                onLanguageChange("id")
                            }, filled = language == "id")
                            GardaMotionButton("🇬🇧 English", {
                                onLanguageChange("en")
                            }, filled = language == "en")
                        }
                    }
                    GardaFoldSection(gText("Tampilan", "Appearance"), "🎨") {
                        GardaMotionButton(
                            title = if (darkMode)
                                gText("☀️ Mode terang", "☀️ Light mode")
                            else gText("🌙 Mode gelap", "🌙 Dark mode"),
                            onClick = onToggleTheme, filled = false
                        )
                        Text(gText(
                            "Navigasi Android 3 tombol dan gesture menggunakan safe-area.",
                            "Android 3-button and gesture navigation use safe-area insets."
                        ), style = MaterialTheme.typography.bodySmall)
                    }
                    GardaAiEventsPanel()
                    GardaCompatibilityPanel()
                    GardaFoldSection(gText("Tentang & pembaruan", "About & updates"), "ℹ️") {
                        GardaAboutUpdates()
                    }
                    Text(if (BuildConfig.IS_FOLD_EDITION)
                        gText("🎥 GARDA CCTV FOLD edition · Penggunaan internal",
                              "🎥 GARDA CCTV FOLD edition · Internal use")
                    else gText("🎥 GARDA CCTV Standard edition · Penggunaan internal",
                               "🎥 GARDA CCTV Standard edition · Internal use"),
                        color = Mint, style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}

@Composable
private fun VideoTile(
    camera: CameraInfo?,
    enabled: Boolean,
    muted: Boolean,
    selected: Boolean,
    onClick: () -> Unit,
    onSurface: (SurfaceView?) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    Box(
        modifier.aspectRatio(16f / 9f)
            .clip(RoundedCornerShape(16.dp))
            .border(2.dp, if (selected) Mint else MaterialTheme.colorScheme.outline.copy(alpha = .25f),
                RoundedCornerShape(16.dp))
            .background(Color(0xFF070B10), RoundedCornerShape(16.dp))
    ) {
        if (camera != null && enabled) {
            key(camera.id, camera.url) {
                val player = remember { ExoPlayer.Builder(context).build() }
                DisposableEffect(player) {
                    try {
                        // Force RTP over RTSP TCP for the user's FH8852V201 dual-lens streams.
                        player.setMediaSource(
                            RtspMediaSource.Factory().setForceUseRtpTcp(true)
                                .createMediaSource(MediaItem.fromUri(camera.url))
                        )
                        player.prepare()
                        player.playWhenReady = true
                    } catch (_: Exception) {
                        // PlayerView displays idle black; no sensitive URL logging.
                    }
                    onDispose { player.release(); onSurface(null) }
                }
                SideEffect { player.volume = if (muted) 0f else 1f }
                AndroidView(
                    modifier = Modifier.fillMaxSize(),
                    factory = { ctx ->
                        PlayerView(ctx).apply {
                            useController = false
                            resizeMode = AspectRatioFrameLayout.RESIZE_MODE_FIT
                            this.player = player
                            onSurface(videoSurfaceView as? SurfaceView)
                        }
                    },
                    update = { view ->
                        view.player = player
                        onSurface(view.videoSurfaceView as? SurfaceView)
                    }
                )
            }
        } else {
            Text(
                if (camera == null) "Empty tile" else "Preview paused\nDecoder budget: max 4",
                modifier = Modifier.align(Alignment.Center),
                color = Muted,
                style = MaterialTheme.typography.bodySmall
            )
        }
        if (camera != null) {
            Row(
                modifier = Modifier.align(Alignment.BottomStart)
                    .fillMaxWidth().background(Color(0xE80B0D13))
                    .clickable(onClick = onClick)
                    .padding(horizontal = 12.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(camera.name, color = Color.White, modifier = Modifier.weight(1f),
                    maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(if (enabled) "● LIVE" else "PAUSED",
                    color = if (enabled) GardaDarkRed else Color.LightGray,
                    style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun AddCameraDialog(onDismiss: () -> Unit, onSave: (String, String, String, String, String) -> Unit) {
    var name by remember { mutableStateOf("") }
    var url by remember { mutableStateOf("") }
    var onvifEndpoint by remember { mutableStateOf("") }
    var onvifUsername by remember { mutableStateOf("") }
    var onvifPassword by remember { mutableStateOf("") }
    val valid = url.startsWith("rtsp://", ignoreCase = true) && url.length > 10 &&
        !url.contains(" ") && name.isNotBlank()
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(gText("Tambah kamera RTSP", "Add RTSP camera")) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text(gText("Nama kamera", "Camera name")) }, singleLine = true)
                OutlinedTextField(
                    value = url,
                    onValueChange = { url = it },
                    label = { Text("RTSP URL") },
                    placeholder = { Text("rtsp://192.168.1.10:554/stream") },
                    singleLine = false,
                    minLines = 2
                )
                OutlinedTextField(
                    value = onvifEndpoint,
                    onValueChange = { onvifEndpoint = it },
                    label = { Text("ONVIF Device service URL (optional)") },
                    placeholder = { Text("http://192.168.1.10/onvif/device_service") },
                    singleLine = true
                )
                OutlinedTextField(
                    value = onvifUsername,
                    onValueChange = { onvifUsername = it },
                    label = { Text("ONVIF username (optional)") },
                    singleLine = true
                )
                OutlinedTextField(
                    value = onvifPassword,
                    onValueChange = { onvifPassword = it },
                    label = { Text("ONVIF password (optional)") },
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
                    singleLine = true
                )
                Text("ONVIF PTZ needs firmware exposing PTZ and Media services. Credentials are encrypted.", color = Muted, style = MaterialTheme.typography.bodySmall)
            }
        },
        confirmButton = { Button(onClick = { onSave(name.trim(), url.trim(), onvifEndpoint.trim(), onvifUsername.trim(), onvifPassword) }, enabled = valid) { Text(gText("Simpan", "Save")) } },
        dismissButton = { TextButton(onClick = onDismiss) { Text(gText("Batal", "Cancel")) } }
    )
}

/** Native Fold-safe camera login. No secrets leave this dialog except to the camera. */
@Composable
private fun CameraLoginDialog(
    camera: LanCamera,
    remembered: CameraLogin?,
    onDismiss: () -> Unit,
    onConnect: (CameraLogin, Boolean, String) -> Unit,
    onAnonymous: () -> Unit
) {
    var username by remember(camera.ip) { mutableStateOf(remembered?.username.orEmpty()) }
    var password by remember(camera.ip) { mutableStateOf(remembered?.password.orEmpty()) }
    var showPassword by remember(camera.ip) { mutableStateOf(false) }
    var rememberPassword by remember(camera.ip) { mutableStateOf(true) }
    var manualRtsp by remember(camera.ip) { mutableStateOf("") }
    val active = username.isNotBlank() && password.isNotBlank()
    AlertDialog(
        onDismissRequest = onDismiss,
        modifier = Modifier.imePadding(),
        title = { Text(gText("Login kamera ", "Camera login ") + camera.ip, maxLines = 2) },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth().heightIn(max = 385.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(9.dp)
            ) {
                Text(gText("ONVIF ditemukan. Masukkan akun kamera untuk membuka video.",
                        "ONVIF found. Enter the camera's login to view video."),
                    color = Muted, style = MaterialTheme.typography.bodySmall)
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it.take(128) },
                    label = { Text("Username ONVIF / RTSP") },
                    placeholder = { Text("admin") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it.take(256) },
                    label = { Text(gText("Password kamera", "Camera password")) },
                    visualTransformation = if (showPassword)
                        androidx.compose.ui.text.input.VisualTransformation.None
                    else androidx.compose.ui.text.input.PasswordVisualTransformation(),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    trailingIcon = {
                        TextButton(onClick = { showPassword = !showPassword }) {
                            Text(if (showPassword) "Hide" else "Show")
                        }
                    }
                )
                Row(
                    modifier = Modifier.fillMaxWidth().clickable { rememberPassword = !rememberPassword },
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(checked = rememberPassword, onCheckedChange = { rememberPassword = it })
                    Text(gText("Ingat login (terenkripsi Android Keystore)",
                        "Remember login (encrypted with Android Keystore)"),
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.weight(1f))
                }
                OutlinedTextField(
                    value = manualRtsp,
                    onValueChange = { manualRtsp = it.take(300) },
                    label = { Text(gText("URL RTSP (opsional)", "RTSP URL (optional fallback)")) },
                    placeholder = { Text("rtsp://${camera.ip}:8554/live") },
                    singleLine = false,
                    minLines = 1,
                    modifier = Modifier.fillMaxWidth()
                )
                Text("Kosongkan RTSP URL agar GARDA mengambil alamat stream otomatis dari ONVIF. " +
                    "Jika login ditolak, periksa akun ONVIF pada pengaturan kamera.",
                    color = Muted, style = MaterialTheme.typography.labelSmall)
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    onConnect(CameraLogin(username.trim(), password), rememberPassword, manualRtsp.trim())
                },
                enabled = active
            ) { Text(gText("Login & Hubungkan", "Login & Connect")) }
        },
        dismissButton = {
            Row(horizontalArrangement = Arrangement.spacedBy(1.dp)) {
                TextButton(onClick = onAnonymous) { Text(gText("Tanpa login", "Without login")) }
                TextButton(onClick = onDismiss) { Text(gText("Batal", "Cancel")) }
            }
        }
    )
}
