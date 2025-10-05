"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BurnoutPrediction } from "@/lib/types";
import { api } from "@/lib/api";
import { mockEvents, mockTasks } from "@/lib/mock-data";

export function StressDashboard() {
  const [prediction, setPrediction] = useState<BurnoutPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [calendarProvider, setCalendarProvider] = useState<string | null>(null);

  useEffect(() => {
    checkAuthStatus();
    loadStressAnalysis();
  }, []);

  async function checkAuthStatus() {
    try {
      const status = await api.getAuthStatus();
      setIsAuthenticated(status.authenticated);
      setCalendarProvider(status.provider);
    } catch (err) {
      console.error("Error checking auth status:", err);
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
      loadStressAnalysis(); // Reload with mock data
    } catch (err) {
      console.error("Error disconnecting calendar:", err);
      setError("Failed to disconnect calendar");
    }
  }

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
            Burnout Prevention Agent
          </h1>
          <p className="text-gray-600">
            AI-powered stress analysis using Amazon Bedrock
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
              <div className="flex items-center gap-4">
                <button
                  onClick={loadStressAnalysis}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Sync Calendar
                </button>
                <button
                  onClick={handleDisconnectCalendar}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Disconnect
                </button>
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
