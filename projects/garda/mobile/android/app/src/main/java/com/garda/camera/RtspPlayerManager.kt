package com.garda.camera

import android.content.Context
import androidx.annotation.OptIn
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.common.PlaybackException
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.rtsp.RtspMediaSource
import androidx.media3.ui.PlayerView

@OptIn(UnstableApi::class)
class RtspPlayerManager(private val context: Context) {
    private var player: ExoPlayer? = null

    fun startStream(playerView: PlayerView, rtspUrl: String, onStateChanged: ((Boolean) -> Unit)? = null) {
        release()
        var created: ExoPlayer? = null
        try {
            val exoPlayer = ExoPlayer.Builder(context).build()
            created = exoPlayer
            exoPlayer.addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_READY) onStateChanged?.invoke(true)
                }
                override fun onPlayerError(error: PlaybackException) {
                    onStateChanged?.invoke(false)
                }
            })
            val mediaItem = MediaItem.fromUri(rtspUrl)

            // Force TCP transport for RTSP to prevent UDP packet loss and screen distortion
            val mediaSource = RtspMediaSource.Factory()
                .setForceUseRtpTcp(true)
                .setTimeoutMs(4000)
                .createMediaSource(mediaItem)

            exoPlayer.setMediaSource(mediaSource)
            playerView.player = exoPlayer
            player = exoPlayer
            exoPlayer.prepare()
            exoPlayer.playWhenReady = true
        } catch (e: Exception) {
            created?.release()
            if (player === created) player = null
            playerView.player = null
            onStateChanged?.invoke(false)
        }
    }

    fun stopStream() {
        release()
    }

    fun release() {
        player?.release()
        player = null
    }
}
