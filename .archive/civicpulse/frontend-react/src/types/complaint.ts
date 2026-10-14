export type ComplaintStatus = 'Reported' | 'Under Review' | 'Assigned' | 'In Progress' | 'Awaiting Verification' | 'Resolved';
export type PriorityLevel = 'Low' | 'Medium' | 'High' | 'Critical';
export interface TimelineEvent { status: ComplaintStatus; at: string; note: string }
export interface Complaint {
  id: string; title: string; category: string; description: string; location: string;
  ward?: string; assetId?: string; reportedAt: string; updatedAt: string; status: ComplaintStatus;
  priorityLevel: PriorityLevel; priorityScore: number; repeatComplaintCount: number;
  assignedTeam?: string; imageReference?: string; timeline: TimelineEvent[];
  latitude?: number; longitude?: number;
}
export type NewComplaint = Pick<Complaint, 'title' | 'category' | 'description' | 'location'> & Partial<Pick<Complaint, 'ward' | 'assetId' | 'latitude' | 'longitude'>>;
