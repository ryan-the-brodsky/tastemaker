import { createContext, useContext, useState, useRef, useCallback, ReactNode } from 'react';
import type { Session, Comparison, StyleRule, SkillGenerateResponse, QuestionAnswer } from '../types';
import { api } from '../services/api';

interface RecentChoice {
  component_type: string;
  choice: string;
}

interface SessionContextType {
  currentSession: Session | null;
  sessions: Session[];
  comparison: Comparison | null;
  rules: StyleRule[];
  loading: boolean;
  loadingBatch: boolean;  // Separate loading state for background batch loading
  submitting: boolean;    // Background submission in progress (doesn't block UI)
  error: string | null;
  comparisonQueue: Comparison[];
  loadSessions: () => Promise<void>;
  createSession: (name: string, projectDescription?: string, brandColors?: string[]) => Promise<Session>;
  selectSession: (sessionId: number) => Promise<void>;
  refreshSession: () => Promise<void>;
  loadComparison: () => Promise<void>;
  loadBatchComparisons: () => Promise<void>;
  submitChoice: (choice: 'a' | 'b' | 'none', decisionTimeMs: number, answers?: QuestionAnswer[]) => Promise<void>;
  loadRules: () => Promise<void>;
  addRule: (statement: string, component?: string) => Promise<void>;
  deleteRule: (ruleId: string) => Promise<void>;
  generateSkill: () => Promise<SkillGenerateResponse>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [comparisonQueue, setComparisonQueue] = useState<Comparison[]>([]);
  const [rules, setRules] = useState<StyleRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingBatch, setLoadingBatch] = useState(false);
  const [submitting, setSubmitting] = useState(false);  // Background submission state
  const [error, setError] = useState<string | null>(null);

  // Track recent choices for adaptive batch generation
  const recentChoices = useRef<RecentChoice[]>([]);
  // Track if a batch request is already in flight
  const batchRequestInFlight = useRef(false);
  // Track pending submission for error recovery
  const pendingSubmission = useRef<{
    comparisonId: number;
    choice: 'a' | 'b' | 'none';
    decisionTimeMs: number;
    answers?: QuestionAnswer[];
  } | null>(null);

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSessions();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const createSession = async (name: string, projectDescription?: string, brandColors?: string[]) => {
    setLoading(true);
    setError(null);
    try {
      const session = await api.createSession(name, projectDescription, brandColors);
      setSessions(prev => [session, ...prev]);
      setCurrentSession(session);
      return session;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const selectSession = async (sessionId: number) => {
    setLoading(true);
    setError(null);
    try {
      const session = await api.getSession(sessionId);
      setCurrentSession(session);
      setComparison(null);
      setRules([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Refresh the current session from the server (after lock-in, etc.)
  const refreshSession = async () => {
    if (!currentSession) return;
    setError(null);
    try {
      const session = await api.getSession(currentSession.id);
      setCurrentSession(session);
      // Clear any stale comparison data when session is refreshed
      // This prevents old A/B comparisons from briefly appearing during phase transitions
      setComparison(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh session');
      throw err;
    }
  };

  const loadComparison = async () => {
    if (!currentSession) return;

    // Check if we have pre-loaded comparisons in the queue
    if (comparisonQueue.length > 0) {
      const [nextComparison, ...rest] = comparisonQueue;
      setComparison(nextComparison);
      setComparisonQueue(rest);

      // If queue is getting low and we're in a batch-supported phase, request more
      if (rest.length <= 2 && !batchRequestInFlight.current) {
        loadBatchComparisons();
      }
      return;
    }

    // Fall back to single comparison loading
    setLoading(true);
    setError(null);
    try {
      const comp = await api.getComparison(currentSession.id);
      setComparison(comp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load comparison');
    } finally {
      setLoading(false);
    }
  };

  // Load a batch of comparisons for faster transitions
  const loadBatchComparisons = useCallback(async () => {
    if (!currentSession) return;
    if (batchRequestInFlight.current) return;  // Prevent duplicate requests

    // Only use batch for territory_mapping and dimension_isolation phases
    if (!['territory_mapping', 'dimension_isolation'].includes(currentSession.phase)) {
      return loadComparison();
    }

    batchRequestInFlight.current = true;
    setLoadingBatch(true);
    setError(null);

    try {
      const response = await api.getBatchComparisons(
        currentSession.id,
        5,  // Batch size
        recentChoices.current.slice(-3)  // Send last 3 choices for context
      );

      const comparisons = response.comparisons;

      if (comparisons.length > 0) {
        // If we don't have a current comparison, set the first one immediately
        if (!comparison && comparisonQueue.length === 0) {
          setComparison(comparisons[0]);
          setComparisonQueue(comparisons.slice(1));
        } else {
          // Otherwise add to the queue
          setComparisonQueue(prev => [...prev, ...comparisons]);
        }
      }
    } catch (err) {
      console.error('Batch loading failed, falling back to single:', err);
      // Fall back to single comparison loading on error
      await loadComparison();
    } finally {
      setLoadingBatch(false);
      batchRequestInFlight.current = false;
    }
  }, [currentSession, comparison, comparisonQueue]);

  const submitChoice = async (choice: 'a' | 'b' | 'none', decisionTimeMs: number, answers?: QuestionAnswer[]) => {
    if (!currentSession || !comparison) return;
    setError(null);

    // Track this choice for adaptive batch generation
    recentChoices.current.push({
      component_type: comparison.component_type,
      choice,
    });
    // Keep only last 5 choices
    if (recentChoices.current.length > 5) {
      recentChoices.current = recentChoices.current.slice(-5);
    }

    const currentComparisonId = comparison.comparison_id;

    // OPTIMISTIC UI: If we have preloaded comparisons, show the next one immediately
    // This makes transitions feel instant while submission happens in background
    const hasPreloadedComparison = comparisonQueue.length > 0;

    if (hasPreloadedComparison) {
      // Immediately show next comparison from queue (no waiting for backend)
      const [nextComparison, ...rest] = comparisonQueue;
      setComparison(nextComparison);
      setComparisonQueue(rest);

      // Trigger batch loading if queue is getting low
      if (rest.length <= 2 && !batchRequestInFlight.current) {
        loadBatchComparisons();
      }
    } else {
      // No preloaded comparisons - we'll need to wait for backend
      setLoading(true);
    }

    // Store pending submission for potential recovery
    pendingSubmission.current = {
      comparisonId: currentComparisonId,
      choice,
      decisionTimeMs,
      answers,
    };
    setSubmitting(true);

    try {
      const progress = await api.submitChoice(
        currentSession.id,
        currentComparisonId,
        choice,
        decisionTimeMs,
        answers
      );

      // Update session with progress from backend
      setCurrentSession(prev => prev ? {
        ...prev,
        comparison_count: progress.comparison_count,
        phase: progress.phase,
        confidence_score: progress.confidence_score,
        established_preferences: progress.established_preferences ?? prev.established_preferences,
      } : null);

      // Handle phase transitions - clear queue and reload if phase changed
      if (progress.next_phase) {
        setComparisonQueue([]);
        recentChoices.current = [];
        // If we optimistically showed a comparison, we need to clear it and load fresh
        setComparison(null);
        setLoading(true);
        await loadComparison();
        setLoading(false);
      } else if (!hasPreloadedComparison) {
        // No preloaded comparison was available, load one now
        await loadComparison();
      }

      pendingSubmission.current = null;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit choice');
      // Note: We don't revert the optimistic UI on error - the user can continue
      // and the error message will be shown. The choice submission can be retried
      // by the backend or ignored (worst case: one choice is lost)
    } finally {
      setSubmitting(false);
      setLoading(false);
    }
  };

  const loadRules = async () => {
    if (!currentSession) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRules(currentSession.id);
      setRules(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rules');
    } finally {
      setLoading(false);
    }
  };

  const addRule = async (statement: string, component?: string) => {
    if (!currentSession) return;
    setLoading(true);
    setError(null);
    try {
      const rule = await api.addRule(currentSession.id, statement, component);
      setRules(prev => [...prev, rule]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add rule');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteRule = async (ruleId: string) => {
    if (!currentSession) return;
    setLoading(true);
    setError(null);
    try {
      await api.deleteRule(currentSession.id, ruleId);
      setRules(prev => prev.filter(r => r.rule_id !== ruleId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete rule');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const generateSkill = async () => {
    if (!currentSession) throw new Error('No session selected');
    setLoading(true);
    setError(null);
    try {
      const response = await api.generateSkill(currentSession.id);
      setCurrentSession(prev => prev ? { ...prev, phase: 'complete' } : null);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate skill');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <SessionContext.Provider
      value={{
        currentSession,
        sessions,
        comparison,
        comparisonQueue,
        rules,
        loading,
        loadingBatch,
        submitting,
        error,
        loadSessions,
        createSession,
        selectSession,
        refreshSession,
        loadComparison,
        loadBatchComparisons,
        submitChoice,
        loadRules,
        addRule,
        deleteRule,
        generateSkill,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
