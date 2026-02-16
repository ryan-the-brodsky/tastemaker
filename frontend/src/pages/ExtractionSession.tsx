import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/shadcn/Button';
import ComparisonView from '@/components/comparison/ComparisonView';
import EstablishedPreferences from '@/components/comparison/EstablishedPreferences';
import ExplorationGrid from '@/components/exploration/ExplorationGrid';
import ErrorBoundary from '@/components/ErrorBoundary';
import type { QuestionAnswer } from '@/types';

export default function ExtractionSession() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const {
    currentSession,
    comparison,
    comparisonQueue,
    selectSession,
    loadComparison,
    loadBatchComparisons,
    submitChoice,
    loading,
    loadingBatch,
    error,
    refreshSession,
  } = useSession();
  const [startTime, setStartTime] = useState<number>(Date.now());
  const initialized = useRef(false);

  useEffect(() => {
    if (sessionId && !initialized.current) {
      initialized.current = true;
      selectSession(parseInt(sessionId));
    }
  }, [sessionId]);

  // Load comparisons when session is loaded and NOT in exploration phase
  // Use batch loading for territory_mapping and dimension_isolation
  useEffect(() => {
    if (currentSession && !isExplorationPhase(currentSession.phase) && !comparison) {
      // Use batch loading for component phases
      if (['territory_mapping', 'dimension_isolation'].includes(currentSession.phase)) {
        loadBatchComparisons();
      } else {
        loadComparison();
      }
    }
  }, [currentSession?.id, currentSession?.phase]);

  useEffect(() => {
    if (comparison) {
      setStartTime(Date.now());
    }
  }, [comparison?.comparison_id]);

  // Redirect based on phase
  useEffect(() => {
    if (currentSession) {
      if (currentSession.phase === 'component_studio') {
        navigate(`/session/${sessionId}/studio`);
      } else if (currentSession.phase === 'stated_preferences' || currentSession.phase === 'complete') {
        navigate(`/session/${sessionId}/review`);
      }
    }
  }, [currentSession?.phase, sessionId, navigate]);

  const handleChoice = useCallback(
    async (choice: 'a' | 'b' | 'none', answers?: QuestionAnswer[]) => {
      const decisionTimeMs = Date.now() - startTime;
      await submitChoice(choice, decisionTimeMs, answers);
    },
    [startTime, submitChoice]
  );

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (loading || !comparison) return;

      switch (e.key) {
        case '1':
          handleChoice('a');
          break;
        case '2':
          handleChoice('b');
          break;
        case '0':
          handleChoice('none');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleChoice, loading, comparison]);

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading session...</p>
      </div>
    );
  }

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, string> = {
      color_exploration: 'Color Selection',
      typography_exploration: 'Typography Selection',
      component_studio: 'Component Studio',
      territory_mapping: 'Component Exploration',
      dimension_isolation: 'Fine-Tuning',
    };
    return labels[phase] || phase;
  };

  const getPhaseDescription = (phase: string) => {
    const descriptions: Record<string, string> = {
      color_exploration: 'Choose your brand color palette',
      typography_exploration: 'Choose your typography style',
      component_studio: 'Customize each component type systematically',
      territory_mapping: 'Explore component aesthetics with your chosen colors & fonts',
      dimension_isolation: 'Fine-tuning individual style properties',
    };
    return descriptions[phase] || '';
  };

  const getTotalForPhase = (phase: string) => {
    if (phase === 'color_exploration') return 10;
    if (phase === 'typography_exploration') return 8;
    if (phase === 'territory_mapping') return 15;
    if (phase === 'dimension_isolation') return 30;
    return 30;
  };

  const isExplorationPhase = (phase: string) => {
    return phase === 'color_exploration' || phase === 'typography_exploration';
  };

  const handleExplorationPhaseComplete = async (newPhase: string) => {
    console.log('handleExplorationPhaseComplete called with newPhase:', newPhase);
    // Refresh session to get updated phase and choices
    // The comparison will be loaded automatically by the phase change effect
    // refreshSession also clears stale comparison data to prevent brief flashes
    await refreshSession();
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b py-3 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="font-semibold">{currentSession.name}</h1>
            <p className="text-sm text-gray-500">
              {getPhaseDescription(currentSession.phase)}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/session/${sessionId}/review`)}
            >
              Skip to Review
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
            >
              Exit
            </Button>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div
        className="bg-white border-b py-2 px-4"
        agent-handle="extraction-progress-indicator"
      >
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <span className="text-sm font-medium">
            {getPhaseLabel(currentSession.phase)}
          </span>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary rounded-full h-2 transition-all"
              style={{
                width: `${Math.min(
                  100,
                  (currentSession.comparison_count / getTotalForPhase(currentSession.phase)) * 100
                )}%`,
              }}
            />
          </div>
          <span className="text-sm text-gray-500">
            {currentSession.comparison_count} / {getTotalForPhase(currentSession.phase)}
          </span>
        </div>
      </div>

      {/* Established Preferences Display */}
      <EstablishedPreferences preferences={currentSession.established_preferences} />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {error && (
          <div className="p-4 text-red-500 bg-red-50 text-center">
            {error}
          </div>
        )}

        {isExplorationPhase(currentSession.phase) ? (
          <ErrorBoundary key={`error-boundary-${currentSession.phase}`}>
            <ExplorationGrid
              key={`exploration-${currentSession.phase}`}
              sessionId={parseInt(sessionId!)}
              explorationType={currentSession.phase === 'color_exploration' ? 'palette' : 'typography'}
              onPhaseComplete={handleExplorationPhaseComplete}
            />
          </ErrorBoundary>
        ) : (loading || loadingBatch) && !comparison ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-500">
                {loadingBatch ? 'Generating component variations...' : 'Loading comparison...'}
              </p>
              <p className="text-xs text-gray-400 mt-2">
                Pre-loading comparisons for faster transitions
              </p>
            </div>
          </div>
        ) : comparison ? (
          <ComparisonView
            comparison={comparison}
            onChoice={handleChoice}
            disabled={loading}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">No more comparisons available</p>
          </div>
        )}
      </main>

      {/* Keyboard Shortcuts Hint and Queue Status */}
      <footer className="bg-white border-t py-2 px-4 flex justify-between items-center text-sm text-gray-500">
        <div>
          Keyboard shortcuts: <kbd className="px-1 py-0.5 bg-gray-100 rounded">1</kbd> Option A,{' '}
          <kbd className="px-1 py-0.5 bg-gray-100 rounded">2</kbd> Option B,{' '}
          <kbd className="px-1 py-0.5 bg-gray-100 rounded">0</kbd> No Preference
        </div>
        {!isExplorationPhase(currentSession.phase) && (
          <div className="flex items-center gap-2">
            {loadingBatch && (
              <span className="flex items-center gap-1 text-xs text-blue-600">
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                Loading more...
              </span>
            )}
            {comparisonQueue.length > 0 && (
              <span className="text-xs text-green-600">
                {comparisonQueue.length} pre-loaded
              </span>
            )}
          </div>
        )}
      </footer>
    </div>
  );
}
