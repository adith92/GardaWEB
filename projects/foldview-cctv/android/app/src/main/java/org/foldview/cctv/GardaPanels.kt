package org.foldview.cctv

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

/** Pure Compose local translations, no cloud and no remote language service. */
internal val LocalGardaLanguage = compositionLocalOf { "id" }
@Composable internal fun gText(id: String, en: String): String =
    if (LocalGardaLanguage.current == "en") en else id

@Composable
internal fun GardaFoldSection(
    title: String,
    icon: String,
    expandedByDefault: Boolean = false,
    content: @Composable ColumnScope.() -> Unit
) {
    var open by rememberSaveable(title) { mutableStateOf(expandedByDefault) }
    Surface(
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 2.dp,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth().animateContentSize()
    ) {
        Column(Modifier.fillMaxWidth().padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth().clickable { open = !open }.padding(vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(9.dp)
            ) {
                Text(icon, style = MaterialTheme.typography.titleLarge)
                Text(title, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.titleSmall)
                Text(if (open) "⌃" else "⌄", color = MaterialTheme.colorScheme.primary,
                    style = MaterialTheme.typography.titleLarge)
            }
            AnimatedVisibility(open) {
                Column(Modifier.padding(top = 7.dp),
                    verticalArrangement = Arrangement.spacedBy(9.dp), content = content)
            }
        }
    }
}

@Composable
internal fun GardaCompatibilityPanel() {
    GardaFoldSection(gText("Privasi & kompatibilitas", "Privacy & compatibility"), "🔐") {
        Text(gText(
            "Data kamera dienkripsi Android Keystore AES-GCM. Tanpa iklan dan pelacak.",
            "Camera data uses Android Keystore AES-GCM. No ads or trackers."
        ), style = MaterialTheme.typography.bodySmall)
        Text(gText(
            "Library Android: Kotlin, Jetpack Compose, Material 3, AndroidX Activity/Core, " +
                "Media3 ExoPlayer RTSP, Android Keystore, dan Storage Access Framework.",
            "Android libraries: Kotlin, Jetpack Compose, Material 3, AndroidX Activity/Core, " +
                "Media3 ExoPlayer RTSP, Android Keystore and Storage Access Framework."
        ), style = MaterialTheme.typography.bodySmall)
        Text(gText(
            "Protokol: ONVIF WS-Discovery, SOAP Device/Media/PTZ, Profile G percobaan, RTSP/RTP TCP. " +
                "AI server terpisah: Python, OpenCV, FastALPR, ONNX, FastAPI, SQLite.",
            "Protocols: ONVIF WS-Discovery, SOAP Device/Media/PTZ, experimental Profile G, RTSP/RTP TCP. " +
                "Separate AI server: Python, OpenCV, FastALPR, ONNX, FastAPI, SQLite."
        ), style = MaterialTheme.typography.bodySmall)
        Text(gText(
            "microSD harus didukung ONVIF Profile G atau API vendor. RTSP tidak membuka direktori SD.",
            "microSD needs ONVIF Profile G or vendor APIs; RTSP cannot browse SD folders."
        ), style = MaterialTheme.typography.bodySmall)
        Text(gText(
            "Lisensi library mengikuti lisensi resmi proyeknya. Tidak ada upload video ke cloud.",
            "Third-party libraries keep their own licenses. No video is sent to the cloud."
        ), style = MaterialTheme.typography.bodySmall)
        Text(gText(
            "Gunakan Wi-Fi privat/VPN. ONVIF dan RTSP lama bisa tanpa enkripsi transport.",
            "Use private Wi-Fi/VPN. Legacy ONVIF and RTSP transport can be unencrypted."
        ), color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
internal fun GardaMediaAndCardPanel(
    camera: CameraInfo?,
    report: GardaMediaReport?,
    checking: Boolean,
    message: String,
    onCheck: () -> Unit,
    onSelectStream: (GardaStreamProfile) -> Unit,
    remoteTracks: List<RemoteRecording>,
    remoteBusy: Boolean,
    remoteStatus: String,
    onScanCard: () -> Unit,
    onPlayCard: (RemoteRecording) -> Unit
) {
    if (camera == null) return
    GardaFoldSection(gText("Resolusi & profil video", "Video resolution & profiles"), "🎞️") {
        if (camera.onvifUrl.isBlank()) {
            Text(gText("URL layanan ONVIF belum terdaftar.", "ONVIF service is not configured."),
                style = MaterialTheme.typography.bodySmall)
        } else {
            GardaMotionButton(gText("Cek kemampuan kamera", "Inspect camera"),
                onCheck, filled = false, enabled = !checking)
            if (checking) LinearProgressIndicator(Modifier.fillMaxWidth())
            if (message.isNotBlank()) Text(message, style = MaterialTheme.typography.bodySmall)
            report?.let { media ->
                Text(gText(
                    "Profil live: ${media.streams.size} · Resolusi terlapor: ${media.encoderOptions.size}",
                    "Live profiles: ${media.streams.size} · Reported resolutions: ${media.encoderOptions.size}"
                ), fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.primary)
                if (media.encoderOptions.isNotEmpty()) {
                    Text(media.encoderOptions.joinToString(" • "),
                        style = MaterialTheme.typography.bodySmall)
                }
                media.streams.forEach { p ->
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text("📹 " + p.name, style = MaterialTheme.typography.bodySmall)
                            Text(p.resolution, style = MaterialTheme.typography.labelSmall)
                        }
                        if (p.rtspUrl != null) GardaMotionButton(
                            gText("Pilih", "Use stream"), { onSelectStream(p) }, filled = false
                        )
                    }
                }
                Text(gText(
                    "Memilih profil hanya mengganti playback aplikasi. Pengaturan encoder kamera tidak ditulis.",
                    "Selecting a profile changes app playback only. Camera encoder settings are not written."
                ), style = MaterialTheme.typography.labelSmall)
            }
        }
    }
    GardaFoldSection(gText("Rekaman microSD kamera", "Camera microSD recordings"), "💾") {
        Text(gText(
            "Melalui ONVIF Profile G bila tersedia. Tanpa dukungan itu, isi kartu tidak bisa dibaca langsung.",
            "Via ONVIF Profile G if supported. Without it, the memory card cannot be browsed directly."
        ), style = MaterialTheme.typography.bodySmall)
        GardaMotionButton(gText("Cek rekaman kamera", "Check recordings"),
            onScanCard, filled = false, enabled = camera.onvifUrl.isNotBlank() && !remoteBusy)
        if (remoteBusy) LinearProgressIndicator(Modifier.fillMaxWidth())
        Text(remoteStatus, style = MaterialTheme.typography.bodySmall)
        remoteTracks.take(30).forEach { track ->
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("📼 " + track.label, Modifier.weight(1f),
                    style = MaterialTheme.typography.bodySmall)
                TextButton(onClick = { onPlayCard(track) }) { Text(gText("Putar", "Play")) }
            }
        }
    }
}
