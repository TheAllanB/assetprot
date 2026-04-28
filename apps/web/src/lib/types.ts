export interface User {
  id: string;
  email: string;
  org_id: string;
  is_active: boolean;
  created_at: string;
}

export interface Asset {
  id: string;
  org_id: string;
  title: string;
  content_type: string;
  status: string;
  territories: string[];
  rights_metadata: Record<string, unknown> | null;
  blockchain_tx_hash: string | null;
  created_at: string;
  updated_at: string;
}

export interface Violation {
  id: string;
  asset_id: string;
  discovered_url: string;
  platform: string;
  status: string;
  confidence: number;
  infringement_type: string | null;
  transformation_types: string[];
  estimated_reach: number | null;
  rights_territory_violation: boolean;
  detected_at: string;
  resolved_at: string | null;
}

export interface ScanRun {
  id: string;
  asset_id: string;
  status: string;
  violations_found: number;
  errors: Record<string, unknown> | null;
  run_at: string;
}

export interface TaskStatus {
  id: string;
  status: string;
  result: Record<string, unknown> | null;
  error: string | null;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  error?: { code: string; message: string };
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  meta: {
    total: number;
    offset: number;
    limit: number;
  };
}