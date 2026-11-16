package org.foldview.cctv

import android.net.Uri
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.ValueCallback
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import java.net.URI

/** Shared authenticated UI. No JavaScript-to-native bridge and no SSL bypass. */
@Composable
internal fun GardaWorkspaceView(server: String, token: String, close: () -> Unit) {
    val origin = remember(server) { URI(server) }
    var view by remember { mutableStateOf<WebView?>(null) }
    var pendingUpload by remember { mutableStateOf<ValueCallback<Array<Uri>>?>(null) }
    val chooseImage = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        pendingUpload?.onReceiveValue(uri?.let { arrayOf(it) })
        pendingUpload = null
    }
    DisposableEffect(Unit) {
        onDispose {
            pendingUpload?.onReceiveValue(null)
            view?.stopLoading()
            view?.destroy()
        }
    }
    Dialog(onDismissRequest = close, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Surface(Modifier.fillMaxSize()) {
            Column(Modifier.fillMaxSize().safeDrawingPadding()) {
                TextButton(onClick = close) { Text("← GARDA CCTV") }
                AndroidView(modifier = Modifier.fillMaxWidth().weight(1f), factory = { context ->
                    WebView(context).apply {
                        view = this
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        settings.allowFileAccess = false
                        settings.allowContentAccess = true // Android photo picker only; server bounds image size.
                        settings.mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
                        webViewClient = object : WebViewClient() {
                            override fun shouldOverrideUrlLoading(v: WebView, request: WebResourceRequest): Boolean {
                                val u = request.url
                                return u.scheme != origin.scheme || u.host != origin.host || u.port != origin.port
                            }
                        }
                        webChromeClient = object : WebChromeClient() {
                            override fun onShowFileChooser(w: WebView, callback: ValueCallback<Array<Uri>>,
                                parameters: WebChromeClient.FileChooserParams): Boolean {
                                pendingUpload?.onReceiveValue(null)
                                pendingUpload = callback
                                chooseImage.launch("image/*")
                                return true
                            }
                        }
                        val cookies = CookieManager.getInstance()
                        cookies.setAcceptThirdPartyCookies(this, false)
                        val secure = if (origin.scheme == "https") "; Secure" else ""
                        if (token.isBlank()) loadUrl(server.trimEnd('/') + "/workspace")
                        else cookies.setCookie(server, "garda_session=$token; Path=/; HttpOnly; SameSite=Strict$secure") {
                            post { loadUrl(server.trimEnd('/') + "/workspace") }
                        }
                    }
                })
            }
        }
    }
}
