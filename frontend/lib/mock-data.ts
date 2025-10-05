// Mock data for demo purposes (UCLA student schedule)

import { CalendarEvent, Task } from "./types";

export const mockEvents: CalendarEvent[] = [
  {
    id: "1",
    summary: "MATH 32A Lecture",
    start: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
    end: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), // 3 hours from now
    description: "Linear Algebra",
  },
  {
    id: "2",
    summary: "CHEM 20A Lab",
    start: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4 hours from now
    end: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(), // 6 hours from now
    description: "Chemistry Lab",
  },
  {
    id: "3",
    summary: "ENGCOMP 3",
    start: new Date(Date.now() + 25 * 60 * 60 * 1000).toISOString(), // ~1 day from now
    end: new Date(Date.now() + 26 * 60 * 60 * 1000).toISOString(),
    description: "English Composition",
  },
];

export const mockTasks: Task[] = [
  {
    id: "1",
    title: "MATH 32A Homework",
    description: "Complete problem set 3",
    due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days from now
    priority: "high",
    completed: false,
  },
  {
    id: "2",
    title: "CHEM Quiz Prep",
    description: "Study chapters 4-6",
    due_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day from now
    priority: "high",
    completed: false,
  },
  {
    id: "3",
    title: "Read Chapter 5",
    description: "English reading assignment",
    due_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days from now
    priority: "medium",
    completed: false,
  },
];
