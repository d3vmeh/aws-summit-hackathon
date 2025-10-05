// TypeScript types matching backend schemas

export interface CalendarEvent {
  id: string;
  summary: string;
  start: string;
  end: string;
  description?: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  due_date?: string;
  priority: "low" | "medium" | "high";
  completed: boolean;
}

export interface StressScore {
  total_score: number;
  calendar_factor: number;
  task_factor: number;
  sleep_factor: number;
  risk_level: "low" | "medium" | "high" | "critical";
  timestamp: string;
}

export interface StressFactors {
  events_next_7_days: number;
  immediate_action_tasks: number;
  calendar_density: number;
  sleep_hours_available: number;
  average_break_length: number;
  sleep_quality_message: string;
}

export interface Intervention {
  id: string;
  type: "reschedule" | "delegate" | "break_down" | "micro_break";
  priority: string;
  title: string;
  description: string;
  impact_score: number;
  effort_score: number;
}

export interface BurnoutPrediction {
  stress_score: StressScore;
  factors: StressFactors;
  predictions: string[];
  interventions: Intervention[];
  historical_comparison?: string;
}
