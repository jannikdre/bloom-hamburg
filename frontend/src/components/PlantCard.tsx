import type { BloomingItem, HarvestItem } from "../types";

const MONTHS_DE = [
  "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
  "Jul", "Aug", "Sep", "Okt", "Nov", "Dez",
];

type Props =
  | { kind: "bloom"; item: BloomingItem }
  | { kind: "harvest"; item: HarvestItem };

export default function PlantCard(props: Props) {
  const { item } = props;
  return (
    <article className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-black/5">
      <div className="aspect-[3/2] w-full bg-bloom-light">
        <img
          src={item.image}
          alt={item.name_de}
          loading="lazy"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900">{item.name_de}</h3>
        {props.kind === "bloom" && (
          <p className="text-sm italic text-gray-500">{props.item.name_lat}</p>
        )}

        {props.kind === "bloom" && (
          <p className="mt-2 text-sm leading-relaxed text-gray-700">
            {props.item.text}
          </p>
        )}

        {props.kind === "harvest" && (
          <div className="mt-2">
            <div className="flex flex-wrap gap-1">
              {MONTHS_DE.map((m, i) => (
                <span
                  key={m}
                  className={
                    "rounded px-1.5 py-0.5 text-[11px] " +
                    (props.item.months.includes(i + 1)
                      ? "bg-bloom-green text-white"
                      : "bg-gray-100 text-gray-400")
                  }
                >
                  {m}
                </span>
              ))}
            </div>
            {props.item.note && (
              <p className="mt-2 text-sm text-gray-700">{props.item.note}</p>
            )}
          </div>
        )}

        <p className="mt-3 text-[11px] text-gray-400">
          {item.image_credit} · Quelle: {item.source}
        </p>
      </div>
    </article>
  );
}
