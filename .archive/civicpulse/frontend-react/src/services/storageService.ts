import { initialComplaints } from '../data/initialComplaints';
import type { Complaint } from '../types/complaint';

const KEY = 'civicpulse_demo_complaints_v1';
const isComplaint = (value: unknown): value is Complaint => {
  if (!value || typeof value !== 'object') return false;
  const item = value as Partial<Complaint>;
  return typeof item.id === 'string' && typeof item.title === 'string' && typeof item.category === 'string' && typeof item.description === 'string' && typeof item.location === 'string' && typeof item.reportedAt === 'string' && typeof item.updatedAt === 'string' && typeof item.priorityScore === 'number' && Array.isArray(item.timeline);
};
export function loadComplaints(): Complaint[] {
  try {
    const stored = window.localStorage.getItem(KEY);
    if (!stored) return initialComplaints;
    const parsed: unknown = JSON.parse(stored);
    if (Array.isArray(parsed) && parsed.every(isComplaint)) return parsed;
    console.warn('CivicPulse demo data was invalid. Restoring sample records.');
    window.localStorage.removeItem(KEY);
  } catch (error) { console.warn('CivicPulse local storage unavailable; using sample records.', error); }
  return initialComplaints;
}
export function saveComplaints(items: Complaint[]): boolean {
  try { window.localStorage.setItem(KEY, JSON.stringify(items)); return true; }
  catch (error) { console.warn('Could not save CivicPulse demo data.', error); return false; }
}
