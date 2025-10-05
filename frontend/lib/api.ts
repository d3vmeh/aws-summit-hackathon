// Simple API client for backend communication

import { BurnoutPrediction, CalendarEvent, Task } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export const api = {
  // Analyze stress based on events and tasks
  async analyzeStress(
    events: CalendarEvent[],
    tasks: Task[]
  ): Promise<BurnoutPrediction> {
    const response = await fetch(`${API_URL}/api/stress/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ events, tasks }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  },

  // Get calendar events (from mock data for now)
  async getCalendarEvents(): Promise<CalendarEvent[]> {
    const response = await fetch(`${API_URL}/api/calendar/events`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  // Get tasks (from mock data for now)
  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${API_URL}/api/tasks/`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },
};
