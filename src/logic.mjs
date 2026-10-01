export function filterEvents(events, filters) {
  return events.filter(
    (e) =>
      (!filters.query ||
        `${e.id} ${e.type} ${e.entity} ${e.camera}`
          .toLowerCase()
          .includes(filters.query.toLowerCase())) &&
      (!filters.camera || e.camera === filters.camera) &&
      (!filters.severity || e.severity === filters.severity) &&
      (!filters.status || e.status === filters.status) &&
      (!filters.date || filters.date === "2026-10-01"),
  );
}
export function transitionIncident(incident, status) {
  if (!["open", "acknowledged", "resolved"].includes(status))
    throw new Error("Invalid incident status");
  return { ...incident, status };
}
export const prompts = [
  "Apa yang terjadi setelah jam 23:00 tadi malam?",
  "Cari kendaraan yang masuk tapi belum keluar.",
  "Kapan terakhir B 1234 GAR terlihat?",
  "Tampilkan unknown face hari ini.",
  "Buat laporan shift malam.",
];
export function answerQuery(query, incidents, plates) {
  const q = query.toLowerCase();
  if (q.includes("23:00"))
    return {
      text: "Tidak ada rekaman setelah 23:00 dalam dataset demo. Data yang tersedia mencakup 22:14–22:22 pada 1 Oktober 2026. Berikut bukti aktivitas terakhir, bukan kejadian setelah 23:00.",
      refs: ["EV-1001", "EV-1002", "EV-1005"],
    };
  if (q.includes("belum keluar"))
    return {
      text: `${plates.filter((p) => p.state === "inside").length} kendaraan masih berada di kawasan: ${plates
        .filter((p) => p.state === "inside")
        .map((p) => `${p.plate} (${p.vehicle}, masuk ${p.firstSeen})`)
        .join("; ")}.`,
      refs: ["EV-1001", "EV-1004"],
    };
  if (q.includes("1234"))
    return {
      text: "B 1234 GAR, Black SUV, terakhir terlihat pukul 22:14 di CAM-07 Rear Gate. Status unknown; belum ada catatan keluar dalam dataset.",
      refs: ["EV-1001"],
    };
  if (q.includes("face") || q.includes("wajah"))
    return {
      text: "2 identitas belum dikenal: Unknown #17 di CAM-07 pukul 21:51 (86%) dan Unknown #18 di CAM-06 pukul 22:15 (91%). Identitas fiktif; tidak ada pemrosesan biometrik nyata.",
      refs: ["EV-1002"],
    };
  if (q.includes("laporan") || q.includes("ringkasan"))
    return {
      text: `Ringkasan shift demo • 1 Oktober 2026. Kamera online 8/8. ${incidents.filter((i) => i.status !== "resolved").length} insiden aktif, 2 wajah unknown, 1 pelat unknown. Penyimpanan 62%. R630 sehat. GPU belum terpasang. Prioritas: verifikasi akses gudang dan kualitas gambar server room.`,
      refs: ["EV-1002", "EV-1005"],
    };
  return {
    text: "Mode demo hanya mendukung lima pertanyaan contoh. Pilih pertanyaan di bawah untuk mendapatkan jawaban deterministik dengan sumber bukti. Tidak ada model AI atau pencarian video nyata yang dipanggil.",
    refs: [],
  };
}
