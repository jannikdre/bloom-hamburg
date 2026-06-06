import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: Für GitHub Project Pages läuft die App unter /<repo>/.
// Lokal (dev/preview) bleibt es "/". Beim Online-Deploy via Env überschreibbar:
//   VITE_BASE=/bloom-hamburg/ npm run build
const base = process.env.VITE_BASE ?? "/";

export default defineConfig({
  base,
  plugins: [react()],
});
