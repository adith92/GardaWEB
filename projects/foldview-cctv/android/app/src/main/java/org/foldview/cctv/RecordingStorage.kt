package org.foldview.cctv

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.documentfile.provider.DocumentFile

/**
 * SAF-only storage choice, compatible with USB-OTG HDD/SSD that Android exposes
 * in its system folder picker. A network/SMB provider is supported only when it
 * supplies persistent, writable, seekable content file descriptors.
 * No MANAGE_EXTERNAL_STORAGE, no raw filesystem path or silent cloud uploads.
 */
object RecordingStorage {
    private const val PREFS = "foldview_recording_storage"
    private const val MODE = "destination"
    private const val TREE = "tree_uri"

    private fun prefs(context: Context) =
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun isExternal(context: Context): Boolean = prefs(context).getString(MODE, "phone") == "external"

    fun selectPhone(context: Context) {
        prefs(context).edit().putString(MODE, "phone").apply()
    }

    fun selectFolder(context: Context, uri: Uri) {
        val flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        context.contentResolver.takePersistableUriPermission(uri, flags)
        val root = DocumentFile.fromTreeUri(context, uri)
            ?: throw IllegalStateException("Folder provider unavailable")
        require(root.isDirectory && root.canWrite()) { "Selected folder is not writable" }
        val old = prefs(context).getString(TREE, null)
        prefs(context).edit().putString(TREE, uri.toString()).putString(MODE, "external").apply()
        if (old != null && old != uri.toString()) {
            try { context.contentResolver.releasePersistableUriPermission(Uri.parse(old), flags) }
            catch (_: Exception) { /* previous grant might already be revoked */ }
        }
    }

    fun treeUri(context: Context): Uri? =
        prefs(context).getString(TREE, null)?.let(Uri::parse)

    fun isGranted(context: Context, uri: Uri): Boolean =
        context.contentResolver.persistedUriPermissions.any {
            it.uri == uri && it.isReadPermission && it.isWritePermission
        }

    fun label(context: Context): String {
        if (!isExternal(context)) return "Phone memory · Movies/FOLDVIEW"
        val uri = treeUri(context) ?: return "External folder missing: choose another folder"
        if (!isGranted(context, uri)) return "External access revoked: choose another folder"
        val doc = DocumentFile.fromTreeUri(context, uri)
        return if (doc?.exists() == true) "External / USB folder · " + (doc.name ?: "Selected")
        else "External folder disconnected or unavailable"
    }

    /** Returns a child folder directly under the user-authorized storage tree. */
    fun recordingsFolder(context: Context): DocumentFile {
        val uri = treeUri(context)
            ?: throw IllegalStateException("External recording folder not configured")
        check(isGranted(context, uri)) { "External folder access revoked: select it again" }
        val root = DocumentFile.fromTreeUri(context, uri)
            ?: throw IllegalStateException("External storage is disconnected")
        check(root.exists() && root.isDirectory && root.canWrite()) {
            "External storage is unavailable or read-only"
        }
        val current = root.findFile("FOLDVIEW")
        val folder = if (current != null && current.isDirectory) current
            else root.createDirectory("FOLDVIEW")
        return folder ?: throw IllegalStateException("Cannot create FOLDVIEW folder on external storage")
    }

    fun createExternalMp4(context: Context, fileName: String): Uri {
        val folder = recordingsFolder(context)
        val clip = folder.createFile("video/mp4", fileName)
            ?: throw IllegalStateException("External storage does not support writing video")
        return clip.uri
    }
}
