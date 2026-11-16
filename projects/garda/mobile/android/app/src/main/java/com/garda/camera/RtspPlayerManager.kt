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
