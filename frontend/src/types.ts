export type Timestamp = number | string;

export interface Project {
  id: string;
  name: string;
  path: string;
  branch: string | null;
  git_state: Record<string, unknown>;
  created_at: Timestamp;
  indexed_at?: Timestamp | null;
  index_stats: {
    file_count?: number;
    symbol_count?: number;
    languages?: Record<string, number> | string[];
    ignored_files?: (string | { path: string; reason: string })[] | number;
    errors?: (string | Record<string, unknown>)[];
    [key: string]: unknown;
  };
}

export interface Session {
  id: string;
  project_id: string;
  task: string;
  created_at: Timestamp;
  last_activity: Timestamp;
  expires_at: Timestamp;
  absolute_expires_at: Timestamp;
  ended_at?: Timestamp | null;
  status?: string;
  memory_count?: number;
}

export interface MemorySource {
  path: string;
  hash: string;
}
export interface Memory {
  id: string;
  session_id: string;
  category: string;
  content: string;
  provenance: string;
  created_at: Timestamp;
  updated_at: Timestamp;
  stale: number | boolean;
  freshness?: string;
  sources: MemorySource[];
}

export interface ContextItem {
  id?: string;
  symbol_id?: string;
  path: string;
  name?: string;
  symbol?: string;
  qualified_name?: string;
  kind?: string;
  signature?: string;
  start_line?: number;
  end_line?: number;
  line_start?: number;
  line_end?: number;
  hash?: string;
  source_hash?: string;
  snippet?: string;
  content?: string;
  reason?: string | string[];
  reasons?: string[];
  score?: number;
  freshness?: string;
  [key: string]: unknown;
}

export interface Dependency {
  id?: string;
  source_file?: string;
  source_symbol?: string | null;
  target_file?: string | null;
  target_symbol?: string | null;
  reference?: string;
  kind?: string;
  resolved?: number | boolean;
  preview_truncated_fields?: string[];
  reference_length?: number;
  [key: string]: unknown;
}

export interface Passport {
  retrieval_id?: string;
  task_id?: string;
  query_id?: string;
  session_id: string;
  status?: string;
  source_freshness?: string | Record<string, unknown>;
  evidence_quality?: string;
  selected_files?: (string | Record<string, unknown>)[];
  selected_symbols?: (string | Record<string, unknown>)[];
  verified_source_hashes?: Record<string, string> | Record<string, unknown>[];
  relevant_dependencies?: Dependency[];
  dependencies?: Dependency[];
  unresolved_dependencies?: (Dependency | string)[];
  related_tests?: (string | Record<string, unknown>)[];
  missing_context?: string[];
  missing_context_indicators?: string[];
  warnings?: string[];
  recommended_next_retrievals?: (string | Record<string, unknown>)[];
  token_budget?: number;
  budget?: number;
  estimated_tokens?: number;
  estimated_tokens_returned?: number;
  [key: string]: unknown;
}

export interface Retrieval {
  retrieval_id: string;
  session_id: string;
  project_id: string;
  query: string;
  level: number;
  budget: number;
  estimated_tokens: number;
  token_estimate_method?: string;
  items: ContextItem[];
  memories: Memory[];
  dependencies: Dependency[];
  warnings: string[];
  truncated: boolean;
  passport: Passport;
  session_events?: {
    id: string;
    type: string;
    created_at: Timestamp;
    path: string;
    deleted: boolean;
  }[];
  session_event_scope?: string;
}

export interface RetrievalRecord {
  id: string;
  session_id: string;
  project_id: string;
  query: string;
  level: number;
  budget: number;
  estimated_tokens: number;
  created_at: Timestamp;
}

export interface Event {
  id: string;
  project_id: string;
  session_id?: string | null;
  type: string;
  detail: Record<string, unknown>;
  created_at: Timestamp;
}

export interface Settings {
  session_ttl_minutes: number;
  max_session_hours: number;
  context_token_budget: number;
  ignored_directories: string[];
  max_file_size: number;
  watch_enabled: boolean;
  event_logging: boolean;
  theme: "dark" | "light" | "system";
}

export interface Overview {
  status: string;
  service: string;
  version: string;
  mcp: { status: string; detail: string };
  counts: {
    projects: number;
    sessions: number;
    files: number;
    symbols: number;
    memories: number;
    retrievals: number;
    database_bytes: number;
  };
  projects: Project[];
  sessions: Session[];
  recent_retrievals: RetrievalRecord[];
  recent_events: Event[];
  warnings: string[];
  settings: Settings;
}
