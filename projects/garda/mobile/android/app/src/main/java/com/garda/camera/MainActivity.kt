package com.garda.camera

import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.garda.camera.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: CameraViewModel by viewModels()

    private lateinit var playerLens1: RtspPlayerManager
    private lateinit var playerLens2: RtspPlayerManager

    private var isStreaming = false
    private var currentStep = 30

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        playerLens1 = RtspPlayerManager(this)
        playerLens2 = RtspPlayerManager(this)

        setupViewModeSpinner()
        setupListeners()
        setupObservers()

        // Start checking telemetry immediately
        val initialIp = binding.etCameraIp.text.toString().trim()
        if (initialIp.isNotEmpty()) {
            viewModel.startTelemetryPolling(initialIp)
        }
    }

    private fun setupViewModeSpinner() {
        val modes = arrayOf(
            getString(R.string.view_dual_vertical),
            getString(R.string.view_dual_horizontal),
            getString(R.string.view_lens1),
            getString(R.string.view_lens2)
        )
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, modes)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spnViewMode.adapter = adapter

        binding.spnViewMode.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                applyViewMode(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun applyViewMode(modeIndex: Int) {
        when (modeIndex) {
            0 -> { // Dual Vertical (Top - Bottom)
                binding.videoContainer.orientation = LinearLayout.VERTICAL
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
            1 -> { // Dual Horizontal (Left - Right)
                binding.videoContainer.orientation = LinearLayout.HORIZONTAL
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
            2 -> { // Lens 1 Only
                binding.lens1Wrapper.visibility = View.VISIBLE
                binding.lens2Wrapper.visibility = View.GONE
            }
            3 -> { // Lens 2 Only
                binding.lens1Wrapper.visibility = View.GONE
                binding.lens2Wrapper.visibility = View.VISIBLE
            }
        }
    }

    private fun setupListeners() {
        binding.btnConnect.setOnClickListener {
            if (!isStreaming) {
                startCameraStream()
            } else {
                stopCameraStream()
            }
        }

        binding.btnScanLan.setOnClickListener {
            viewModel.scanLan { ips ->
                if (ips.isNotEmpty()) {
                    binding.etCameraIp.setText(ips[0])
                    viewModel.startTelemetryPolling(ips[0])
                    Toast.makeText(this, "Kamera ditemukan: ${ips[0]}", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Tidak ada kamera ditemukan di subnet ini", Toast.LENGTH_SHORT).show()
                }
            }
        }

        binding.sliderStep.addOnChangeListener { _, value, _ ->
            currentStep = value.toInt()
            binding.tvStepLabel.text = "Step: $currentStep"
        }

        // PTZ D-Pad Listeners
        val ipProvider = { binding.etCameraIp.text.toString().trim() }
        binding.btnPtzUp.setOnClickListener { viewModel.movePtz(ipProvider(), "up", currentStep) }
        binding.btnPtzDown.setOnClickListener { viewModel.movePtz(ipProvider(), "down", currentStep) }
        binding.btnPtzLeft.setOnClickListener { viewModel.movePtz(ipProvider(), "left", currentStep) }
        binding.btnPtzRight.setOnClickListener { viewModel.movePtz(ipProvider(), "right", currentStep) }

        binding.btnPtzUpLeft.setOnClickListener {
            viewModel.movePtz(ipProvider(), "up", currentStep)
            viewModel.movePtz(ipProvider(), "left", currentStep)
        }
        binding.btnPtzUpRight.setOnClickListener {
            viewModel.movePtz(ipProvider(), "up", currentStep)
            viewModel.movePtz(ipProvider(), "right", currentStep)
        }
        binding.btnPtzDownLeft.setOnClickListener {
            viewModel.movePtz(ipProvider(), "down", currentStep)
            viewModel.movePtz(ipProvider(), "left", currentStep)
        }
        binding.btnPtzDownRight.setOnClickListener {
            viewModel.movePtz(ipProvider(), "down", currentStep)
            viewModel.movePtz(ipProvider(), "right", currentStep)
        }

        binding.btnPtzCenter.setOnClickListener { viewModel.centerPtz(ipProvider()) }
        binding.btnPtzCalibrate.setOnClickListener { viewModel.calibratePtz(ipProvider()) }

        // Lighting & Filters
        binding.btnToggleSpotlight.setOnClickListener { viewModel.toggleWhiteLight(ipProvider()) }
        binding.btnToggleNightIr.setOnClickListener { viewModel.toggleNightIr(ipProvider()) }
        binding.btnIrCutDay.setOnClickListener { viewModel.setIrCutFilter(ipProvider(), false) }
        binding.btnIrCutNight.setOnClickListener { viewModel.setIrCutFilter(ipProvider(), true) }

        // AI & Patrol
        binding.btnToggleTracking.setOnClickListener { viewModel.toggleTracking(ipProvider()) }
        binding.btnToggleCruise.setOnClickListener { viewModel.toggleCruise(ipProvider()) }
    }

    private fun setupObservers() {
        viewModel.isOnline.observe(this) { online ->
            if (online) {
                binding.tvOnvifBadge.text = "ONVIF :8899 ONLINE"
                binding.tvOnvifBadge.setTextColor(getColor(R.color.emerald_online))
            } else {
                binding.tvOnvifBadge.text = "ONVIF :8899 OFFLINE"
                binding.tvOnvifBadge.setTextColor(getColor(R.color.rose_alert))
            }
        }

        viewModel.telemetry.observe(this) { t ->
            if (t != null) {
                val upSec = t.uptimeSec?.toLong() ?: 0L
                val hrs = upSec / 3600
                val mins = (upSec % 3600) / 60
                val secs = upSec % 60
                binding.tvUptimeChip.text = "⏱️ Uptime: ${hrs}h ${mins}m ${secs}s"
                binding.tvRamChip.text = "🧠 Free RAM: ${t.freeRamKb ?: "-"} KB"
            }
        }

        viewModel.whiteLightOn.observe(this) { on ->
            binding.btnToggleSpotlight.text = if (on) getString(R.string.spotlight_on) else getString(R.string.spotlight_off)
            binding.btnToggleSpotlight.setBackgroundColor(getColor(if (on) R.color.amber_warning else R.color.border_primary))
            binding.btnToggleSpotlight.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.irNightOn.observe(this) { on ->
            binding.btnToggleNightIr.text = if (on) getString(R.string.ir_on) else getString(R.string.ir_off)
            binding.btnToggleNightIr.setBackgroundColor(getColor(if (on) R.color.purple_accent else R.color.border_primary))
            binding.btnToggleNightIr.setTextColor(if (on) 0xFFFFFFFF.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.trackingOn.observe(this) { on ->
            binding.btnToggleTracking.text = if (on) getString(R.string.tracking_on) else getString(R.string.tracking_off)
            binding.btnToggleTracking.setBackgroundColor(getColor(if (on) R.color.emerald_online else R.color.border_primary))
            binding.btnToggleTracking.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.cruiseOn.observe(this) { on ->
            binding.btnToggleCruise.text = if (on) getString(R.string.cruise_on) else getString(R.string.cruise_off)
            binding.btnToggleCruise.setBackgroundColor(getColor(if (on) R.color.cyan_accent else R.color.border_primary))
            binding.btnToggleCruise.setTextColor(if (on) 0xFF000000.toInt() else 0xFFF8FAFC.toInt())
        }

        viewModel.logMessage.observe(this) { msg ->
            val prev = binding.tvLogConsole.text.toString()
            binding.tvLogConsole.text = "$prev> $msg\n"
        }
    }

    private fun startCameraStream() {
        val ip = binding.etCameraIp.text.toString().trim()
        if (ip.isEmpty()) {
            Toast.makeText(this, "Masukkan IP Kamera terlebih dahulu", Toast.LENGTH_SHORT).show()
            return
        }

        val rtspUrl1 = "rtsp://$ip:1234/"
        val rtspUrl2 = "rtsp://$ip:1235/"

        binding.tvStreamBadge.text = "CONNECTING..."
        binding.tvStreamBadge.setTextColor(getColor(R.color.amber_warning))

        playerLens1.startStream(binding.playerViewLens1, rtspUrl1) { ok1 ->
            if (ok1) {
                binding.tvStreamBadge.text = "DUAL LIVE 1080P"
                binding.tvStreamBadge.setTextColor(getColor(R.color.emerald_online))
            }
        }

        playerLens2.startStream(binding.playerViewLens2, rtspUrl2)

        isStreaming = true
        binding.btnConnect.text = getString(R.string.btn_disconnect)
        binding.btnConnect.setBackgroundColor(getColor(R.color.rose_alert))
        binding.btnConnect.setTextColor(0xFFFFFFFF.toInt())

        viewModel.startTelemetryPolling(ip)
    }

    private fun stopCameraStream() {
        playerLens1.stopStream()
        playerLens2.stopStream()

        isStreaming = false
        binding.tvStreamBadge.text = getString(R.string.status_standby)
        binding.tvStreamBadge.setTextColor(getColor(R.color.text_muted))

        binding.btnConnect.text = getString(R.string.btn_connect)
        binding.btnConnect.setBackgroundColor(getColor(R.color.cyan_accent))
        binding.btnConnect.setTextColor(0xFF000000.toInt())
    }

    override fun onDestroy() {
        super.onDestroy()
        playerLens1.release()
        playerLens2.release()
        viewModel.stopTelemetryPolling()
    }
}
