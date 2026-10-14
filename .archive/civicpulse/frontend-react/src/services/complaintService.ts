import { loadComplaints, saveComplaints } from './storageService';
import type { Complaint, NewComplaint } from '../types/complaint';

let complaints = loadComplaints();
const stages: Complaint['status'][] = ['Reported','Under Review','Assigned','In Progress','Awaiting Verification','Resolved'];
export const complaintService = {
  getAllComplaints: () => [...complaints],
  getComplaintById: (id: string) => complaints.find(item => item.id.toUpperCase() === id.trim().toUpperCase()),
  searchComplaints: (query: string) => { const q = query.trim().toLowerCase(); return q ? complaints.filter(item => [item.id,item.title,item.location,item.assetId ?? ''].some(v => v.toLowerCase().includes(q))) : [...complaints]; },
  createComplaint: (input: NewComplaint): { complaint: Complaint; saved: boolean } => {
    const year = new Date().getFullYear();
    const sequences = complaints.map(item => Number(item.id.match(/(\d+)$/)?.[1] ?? 0));
    let sequence = Math.max(100, ...sequences) + 1;
    let id = `CP-${year}-${String(sequence).padStart(4,'0')}`;
    while (complaints.some(item => item.id === id)) { sequence += 1; id = `CP-${year}-${String(sequence).padStart(4,'0')}`; }
    const now = new Date().toISOString();
    const complaint: Complaint = { ...input, id, reportedAt:now, updatedAt:now, status:'Reported', priorityLevel:'Medium', priorityScore:50, repeatComplaintCount:0, timeline:[{status:'Reported',at:now,note:'Your report was received in this local demonstration.'}] };
    const next = [complaint, ...complaints];
    const saved = saveComplaints(next);
    if (saved) complaints = next;
    return { complaint, saved };
  },
  updateComplaint: (id: string, updates: Partial<Complaint>) => { complaints = complaints.map(item => item.id === id ? { ...item, ...updates } : item); return saveComplaints(complaints); },
  filterComplaints: (filters: { category?:string; status?:string; priority?:string; ward?:string; query?:string }) => complaintService.searchComplaints(filters.query ?? '').filter(item => (!filters.category || item.category === filters.category) && (!filters.status || item.status === filters.status) && (!filters.priority || item.priorityLevel === filters.priority) && (!filters.ward || item.ward === filters.ward))
};
export const workflowStages = stages;
