import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
const isV2 = /^\/V2(?:\/|$)/.test(window.location.pathname);

// Load only the selected design and stylesheet to keep the two layouts isolated.
const selectedDesign = isV2
  ? Promise.all([import("./App"), import("./styles.css")])
  : Promise.all([import("./legacy/App"), import("./legacy/styles.css")]);

selectedDesign.then(([{ default: App }]) => {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <BrowserRouter basename={isV2 ? "/V2" : "/"}>
        <App />
      </BrowserRouter>
    </React.StrictMode>,
  );
});
