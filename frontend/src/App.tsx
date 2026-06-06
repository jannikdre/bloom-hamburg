import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { CurrentData } from "./types";
import { loadCurrentData } from "./data";
import PlantCard from "./components/PlantCard";

type Tab = "bloom" | "harvest";

function formatStand(data: CurrentData): string {
  const d = new Date(data.generated_at);
  const date = isNaN(d.getTime())
    ? data.generated_at
    : d.toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
  return `Stand: KW ${data.week} · ${date}`;
}

export default function App() {
  const [data, setData] = useState<CurrentData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("bloom");

  useEffect(() => {
    loadCurrentData().then(setData).catch((e) => setError(String(e.message ?? e)));
  }, []);

  return (
    <div className="min-h-screen bg-bloom-light text-gray-900">
      <header className="bg-bloom-green px-4 pb-4 pt-[max(1rem,env(safe-area-inset-top))] text-white">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-xl font-bold leading-tight">Hamburg blüht & erntet</h1>
          <p className="text-sm text-white/80">
            Region {data?.region ?? "Hamburg"}
            {data ? ` · ${formatStand(data)}` : ""}
          </p>
          {data?.is_mock && (
            <p className="mt-1 inline-block rounded bg-white/20 px-2 py-0.5 text-xs">
              Beispieldaten (Pipeline noch nicht gelaufen)
            </p>
          )}
        </div>
      </header>

      <nav className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto flex max-w-3xl">
          <TabButton active={tab === "bloom"} onClick={() => setTab("bloom")}>
            🌼 Jetzt in Blüte
          </TabButton>
          <TabButton active={tab === "harvest"} onClick={() => setTab("harvest")}>
            🥕 Erntezeit
          </TabButton>
        </div>
      </nav>

      <main className="mx-auto max-w-3xl px-4 py-4">
        {error && (
          <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</p>
        )}
        {!data && !error && <p className="text-gray-500">Lädt…</p>}

        {data && tab === "bloom" && (
          <Grid>
            {data.blooming.map((item) => (
              <PlantCard key={item.name_de} kind="bloom" item={item} />
            ))}
          </Grid>
        )}

        {data && tab === "harvest" && (
          <Grid>
            {data.harvesting.map((item) => (
              <PlantCard key={item.name_de} kind="harvest" item={item} />
            ))}
          </Grid>
        )}
      </main>

      <footer className="mx-auto max-w-3xl px-4 py-6 text-center text-xs text-gray-400">
        Quelle Phänologie: Deutscher Wetterdienst (DWD), Open Data · Gemüse:
        kuratierter Saisonkalender · Bilder/Texte: Wikipedia/Wikimedia Commons
        (CC-BY).
      </footer>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "flex-1 px-4 py-3 text-sm font-medium transition-colors " +
        (active
          ? "border-b-2 border-bloom-green text-bloom-green"
          : "text-gray-500 hover:text-gray-700")
      }
    >
      {children}
    </button>
  );
}

function Grid({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {children}
    </div>
  );
}
