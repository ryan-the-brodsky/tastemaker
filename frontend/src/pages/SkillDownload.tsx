import { useEffect, useState, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { api } from '@/services/api';
import { Button } from '@/components/ui/shadcn/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/shadcn/Card';
import type { SkillGenerateResponse } from '@/types';

export default function SkillDownload() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const location = useLocation();
  const { currentSession, selectSession, generateSkill } = useSession();
  const [skill, setSkill] = useState<SkillGenerateResponse | null>(
    (location.state as { skill?: SkillGenerateResponse })?.skill || null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportingLibrary, setExportingLibrary] = useState(false);
  const initialized = useRef(false);

  useEffect(() => {
    if (sessionId && !initialized.current) {
      initialized.current = true;
      selectSession(parseInt(sessionId)).then(() => {
        // If no skill passed via state, generate one
        if (!skill) {
          handleGenerate();
        }
      });
    }
  }, [sessionId]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateSkill();
      setSkill(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate skill');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!skill) return;

    // Create a link and trigger download
    const token = api.getToken();
    const downloadUrl = `${api.getSkillDownloadUrl(skill.skill_id)}`;

    // Use fetch with auth header
    fetch(downloadUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tastemaker-skill.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      })
      .catch((err) => {
        console.error('Download failed:', err);
        setError('Download failed. Please try again.');
      });
  };

  const handleExportLibrary = async () => {
    if (!sessionId) return;

    setExportingLibrary(true);
    setError(null);

    try {
      const blob = await api.exportComponentLibrary(parseInt(sessionId), 'react');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tastemaker-components-${sessionId}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('Export failed:', err);
      setError('Export failed. Please try again.');
    } finally {
      setExportingLibrary(false);
    }
  };

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading session...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="font-semibold">Skill Package Ready</h1>
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {/* Error Display */}
        {error && (
          <div className="p-4 mb-6 text-red-500 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        {loading ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-500">Generating your skill package...</p>
            </CardContent>
          </Card>
        ) : skill ? (
          <>
            {/* Success Card */}
            <Card className="mb-8 border-green-200 bg-green-50">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-3xl">✓</span>
                </div>
                <CardTitle className="text-2xl text-green-800">
                  Your Skill Package is Ready!
                </CardTitle>
                <CardDescription className="text-green-700">
                  Download your personalized style guide for AI coding tools
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <Button
                  size="lg"
                  onClick={handleDownload}
                  className="bg-green-600 hover:bg-green-700"
                  agent-handle="skill-download-button-zip"
                >
                  Download Skill Package (.zip)
                </Button>
                <div className="pt-2">
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={handleExportLibrary}
                    disabled={exportingLibrary}
                    agent-handle="skill-export-library-button"
                  >
                    {exportingLibrary ? 'Exporting...' : 'Export Component Library'}
                  </Button>
                  <p className="mt-2 text-sm text-gray-500">
                    Get all 7 component types as ready-to-use React files
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Preview Card */}
            <Card agent-handle="skill-preview-content">
              <CardHeader>
                <CardTitle>Package Contents</CardTitle>
                <CardDescription>
                  Your skill package includes the following:
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Stats */}
                  <div>
                    <h4 className="font-medium mb-3">Rules Summary</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Rules</span>
                        <span className="font-medium">{skill.preview.total_rules}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Extracted</span>
                        <span className="font-medium">{skill.preview.extracted_rules}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Stated</span>
                        <span className="font-medium">{skill.preview.stated_rules}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Baseline (WCAG/Nielsen)</span>
                        <span className="font-medium">{skill.preview.baseline_rules}</span>
                      </div>
                    </div>

                    {skill.preview.components_covered.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Components Covered</h4>
                        <div className="flex flex-wrap gap-2">
                          {skill.preview.components_covered.map((comp) => (
                            <span
                              key={comp}
                              className="px-2 py-1 bg-gray-100 rounded text-sm"
                            >
                              {comp}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Files */}
                  <div>
                    <h4 className="font-medium mb-3">Included Files</h4>
                    <ul className="space-y-1 text-sm">
                      {skill.preview.files_included.map((file) => (
                        <li key={file} className="flex items-center gap-2">
                          <span className="text-gray-400">📄</span>
                          <span className="font-mono text-gray-600">{file}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Instructions */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>How to Use</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Claude Code</h4>
                    <p className="text-sm text-gray-600">
                      Extract the ZIP and add the folder to your project. Claude Code will
                      automatically detect and use the SKILL.md file.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Other AI Tools</h4>
                    <p className="text-sm text-gray-600">
                      Reference the SKILL.md file in your prompts, or use the rules.json
                      file for programmatic integration.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-500 mb-4">No skill package generated yet.</p>
              <Button onClick={handleGenerate}>Generate Skill Package</Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
