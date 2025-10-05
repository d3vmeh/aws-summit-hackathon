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

  // Get calendar events from Google Calendar
  async getCalendarEvents(): Promise<CalendarEvent[]> {
    const response = await fetch(`${API_URL}/api/calendar/events`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  // Get tasks
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

  // Google Calendar Auth
  async getGoogleAuthUrl(): Promise<{ auth_url: string }> {
    const response = await fetch(`${API_URL}/auth/google`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async getAuthStatus(): Promise<{ authenticated: boolean; provider: string | null }> {
    const response = await fetch(`${API_URL}/auth/status`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async disconnectCalendar(): Promise<{ status: string }> {
    const response = await fetch(`${API_URL}/auth/disconnect`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async syncCalendar(daysAhead: number = 7): Promise<{ status: string; events_count: number; events: CalendarEvent[] }> {
    const response = await fetch(`${API_URL}/api/calendar/sync?days_ahead=${daysAhead}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  // Calendar selection
  async listCalendars(): Promise<{ calendars: Array<{ id: string; summary: string; primary: boolean; backgroundColor: string }> }> {
    const response = await fetch(`${API_URL}/api/calendar/list`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async getSelectedCalendars(): Promise<{ selected_calendar_ids: string[] }> {
    const response = await fetch(`${API_URL}/api/calendar/selected`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async setSelectedCalendars(calendarIds: string[]): Promise<{ selected_calendar_ids: string[] }> {
    const response = await fetch(`${API_URL}/api/calendar/selected`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(calendarIds),
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },
};
