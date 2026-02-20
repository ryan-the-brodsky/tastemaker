import type {
  AuthResponse,
  User,
  Session,
  Comparison,
  SessionProgress,
  StyleRule,
  SkillGenerateResponse,
  QuestionAnswer,
  LockInRequest,
  LockInResponse,
  StudioProgress,
  ComponentDimensions,
  ComponentState,
  DimensionChoiceSubmit,
  CheckpointData,
  LockComponentResponse,
  ComponentStyles,
} from '../types';

const API_BASE = '/api';

class ApiService {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    signal?: AbortSignal
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      signal,
    });

    if (!response.ok) {
      // Handle 401 Unauthorized - clear token and redirect to login
      if (response.status === 401) {
        this.setToken(null);
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
      }

      // Handle 403 Premium gating
      if (response.status === 403) {
        const errorBody = await response.json().catch(() => ({ detail: 'Access denied' }));
        if (typeof errorBody.detail === 'string' && errorBody.detail.includes('Premium subscription required')) {
          throw new Error('This feature requires a Premium subscription. Upgrade to access interactive video audits.');
        }
        throw new Error(typeof errorBody.detail === 'string' ? errorBody.detail : 'Access denied');
      }

      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      // Handle FastAPI validation errors (422) where detail is an array
      let errorMessage = 'Request failed';
      if (error.detail) {
        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else if (Array.isArray(error.detail)) {
          // FastAPI validation error format: [{loc: [...], msg: "...", type: "..."}]
          errorMessage = error.detail
            .map((e: { msg?: string; loc?: string[] }) => e.msg || 'Validation error')
            .join(', ');
        } else if (typeof error.detail === 'object') {
          errorMessage = JSON.stringify(error.detail);
        }
      }
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  }

  // Auth endpoints
  async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.access_token);
    return response;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  // Session endpoints
  async createSession(name: string, projectDescription?: string, brandColors?: string[]): Promise<Session> {
    return this.request<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({
        name,
        project_description: projectDescription || null,
        brand_colors: brandColors,
      }),
    });
  }

  async getSessions(): Promise<Session[]> {
    return this.request<Session[]>('/sessions');
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.request<Session>(`/sessions/${sessionId}`);
  }

  async deleteSession(sessionId: string): Promise<void> {
    return this.request<void>(`/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // Comparison endpoints
  async getComparison(sessionId: string): Promise<Comparison> {
    return this.request<Comparison>(`/sessions/${sessionId}/comparison`);
  }

  async submitChoice(
    sessionId: string,
    comparisonId: number,  // sequential counter, not UUID
    choice: 'a' | 'b' | 'none',
    decisionTimeMs: number,
    answers?: QuestionAnswer[]
  ): Promise<SessionProgress> {
    return this.request<SessionProgress>(
      `/sessions/${sessionId}/comparison/${comparisonId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          choice,
          decision_time_ms: decisionTimeMs,
          answers: answers || null,
        }),
      }
    );
  }

  // Lock-in endpoint for "That's it!" button in color/typography phases
  async lockInChoice(
    sessionId: string,
    data: LockInRequest
  ): Promise<LockInResponse> {
    return this.request<LockInResponse>(
      `/sessions/${sessionId}/lock-in`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  // Rule endpoints
  async getRules(sessionId: string): Promise<StyleRule[]> {
    return this.request<StyleRule[]>(`/sessions/${sessionId}/rules`);
  }

  async addRule(
    sessionId: string,
    statement: string,
    component?: string
  ): Promise<StyleRule> {
    return this.request<StyleRule>(`/sessions/${sessionId}/rules`, {
      method: 'POST',
      body: JSON.stringify({ statement, component }),
    });
  }

  async updateRule(
    sessionId: string,
    ruleId: string,
    updates: { value?: unknown; severity?: string; message?: string }
  ): Promise<StyleRule> {
    return this.request<StyleRule>(`/sessions/${sessionId}/rules/${ruleId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  async deleteRule(sessionId: string, ruleId: string): Promise<void> {
    return this.request<void>(`/sessions/${sessionId}/rules/${ruleId}`, {
      method: 'DELETE',
    });
  }

  // Skill endpoints
  async generateSkill(sessionId: string): Promise<SkillGenerateResponse> {
    return this.request<SkillGenerateResponse>(
      `/sessions/${sessionId}/generate-skill`,
      { method: 'POST' }
    );
  }

  getSkillDownloadUrl(skillId: string): string {
    return `${API_BASE}/skills/${skillId}/download`;
  }

  // Audit endpoints
  async auditScreenshot(formData: FormData): Promise<{
    violations: Array<{
      rule_id: string;
      severity: 'error' | 'warning' | 'info';
      property: string;
      expected: string;
      found: string;
      message: string;
      suggestion: string;
    }>;
    summary: string;
    score: number;
  }> {
    const token = this.getToken();
    const response = await fetch(`${API_BASE}/audit/screenshot`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Audit failed' }));
      throw new Error(error.detail || 'Audit failed');
    }

    return response.json();
  }

  async auditUrl(url: string, sessionId: string): Promise<{
    violations: Array<{
      rule_id: string;
      severity: 'error' | 'warning' | 'info';
      property: string;
      expected: string;
      found: string;
      message: string;
      suggestion: string;
    }>;
    summary: string;
    score: number;
  }> {
    return this.request('/audit/url', {
      method: 'POST',
      body: JSON.stringify({ url, session_id: sessionId }),
    });
  }

  // Interactive Video Audit endpoints
  async submitVideoAudit(formData: FormData): Promise<VideoAuditRecording> {
    const token = this.getToken();
    const response = await fetch(`${API_BASE}/audit/interactive/video`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Video upload failed' }));
      throw new Error(error.detail || 'Video upload failed');
    }

    return response.json();
  }

  async getVideoRecordingStatus(recordingId: string): Promise<VideoAuditRecording> {
    return this.request<VideoAuditRecording>(`/audit/interactive/recording/${recordingId}`);
  }

  async getVideoAuditResults(recordingId: string): Promise<InteractiveAuditResult> {
    return this.request<InteractiveAuditResult>(`/audit/interactive/recording/${recordingId}/results`);
  }

  // Generator endpoints
  async generateComponent(data: {
    session_id: string;
    component_type: string;
    variant: string;
    output_format: string;
    custom_prompt?: string;
  }): Promise<{ code: string }> {
    return this.request<{ code: string }>('/generate/component', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Component library export
  async exportComponentLibrary(sessionId: string, format: string = 'react'): Promise<Blob> {
    const token = this.getToken();
    const formData = new FormData();
    formData.append('session_id', sessionId.toString());
    formData.append('output_format', format);

    const response = await fetch(`${API_BASE}/generate/library`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Export failed' }));
      throw new Error(error.detail || 'Export failed');
    }

    return response.blob();
  }

  // Mockup generation
  async generateMockupPngs(sessionId: string): Promise<{ mockups: string[] }> {
    return this.request<{ mockups: string[] }>(
      `/sessions/${sessionId}/generate-mockup-pngs`,
      { method: 'POST' }
    );
  }

  // Exploration endpoints (trie-style color/typography discovery)
  async getPaletteOptions(sessionId: string, signal?: AbortSignal): Promise<ExplorationResponse> {
    return this.request<ExplorationResponse>(`/sessions/${sessionId}/explore/palettes`, {}, signal);
  }

  async selectPalette(
    sessionId: string,
    selectedOptionId: string,
    selectedOption: Record<string, unknown>,
    wantsRefinement: boolean = true
  ): Promise<ExplorationProgressResponse> {
    return this.request<ExplorationProgressResponse>(
      `/sessions/${sessionId}/explore/palettes/select`,
      {
        method: 'POST',
        body: JSON.stringify({
          selected_option_id: selectedOptionId,
          selected_option: selectedOption,
          wants_refinement: wantsRefinement,
        }),
      }
    );
  }

  async getTypographyOptions(sessionId: string, signal?: AbortSignal): Promise<ExplorationResponse> {
    return this.request<ExplorationResponse>(`/sessions/${sessionId}/explore/typography`, {}, signal);
  }

  async selectTypography(
    sessionId: string,
    selectedOptionId: string,
    selectedOption: Record<string, unknown>,
    wantsRefinement: boolean = true
  ): Promise<ExplorationProgressResponse> {
    return this.request<ExplorationProgressResponse>(
      `/sessions/${sessionId}/explore/typography/select`,
      {
        method: 'POST',
        body: JSON.stringify({
          selected_option_id: selectedOptionId,
          selected_option: selectedOption,
          wants_refinement: wantsRefinement,
        }),
      }
    );
  }

  // Component Studio endpoints
  async getStudioProgress(sessionId: string): Promise<StudioProgress> {
    return this.request<StudioProgress>(`/sessions/${sessionId}/studio/progress`);
  }

  async getComponentDimensions(sessionId: string, componentType: string): Promise<ComponentDimensions> {
    return this.request<ComponentDimensions>(`/sessions/${sessionId}/studio/component/${componentType}/dimensions`);
  }

  async getComponentState(sessionId: string, componentType: string): Promise<ComponentState> {
    return this.request<ComponentState>(`/sessions/${sessionId}/studio/component/${componentType}/state`);
  }

  async submitDimensionChoice(
    sessionId: string,
    componentType: string,
    choice: DimensionChoiceSubmit
  ): Promise<{ success: boolean; dimension_index: number; total_dimensions: number }> {
    return this.request(`/sessions/${sessionId}/studio/component/${componentType}/dimension`, {
      method: 'POST',
      body: JSON.stringify(choice),
    });
  }

  async lockComponent(sessionId: string): Promise<LockComponentResponse> {
    return this.request<LockComponentResponse>(`/sessions/${sessionId}/studio/component/lock`, {
      method: 'POST',
    });
  }

  async getCheckpointData(sessionId: string, checkpointId: string): Promise<CheckpointData> {
    return this.request<CheckpointData>(`/sessions/${sessionId}/studio/checkpoint/${checkpointId}`);
  }

  async approveCheckpoint(
    sessionId: string,
    checkpointId: string
  ): Promise<{ success: boolean; next_component: string | null; is_studio_complete: boolean }> {
    return this.request(`/sessions/${sessionId}/studio/checkpoint/${checkpointId}/approve`, {
      method: 'POST',
    });
  }

  async goBackToComponent(sessionId: string, componentType: string): Promise<{ success: boolean }> {
    return this.request(`/sessions/${sessionId}/studio/component/${componentType}/go-back`, {
      method: 'POST',
    });
  }

  async getPreviewStyles(sessionId: string): Promise<ComponentStyles> {
    return this.request<ComponentStyles>(`/sessions/${sessionId}/studio/preview-styles`);
  }

  // Batch comparison endpoint for faster A/B testing
  async getBatchComparisons(
    sessionId: string,
    batchSize: number = 5,
    recentChoices?: Array<{ component_type: string; choice: string }>
  ): Promise<BatchComparisonResponse> {
    return this.request<BatchComparisonResponse>(
      `/sessions/${sessionId}/comparisons/batch`,
      {
        method: 'POST',
        body: JSON.stringify({
          batch_size: batchSize,
          recent_choices: recentChoices || null,
        }),
      }
    );
  }
}

// Exploration types
export interface ExplorationResponse {
  options: ExplorationOption[];
  context?: string;
  exploration_depth: number;
  exploration_type: 'palette' | 'typography';
  can_lock_in: boolean;
}

export interface ExplorationOption {
  id: string;
  name: string;
  category: string;
  description?: string;
  // For palettes
  primary?: string;
  secondary?: string;
  accent?: string;
  accentSoft?: string;
  background?: string;
  // For typography
  heading?: string;
  body?: string;
  headingCategory?: string;
  bodyCategory?: string;
}

export interface ExplorationProgressResponse {
  success: boolean;
  exploration_depth: number;
  next_options?: ExplorationOption[];
  locked_in: boolean;
  new_phase?: string;
  message: string;
}

// Batch comparison types
export interface BatchComparisonResponse {
  comparisons: Comparison[];
  batch_id: string;
  has_more: boolean;
}

// Interactive Video Audit types
export interface VideoAuditRecording {
  id: string;
  session_id: string;
  source_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  frame_count: number;
  duration_ms?: number;
}

export interface InteractiveAuditViolation {
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  measured_value?: number;
  threshold?: number;
}

export interface InteractiveAuditResult {
  recording_id: string;
  total_frames: number;
  duration_ms?: number;
  temporal_violations: InteractiveAuditViolation[];
  spatial_violations: InteractiveAuditViolation[];
  behavioral_violations: InteractiveAuditViolation[];
  pattern_violations: InteractiveAuditViolation[];
  summary: {
    total_violations: number;
    errors: number;
    warnings: number;
    temporal_metrics_count: number;
    frames_analyzed: number;
  };
}

export const api = new ApiService();
