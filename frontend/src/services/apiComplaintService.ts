/**
 * CivicPulse API Complaint Service
 *
 * Backend-backed complaint data service.
 * Replaces localStorage-based data with live API calls.
 * All complaint data is persisted in SQLite backend.
 */

import { apiGet, apiPost, apiPatch, apiPut } from './apiClient';
import type { Complaint, NewComplaint } from '../types/complaint';

/**
 * Map backend response to frontend Complaint type
 */
function mapBackendToFrontend(backend: any): Complaint {
  return {
    id: backend.id,
    title: backend.title,
    description: backend.description,
    category: backend.category,
    location: backend.location_text, // Map field name
    latitude: backend.latitude,
    longitude: backend.longitude,
    ward: backend.ward,
    assetId: backend.asset_id, // Map field name
    reportedAt: backend.reported_at,
    updatedAt: backend.updated_at,
    status: backend.status,
    priorityLevel: backend.priority, // Map field name
    priorityScore: backend.priority_score, // Map field name
    repeatComplaintCount: backend.repeat_complaint_count, // Map field name
    assignedTeam: backend.assigned_team,
    imageReference: backend.image_reference,
    timeline: (backend.timeline_entries || []).map((entry: any) => ({
      status: entry.status,
      at: entry.timestamp,
      note: entry.note,
    })),
  };
}

/**
 * Map frontend NewComplaint to backend request format
 */
function mapFrontendToBackend(frontend: NewComplaint) {
  return {
    title: frontend.title,
    description: frontend.description,
    category: frontend.category,
    location_text: frontend.location,
    latitude: frontend.latitude,
    longitude: frontend.longitude,
    ward: frontend.ward,
    asset_id: frontend.assetId,
  };
}

/**
 * API Complaint Service
 *
 * All methods return data from the backend API.
 * Data is persisted in SQLite and survives page refreshes.
 */
export const apiComplaintService = {
  /**
   * Get all complaints with optional filtering and pagination
   */
  async getComplaints(options?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
    category?: string;
    ward?: string;
  }): Promise<Complaint[]> {
    try {
      const response = await apiGet<any>('/api/complaints', {
        skip: options?.skip || 0,
        limit: options?.limit || 100,
        ...(options?.status && { status: options.status }),
        ...(options?.priority && { priority: options.priority }),
        ...(options?.category && { category: options.category }),
        ...(options?.ward && { ward: options.ward }),
      });

      // Handle paginated response (may be wrapped in items property)
      let items = response.items || response;
      
      // Ensure we have an array
      if (!Array.isArray(items)) {
        console.warn('Unexpected response format, expected array or paginated object', response);
        items = [];
      }
      
      return items.map(mapBackendToFrontend);
    } catch (error) {
      console.error('Failed to fetch complaints:', error);
      throw error;
    }
  },

  /**
   * Get a single complaint by ID
   */
  async getComplaintById(id: string): Promise<Complaint> {
    try {
      const response = await apiGet<any>(`/api/complaints/${id}`);
      return mapBackendToFrontend(response);
    } catch (error) {
      console.error(`Failed to fetch complaint ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new complaint
   *
   * Returns the created complaint with auto-generated ID and initial status.
   */
  async createComplaint(input: NewComplaint): Promise<Complaint> {
    try {
      const backendData = mapFrontendToBackend(input);
      const response = await apiPost<any>('/api/complaints', backendData);
      return mapBackendToFrontend(response);
    } catch (error) {
      console.error('Failed to create complaint:', error);
      throw error;
    }
  },

  /**
   * Update complaint fields (PATCH)
   */
  async updateComplaint(id: string, updates: Partial<Complaint>): Promise<Complaint> {
    try {
      // Map frontend field names to backend
      const backendUpdates: any = {};
      if (updates.priorityLevel) backendUpdates.priority = updates.priorityLevel;
      if (updates.priorityScore !== undefined) backendUpdates.priority_score = updates.priorityScore;
      if (updates.repeatComplaintCount !== undefined) backendUpdates.repeat_complaint_count = updates.repeatComplaintCount;
      if (updates.title) backendUpdates.title = updates.title;
      if (updates.description) backendUpdates.description = updates.description;
      if (updates.assignedTeam) backendUpdates.assigned_team = updates.assignedTeam;

      const response = await apiPatch<any>(`/api/complaints/${id}`, backendUpdates);
      return mapBackendToFrontend(response);
    } catch (error) {
      console.error(`Failed to update complaint ${id}:`, error);
      throw error;
    }
  },

  /**
   * Update complaint status (status transition with validation)
   */
  async updateComplaintStatus(
    id: string,
    status: string,
    note?: string
  ): Promise<Complaint> {
    try {
      const response = await apiPut<any>(`/api/complaints/${id}/status`, {
        status,
        note: note || undefined,
      });
      return mapBackendToFrontend(response);
    } catch (error) {
      console.error(`Failed to update complaint ${id} status:`, error);
      throw error;
    }
  },

  /**
   * Get AI priority evaluation for a complaint
   *
   * Returns priority category, score, and explanation.
   * May show "development-mock-v1" for demo/development.
   */
  async getComplaintPriority(id: string): Promise<{
    complaint_id: string;
    priority_category: string;
    priority_score: number;
    explanation: string;
    contributing_factors?: string[];
    model_version: string;
    timestamp: string;
  }> {
    try {
      return await apiGet<any>(`/api/complaints/${id}/priority`);
    } catch (error) {
      console.error(`Failed to get priority for complaint ${id}:`, error);
      throw error;
    }
  },

  /**
   * Evaluate complaint priority (trigger re-evaluation)
   */
  async evaluateComplaintPriority(id: string): Promise<{
    complaint_id: string;
    priority_category: string;
    priority_score: number;
    explanation: string;
    contributing_factors?: string[];
    model_version: string;
    timestamp: string;
  }> {
    try {
      return await apiPost<any>(
        `/api/complaints/${id}/priority/evaluate`,
        {}
      );
    } catch (error) {
      console.error(`Failed to evaluate priority for complaint ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get complaint timeline
   */
  async getComplaintTimeline(id: string): Promise<any[]> {
    try {
      return await apiGet<any>(`/api/complaints/${id}/timeline`);
    } catch (error) {
      console.error(`Failed to fetch timeline for complaint ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(days: number = 30): Promise<{
    timestamp: string;
    period_days: number;
    complaints: {
      total: number;
      open: number;
      resolved: number;
      recent: number;
      high_repeat_issues: number;
      average_priority_score: number;
    };
    status_distribution: Record<string, number>;
    category_distribution: Record<string, number>;
    repairs: {
      total_records: number;
      verified: number;
      failed: number;
      pending: number;
      rejected: number;
    };
    teams_active: number;
  }> {
    try {
      return await apiGet<any>('/api/dashboard/stats', {
        days: Math.max(1, Math.min(365, days)),
      });
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      throw error;
    }
  },

  /**
   * Get map data (all geolocated complaints and assets for map display)
   */
  async getMapData(options?: {
    priority_filter?: string;
    status_filter?: string;
    asset_type_filter?: string;
    ward_filter?: string;
    coordinates_only?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<{
    complaints: any[];
    assets: any[];
    total_count: number;
  }> {
    try {
      return await apiGet<any>('/api/dashboard/map-data', {
        priority_filter: options?.priority_filter,
        status_filter: options?.status_filter,
        asset_type_filter: options?.asset_type_filter,
        ward_filter: options?.ward_filter,
        coordinates_only: options?.coordinates_only || true,
        skip: options?.skip || 0,
        limit: options?.limit || 500,
      });
    } catch (error) {
      console.error('Failed to fetch map data:', error);
      throw error;
    }
  },

  /**
   * Get all complaints as a collection (same as getComplaints with defaults)
   *
   * Used by components that just want all data without pagination concerns.
   */
  async getAllComplaints(): Promise<Complaint[]> {
    return this.getComplaints({ limit: 1000 });
  },

  /**
   * Search/filter complaints
   *
   * Combines getComplaints with query string matching.
   */
  async searchComplaints(query: string): Promise<Complaint[]> {
    if (!query.trim()) {
      return this.getComplaints();
    }

    try {
      const all = await this.getComplaints({ limit: 1000 });
      const q = query.trim().toLowerCase();

      return all.filter(item =>
        [item.id, item.title, item.location, item.assetId || '']
          .some(v => v.toLowerCase().includes(q))
      );
    } catch (error) {
      console.error('Search failed:', error);
      return [];
    }
  },

  /**
   * Filter complaints by multiple criteria
   */
  async filterComplaints(filters: {
    category?: string;
    status?: string;
    priority?: string;
    ward?: string;
    query?: string;
  }): Promise<Complaint[]> {
    return this.getComplaints({
      category: filters.category,
      status: filters.status,
      priority: filters.priority,
      ward: filters.ward,
    });
  },
};

/**
 * Workflow stages (same as backend)
 */
export const workflowStages = [
  'Reported',
  'Under Review',
  'Assigned',
  'In Progress',
  'Awaiting Verification',
  'Resolved',
] as const;

export type WorkflowStage = typeof workflowStages[number];
