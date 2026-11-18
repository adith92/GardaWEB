import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

// Three distinct lab surfaces: root legacy demo, /V2 demo and /workspace actual server UI.
const pathname = window.location.pathname;
const isV2 = /^\/V2(?:\/|$)/.test(pathname);
const isWorkspace = /^\/workspace(?:\/|$)/.test(pathname);
const selected = (isV2 || isWorkspace)
  ? Promise.all([import("./App"), import("./styles.css")])
  : Promise.all([import("./legacy/App"), import("./legacy/styles.css")]);
void selected.then(([{ default: App }]) => {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <BrowserRouter basename={isV2 ? "/V2" : "/"}>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  );
}).catch((error) => {
  console.error("GARDA view failed to load", error);
  const root = document.getElementById("root");
  if (root) root.textContent = "GARDA gagal memuat tampilan. Periksa koneksi lalu refresh.";
});
