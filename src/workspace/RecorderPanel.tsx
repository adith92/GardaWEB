import { useEffect, useState } from "react";
import { HardDrive, Video } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableCaption } from "@/components/ui/table";
import { request, apiRoot } from "./api";
type Nvr = {status: string; engine: string; engine_version: string; storage?: string; retention_days: number;
  restart_count: number; free_bytes?: number; reserve_bytes?: number; disk_paused: boolean;
  cameras: {id: string; source_ready: boolean; recording_enabled: boolean; recording_active: boolean;
    last_segment: {name: string; size_bytes: number; age_seconds: number} | null}[]};
type Clip = {start: string; duration: number};
const statuses: Record<string,string> = {configuration_required: "Server rekaman belum dikonfigurasi", starting: "Memulai mesin rekam", recovering: "Memulihkan mesin rekam", running: "Mesin rekam aktif", disk_low: "Rekaman dijeda: disk rendah", stopped: "Mesin rekam berhenti"};
const gib = (bytes?: number) => bytes === undefined ? "—" : `${(bytes/1024**3).toFixed(1)} GiB`;
export default function RecorderPanel({csrf, admin}: {csrf: string; admin: boolean}) {
  const [status,setStatus] = useState<Nvr | null>(null);
  const [clips,setClips] = useState<Clip[]>([]);
  const [camera,setCamera] = useState("");
  const [video,setVideo] = useState("");
  const [error,setError] = useState("");
  const [pending,setPending] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    let inflight = false;
    async function refresh() {
      if (document.hidden || inflight) return;
      inflight = true;
      try {setStatus(await request<Nvr>("/api/v1/nvr/status", {signal: controller.signal}));}
      catch(e) {if ((e as Error).name !== "AbortError") setError((e as Error).message);}
      finally {inflight=false;}
    }
    void refresh(); const timer=window.setInterval(() => void refresh(),3000);
    return () => {controller.abort();window.clearInterval(timer);};
  },[]);
  async function timeline(id: string) {
    setPending(true);setError("");setCamera(id);setVideo("");
    try {setClips((await request<{recordings:Clip[]}>(`/api/v1/nvr/cameras/${id}/timeline`)).recordings);}
    catch(e){setError((e as Error).message);setClips([]);}finally{setPending(false);}
  }
  async function toggle(id: string, enabled: boolean) {
    setPending(true);setError("");
    try {await request(`/api/v1/nvr/cameras/${id}/recording`,{method:"PUT",body:JSON.stringify({enabled})},csrf);}
    catch(e){setError((e as Error).message);}finally{setPending(false);}
  }
  return <section className="gw-network flex flex-col gap-6">
    <Alert><HardDrive/><AlertTitle>Rekaman kontinu terpisah dari AI</AlertTitle><AlertDescription>Kamera yang dikonfigurasi direkam oleh server, termasuk saat client ditutup. Menghentikan preview/AI tidak menghentikan recorder. Status rekaman aktif memerlukan bukti file yang masih diperbarui.</AlertDescription></Alert>
    {error ? <Alert variant="destructive"><AlertTitle>Permintaan belum berhasil</AlertTitle><AlertDescription>{error}</AlertDescription></Alert> : null}
    <Card><CardHeader><CardTitle>{status ? statuses[status.status] ?? status.status : "Memeriksa recorder…"}</CardTitle><CardDescription>{status?.engine} {status?.engine_version} · retensi {status?.retention_days ?? "—"} hari · pemulihan proses {status?.restart_count ?? 0} kali</CardDescription></CardHeader>
      <CardContent><p>Lokasi rekaman: {status?.storage ?? "Atur melalui setup server lokal"}</p><p>Ruang kosong {gib(status?.free_bytes)} · cadangan minimum {gib(status?.reserve_bytes)}</p>
        {status?.disk_paused ? <Alert variant="destructive"><AlertTitle>Disk hampir penuh</AlertTitle><AlertDescription>Recorder menjaga cadangan ruang dan menjeda rekaman. File pribadi tidak dihapus. Rekaman otomatis dilanjutkan setelah ruang tersedia.</AlertDescription></Alert> : null}
        <Table><TableCaption>{status?.cameras.length ? "Status sumber dan rekaman diperbarui dari server." : "Belum ada kamera dengan URL RTSP tersimpan. Tambahkan di Perangkat."}</TableCaption><TableHeader><TableRow><TableHead>Kamera</TableHead><TableHead>Sumber</TableHead><TableHead>Rekaman</TableHead><TableHead>Berkas terakhir</TableHead><TableHead>Aksi</TableHead></TableRow></TableHeader>
          <TableBody>{status?.cameras.map(c => <TableRow key={c.id}><TableCell>{c.id}</TableCell><TableCell>{c.source_ready ? "Terhubung" : "Menunggu kamera"}</TableCell><TableCell>{c.recording_active ? "Merekam" : !c.recording_enabled ? "Dijeda operator" : status.disk_paused ? "Disk rendah" : "Belum terverifikasi"}</TableCell><TableCell>{c.last_segment ? `${(c.last_segment.size_bytes/1024**2).toFixed(1)} MiB · ${c.last_segment.age_seconds}s lalu` : "—"}</TableCell><TableCell><div className="flex gap-2"><Button variant="outline" disabled={pending} onClick={() => void timeline(c.id)}>Lihat rekaman</Button>{admin ? <Button variant="outline" disabled={pending} onClick={() => void toggle(c.id,!c.recording_enabled)}>{c.recording_enabled ? "Jeda rekam" : "Lanjutkan rekam"}</Button> : null}</div></TableCell></TableRow>)}</TableBody></Table>
      </CardContent><CardFooter><CardDescription>Retensi berlaku hanya pada berkas dalam folder rekaman yang dikelola GARDA. Kamera terputus dan disk rendah menghasilkan celah rekaman; status sumber ditampilkan terpisah.</CardDescription></CardFooter></Card>
    {camera ? <Card><CardHeader><CardTitle>Playback · {camera}</CardTitle><CardDescription>{pending ? "Memuat…" : `${clips.length} rentang rekaman tersedia`}</CardDescription></CardHeader><CardContent className="flex flex-col gap-4">
      {video ? <video src={video} controls preload="metadata" aria-label={`Playback ${camera}`} className="w-full"/> : null}
      <Table><TableCaption>Putar potongan sampai 10 menit. Dukungan codec mengikuti perangkat client.</TableCaption><TableHeader><TableRow><TableHead>Mulai</TableHead><TableHead>Durasi</TableHead><TableHead>Aksi</TableHead></TableRow></TableHeader><TableBody>{clips.slice(0,100).map(c => <TableRow key={c.start}><TableCell>{new Date(c.start).toLocaleString("id-ID")}</TableCell><TableCell>{c.duration.toFixed(1)} detik</TableCell><TableCell><Button onClick={() => setVideo(`${apiRoot}/api/v1/nvr/cameras/${camera}/playback.mp4?start=${encodeURIComponent(c.start)}&duration=${Math.max(1,Math.min(600,c.duration))}`)}><Video data-icon="inline-start"/>Putar</Button></TableCell></TableRow>)}</TableBody></Table>
    </CardContent></Card> : null}
  </section>;
}
