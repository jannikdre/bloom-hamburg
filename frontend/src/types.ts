export interface BloomingItem {
  name_de: string;
  name_lat: string;
  image: string;
  image_credit: string;
  text: string;
  source: string;
}

export interface HarvestItem {
  name_de: string;
  image: string;
  image_credit: string;
  months: number[];
  note: string;
  source: string;
}

export interface CurrentData {
  generated_at: string;
  week: number;
  region: string;
  is_mock?: boolean;
  blooming: BloomingItem[];
  harvesting: HarvestItem[];
}
