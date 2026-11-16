package org.foldview.cctv

import android.content.Intent
import android.net.Uri
import android.os.Handler
import android.os.Looper
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

@Composable
internal fun GardaAboutUpdates() {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("garda_internal_ota", android.content.Context.MODE_PRIVATE) }
    val scope = rememberCoroutineScope()
    val installed = remember { GardaUpdateClient.version(context) }
    var manifestUrl by remember { mutableStateOf(prefs.getString("manifest_url", "").orEmpty()) }
    var loading by remember { mutableStateOf(false) }
    var downloading by remember { mutableStateOf(false) }
    var progress by remember { mutableIntStateOf(0) }
    var status by remember { mutableStateOf("Check for updates against your private GARDA Desktop OTA server.") }
    var candidate by remember { mutableStateOf<GardaRelease?>(null) }
    var prepared by remember { mutableStateOf<File?>(null) }
    val mainHandler = remember { Handler(Looper.getMainLooper()) }

    GardaSectionHeading(gText("Tentang GARDA", "About GARDA"), "INTERNAL")
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = androidx.compose.foundation.shape.RoundedCornerShape(18.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(15.dp),
            verticalArrangement = Arrangement.spacedBy(7.dp)
        ) {
            Text(if (BuildConfig.IS_FOLD_EDITION) "GARDA CCTV FOLD edition" else "GARDA CCTV Standard edition",
                fontWeight = FontWeight.ExtraBold,
                style = MaterialTheme.typography.titleMedium)
            Text(gText("Versi ", "Version ") + installed.first + " · Build " + installed.second,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold)
            Text("Dikembangkan oleh Adithya Pratama",
                style = MaterialTheme.typography.bodyMedium)
            Text("Developer: Adithya Pratama",
                color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("For internal use only",
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold)
            Text("Native Android · Local CCTV / ONVIF / RTSP",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
    GardaSectionHeading(gText("Pembaruan aplikasi", "App updates"), gText("PERLU IZIN", "USER CONFIRMED"))
    OutlinedTextField(
        value = manifestUrl,
        onValueChange = { value ->
            manifestUrl = value.take(280)
            prefs.edit().putString("manifest_url", manifestUrl).apply()
            candidate = null
            prepared = null
        },
        label = { Text(gText("URL server pembaruan GARDA", "GARDA Desktop OTA manifest URL")) },
        placeholder = { Text("http://192.168.1.3:8877/manifest.json") },
        singleLine = false,
        modifier = Modifier.fillMaxWidth(),
        supportingText = {
            Text(gText("Gunakan alamat LAN PC dan server GARDA internal. Tidak perlu rilis publik.",
                "Use your PC's current LAN IP and private GARDA OTA server. No public release required."))
        }
    )
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        GardaMotionButton(
            title = if (loading) gText("Memeriksa…", "Checking…")
                else gText("🔄 Cek pembaruan", "🔄 Check for updates"),
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading && !downloading && manifestUrl.isNotBlank(),
            onClick = {
                loading = true
                status = "Checking internal update server…"
                candidate = null
                prepared = null
                scope.launch {
                    try {
                        val latest = withContext(Dispatchers.IO) {
                            GardaUpdateClient.check(context, manifestUrl.trim())
                        }
                        if (latest.versionCode > installed.second) {
                            candidate = latest
                            status = "Update available: " + latest.versionName +
                                " (build " + latest.versionCode + ")"
                        } else {
                            status = "Up to date. Installed: " + installed.first + "."
                        }
                    } catch (error: Exception) {
                        status = "Update check failed: " +
                            (error.message?.take(120) ?: "Unreachable server")
                    } finally {
                        loading = false
                    }
                }
            }
        )
        GardaMotionButton(
            title = gText("📁 Rilis Google Drive", "📁 Google Drive releases"),
            modifier = Modifier.fillMaxWidth(),
            filled = false,
            onClick = {
                context.startActivity(
                    Intent(Intent.ACTION_VIEW, Uri.parse(GardaUpdateClient.RELEASES_DRIVE_FOLDER))
                )
            }
        )
    }
    if (loading || downloading) {
        if (downloading) {
            LinearProgressIndicator(progress = { progress / 100f }, modifier = Modifier.fillMaxWidth())
            Text("Downloading verified APK… $progress%",
                style = MaterialTheme.typography.labelMedium)
        } else {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
        }
    }
    Text(status, style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant)
    candidate?.let { release ->
        Surface(
            shape = androidx.compose.foundation.shape.RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.primaryContainer
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text("Available: v" + release.versionName,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer)
                if (release.notes.isNotBlank()) {
                    Text(release.notes, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer)
                }
                GardaMotionButton(
                    title = if (downloading) gText("Mengunduh…", "Downloading…")
                    else gText("⬇️ Unduh pembaruan", "⬇️ Download update"),
                    enabled = !downloading && !loading && prepared == null,
                    onClick = {
                        downloading = true
                        progress = 0
                        status = "Downloading update from private server…"
                        scope.launch {
                            try {
                                prepared = withContext(Dispatchers.IO) {
                                    GardaUpdateClient.download(context, release) { percent ->
                                        mainHandler.post { progress = percent }
                                    }
                                }
                                status = "APK checksum, package and signing identity verified. Ready to install."
                            } catch (error: Exception) {
                                prepared = null
                                status = "Update blocked: " +
                                    (error.message?.take(240) ?: "Download or signature failed")
                            } finally {
                                downloading = false
                            }
                        }
                    }
                )
                prepared?.let { apk ->
                    GardaMotionButton(
                        title = gText("📦 Pasang APK terverifikasi", "📦 Install verified APK"),
                        onClick = {
                            try {
                                GardaUpdateClient.requestInstall(context, apk)
                                status = "Follow Android's install prompt. If unknown-source permission was requested, return here and tap Install again."
                            } catch (error: Exception) {
                                status = error.message ?: "Android package installer unavailable"
                            }
                        }
                    )
                }
            }
        }
    }
    Text(
        gText(
            "Keamanan: APK dicek SHA-256, ID paket, nomor versi, dan sertifikat tanda tangan. " +
                "Sertifikat debug berbeda tidak bisa OTA. Android meminta persetujuan pemasangan.",
            "Security: GARDA checks SHA-256, package ID, version and signing certificate. " +
                "Different debug signing keys cannot update in place. Android requests installation approval."
        ),
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}
