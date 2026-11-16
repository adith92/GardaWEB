package com.garda.camera

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class CameraViewModel : ViewModel() {
    private val apiClient = GardaApiClient()
    private val nativePtz = GardaNativePtz()
    private val discovery = OnvifDiscovery()

    private val _telemetry = MutableLiveData<TelemetryResponse?>()
    val telemetry: LiveData<TelemetryResponse?> = _telemetry

    private val _isOnline = MutableLiveData<Boolean>(false)
    val isOnline: LiveData<Boolean> = _isOnline

    private val _logMessage = MutableLiveData<String>()
    val logMessage: LiveData<String> = _logMessage

    private val _whiteLightOn = MutableLiveData<Boolean>(false)
    val whiteLightOn: LiveData<Boolean> = _whiteLightOn

    private val _irNightOn = MutableLiveData<Boolean>(false)
    val irNightOn: LiveData<Boolean> = _irNightOn

    private val _trackingOn = MutableLiveData<Boolean>(false)
    val trackingOn: LiveData<Boolean> = _trackingOn

    private val _cruiseOn = MutableLiveData<Boolean>(false)
    val cruiseOn: LiveData<Boolean> = _cruiseOn

    private var pollingJob: Job? = null

    fun startTelemetryPolling(ip: String) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            while (isActive) {
                val res = apiClient.getTelemetry(ip)
                if (res.isSuccess) {
                    val data = res.getOrNull()
                    _telemetry.postValue(data)
                    _isOnline.postValue(data?.status == "online")
                } else {
                    _isOnline.postValue(false)
                }
                delay(3000)
            }
        }
    }

    fun stopTelemetryPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    fun scanLan(onResult: (List<String>) -> Unit) {
        viewModelScope.launch {
            _logMessage.postValue("Scanning WS-Discovery (UDP 3702)...")
            val ips = discovery.discoverCameras()
            onResult(ips)
            if (ips.isNotEmpty()) {
                _logMessage.postValue("Ditemukan kamera: ${ips.joinToString(", ")}")
            } else {
                _logMessage.postValue("Scan selesai. Tidak ditemukan kamera baru.")
            }
        }
    }

    fun movePtz(ip: String, direction: String, step: Int) {
        viewModelScope.launch {
            // First try REST API
            val res = apiClient.sendPtz(ip, direction)
            if (res.isSuccess) {
                _logMessage.postValue("PTZ $direction: OK (REST)")
            } else {
                // Fallback to Native TCP Port 7777
                val opcode = when (direction) {
                    "left" -> GardaNativePtz.CMD_LEFT
                    "right" -> GardaNativePtz.CMD_RIGHT
                    "up" -> GardaNativePtz.CMD_UP
                    "down" -> GardaNativePtz.CMD_DOWN
                    else -> GardaNativePtz.CMD_RESET
                }
                val natRes = nativePtz.sendCommand(ip, opcode, step)
                if (natRes.isSuccess) {
                    _logMessage.postValue("PTZ $direction: OK (Native 7777)")
                } else {
                    _logMessage.postValue("PTZ $direction gagal: ${res.exceptionOrNull()?.message}")
                }
            }
        }
    }

    fun centerPtz(ip: String) {
        viewModelScope.launch {
            val res = apiClient.sendPtz(ip, "center")
            _logMessage.postValue("PTZ Center (x=515, y=70): ${if (res.isSuccess) "OK" else "Error"}")
        }
    }

    fun calibratePtz(ip: String) {
        viewModelScope.launch {
            val res = nativePtz.sendCommand(ip, GardaNativePtz.CMD_RESET, 0)
            _logMessage.postValue("Kalibrasi Motor PTZ: ${if (res.isSuccess) "OK" else "Error"}")
        }
    }

    fun toggleWhiteLight(ip: String) {
        val newState = !(_whiteLightOn.value ?: false)
        viewModelScope.launch {
            val mode = if (newState) "white_on" else "white_off"
            val res = apiClient.sendLed(ip, mode)
            if (res.isSuccess) {
                _whiteLightOn.postValue(newState)
                _logMessage.postValue("Spotlight: ${if (newState) "ON" else "OFF"}")
            }
        }
    }

    fun toggleNightIr(ip: String) {
        val newState = !(_irNightOn.value ?: false)
        viewModelScope.launch {
            val mode = if (newState) "ir_on" else "ir_off"
            val res = apiClient.sendLed(ip, mode)
            if (res.isSuccess) {
                _irNightOn.postValue(newState)
                _logMessage.postValue("Night IR (GPIO 44): ${if (newState) "ON" else "OFF"}")
            }
        }
    }

    fun setIrCutFilter(ip: String, nightMode: Boolean) {
        viewModelScope.launch {
            val mode = if (nightMode) "ircut_night" else "ircut_day"
            val res = apiClient.sendLed(ip, mode)
            _logMessage.postValue("IR-Cut Filter: ${if (nightMode) "Night Filter" else "Day Filter"} (${if (res.isSuccess) "OK" else "Error"})")
        }
    }

    fun toggleTracking(ip: String) {
        val newState = !(_trackingOn.value ?: false)
        viewModelScope.launch {
            val opcode = if (newState) GardaNativePtz.CMD_TRACKING else GardaNativePtz.CMD_MANUAL
            val res = nativePtz.sendCommand(ip, opcode, 0)
            if (res.isSuccess) {
                _trackingOn.postValue(newState)
                _logMessage.postValue("AI Human Tracking: ${if (newState) "AKTIF" else "NONAKTIF"}")
            }
        }
    }

    fun toggleCruise(ip: String) {
        val newState = !(_cruiseOn.value ?: false)
        viewModelScope.launch {
            val opcode = if (newState) GardaNativePtz.CMD_CRUISE else GardaNativePtz.CMD_MANUAL
            val res = nativePtz.sendCommand(ip, opcode, 0)
            if (res.isSuccess) {
                _cruiseOn.postValue(newState)
                _logMessage.postValue("Patroli 360°: ${if (newState) "AKTIF" else "BERHENTI"}")
            }
        }
    }
}
