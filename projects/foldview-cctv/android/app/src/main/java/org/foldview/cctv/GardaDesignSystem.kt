package org.foldview.cctv

import android.provider.Settings
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

internal val GardaRed = Color(0xFFC51A36)
internal val GardaDarkRed = Color(0xFFFF556C)
internal val GardaDarkBg = Color(0xFF0B0D13)
internal val GardaLightBg = Color(0xFFF7F8FA)
internal val GardaDarkSurface = Color(0xFF171A22)

internal fun gardaScheme(dark: Boolean): ColorScheme = if (dark) darkColorScheme(
    primary = GardaDarkRed,
    onPrimary = Color(0xFF26030C),
    primaryContainer = Color(0xFF4B1B2A),
    onPrimaryContainer = Color(0xFFFFCFD7),
    background = GardaDarkBg,
    onBackground = Color(0xFFF8F9FB),
    surface = GardaDarkSurface,
    onSurface = Color(0xFFF8F9FC),
    surfaceVariant = Color(0xFF242833),
    onSurfaceVariant = Color(0xFFCDD0DA),
    outline = Color(0xFF737B8C)
) else lightColorScheme(
    primary = GardaRed,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFFFDFE3),
    onPrimaryContainer = Color(0xFF801126),
    background = GardaLightBg,
    onBackground = Color(0xFF191923),
    surface = Color.White,
    onSurface = Color(0xFF191923),
    surfaceVariant = Color(0xFFF2F3F6),
    onSurfaceVariant = Color(0xFF555D6B),
    outline = Color(0xFFD8DBE1)
)

@Composable
internal fun GardaLogo(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.size(38.dp).clip(RoundedCornerShape(11.dp))
            .background(MaterialTheme.colorScheme.primary),
        contentAlignment = Alignment.Center
    ) {
        Text("G", color = MaterialTheme.colorScheme.onPrimary, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
    }
}

/** Compact and wide Fold states use the same branded header. */
@Composable
internal fun GardaHeader(title: String, subtitle: String, cameraCount: Int) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(11.dp)
    ) {
        GardaLogo()
        Column(Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold,
                maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(subtitle, style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1)
        }
        Surface(color = MaterialTheme.colorScheme.primaryContainer, shape = RoundedCornerShape(12.dp)) {
            Text("$cameraCount CAM", modifier = Modifier.padding(horizontal = 9.dp, vertical = 7.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer,
                style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
        }
    }
}

/** Touch press gets immediate native 120 ms feedback. No browser/WebGL in camera tiles. */
@Composable
internal fun GardaMotionButton(
    title: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    filled: Boolean = true,
    enabled: Boolean = true
) {
    val source = remember { MutableInteractionSource() }
    val pressed by source.collectIsPressedAsState()
    val scale by animateFloatAsState(if (pressed) 0.95f else 1f,
        animationSpec = tween(125), label = "button press")
    if (filled) {
        Button(onClick = onClick, enabled = enabled, interactionSource = source,
            modifier = modifier.defaultMinSize(minHeight = 48.dp).graphicsLayer { scaleX = scale; scaleY = scale },
            shape = RoundedCornerShape(13.dp),
            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 10.dp)) {
            Text(title, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    } else {
        OutlinedButton(onClick = onClick, enabled = enabled, interactionSource = source,
            modifier = modifier.defaultMinSize(minHeight = 48.dp).graphicsLayer { scaleX = scale; scaleY = scale },
            shape = RoundedCornerShape(13.dp),
            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 10.dp)) {
            Text(title, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
internal fun GardaMetric(label: String, value: String, modifier: Modifier = Modifier, accent: Boolean = false) {
    Surface(modifier = modifier, color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(16.dp),
        tonalElevation = 2.dp,
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = .32f))) {
        Column(Modifier.padding(horizontal = 12.dp, vertical = 11.dp)) {
            Text(value, color = if (accent) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
            Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.labelSmall, maxLines = 1)
        }
    }
}

/** Render only during a real background operation, never over an active decoder. */
@Composable
internal fun GardaScanSkeleton() {
    val context = LocalContext.current
    val reduceMotion = remember {
        Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
    }
    if (reduceMotion) {
        SkeletonShapes(0.55f)
    } else {
        val pulse = rememberInfiniteTransition(label = "skeleton pulse")
        val alpha by pulse.animateFloat(0.32f, 0.76f,
            animationSpec = infiniteRepeatable(tween(1150), RepeatMode.Reverse),
            label = "skeleton fade")
        SkeletonShapes(alpha)
    }
}

@Composable
private fun SkeletonShapes(alpha: Float) {
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        repeat(3) {
            Surface(color = MaterialTheme.colorScheme.surface, shape = RoundedCornerShape(16.dp)) {
                Row(Modifier.fillMaxWidth().padding(13.dp), verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Box(Modifier.size(width = 76.dp, height = 49.dp)
                        .clip(RoundedCornerShape(11.dp))
                        .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha * .18f)))
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box(Modifier.fillMaxWidth(.72f).height(11.dp).clip(CircleShape)
                            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha * .21f)))
                        Box(Modifier.fillMaxWidth(.48f).height(9.dp).clip(CircleShape)
                            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha * .15f)))
                    }
                }
            }
        }
    }
}

@Composable
internal fun GardaSectionHeading(title: String, detail: String = "") {
    Row(Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 4.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(title, Modifier.weight(1f), style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold)
        if (detail.isNotBlank()) Text(detail, color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.labelSmall)
    }
}
