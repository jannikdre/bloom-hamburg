import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service Worker registrieren (PWA / Offline). Pfad respektiert den Vite-base,
// damit es auch unter dem GitHub-Pages-Unterpfad /<repo>/ funktioniert.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    const base = import.meta.env.BASE_URL;
    navigator.serviceWorker.register(`${base}sw.js`, { scope: base }).catch(() => {
      /* SW-Registrierung fehlgeschlagen – App läuft trotzdem (ohne Offline). */
    });
  });
}
