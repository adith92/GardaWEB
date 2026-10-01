import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import seed from "../DEMO_DATA.json";
import { transitionIncident } from "./logic.mjs";
export type Camera = (typeof seed.cameras)[number];
export type Event = (typeof seed.events)[number];
export type Incident = (typeof seed.incidents)[number] & {
  notes?: string[];
  evidence?: string[];
};
export type VaultFile = {
  id: string;
  name: string;
  folder: string;
  type: string;
  size: string;
  owner: string;
  retention: string;
  archived?: boolean;
  shared?: boolean;
  shareRole?: string;
  shareExpiry?: string;
};
export const cameras = seed.cameras;
export const defaultFolders = [
  "Incident Evidence",
  "CCTV Exports",
  "Command Reports",
  "Shared Operations",
  "Personal",
];
const initialFiles: VaultFile[] = [
  {
    id: "F-01",
    name: "INC-0184_evidence.json",
    folder: "Incident Evidence",
    type: "JSON",
    size: "2.4 KB",
    owner: "Operator 01",
    retention: "180 hari",
  },
  {
    id: "F-02",
    name: "Rear-gate_snapshot.png",
    folder: "Incident Evidence",
    type: "Image",
    size: "1.2 MB",
    owner: "Operator 02",
    retention: "180 hari",
  },
  {
    id: "F-03",
    name: "Shift-malam_report.txt",
    folder: "Command Reports",
    type: "Text",
    size: "4 KB",
    owner: "Supervisor",
    retention: "365 hari",
  },
  {
    id: "F-04",
    name: "CAM-01_clip-metadata.json",
    folder: "CCTV Exports",
    type: "JSON",
    size: "1 KB",
    owner: "Operator 01",
    retention: "30 hari",
  },
];
const initial = {
  incidents: seed.incidents as Incident[],
  events: seed.events,
  faces: seed.faces,
  plates: seed.plates,
  files: initialFiles,
  folders: defaultFolders,
  audit: [
    { time: "22:00:00", action: "Sesi demo dimulai", target: "Operator 01" },
  ],
  settings: { retention: "30", alerts: true, role: "Command Supervisor" },
  feedIndex: 0,
};
type State = typeof initial;
const key = "pmc-garda-demo-v1";
function read(): State {
  try {
    const s = JSON.parse(localStorage.getItem(key) || "null");
    return s &&
      Array.isArray(s.incidents) &&
      Array.isArray(s.files) &&
      s.settings
      ? { ...initial, ...s }
      : initial;
  } catch {
    return initial;
  }
}
function useStore() {
  const [state, setState] = useState<State>(read);
  const [toast, setToast] = useState("");
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {
      setToast(
        "Penyimpanan browser penuh. Perubahan hanya berlaku pada sesi ini.",
      );
    }
  }, [state]);
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 4200);
      return () => clearTimeout(t);
    }
  }, [toast]);
  function log(action: string, target: string) {
    setState((s) => ({
      ...s,
      audit: [
        {
          time: new Date().toLocaleTimeString("en-GB", {
            timeZone: "Asia/Jakarta",
          }),
          action,
          target,
        },
        ...s.audit,
      ],
    }));
  }
  function updateIncident(id: string, patch: Partial<Incident>) {
    setState((s) => ({
      ...s,
      incidents: s.incidents.map((i) =>
        i.id === id
          ? {
              ...(patch.status ? transitionIncident(i, patch.status) : i),
              ...patch,
            }
          : i,
      ),
    }));
    log("Insiden diperbarui", id);
    setToast("Perubahan insiden disimpan lokal");
  }
  function createIncident(camera: string) {
    const id = `INC-DEMO-${Date.now().toString().slice(-7)}`;
    setState((s) => ({
      ...s,
      incidents: [
        {
          id,
          title: "Verifikasi manual operator",
          severity: "medium",
          status: "open",
          camera,
          time: "22:24",
          assignee: "Operator 01",
        },
        ...s.incidents,
      ],
    }));
    log("Insiden dibuat", id);
    setToast(`Insiden ${id} dibuat`);
    return id;
  }
  return {
    state,
    setState,
    toast,
    notify: setToast,
    log,
    updateIncident,
    createIncident,
    reset: () => {
      setState(initial);
      setToast("Data demo dikembalikan ke kondisi awal");
    },
  };
}
const Context = createContext<ReturnType<typeof useStore> | null>(null);
export function StoreProvider({ children }: { children: ReactNode }) {
  const value = useStore();
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useDemo() {
  return useContext(Context)!;
}
export function download(
  name: string,
  content: string,
  type = "application/json",
) {
  const u = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = u;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(u), 1000);
}
