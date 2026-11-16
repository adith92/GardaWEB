package org.foldview.cctv

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

/** Deterministic layout rules; never infer a fold from a phone's landscape width. */
internal object GardaLayoutRules {
    fun useNavigationRail(foldEdition: Boolean, widthDp: Float): Boolean =
        foldEdition && widthDp >= 680f

    fun compactMetrics(widthDp: Float): Boolean = widthDp < 480f

    fun videoColumns(grid: Int, wide: Boolean): Int = when (grid) {
        1 -> 1
        2 -> if (wide) 2 else 1
        4 -> 2
        9 -> if (wide) 3 else 2
        else -> if (wide) 4 else 2
    }
}

@Composable
internal fun GardaEmptyCameraArtwork(modifier: Modifier = Modifier) {
    val bright = MaterialTheme.colorScheme.primary
    val surface = MaterialTheme.colorScheme.surfaceVariant
    val outline = MaterialTheme.colorScheme.outline
    Box(
        modifier = modifier.size(width = 222.dp, height = 142.dp)
            .background(
                Brush.horizontalGradient(listOf(
                    MaterialTheme.colorScheme.primaryContainer, surface
                )),
                RoundedCornerShape(26.dp)
            ),
        contentAlignment = Alignment.Center
    ) {
        Canvas(Modifier.fillMaxSize()) {
            val x = size.width
            val y = size.height
            // Background orbit rings and connection trails.
            drawCircle(bright.copy(alpha = .13f), radius = x * .43f, center = Offset(x * .51f, y * .56f))
            drawCircle(bright.copy(alpha = .15f), radius = x * .32f, center = Offset(x * .51f, y * .56f))
            drawLine(outline.copy(alpha = .38f),
                Offset(x * .18f, y * .24f), Offset(x * .39f, y * .24f),
                strokeWidth = 2.dp.toPx())
            drawLine(outline.copy(alpha = .38f),
                Offset(x * .69f, y * .78f), Offset(x * .83f, y * .78f),
                strokeWidth = 2.dp.toPx())
            // Camera housing and pivot stand.
            drawRoundRect(
                color = bright,
                topLeft = Offset(x * .25f, y * .28f),
                size = Size(x * .48f, y * .40f),
                cornerRadius = CornerRadius(15.dp.toPx(), 15.dp.toPx())
            )
            drawRoundRect(
                color = Color.White.copy(alpha = .83f),
                topLeft = Offset(x * .29f, y * .32f),
                size = Size(x * .29f, y * .10f),
                cornerRadius = CornerRadius(8.dp.toPx(), 8.dp.toPx())
            )
            drawCircle(
                color = Color(0xFF151922),
                radius = x * .087f,
                center = Offset(x * .58f, y * .50f)
            )
            drawCircle(
                color = Color(0xFFB8D6F2),
                radius = x * .049f,
                center = Offset(x * .58f, y * .50f)
            )
            drawCircle(
                color = Color.White,
                radius = x * .016f,
                center = Offset(x * .56f, y * .48f)
            )
            drawLine(
                color = outline, start = Offset(x * .44f, y * .68f),
                end = Offset(x * .44f, y * .79f), strokeWidth = 7.dp.toPx()
            )
            drawLine(
                color = outline, start = Offset(x * .36f, y * .81f),
                end = Offset(x * .52f, y * .81f), strokeWidth = 6.dp.toPx()
            )
            // Small red online signal indicator.
            drawCircle(color = Color(0xFF27D3A2), radius = x * .019f,
                center = Offset(x * .29f, y * .54f))
        }
    }
}

@Composable
internal fun GardaDeviceThumbnail(modifier: Modifier = Modifier) {
    val primary = MaterialTheme.colorScheme.primary
    val bg = MaterialTheme.colorScheme.primaryContainer
    Box(
        modifier.size(62.dp)
            .background(bg, RoundedCornerShape(16.dp)),
        contentAlignment = Alignment.Center
    ) {
        Canvas(Modifier.fillMaxSize()) {
            val w = size.width
            val h = size.height
            drawRoundRect(
                primary,
                topLeft = Offset(w * .16f, h * .27f),
                size = Size(w * .69f, h * .43f),
                cornerRadius = CornerRadius(9.dp.toPx())
            )
            drawCircle(Color(0xFF111722), w * .11f, Offset(w * .60f, h * .48f))
            drawCircle(Color(0xFFAADDF1), w * .052f, Offset(w * .60f, h * .48f))
            drawCircle(Color.White, w * .014f, Offset(w * .59f, h * .46f))
            drawCircle(Color(0xFF24C08D), w * .028f, Offset(w * .28f, h * .51f))
        }
    }
}

@Composable
internal fun GardaProtocolChip(symbol: String, label: String) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            "$symbol  $label",
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
internal fun GardaDashboardMetrics(count: Int, grid: Int, native: Boolean) {
    BoxWithConstraints(Modifier.fillMaxWidth()) {
        val titleSaved = gText("Stream", "Streams")
        val titleLayout = gText("Tampilan", "Layout")
        val layout = when (grid) {
            1 -> "FOCUS"
            2 -> "DUAL"
            else -> "$grid"
        }
        if (GardaLayoutRules.compactMetrics(maxWidth.value)) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    GardaMetric(titleSaved, count.toString(), Modifier.weight(1f), accent = true)
                    GardaMetric(titleLayout, layout, Modifier.weight(1f))
                }
                Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    GardaProtocolChip("📡", "RTSP")
                    if (native) GardaProtocolChip("🔴", "GARDA")
                    GardaProtocolChip("🔒", gText("Lokal", "Local"))
                }
            }
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                GardaMetric(titleSaved, count.toString(), Modifier.weight(1f), accent = true)
                GardaMetric(titleLayout, layout, Modifier.weight(1f))
                GardaMetric("Protocol", if (native) "GARDA" else "RTSP", Modifier.weight(1f))
            }
        }
    }
}

@Composable
internal fun GardaSavedCameraCard(
    camera: CameraInfo,
    onView: () -> Unit,
    onDelete: () -> Unit
) {
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(18.dp),
        border = androidx.compose.foundation.BorderStroke(
            1.dp, MaterialTheme.colorScheme.outline.copy(alpha = .36f)
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(Modifier.fillMaxWidth().padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                GardaDeviceThumbnail()
                Column(Modifier.weight(1f)) {
                    Text(camera.name, style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold,
                        maxLines = 2, overflow = TextOverflow.Ellipsis)
                    val ip = runCatching { java.net.URI(camera.url).host ?: "" }.getOrDefault("")
                    Text(ip, style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Row(horizontalArrangement = Arrangement.spacedBy(5.dp)) {
                        GardaProtocolChip("📷", "RTSP")
                        if (camera.onvifUrl.isNotBlank()) GardaProtocolChip("🔗", "ONVIF")
                    }
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                GardaMotionButton(
                    "▶ " + gText("Lihat", "View"), onView,
                    modifier = Modifier.weight(1f)
                )
                GardaMotionButton(
                    "🗑 " + gText("Hapus", "Delete"), onDelete,
                    modifier = Modifier.weight(1f), filled = false
                )
            }
        }
    }
}
