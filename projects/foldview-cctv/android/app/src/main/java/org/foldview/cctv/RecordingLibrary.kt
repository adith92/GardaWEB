package org.foldview.cctv

import android.content.ContentUris
import android.content.Context
import android.net.Uri
import android.provider.MediaStore
import androidx.documentfile.provider.DocumentFile
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import java.text.DateFormat
import java.util.Date

data class LocalClip(val id: Long, val name: String, val uri: Uri, val dateSeconds: Long, val durationMs: Long)

object RecordingLibrary {
    fun list(context: Context): List<LocalClip> {
        val columns = arrayOf(
            MediaStore.Video.Media._ID,
            MediaStore.Video.Media.DISPLAY_NAME,
            MediaStore.Video.Media.DATE_ADDED,
            MediaStore.Video.Media.DURATION,
            MediaStore.Video.Media.RELATIVE_PATH
        )
        val clips = mutableListOf<LocalClip>()
        try {
            context.contentResolver.query(
                MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                columns,
                "${MediaStore.Video.Media.RELATIVE_PATH} LIKE ?",
                arrayOf("Movies/FOLDVIEW/%"),
                "${MediaStore.Video.Media.DATE_ADDED} DESC"
            )?.use { cursor ->
                val idCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media._ID)
                val nameCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME)
                val dateCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_ADDED)
                val durationCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DURATION)
                while (cursor.moveToNext() && clips.size < 250) {
                    val id = cursor.getLong(idCol)
                    clips.add(
                        LocalClip(
                            id = id,
                            name = cursor.getString(nameCol) ?: "Recording",
                            uri = ContentUris.withAppendedId(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, id),
                            dateSeconds = cursor.getLong(dateCol),
                            durationMs = cursor.getLong(durationCol)
                        )
                    )
                }
            }
        } catch (_: Exception) {
            // Only app-owned recordings are accessible without broad media permission.
        }
        // SAF files on user-selected USB HDD/SSD (or compatible DocumentsProvider).
        // The app cannot read arbitrary device storage outside this granted tree.
        val external = try {
            RecordingStorage.recordingsFolder(context).listFiles().asSequence()
                .filter { it.isFile && (it.name?.endsWith(".mp4", true) == true) }
                .take(250)
                .map { item ->
                    val uri = item.uri
                    LocalClip(
                        id = -(uri.toString().hashCode().toLong() and 0x7fffffffL) - 1,
                        name = item.name ?: "External video",
                        uri = uri,
                        dateSeconds = item.lastModified() / 1000,
                        durationMs = 0L
                    )
                }.toList()
        } catch (_: Exception) { emptyList() }
        return (clips + external).distinctBy { it.uri.toString() }
            .sortedByDescending { it.dateSeconds }.take(250)
    }
}

@Composable
fun RecordingsScreen(
    clips: List<LocalClip>,
    recording: Boolean,
    onRefresh: () -> Unit,
    onPlay: (LocalClip) -> Unit,
    storageLabel: String,
    storageExternal: Boolean,
    onUsePhone: () -> Unit,
    onChooseFolder: () -> Unit,
    remote: List<RemoteRecording>,
    remoteMessage: String,
    remoteBusy: Boolean,
    onFindRemote: () -> Unit,
    onOpenRemote: (RemoteRecording) -> Unit
) {
    Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(9.dp)) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Text(gText("📼 Rekaman", "📼 Recordings"), modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.titleMedium)
            TextButton(onClick = onRefresh) { Text(gText("Segarkan", "Refresh")) }
        }
        GardaFoldSection(gText("Penyimpanan lokal", "Local storage"), "📁") {
            Text(gText("Tujuan: ", "Destination: ") + storageLabel,
                color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.bodySmall)
            Row(
                Modifier.fillMaxWidth().horizontalScroll(androidx.compose.foundation.rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                GardaMotionButton(gText("Memori HP", "Phone memory"),
                    onUsePhone, filled = !storageExternal, enabled = !recording)
                GardaMotionButton("USB / HDD", onChooseFolder, filled = false,
                    enabled = !recording)
            }
            Text(gText(
                "Rekaman MP4 layar memerlukan izin Android, maksimal 30 menit. " +
                    "Penyimpanan USB membutuhkan izin akses folder.",
                "Screen-recorded MP4 requires Android approval (30-min max). " +
                    "USB recordings need authorized folder access."
            ), style = MaterialTheme.typography.bodySmall)
        }
        GardaFoldSection(gText("microSD kamera (ONVIF G)", "Camera microSD (ONVIF G)"), "💾") {
            GardaMotionButton(
                if (remoteBusy) gText("Mencari…", "Searching…")
                else gText("Cek rekaman", "Discover recordings"),
                onFindRemote, enabled = !remoteBusy, filled = false
            )
            Text(remoteMessage, style = MaterialTheme.typography.bodySmall)
            remote.take(25).forEach { item ->
                Row(Modifier.fillMaxWidth(),
                    verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                    Text("📹 " + item.label, Modifier.weight(1f),
                        style = MaterialTheme.typography.bodySmall)
                    TextButton(onClick = { onOpenRemote(item) }, enabled = !remoteBusy) {
                        Text(gText("Putar", "Replay"))
                    }
                }
            }
            Text(gText(
                "Jika kamera tidak mendukung Profile G, microSD tidak dapat dibuka lewat ONVIF.",
                "If camera firmware lacks Profile G, ONVIF cannot access its microSD recordings."
            ), style = MaterialTheme.typography.labelSmall)
        }
        if (recording) Text(gText("● Rekaman sedang berjalan", "● Recording in progress"),
            color = MaterialTheme.colorScheme.primary)
        GardaSectionHeading(gText("Video tersimpan", "Saved videos"))
        LazyColumn(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            if (clips.isEmpty()) {
                item { Text(gText("Belum ada video lokal.", "No local videos yet."),
                    color = MaterialTheme.colorScheme.onSurfaceVariant) }
            }
            items(clips, key = { "local:" + it.uri.toString() }) { clip ->
                Card {
                    Row(Modifier.fillMaxWidth().padding(12.dp),
                        verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(clip.name)
                            Text(DateFormat.getDateTimeInstance().format(
                                Date(clip.dateSeconds * 1000)) + " · " +
                                if (clip.durationMs > 0) (clip.durationMs / 1000).toString() + "s"
                                else "USB/Unknown",
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.bodySmall)
                        }
                        TextButton(onClick = { onPlay(clip) }) { Text(gText("Putar", "Play")) }
                    }
                }
            }
        }
    }
}

@Composable
fun LocalClipPlayer(clip: LocalClip, onDismiss: () -> Unit) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val player = remember(clip.uri) {
        ExoPlayer.Builder(context).build().apply {
            setMediaItem(MediaItem.fromUri(clip.uri))
            prepare()
            playWhenReady = true
        }
    }
    DisposableEffect(player) { onDispose { player.release() } }
    Dialog(onDismissRequest = onDismiss) {
        Card {
            Column(Modifier.fillMaxWidth().padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(clip.name, style = MaterialTheme.typography.titleSmall)
                AndroidView(
                    factory = { ctx -> PlayerView(ctx).apply { this.player = player; useController = true } },
                    update = { it.player = player },
                    modifier = Modifier.fillMaxWidth().height(250.dp)
                )
                TextButton(onClick = onDismiss) { Text("Close") }
            }
        }
    }
}
