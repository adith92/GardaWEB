package org.foldview.cctv

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

/** Read-only API and local credential persistence, shared by both Android flavors. */
@Composable
internal fun GardaAiEventsPanel() {
    val context = LocalContext.current
    val client = remember { GardaAiClient(context) }
    val coroutine = rememberCoroutineScope()
    var url by remember { mutableStateOf(client.savedUrl()) }
    var secret by remember { mutableStateOf(client.savedKey()) }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var showWorkspace by remember { mutableStateOf(false) }
    var labMode by remember { mutableStateOf(false) }
    var requiresLogin by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("") }
    var stats by remember { mutableStateOf<JSONObject?>(null) }
    var events by remember { mutableStateOf<List<GardaAiEvent>>(emptyList()) }
    var kind by remember { mutableStateOf("") }
    var chosen by remember { mutableStateOf<GardaAiEvent?>(null) }
    var evidence by remember { mutableStateOf<Bitmap?>(null) }
    var evidenceLoading by remember { mutableStateOf(false) }

    fun refresh(filter: String) {
        if (busy) return
        busy = true
        coroutine.launch {
            val result = withContext(Dispatchers.IO) {
                runCatching { client.stats() to client.events(filter) }
            }
            result.onSuccess {
                stats = it.first
                events = it.second
                status = "✅ " + it.second.size + " " +
                    if (filter.isBlank()) "events" else filter
            }.onFailure { error ->
                status = "⚠ " + (error.message?.take(125) ?: "Could not reach GARDA AI")
            }
            busy = false
        }
    }

    GardaFoldSection(gText("GARDA AI • Plat & Wajah", "GARDA AI • Plates & Faces"), "🧠") {
        Text(
            gText("Backend Windows/Linux, koneksi aman HTTPS. AI tidak dijalankan di HP.",
                "Windows/Linux backend over HTTPS. No AI inference on the phone."),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        OutlinedTextField(
            value = url, onValueChange = { url = it.take(250) },
            label = { Text(gText("URL server HTTPS", "HTTPS server URL")) },
            singleLine = true, modifier = Modifier.fillMaxWidth()
        )
        if (requiresLogin) {
        OutlinedTextField(
            value = username, onValueChange = { username = it.take(80) },
            label = { Text(gText("Nama pengguna", "Username")) },
            singleLine = true, modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = password, onValueChange = { password = it.take(256) },
            label = { Text(gText("Kata sandi", "Password")) },
            visualTransformation = PasswordVisualTransformation(),
            singleLine = true, modifier = Modifier.fillMaxWidth()
        )
        GardaMotionButton(gText("Masuk ke server", "Sign in to server"), {
            busy = true
            coroutine.launch {
                val result = withContext(Dispatchers.IO) { runCatching { client.login(url, username, password) } }
                password = ""
                result.onSuccess { secret = client.savedKey(); status = "Session connected" }
                    .onFailure { status = it.message?.take(125) ?: "Login failed" }
                busy = false
            }
        }, enabled = !busy && username.isNotBlank() && password.isNotBlank())
        }
        GardaMotionButton(gText("Workspace · 8 kamera & administrasi", "Workspace · 8 cameras & administration"), {
            showWorkspace = true
        }, enabled = client.savedUrl().isNotBlank() && (labMode || secret.isNotBlank()), filled = false)
        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            GardaMotionButton(gText("Hubungkan server", "Connect server"), {
                busy = true
                coroutine.launch {
                    val result = withContext(Dispatchers.IO) { runCatching { client.connect(url) } }
                    result.onSuccess { localAdmin ->
                        labMode = localAdmin
                        secret = client.savedKey()
                        requiresLogin = false
                        status = if (localAdmin) "Admin lokal · Semua akses" else "Session connected"
                    }.onFailure {
                        requiresLogin = it.message?.contains("named login") == true
                        status = it.message?.take(125) ?: "Server unavailable"
                    }
                    busy = false
                }
            }, enabled = !busy)
            GardaMotionButton(gText("Hapus koneksi", "Forget"), {
                client.forget()
                url = ""; secret = ""; events = emptyList(); stats = null
                status = "Local GARDA AI server connection cleared"
            }, filled = false)
            GardaMotionButton(gText("Segarkan", "Refresh"), { refresh(kind) },
                filled = false, enabled = !busy)
        }
        Text(status, style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())

        stats?.let { current ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("plate" to "🚗", "face" to "👤", "motion" to "🎞️").forEach { (name, icon) ->
                    Surface(color = MaterialTheme.colorScheme.surfaceVariant,
                        shape = RoundedCornerShape(12.dp)) {
                        Text("$icon ${current.optInt(name, 0)}",
                            modifier = Modifier.padding(horizontal = 11.dp, vertical = 9.dp))
                    }
                }
            }
        }
        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            listOf("" to "Semua / All", "plate" to "🚗 Plat",
                "face" to "👤 Wajah", "motion" to "🎞 Gerakan").forEach { (id, title) ->
                FilterChip(selected = kind == id,
                    onClick = { kind = id; refresh(id) }, label = { Text(title) })
            }
        }
        events.take(12).forEach { event ->
            Surface(color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(13.dp), tonalElevation = 2.dp,
                modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(when (event.kind) {
                            "plate" -> "🚗 " + event.plate.ifBlank { "Unreadable plate" }
                            "face" -> "👤 " + event.faceLabel.ifBlank { "Unknown face" }
                            else -> "🎞️ Motion"
                        }, modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.titleSmall)
                        TextButton(onClick = {
                            chosen = event
                            evidence = null
                            evidenceLoading = true
                            coroutine.launch {
                                val result = withContext(Dispatchers.IO) {
                                    runCatching {
                                        val id = client.photoIds(event.id).firstOrNull()
                                        id?.let { photoId ->
                                            val bytes = client.photo(event.id, photoId)
                                            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                                        }
                                    }
                                }
                                result.onSuccess { evidence = it }.onFailure {
                                    status = "⚠ " + (it.message ?: "Evidence unavailable")
                                }
                                evidenceLoading = false
                            }
                        }) { Text(gText("Bukti", "Evidence")) }
                    }
                    Text("${event.camera} • ${event.whenUtc}",
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.labelSmall)
                }
            }
        }
        if (events.isEmpty() && !busy) {
            Text(gText("Belum ada event dari server yang terhubung.",
                "No events loaded from a connected server."),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall)
        }
    }
    if (chosen != null) {
        AlertDialog(
            onDismissRequest = { chosen = null; evidence = null },
            title = { Text(gText("Bukti kejadian", "Event evidence")) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("${chosen?.kind} • ${chosen?.camera}",
                        style = MaterialTheme.typography.bodySmall)
                    if (evidenceLoading) LinearProgressIndicator(Modifier.fillMaxWidth())
                    val currentEvidence = evidence
                    if (currentEvidence != null) {
                        Image(currentEvidence.asImageBitmap(),
                            contentDescription = "GARDA event evidence",
                            modifier = Modifier.fillMaxWidth().heightIn(max = 300.dp))
                    } else if (!evidenceLoading) {
                        Text(gText("Belum ada gambar atau tidak dapat diakses.",
                            "No image available or access failed."),
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { chosen = null; evidence = null }) {
                    Text(gText("Tutup", "Close"))
                }
            }
        )
    }
    if (showWorkspace) {
        GardaWorkspaceView(client.savedUrl(), client.savedKey()) { showWorkspace = false }
    }
}
