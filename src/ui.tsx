import { useEffect, useRef, useState as useLocal, type ReactNode } from "react";
import { X, ArrowUpRight, Camera as CameraIcon, Download } from "lucide-react";
import { cameras, download, useDemo, type Camera } from "./store";
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function PageTitle({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <div className="page-title">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="actions">{children}</div>
    </div>
  );
}
export function Panel({
  title,
  actions,
  children,
  className = "",
}: {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      {title && (
        <div className="panel-head">
          <h2>{title}</h2>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
export function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
    return () => ref.current?.close();
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="panel-head">
        <h2>{title}</h2>
        <button className="icon-button" onClick={onClose} aria-label="Tutup">
          <X size={20} />
        </button>
      </div>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}
export function CameraImage({
  camera,
  className = "",
  children,
}: {
  camera?: Camera | null;
  className?: string;
  children?: ReactNode;
}) {
  const i = camera ? cameras.findIndex((c) => c.id === camera.id) : -1;
  const knownCamera = camera != null && i >= 0;
  return (
    <div
      role="img"
      aria-label={knownCamera ? `Simulasi kamera ${camera?.name}` : "Kamera tidak tersedia"}
      className={`camera-image ${className}`}
      style={{
        backgroundImage: knownCamera ? "url(/cameras.png)" : "none",
        backgroundSize: "400% 200%",
        backgroundPosition: `${((i % 4) * 100) / 3}% ${Math.floor(i / 4) * 100}%`,
      }}
    >
      {knownCamera ? children : <span>Kamera tidak tersedia</span>}
    </div>
  );
}
export function CameraTile({
  camera,
  onClick,
  selected = false,
}: {
  camera: Camera;
  onClick: () => void;
  selected?: boolean;
}) {
  return (
    <button
      className={`camera-tile ${selected ? "selected" : ""}`}
      onClick={onClick}
    >
      <CameraImage camera={camera}>
        <span className="camera-top">
          <span>
            <CameraIcon size={12} /> {camera.id}
          </span>
          <span className="sim-label">SIMULASI</span>
        </span>
        <span className="camera-bottom">
          <span>
            <b>{camera.name}</b>
            <small>01.10.2026 · 22:24:06</small>
          </span>
          <ArrowUpRight size={17} />
        </span>
      </CameraImage>
    </button>
  );
}
export function CameraDetail({
  camera,
  onClose,
  onPlayback,
  onIncident,
}: {
  camera: Camera;
  onClose: () => void;
  onPlayback: () => void;
  onIncident: () => void;
}) {
  const { notify, log } = useDemo();
  const [recording, setRecording] = useLocal(false);
  const [ptz, setPtz] = useLocal({ x: 0, y: 0 });
  return (
    <Modal title={`${camera.id} · ${camera.name}`} onClose={onClose}>
      <CameraImage camera={camera} className="detail-image" />
      <div className="detail-meta">
        <Badge tone="success">Online</Badge>
        <span>{camera.fps} FPS</span>
        <span>{camera.bitrateMbps} Mbps</span>
        <span>{camera.zone}</span>
      </div>
      <p className="muted">
        Gambar sintetis. Kontrol berikut merupakan simulasi lokal, bukan koneksi
        RTSP.
      </p>
      <div className="button-grid">
        <button
          onClick={() => {
            const a = document.createElement("a");
            a.href = "/cameras.png";
            a.download = `${camera.id}-synthetic-atlas.png`;
            a.click();
            log("Snapshot sintetis diekspor", camera.id);
            notify("Atlas snapshot sintetis diunduh");
          }}
        >
          <Download size={16} /> Snapshot
        </button>
        <button
          className={recording ? "danger" : ""}
          onClick={() => {
            if (recording) {
              download(
                `${camera.id}-recording-demo.json`,
                JSON.stringify({
                  camera: camera.id,
                  simulated: true,
                  note: "Metadata simulasi; tidak berisi video.",
                }),
              );
            }
            setRecording(!recording);
            notify(
              recording
                ? "Metadata sesi rekam diunduh"
                : "Sesi rekam simulasi dimulai",
            );
          }}
        >
          {recording ? "Stop recording" : "Manual record"}
        </button>
        <button onClick={onPlayback}>Open playback</button>
        <button className="primary" onClick={onIncident}>
          Create incident
        </button>
      </div>
      {camera.ptz ? (
        <div className="ptz">
          <h3>PTZ · preview posisi</h3>
          <div className="actions">
            {[
              ["Kiri", -10, 0],
              ["Atas", 0, -10],
              ["Reset", 0, 0],
              ["Bawah", 0, 10],
              ["Kanan", 10, 0],
            ].map(([name, x, y]) => (
              <button
                key={name}
                onClick={() =>
                  setPtz(
                    name === "Reset"
                      ? { x: 0, y: 0 }
                      : { x: ptz.x + Number(x), y: ptz.y + Number(y) },
                  )
                }
              >
                {name}
              </button>
            ))}
          </div>
          <p>
            Pan {ptz.x}° · Tilt {ptz.y}° — simulasi, tidak menggerakkan kamera.
          </p>
        </div>
      ) : (
        <p className="muted">Kamera fixed · PTZ tidak didukung.</p>
      )}
    </Modal>
  );
}

