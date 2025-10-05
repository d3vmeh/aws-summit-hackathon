"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BurnoutPrediction } from "@/lib/types";
import { api } from "@/lib/api";
import { mockEvents, mockTasks } from "@/lib/mock-data";

interface Calendar {
  id: string;
  summary: string;
  primary: boolean;
  backgroundColor: string;
}

export function StressDashboard() {
  const [prediction, setPrediction] = useState<BurnoutPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [calendarProvider, setCalendarProvider] = useState<string | null>(null);
  const [availableCalendars, setAvailableCalendars] = useState<Calendar[]>([]);
  const [selectedCalendarIds, setSelectedCalendarIds] = useState<string[]>(['primary']);
  const [showCalendarSelector, setShowCalendarSelector] = useState(false);

  useEffect(() => {
    checkAuthStatus();
    // Don't auto-load analysis on mount - let user select calendars first
  }, []);

  async function checkAuthStatus() {
    try {
      const status = await api.getAuthStatus();
      setIsAuthenticated(status.authenticated);
      setCalendarProvider(status.provider);

      if (status.authenticated) {
        // Load available calendars and selected ones
        const [calendarsRes, selectedRes] = await Promise.all([
          api.listCalendars(),
          api.getSelectedCalendars(),
        ]);
        setAvailableCalendars(calendarsRes.calendars);
        setSelectedCalendarIds(selectedRes.selected_calendar_ids);
      }
    } catch (err) {
      console.error("Error checking auth status:", err);
    } finally {
      setInitializing(false);
    }
  }

  async function loadStressAnalysis() {
    try {
      setLoading(true);
      setError(null);

      // Try to get real calendar events if authenticated, otherwise use mock data
      let events = mockEvents;
      if (isAuthenticated) {
        try {
          events = await api.getCalendarEvents();
        } catch (err) {
          console.warn("Failed to fetch calendar events, using mock data:", err);
        }
      }

      const result = await api.analyzeStress(events, mockTasks);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analysis");
      console.error("Error loading stress analysis:", err);
    } finally {
      setLoading(false);
    }
  }

  // Show loading spinner when actively analyzing
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing your stress levels...</p>
        </div>
      </div>
    );
  }

  // Show initial state without running analysis
  if (initializing || !prediction) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-6xl mx-auto px-6 py-12">
          {/* Hero Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              Powered by Claude Sonnet 4.5
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
              Clarity AI
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Your intelligent companion for preventing burnout and maintaining peak mental wellness
            </p>
          </div>

          {/* Features Grid - Only show when NOT authenticated */}
          {!isAuthenticated && (
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Smart Calendar Analysis</h3>
                <p className="text-gray-600 text-sm">AI analyzes your schedule to identify burnout risks before they happen</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Personalized Insights</h3>
                <p className="text-gray-600 text-sm">Get specific recommendations tailored to your unique schedule and habits</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Actionable Steps</h3>
                <p className="text-gray-600 text-sm">Receive prioritized interventions ranked by impact and effort</p>
              </div>
            </div>
          )}

          {/* Google Calendar Connection Card */}
          <Card className="border-2 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-lg">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">📅</span>
                  <span>Calendar Connection</span>
                </div>
                {isAuthenticated && (
                  <Badge className="bg-green-100 text-green-700 border-green-200">
                    ✓ Connected
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-base">
                {isAuthenticated
                  ? `Connected to ${calendarProvider} - Select your calendars and run analysis`
                  : "Connect your Google Calendar to unlock personalized burnout prevention insights"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isAuthenticated ? (
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      onClick={loadStressAnalysis}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-semibold shadow-md hover:shadow-lg"
                    >
                      🧠 Run Stress Analysis
                    </button>
                    <button
                      onClick={() => setShowCalendarSelector(!showCalendarSelector)}
                      className="px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                    >
                      {showCalendarSelector ? "Hide" : "📋 Select"} Calendars ({selectedCalendarIds.length})
                    </button>
                    <button
                      onClick={handleDisconnectCalendar}
                      className="px-4 py-3 bg-gray-100 text-gray-600 rounded-lg hover:bg-red-50 hover:text-red-600 transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>

                  {showCalendarSelector && (
                    <div className="border-2 border-blue-100 rounded-lg p-4 bg-blue-50/50">
                      <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                        Select Calendars to Include:
                      </h3>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {availableCalendars.map((calendar) => (
                          <label
                            key={calendar.id}
                            className="flex items-center gap-3 p-3 hover:bg-white rounded-lg cursor-pointer transition-colors border border-transparent hover:border-blue-200"
                          >
                            <input
                              type="checkbox"
                              checked={selectedCalendarIds.includes(calendar.id)}
                              onChange={() => toggleCalendarSelection(calendar.id)}
                              className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <div
                              className="w-4 h-4 rounded-full shadow-sm"
                              style={{ backgroundColor: calendar.backgroundColor }}
                            />
                            <span className="text-sm text-gray-900 font-medium flex-1">
                              {calendar.summary}
                              {calendar.primary && (
                                <span className="ml-2 text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">Primary</span>
                              )}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <button
                    onClick={handleConnectCalendar}
                    className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all flex items-center justify-center gap-3 font-semibold shadow-lg hover:shadow-xl"
                  >
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                    </svg>
                    Connect Google Calendar
                  </button>
                  <p className="text-sm text-gray-500 text-center md:text-left">
                    🔒 Secure OAuth 2.0 authentication • We only read your calendar data
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Bottom Info - Only show when NOT authenticated */}
          {!isAuthenticated && (
            <div className="mt-12 text-center">
              <p className="text-gray-500 mb-6">Trusted by students at top universities worldwide</p>
              <div className="flex items-center justify-center gap-8 text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Privacy First
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                  </svg>
                  Used by 1000+ Students
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                  </svg>
                  Instant Analysis
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  async function handleConnectCalendar() {
    try {
      const { auth_url } = await api.getGoogleAuthUrl();
      window.location.href = auth_url;
    } catch (err) {
      console.error("Error getting auth URL:", err);
      setError("Failed to initiate Google Calendar connection");
    }
  }

  async function handleDisconnectCalendar() {
    try {
      await api.disconnectCalendar();
      setIsAuthenticated(false);
      setCalendarProvider(null);
      setAvailableCalendars([]);
      setSelectedCalendarIds(['primary']);
      setPrediction(null); // Clear prediction to return to initial state
    } catch (err) {
      console.error("Error disconnecting calendar:", err);
      setError("Failed to disconnect calendar");
    }
  }

  async function toggleCalendarSelection(calendarId: string) {
    const newSelection = selectedCalendarIds.includes(calendarId)
      ? selectedCalendarIds.filter(id => id !== calendarId)
      : [...selectedCalendarIds, calendarId];

    // Ensure at least one calendar is selected
    if (newSelection.length === 0) return;

    try {
      await api.setSelectedCalendars(newSelection);
      setSelectedCalendarIds(newSelection);
      // Don't auto-reload - let user select multiple calendars then click "Run Analysis"
    } catch (err) {
      console.error("Error updating calendar selection:", err);
      setError("Failed to update calendar selection");
    }
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{error}</p>
            <button
              onClick={loadStressAnalysis}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!prediction) {
    return null;
  }

  const { stress_score, factors, predictions, interventions } = prediction;

  // Get risk level color
  const getRiskColor = (level: string) => {
    switch (level) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const getRiskBadgeVariant = (level: string) => {
    switch (level) {
      case "critical":
        return "destructive";
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Clarity AI
          </h1>
          <p className="text-gray-600">
            AI-powered burnout prevention for students
          </p>
        </div>

        {/* Google Calendar Connection Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>📅 Calendar Connection</span>
              {isAuthenticated && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Connected
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              {isAuthenticated
                ? `Connected to ${calendarProvider} - Using real calendar data`
                : "Connect your Google Calendar for personalized stress analysis"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isAuthenticated ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={loadStressAnalysis}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {prediction ? "Refresh Analysis" : "Run Analysis"}
                  </button>
                  <button
                    onClick={() => setShowCalendarSelector(!showCalendarSelector)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    {showCalendarSelector ? "Hide" : "Select"} Calendars ({selectedCalendarIds.length})
                  </button>
                  <button
                    onClick={handleDisconnectCalendar}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Disconnect
                  </button>
                </div>

                {showCalendarSelector && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <h3 className="font-semibold text-gray-900 mb-3">Select Calendars to Include:</h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {availableCalendars.map((calendar) => (
                        <label
                          key={calendar.id}
                          className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedCalendarIds.includes(calendar.id)}
                            onChange={() => toggleCalendarSelection(calendar.id)}
                            className="w-4 h-4 text-blue-600 rounded"
                          />
                          <div
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: calendar.backgroundColor }}
                          />
                          <span className="text-sm text-gray-900">
                            {calendar.summary}
                            {calendar.primary && (
                              <span className="ml-2 text-xs text-gray-500">(Primary)</span>
                            )}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={handleConnectCalendar}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                Connect Google Calendar
              </button>
            )}
          </CardContent>
        </Card>

        {/* Stress Score Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Your Stress Level</span>
              <Badge variant={getRiskBadgeVariant(stress_score.risk_level)}>
                {stress_score.risk_level.toUpperCase()}
              </Badge>
            </CardTitle>
            <CardDescription>
              Overall stress score based on your schedule and tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Overall Score */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-2xl font-bold">
                  {Math.round(stress_score.total_score)}/100
                </span>
              </div>
              <Progress
                value={stress_score.total_score}
                className={getRiskColor(stress_score.risk_level)}
              />
            </div>

            {/* Individual Factors */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Calendar Load</p>
                <div className="text-2xl font-bold">
                  {Math.round(stress_score.calendar_factor)}
                </div>
                <Progress value={stress_score.calendar_factor} />
                <p className="text-xs text-gray-500">
                  {factors.events_next_7_days} events this week
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Task Pressure</p>
                <div className="text-2xl font-bold">
                  {Math.round(stress_score.task_factor)}
                </div>
                <Progress value={stress_score.task_factor} />
                <p className="text-xs text-gray-500">
                  {factors.high_priority_tasks} high priority tasks
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Sleep Impact</p>
                <div className="text-2xl font-bold">
                  {Math.round(stress_score.sleep_factor)}
                </div>
                <Progress value={stress_score.sleep_factor} />
                <p className="text-xs text-gray-500">
                  {factors.sleep_hours_available.toFixed(1)} hours available
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Predictions */}
        <Card>
          <CardHeader>
            <CardTitle>🤖 AI Burnout Predictions</CardTitle>
            <CardDescription>
              Generated by Amazon Bedrock (Claude Sonnet 4.5)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {predictions.map((prediction, index) => (
                <div
                  key={index}
                  className="p-4 bg-blue-50 border border-blue-200 rounded-lg"
                >
                  <p className="text-gray-800">{prediction}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Interventions */}
        <Card>
          <CardHeader>
            <CardTitle>💡 Recommended Actions</CardTitle>
            <CardDescription>
              Personalized interventions to reduce burnout risk
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {interventions.map((intervention, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {intervention.title}
                      </h3>
                      <Badge variant="outline" className="mt-1">
                        {intervention.type}
                      </Badge>
                    </div>
                    <Badge variant={getRiskBadgeVariant(intervention.priority)}>
                      {intervention.priority}
                    </Badge>
                  </div>
                  <p className="text-gray-700 mb-3">{intervention.description}</p>
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">Impact:</span>
                      <span className="font-medium text-green-600">
                        {intervention.impact_score}/100
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">Effort:</span>
                      <span className="font-medium text-blue-600">
                        {intervention.effort_score}/100
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Refresh Button */}
        <div className="text-center">
          <button
            onClick={loadStressAnalysis}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
