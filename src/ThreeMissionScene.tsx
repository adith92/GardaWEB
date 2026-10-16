import { useState } from "react";

/** Decorative demo illustration. No live video, telemetry or camera control. */
export function ThreeMissionScene() {
  const [mode, setMode] = useState<"cctv" | "logo">("cctv");
  const [paused, setPaused] = useState(false);
  return (
    <div className={`mission-scene garda-visual ${paused ? "motion-paused" : ""}`}>
      <div className="garda-visual-art" role="img" aria-label={mode === "cctv" ? "Animasi kamera CCTV GARDA sedang memindai, ilustrasi demo" : "Logo PUSADA pada identitas GARDA berputar, ilustrasi demo"}>
        {mode === "cctv" ? <svg viewBox="0 0 520 250" aria-hidden="true">
          <defs>
            <linearGradient id="garda-camera-body" x2="0.8" y2="1"><stop stopColor="#f4f7fa"/><stop offset="1" stopColor="#8295a5"/></linearGradient>
            <radialGradient id="garda-lens"><stop stopColor="#316e8b"/><stop offset=".55" stopColor="#102d40"/><stop offset="1" stopColor="#050d16"/></radialGradient>
            <linearGradient id="garda-field"><stop stopColor="#e63b55" stopOpacity=".22"/><stop offset="1" stopColor="#e63b55" stopOpacity="0"/></linearGradient>
          </defs>
          <ellipse cx="270" cy="218" rx="138" ry="12" fill="#0b1520" opacity=".3"/>
          <path d="M210 181v32h77" fill="none" stroke="#718391" strokeWidth="14" strokeLinejoin="round"/>
          <rect x="275" y="195" width="16" height="37" rx="4" fill="#a9bac5"/>
          <g className="cctv-pan">
            <path d="M327 119L505 48v160z" fill="url(#garda-field)"/>
            <path d="M327 119L495 59M327 119l168 80" stroke="#ed4b65" strokeOpacity=".3" strokeDasharray="4 7"/>
            <path d="M150 67h160l38 37-16 70H174l-24-21z" fill="url(#garda-camera-body)" stroke="#c9d4de" strokeWidth="2"/>
            <path d="M140 59h179l37 37H170z" fill="#e9eef3"/>
            <path d="M309 88l39 16-16 70-36-17z" fill="#233644"/>
            <ellipse cx="322" cy="130" rx="22" ry="34" fill="#0a1520" transform="rotate(13 322 130)"/>
            <ellipse cx="322" cy="130" rx="15" ry="25" fill="url(#garda-lens)" transform="rotate(13 322 130)"/>
            <ellipse cx="319" cy="122" rx="4" ry="7" fill="#8ccee8" opacity=".7"/>
            <circle className="cctv-rec" cx="280" cy="139" r="4" fill="#e51e45"/>
            <text x="182" y="123" fill="#253946" fontSize="20" fontWeight="800" fontFamily="system-ui">GARDA</text>
            <text x="182" y="144" fill="#415666" fontSize="9" letterSpacing="2" fontFamily="system-ui">PUSADA PMC</text>
          </g>
          <text x="365" y="225" fill="#c26679" fontSize="9" letterSpacing="2" fontFamily="system-ui">CCTV / DEMO</text>
        </svg> : <div className="garda-logo-stage"><div className="garda-logo-coin"><img src="/logo.png" alt="" /></div><strong>GARDA</strong><span>PUSADA MONITORING CENTER</span></div>}
      </div>
      <div className="garda-motion-controls" aria-label="Pilihan animasi demo">
        <button aria-pressed={mode === "cctv"} onClick={() => setMode("cctv")}>CCTV</button>
        <button aria-pressed={mode === "logo"} onClick={() => setMode("logo")}>Logo GARDA</button>
        <button aria-pressed={paused} onClick={() => setPaused(!paused)}>{paused ? "Putar animasi" : "Jeda animasi"}</button>
      </div>
    </div>
  );
}
