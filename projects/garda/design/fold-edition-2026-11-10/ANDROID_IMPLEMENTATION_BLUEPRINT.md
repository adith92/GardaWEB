# GARDA CCTV FOLD edition — Native Android implementation blueprint

**Stage:** Design-only. The 10 interactive concepts and their screenshots are mockups, not compiled APKs. Camera feed illustrations and simulated device state must not be presented as real camera telemetry.

**Requested identity:** `GARDA CCTV FOLD edition` (launcher label, display title and supporting brand). Preserve Android application ID `org.foldview.cctv` for an in-place migration path; do not silently replace `com.garda.camera` or uninstall either app.

## Architecture decision

Use **Kotlin + Jetpack Compose** with Material 3 and responsive layouts. Use `ViewModel`, `StateFlow`, Kotlin coroutines, Media3 RTSP and the existing encrypted camera vault. `BoxWithConstraints` or a window-size-class adapter can switch **fold cover** bottom navigation to **fold-open** side rail with a responsive camera grid.

**Three.js is NOT a Kotlin-native Android UI engine.** It is used only as an optional 3D accent in this HTML prototype (concept 10); it is loaded from a CDN in the sandboxed browser preview with a CSS fallback. For the shipped app, replace this with native Compose Canvas / graphicsLayer / small OpenGL scene if genuinely needed. Never use an active JS/WebGL renderer per CCTV tile. The live video pipeline is the priority.

## Fix bottom Android 3-button overlap

In current user-reported behavior, lower controls collide with the system Back, Home and Recents keys. Use the actual Android insets, not a magic `bottom=24.dp` offset. A safe baseline:

```kotlin
@Composable
fun GardaScreen() {
    Scaffold(
        contentWindowInsets = WindowInsets.safeDrawing,
        bottomBar = {
            NavigationBar { /* responsive and reachable navigation items */ }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .consumeWindowInsets(innerPadding)
        ) {
            CameraControls()
            // Ensure grids/panels scroll; never place controls under the system nav bar.
        }
    }
}
```

If using an edge-to-edge custom layout instead of `Scaffold`, use `Modifier.safeDrawingPadding()` around interactive controls. Avoid applying `navigationBarsPadding()` twice to an existing `NavigationBar` that already handles navigation insets. Test Android's **3-button**, gesture, portrait, and landscape modes, especially when the Fold cover is active.

Official Android documentation (retrieved through Context7):
- [Insets UI](https://developer.android.com/develop/ui/compose/system/insets-ui)
- [Edge-to-edge setup](https://developer.android.com/develop/ui/compose/system/setup-e2e)
- [Compose adaptive layout constraints](https://developer.android.com/develop/ui/compose/layouts/basics)

## Update UI before a slow network operation

Network scans, ONVIF SOAP queries, RTSP probe or recording-library loading must NEVER run on the main thread. Update loading state immediately and execute slow work on `Dispatchers.IO`:

```kotlin
data class CamerasUiState(
    val loading: Boolean = false,
    val devices: List<CameraCard> = emptyList(),
    val error: String? = null
)

class CamerasViewModel(private val discovery: CameraDiscovery) : ViewModel() {
    private val _state = MutableStateFlow(CamerasUiState())
    val state: StateFlow<CamerasUiState> = _state.asStateFlow()

    fun scan() {
        _state.update { it.copy(loading = true, error = null) } // immediate UI feedback
        viewModelScope.launch {
            runCatching { withContext(Dispatchers.IO) { discovery.scanLan() } }
                .onSuccess { devices ->
                    _state.update { it.copy(loading = false, devices = devices) }
                }
                .onFailure { e ->
                    _state.update { it.copy(loading = false, error = e.message) }
                }
        }
    }
}
```

In production inject the discovery implementation and `viewModelScope`; treat `CameraCard` and `CameraDiscovery` as interface types to implement, not currently existing classes. Persist stable camera IDs and credentials in the existing Keystore-backed vault. Do not scan every port or address automatically on app launch.

Skeleton cards: show two or four nonblocking placeholders while the scan starts; stop immediately when data or errors arrive. Prefer lightweight `rememberInfiniteTransition` alpha/translation shimmer on a handful of placeholders; never animate continuously behind four decoded 1080p streams. Respect reduced-motion preferences and thermal limits.

## Interaction motion spec

| Interaction | Duration | Native technique |
|---|---:|---|
| Primary button press | 100–150 ms | `animateFloatAsState` scale 1 → .95 → 1 |
| Side/bottom nav change | 180–240 ms | `AnimatedContent` / transition |
| Camera tile hover/focus | 120–180 ms | Border and elevation transition |
| PTZ press-and-release | Immediate | Visual pressed state, explicit Stop on release |
| Skeleton shimmer | ~1100–1400 ms | Small animated gradient/alpha |
| Loading/error state | < 1 frame UI change | `StateFlow` snapshot before IO |
| 3D ornamental effect | Optional / battery-aware | Native Canvas; suspend when not visible |

Do not animate large video surfaces during decoder startup, do not execute endless radar/3D loops while offscreen, and do not use animations as a substitute for confirming real hardware actions.

## Recommended concept combinations

**Primary choice: concept 08 Dual Vision + concept 01 Command Deck.** On the Fold cover, show two lenses as a vertical stack or two columns when minimum tile sizes permit; on the unfolded Fold, show both feeds side-by-side and a collapsible PTZ/lighting rail. Concepts 02 and 05 can inform multi-camera and alert navigation. Reserve concept 10 as an optional visual skin.

## Security and accuracy gates

- The physical FH8852V201 daemon, ONVIF SOAP/PTZ, lighting GPIO and reboot persistence were previously user-reported; this design artifact does not test the camera.
- Control API `http://<private-ip>:8899/api/ptz` and `/api/led` is plain HTTP and may be unauthenticated. No port forwarding. Prefer VLAN/VPN and proper authentication before general release.
- PTZ must support stop on release, limit movement duration, and prevent automatic uncontrolled motion.
- Device scanning must remain explicitly user-triggered and bounded to the authorized active LAN.
- APK v0.7.0 CI debug-signing may not permit an in-place upgrade due to changing debug certificate. Preserve camera profiles before migration.

## Implementation milestones after selecting a design

1. Apply new display name and adaptive Compose shell with edge-to-edge insets.
2. Replace linear layout with Fold-open/cover layouts and both camera streams.
3. Refactor scan to `ViewModel` `StateFlow` + `Dispatchers.IO`, render skeleton/error/empty/loaded states.
4. Implement native touch motion and PTZ stop-on-release, differentiate command acknowledgement from motion confirmation.
5. Build a signed APK, verify signature and test on Fold7 with 3-button and gesture navigation; then upload to GitHub/Drive only after verification.

## Sources consulted with Context7

- Jetpack Compose: `/websites/developer_android_develop_ui_compose`
- Three.js: `/mrdoob/three.js` (r180 CDN for prototype)
- [Three.js setAnimationLoop](https://github.com/mrdoob/three.js/blob/dev/manual/pages/creating-a-scene.html)
- [Three.js resource cleanup](https://github.com/mrdoob/three.js/blob/dev/manual/examples/cleanup-simple.html)
