import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Network, Search, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldDescription, FieldGroup, FieldLabel, FieldSet, FieldLegend } from "@/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { request } from "./api";

type Interface = { name: string; ip: string; network: string; suggested: string };
type Scan = { status: string; completed: number; total: number; results: {ip: string; port: number; hint: string}[]; truncated?: boolean };
const labels: Record<string, string> = { idle: "Siap", running: "Memindai", completed: "Selesai", cancelled: "Dihentikan", timed_out: "Batas waktu tercapai", failed: "Gagal" };

export default function NetworkPanel({ csrf }: { csrf: string }) {
  const [interfaces, setInterfaces] = useState<Interface[]>([]);
  const [target, setTarget] = useState("");
  const [ports, setPorts] = useState("");
  const [profile, setProfile] = useState("recommended");
  const [scan, setScan] = useState<Scan>({status: "idle", completed: 0, total: 0, results: []});
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    request<{interfaces: Interface[]; default_ports: string}>("/api/v1/network/interfaces", {signal: controller.signal}).then(data => {
      setInterfaces(data.interfaces); setTarget(data.interfaces[0]?.suggested ?? ""); setPorts(data.default_ports);
    }).catch(e => {if (e.name !== "AbortError") setError(e.message);});
    async function refresh() {
      try { setScan(await request<Scan>("/api/v1/network/scan", {signal: controller.signal})); }
      catch (e) {if ((e as Error).name !== "AbortError") setError((e as Error).message);}
    }
    void refresh();
    const timer = window.setInterval(() => {if (!document.hidden) void refresh();}, 1500);
    return () => {controller.abort(); window.clearInterval(timer);};
  }, []);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setPending(true);
    try {setScan(await request<Scan>("/api/v1/network/scan", {method: "POST", body: JSON.stringify({target, profile})}, csrf));}
    catch (e) {setError((e as Error).message);} finally {setPending(false);}
  }
  const running = scan.status === "running";
  return <section className="gw-network flex flex-col gap-6">
    <Alert><Network/><AlertTitle>Pemindaian dari server GARDA</AlertTitle><AlertDescription>Semua client melihat LAN server yang sama. Port terbuka adalah petunjuk; ONVIF, video, audio, dan PTZ tetap perlu diuji pada kamera.</AlertDescription></Alert>
    <Card><CardHeader><CardTitle>Temukan perangkat & port LAN</CardTitle><CardDescription>TCP scanner bawaan · maksimal /24 · tanpa instalasi Nmap.</CardDescription></CardHeader>
      <CardContent><form id="network-scan" onSubmit={submit}><FieldGroup>
        <Field><FieldLabel htmlFor="scan-target">IP atau subnet target</FieldLabel><Input id="scan-target" value={target} onChange={e => setTarget(e.target.value)} placeholder="192.168.1.0/24" maxLength={32} required disabled={running}/><FieldDescription>Interface aktif: {interfaces.length ? interfaces.map(i => `${i.name} (${i.ip}, ${i.network})`).join("; ") : "Belum ditemukan. Periksa koneksi LAN server."}</FieldDescription></Field>
        <FieldDescription>{profile === "recommended" ? <>Otomatis memakai <strong>Recommended Ports</strong>: {ports}. Full Port hanya dijalankan jika dipilih di pengaturan lanjutan.</> : <>Profil aktif: <strong>Full Port · 1–65535</strong>. Dipilih secara manual di Advanced Settings; hanya untuk satu IP.</>}</FieldDescription>
        <details className="gw-advanced"><summary>Advanced Settings</summary><FieldSet disabled={running}><FieldLegend>Profil pemindaian</FieldLegend>
          <RadioGroup value={profile} onValueChange={setProfile} disabled={running} aria-label="Profil pemindaian">
            <Field orientation="horizontal"><RadioGroupItem id="scan-recommended" value="recommended"/><FieldLabel htmlFor="scan-recommended">Recommended Ports · cepat (default)</FieldLabel></Field>
            <Field orientation="horizontal"><RadioGroupItem id="scan-full" value="full"/><FieldLabel htmlFor="scan-full">Full Port · 1–65535, satu IP</FieldLabel></Field>
          </RadioGroup><FieldDescription>{profile === "full" ? "Full Port aktif. Masukkan satu IP kamera; durasi maksimal 5 menit, hasil parsial tetap tampil." : "Hanya port umum CCTV yang diperiksa. Tidak menjalankan full scan otomatis."}</FieldDescription>
        </FieldSet></details>
      </FieldGroup></form></CardContent>
      <CardFooter className="flex flex-wrap gap-3"><Button type="submit" form="network-scan" disabled={running || pending || !interfaces.length}><Search data-icon="inline-start"/>{pending ? "Memulai…" : "Mulai pindai"}</Button><Button variant="outline" disabled={!running || pending} onClick={async () => {try {setScan(await request<Scan>("/api/v1/network/scan/cancel", {method: "POST"}, csrf));} catch (e) {setError((e as Error).message);}}}><Square data-icon="inline-start"/>Hentikan</Button></CardFooter>
    </Card>
    {error ? <Alert variant="destructive"><AlertTitle>Periksa permintaan scan</AlertTitle><AlertDescription>{error}</AlertDescription></Alert> : null}
    <Card><CardHeader><CardTitle>Hasil pemindaian <Badge variant="secondary">{labels[scan.status] ?? scan.status}</Badge></CardTitle><CardDescription role="status" aria-live="polite">{scan.completed} / {scan.total} koneksi diperiksa · {scan.results.length} port terbuka</CardDescription></CardHeader>
      <CardContent className="flex flex-col gap-4"><Progress value={scan.total ? 100*scan.completed/scan.total : 0} aria-label="Progres pemindaian"/>
        <Table><TableCaption>{scan.results.length ? "Petunjuk layanan berdasarkan nomor port; belum dikonfirmasi." : "Belum ada port terbuka yang ditemukan."}</TableCaption><TableHeader><TableRow><TableHead>IP</TableHead><TableHead>Port TCP</TableHead><TableHead>Petunjuk layanan</TableHead></TableRow></TableHeader><TableBody>{scan.results.map(r => <TableRow key={`${r.ip}:${r.port}`}><TableCell>{r.ip}</TableCell><TableCell>{r.port}</TableCell><TableCell>{r.hint}</TableCell></TableRow>)}</TableBody></Table>
        {scan.truncated ? <p>Hasil ditampilkan sampai 1000 port; perkecil target untuk melihat rincian.</p> : null}
      </CardContent><CardFooter><CardDescription>Data hasil scan disimpan dalam memori server sampai scan berikutnya atau server dimulai ulang.</CardDescription></CardFooter>
    </Card>
  </section>;
}
