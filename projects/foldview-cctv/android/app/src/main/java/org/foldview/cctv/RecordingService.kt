package org.foldview.cctv

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.ContentValues
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Point
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.MediaRecorder
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.provider.DocumentsContract
import android.system.Os
import android.system.OsConstants
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.provider.MediaStore
import android.util.DisplayMetrics
import kotlin.math.max
import kotlin.math.min

/**
 * On-device, USER-APPROVED *screen* video capture to Movies/FOLDVIEW.
 * Not a direct RTSP bitstream recorder, camera SD recorder, or audio recorder.
 * Requires a new system permission prompt for every capture session.
 */
class RecordingService : Service() {
    companion object {
        const val START = "org.foldview.cctv.REC_START"
        const val STOP = "org.foldview.cctv.REC_STOP"
        const val RESULT = "result"
        const val DATA = "data"
        private const val CHANNEL = "foldview_recording"
        private const val NOTIFICATION_ID = 4172
    }

    private var projection: MediaProjection? = null
    private var recorder: MediaRecorder? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var output: Uri? = null
    private var externalOutput = false
    private var descriptor: android.os.ParcelFileDescriptor? = null
    private var sessionStarted = false
    private var finishing = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        val channel = NotificationChannel(
            CHANNEL, "FOLDVIEW local recording", NotificationManager.IMPORTANCE_LOW
        )
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == STOP) {
            finishRecording()
            return START_NOT_STICKY
        }
        if (intent?.action != START || finishing || sessionStarted) return START_NOT_STICKY
        try {
            val data = if (Build.VERSION.SDK_INT >= 33) {
                intent.getParcelableExtra(DATA, Intent::class.java)
            } else {
                @Suppress("DEPRECATION")
                intent.getParcelableExtra<Intent>(DATA)
            } ?: throw IllegalArgumentException("Screen capture consent missing")
            val code = intent.getIntExtra(RESULT, 0)
            if (code != android.app.Activity.RESULT_OK) {
                throw IllegalArgumentException("Screen capture consent denied")
            }
            val stopIntent = Intent(this, RecordingService::class.java).setAction(STOP)
            val stopAction = PendingIntent.getService(
                this, 7, stopIntent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            )
            val notification = Notification.Builder(this, CHANNEL)
                .setContentTitle("FOLDVIEW recording · " + if (RecordingStorage.isExternal(this)) "external storage" else "phone memory")
                .setContentText("Capturing visible screen, video only. Stop to finish MP4.")
                .setSmallIcon(android.R.drawable.ic_menu_camera)
                .setOngoing(true)
                .addAction(android.R.drawable.ic_media_pause, "Stop", stopAction)
                .build()
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            )
            startCapture(code, data)
            sessionStarted = true
        } catch (e: Exception) {
            val issue = (e.message ?: "Recording could not start").take(150)
            getSharedPreferences("foldview_rec_state", MODE_PRIVATE).edit()
                .putString("last_error", issue).apply()
            try {
                getSystemService(NotificationManager::class.java).notify(
                    NOTIFICATION_ID + 1,
                    Notification.Builder(this, CHANNEL)
                        .setContentTitle("FOLDVIEW recording failed")
                        .setContentText(issue)
                        .setSmallIcon(android.R.drawable.stat_notify_error)
                        .build()
                )
            } catch (_: Exception) {}
            finishRecording()
        }
        return START_NOT_STICKY
    }

    private fun startCapture(code: Int, consent: Intent) {
        val manager = getSystemService(MediaProjectionManager::class.java)
        val activeProjection = manager.getMediaProjection(code, consent)
            ?: throw IllegalStateException("Android denied MediaProjection session")
        projection = activeProjection
        activeProjection.registerCallback(object : MediaProjection.Callback() {
            override fun onStop() {
                finishRecording()
            }
        }, Handler(Looper.getMainLooper()))

        // Preserve aspect ratio on phone cover screen and unfolded inner screen.
        val dm: DisplayMetrics = resources.displayMetrics
        val inputW = max(dm.widthPixels, 320)
        val inputH = max(dm.heightPixels, 320)
        val factor = min(1.0, 1280.0 / max(inputW, inputH).toDouble())
        val width = max(320, (inputW * factor).toInt() / 16 * 16)
        val height = max(320, (inputH * factor).toInt() / 16 * 16)
        // SAF output writes directly to a user-selected USB HDD/SSD, when its
        // provider exposes a real seekable FD. No intermediate phone copy.
        // If the USB drive is removed, fail visibly rather than silently
        // redirecting a privacy-sensitive camera recording.
        val name = "FOLDVIEW_" + System.currentTimeMillis() + ".mp4"
        externalOutput = RecordingStorage.isExternal(this)
        if (externalOutput) {
            output = RecordingStorage.createExternalMp4(this, name)
            descriptor = contentResolver.openFileDescriptor(output!!, "rw")
                ?: throw IllegalStateException("External storage cannot open MP4 for writing")
            try {
                Os.lseek(descriptor!!.fileDescriptor, 0, OsConstants.SEEK_CUR)
            } catch (_: Exception) {
                throw IllegalStateException("External storage provider is not seekable; select a USB/phone folder")
            }
        } else {
            val values = ContentValues().apply {
                put(MediaStore.Video.Media.DISPLAY_NAME, name)
                put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
                put(MediaStore.Video.Media.RELATIVE_PATH, "Movies/FOLDVIEW/")
                put(MediaStore.Video.Media.IS_PENDING, 1)
            }
            output = contentResolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values)
                ?: throw IllegalStateException("Unable to create local recording")
            descriptor = contentResolver.openFileDescriptor(output!!, "rw")
                ?: throw IllegalStateException("Unable to open local recording")
        }
        val r = @Suppress("DEPRECATION") MediaRecorder()
        recorder = r
        r.setVideoSource(MediaRecorder.VideoSource.SURFACE)
        r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
        r.setVideoEncoder(MediaRecorder.VideoEncoder.H264)
        r.setVideoEncodingBitRate(4_000_000)
        r.setVideoFrameRate(24)
        r.setVideoSize(width, height)
        // Limit a single user-approved screen capture; this is not 24/7 NVR recording.
        r.setMaxDuration(30 * 60 * 1000)
        r.setOnInfoListener { _, what, _ ->
            if (what == MediaRecorder.MEDIA_RECORDER_INFO_MAX_DURATION_REACHED) finishRecording()
        }
        r.setOutputFile(descriptor!!.fileDescriptor)
        r.prepare()
        virtualDisplay = activeProjection.createVirtualDisplay(
            "FOLDVIEW-local-MP4",
            width,
            height,
            dm.densityDpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            r.surface,
            null,
            Handler(Looper.getMainLooper())
        )
        r.start()
    }

    private fun finishRecording() {
        if (finishing) return
        finishing = true
        var validFile = false
        try {
            if (sessionStarted) {
                try {
                    recorder?.stop()
                    validFile = true
                } catch (_: Exception) {
                    validFile = false
                }
            }
        } finally {
            try { recorder?.reset() } catch (_: Exception) {}
            try { recorder?.release() } catch (_: Exception) {}
            recorder = null
            try { virtualDisplay?.release() } catch (_: Exception) {}
            virtualDisplay = null
            try { projection?.stop() } catch (_: Exception) {}
            projection = null
            try { descriptor?.close() } catch (_: Exception) {}
            descriptor = null
            output?.let { uri ->
                try {
                    if (externalOutput) {
                        if (!validFile) DocumentsContract.deleteDocument(contentResolver, uri)
                    } else if (validFile) {
                        contentResolver.update(uri, ContentValues().apply {
                            put(MediaStore.Video.Media.IS_PENDING, 0)
                        }, null, null)
                    } else {
                        contentResolver.delete(uri, null, null)
                    }
                } catch (_: Exception) {
                    // USB removal can make deletion impossible; avoid crashing cleanup.
                }
            }
            output = null
            externalOutput = false
            sessionStarted = false
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }

    override fun onDestroy() {
        if (!finishing) finishRecording()
        super.onDestroy()
    }
}
