export interface PumpConfig {
  icr: number;
  isf: number;
  target_glucose: number;
}

export interface Summary {
  cgm_readings: number;
  bolus_events: number;
  pod_failures: number;
  clean_windows: number;
  rejected_windows: number;
}

export interface RatioBlock {
  configured: number;
  implied_median: number;
  evaluated: number;
  trended_high: number;
  recommendation: string;
  suggested: number | null;
}

export interface MealHabit {
  events: number;
  avg_carbs: number;
  avg_bolus: number;
  median_hour: number;
}

export interface SlotGrades {
  high: number;
  ok: number;
  low: number;
}

export interface DaySummary {
  date: string;
  total_basal: number;
  total_bolus: number;
  total_insulin: number;
  basal_pct: number;
  bolus_pct: number;
  pod_failure: boolean;
}

export interface AnalysisResult {
  summary: Summary;
  isf: RatioBlock;
  icr: RatioBlock;
  meal_habits: Record<string, MealHabit>;
  time_of_day_breakdown: Record<string, SlotGrades>;
  daily_summary: DaySummary[];
}

/** Order slots consistently across the UI. */
export const SLOT_ORDER = ["Breakfast", "Lunch", "Dinner", "Night"] as const;
