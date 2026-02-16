import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/shadcn/Button';
import { Input } from '@/components/ui/shadcn/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/shadcn/Card';
import NavBar from '@/components/NavBar';

export default function Dashboard() {
  const navigate = useNavigate();
  const { sessions, loadSessions, createSession, selectSession, loading, error } = useSession();
  const [showNewSession, setShowNewSession] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionName.trim()) return;

    setCreating(true);
    try {
      const session = await createSession(
        sessionName.trim(),
        projectDescription.trim() || undefined
      );
      await selectSession(session.id);
      navigate(`/session/${session.id}`);
    } catch {
      // Error is handled by context
    } finally {
      setCreating(false);
    }
  };

  const handleContinueSession = async (sessionId: number) => {
    try {
      await selectSession(sessionId);
      navigate(`/session/${sessionId}`);
    } catch {
      // Error is handled by context
    }
  };

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, string> = {
      color_exploration: 'Color Selection',
      typography_exploration: 'Typography Selection',
      component_studio: 'Component Studio',
      territory_mapping: 'Territory Mapping',
      dimension_isolation: 'Dimension Isolation',
      stated_preferences: 'Stated Preferences',
      complete: 'Complete',
    };
    return labels[phase] || phase;
  };

  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      color_exploration: 'bg-pink-100 text-pink-800',
      typography_exploration: 'bg-indigo-100 text-indigo-800',
      component_studio: 'bg-cyan-100 text-cyan-800',
      territory_mapping: 'bg-blue-100 text-blue-800',
      dimension_isolation: 'bg-yellow-100 text-yellow-800',
      stated_preferences: 'bg-purple-100 text-purple-800',
      complete: 'bg-green-100 text-green-800',
    };
    return colors[phase] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Page Title */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-bold">Your Sessions</h2>
            <p className="text-gray-600">
              Create a new session or continue an existing one
            </p>
          </div>
          <Button
            onClick={() => setShowNewSession(true)}
            agent-handle="dashboard-sessions-button-create"
          >
            New Session
          </Button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 mb-6 text-red-500 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        {/* New Session Form */}
        {showNewSession && (
          <Card className="mb-6">
            <form onSubmit={handleCreateSession}>
              <CardHeader>
                <CardTitle>Create New Session</CardTitle>
                <CardDescription>
                  Describe your project to get style suggestions tailored to your use case
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="sessionName" className="text-sm font-medium">
                    Session Name
                  </label>
                  <Input
                    id="sessionName"
                    placeholder="e.g., My Brand Style"
                    value={sessionName}
                    onChange={(e) => setSessionName(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="projectDescription" className="text-sm font-medium">
                    Describe Your Project <span className="text-gray-400 font-normal">(optional)</span>
                  </label>
                  <textarea
                    id="projectDescription"
                    placeholder="e.g., Enterprise B2B analytics dashboard for financial services, targeting professional users who value clarity and data density..."
                    value={projectDescription}
                    onChange={(e) => setProjectDescription(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                  />
                  <p className="text-xs text-gray-500">
                    This helps generate more relevant style options for your project type
                  </p>
                </div>
              </CardContent>
              <CardFooter className="gap-2">
                <Button type="submit" disabled={creating || !sessionName.trim()}>
                  {creating ? 'Creating...' : 'Create Session'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowNewSession(false);
                    setSessionName('');
                    setProjectDescription('');
                  }}
                >
                  Cancel
                </Button>
              </CardFooter>
            </form>
          </Card>
        )}

        {/* Sessions List */}
        {loading && sessions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Loading sessions...
          </div>
        ) : sessions.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-500 mb-4">
                You don't have any sessions yet
              </p>
              <Button onClick={() => setShowNewSession(true)}>
                Create Your First Session
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => (
              <Card
                key={session.id}
                className="hover:shadow-md transition-shadow"
                agent-handle={`dashboard-sessions-card-${session.id}`}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{session.name}</CardTitle>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${getPhaseColor(
                        session.phase
                      )}`}
                    >
                      {getPhaseLabel(session.phase)}
                    </span>
                  </div>
                  <CardDescription>
                    {session.comparison_count} comparisons
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Confidence</span>
                      <span className="font-medium">
                        {(session.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary rounded-full h-2 transition-all"
                        style={{ width: `${session.confidence_score * 100}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full"
                    variant={session.phase === 'complete' ? 'outline' : 'default'}
                    onClick={() => handleContinueSession(session.id)}
                    agent-handle={`dashboard-sessions-button-continue-${session.id}`}
                  >
                    {session.phase === 'complete' ? 'View Results' : 'Continue'}
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
