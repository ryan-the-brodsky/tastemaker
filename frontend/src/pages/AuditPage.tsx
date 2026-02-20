/**
 * Audit Page - Upload screenshots or videos and get style violation feedback.
 *
 * Supports three audit modes:
 * 1. Screenshot - Upload a single image for static rule analysis
 * 2. Live URL - Capture and analyze a URL via Playwright
 * 3. Video - Upload a video for interactive UX rule analysis (temporal, spatial, pattern)
 */
import { useState, useRef, useEffect } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/shadcn/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/shadcn/Card';
import { api, VideoAuditRecording, InteractiveAuditResult, InteractiveAuditViolation } from '@/services/api';
import NavBar from '@/components/NavBar';

interface Violation {
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  property: string;
  expected: string;
  found: string;
  message: string;
  suggestion: string;
}

interface AuditResult {
  violations: Violation[];
  summary: string;
  score: number;
}

export default function AuditPage() {
  const { sessions, loadSessions } = useSession();
  const { user } = useAuth();
  const isPremium = user?.subscription_tier === 'premium';
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [videoResult, setVideoResult] = useState<InteractiveAuditResult | null>(null);
  const [videoRecording, setVideoRecording] = useState<VideoAuditRecording | null>(null);
  const [auditMode, setAuditMode] = useState<'screenshot' | 'url' | 'video'>('screenshot');
  const [urlToAudit, setUrlToAudit] = useState<string>('');

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === 'image/png' || file.type === 'image/jpeg')) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedVideo(file);
      setVideoResult(null);
      setVideoRecording(null);
      setError(null);
    }
  };

  const handleVideoDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type.startsWith('video/'))) {
      setSelectedVideo(file);
      setVideoResult(null);
      setVideoRecording(null);
      setError(null);
    }
  };

  const pollVideoStatus = async (recordingId: string) => {
    const maxAttempts = 60; // Poll for up to 5 minutes
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await api.getVideoRecordingStatus(recordingId);
        setVideoRecording(status);

        if (status.status === 'completed') {
          // Fetch full results
          const results = await api.getVideoAuditResults(recordingId);
          setVideoResult(results);
          setLoading(false);
        } else if (status.status === 'failed') {
          setError(status.error_message || 'Video processing failed');
          setLoading(false);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setError('Video processing timed out');
          setLoading(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to check status');
        setLoading(false);
      }
    };

    poll();
  };

  const handleAudit = async () => {
    if (!selectedSession) {
      setError('Please select a session');
      return;
    }

    if (auditMode === 'screenshot' && !selectedFile) {
      setError('Please upload a screenshot');
      return;
    }

    if (auditMode === 'url' && !urlToAudit) {
      setError('Please enter a URL');
      return;
    }

    if (auditMode === 'video' && !selectedVideo) {
      setError('Please upload a video');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (auditMode === 'screenshot') {
        const formData = new FormData();
        formData.append('file', selectedFile!);
        formData.append('session_id', selectedSession.toString());
        const response = await api.auditScreenshot(formData);
        setResult(response);
        setLoading(false);
      } else if (auditMode === 'url') {
        const response = await api.auditUrl(urlToAudit, selectedSession);
        setResult(response);
        setLoading(false);
      } else if (auditMode === 'video') {
        // Submit video for processing
        const formData = new FormData();
        formData.append('video', selectedVideo!);
        formData.append('session_id', selectedSession.toString());
        const recording = await api.submitVideoAudit(formData);
        setVideoRecording(recording);
        // Start polling for results
        pollVideoStatus(recording.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit failed');
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const groupedViolations = result?.violations.reduce((acc, v) => {
    if (!acc[v.severity]) acc[v.severity] = [];
    acc[v.severity].push(v);
    return acc;
  }, {} as Record<string, Violation[]>);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      {/* Page Header */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="font-semibold text-lg">Style Auditor</h1>
          <p className="text-sm text-gray-500">
            Upload a screenshot to check for style violations
          </p>
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            {/* Session Selector */}
            <Card>
              <CardHeader>
                <CardTitle>1. Select Style Profile</CardTitle>
                <CardDescription>
                  Choose which TasteMaker session to audit against
                </CardDescription>
              </CardHeader>
              <CardContent>
                <select
                  className="w-full px-3 py-2 border rounded-lg"
                  value={selectedSession || ''}
                  onChange={(e) => setSelectedSession(e.target.value || null)}
                  agent-handle="audit-select-session"
                >
                  <option value="">Select a session...</option>
                  {sessions.map((session) => (
                    <option key={session.id} value={session.id}>
                      {session.name}
                    </option>
                  ))}
                </select>
              </CardContent>
            </Card>

            {/* Audit Mode Toggle */}
            <Card>
              <CardHeader>
                <CardTitle>2. Choose Audit Method</CardTitle>
                <CardDescription>
                  Static rules (screenshot/URL) or interactive UX rules (video)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <button
                    className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
                      auditMode === 'screenshot'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setAuditMode('screenshot')}
                    agent-handle="audit-mode-screenshot"
                  >
                    Screenshot
                  </button>
                  <button
                    className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
                      auditMode === 'url'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setAuditMode('url')}
                    agent-handle="audit-mode-url"
                  >
                    Live URL
                  </button>
                  <button
                    className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
                      auditMode === 'video'
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isPremium ? 'opacity-60' : ''}`}
                    onClick={() => setAuditMode('video')}
                    agent-handle="audit-mode-video"
                  >
                    Video {!isPremium && <span className="text-xs ml-1">(Premium)</span>}
                  </button>
                </div>
                {auditMode === 'video' && (
                  <p className="mt-3 text-sm text-purple-600">
                    Video audit checks interactive UX rules: Fitts's Law, Hick's Law, Doherty Threshold, dark patterns, and more.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Screenshot Upload, URL Input, or Video Upload */}
            {auditMode === 'screenshot' && (
              <Card>
                <CardHeader>
                  <CardTitle>3. Upload Screenshot</CardTitle>
                  <CardDescription>
                    Drop an image or click to select (PNG, JPG)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      previewUrl ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => fileInputRef.current?.click()}
                    onDrop={handleDrop}
                    onDragOver={(e) => e.preventDefault()}
                    agent-handle="audit-dropzone"
                  >
                    {previewUrl ? (
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="max-h-48 mx-auto rounded"
                      />
                    ) : (
                      <div className="text-gray-500">
                        <p className="text-lg mb-2">Drop image here</p>
                        <p className="text-sm">or click to browse</p>
                      </div>
                    )}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/png,image/jpeg"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                  </div>
                  {selectedFile && (
                    <p className="mt-2 text-sm text-gray-500">
                      Selected: {selectedFile.name}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {auditMode === 'url' && (
              <Card>
                <CardHeader>
                  <CardTitle>3. Enter URL</CardTitle>
                  <CardDescription>
                    We'll capture a screenshot and analyze it
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <input
                    type="url"
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="https://example.com"
                    value={urlToAudit}
                    onChange={(e) => setUrlToAudit(e.target.value)}
                    agent-handle="audit-url-input"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Enter a publicly accessible URL to audit
                  </p>
                </CardContent>
              </Card>
            )}

            {auditMode === 'video' && !isPremium && (
              <Card>
                <CardHeader>
                  <CardTitle>Premium Feature</CardTitle>
                  <CardDescription>
                    Interactive video auditing is available for Premium subscribers
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-6">
                    <div className="text-4xl mb-3">&#x1f512;</div>
                    <p className="text-gray-600 mb-4">
                      Video audits analyze interactive UX patterns like response timing,
                      touch target sizes, and dark patterns using AI vision analysis.
                    </p>
                    <div className="px-4 py-3 bg-purple-50 border border-purple-200 rounded-lg text-purple-700 text-sm">
                      Premium subscriptions are coming soon. Stay tuned!
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {auditMode === 'video' && isPremium && (
              <Card>
                <CardHeader>
                  <CardTitle>3. Upload Video</CardTitle>
                  <CardDescription>
                    Record your user interaction and upload (MP4, WebM, MOV)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      selectedVideo ? 'border-purple-300 bg-purple-50' : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => videoInputRef.current?.click()}
                    onDrop={handleVideoDrop}
                    onDragOver={(e) => e.preventDefault()}
                    agent-handle="audit-video-dropzone"
                  >
                    {selectedVideo ? (
                      <div className="text-purple-600">
                        <p className="text-lg mb-2">Video selected</p>
                        <p className="text-sm">{selectedVideo.name}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {(selectedVideo.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    ) : (
                      <div className="text-gray-500">
                        <p className="text-lg mb-2">Drop video here</p>
                        <p className="text-sm">or click to browse</p>
                        <p className="text-xs mt-2">Max 100MB</p>
                      </div>
                    )}
                    <input
                      ref={videoInputRef}
                      type="file"
                      accept="video/mp4,video/webm,video/quicktime"
                      className="hidden"
                      onChange={handleVideoSelect}
                    />
                  </div>
                  {videoRecording && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium">Processing Status</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className={`w-2 h-2 rounded-full ${
                          videoRecording.status === 'completed' ? 'bg-green-500' :
                          videoRecording.status === 'failed' ? 'bg-red-500' :
                          'bg-yellow-500 animate-pulse'
                        }`} />
                        <span className="text-sm capitalize">{videoRecording.status}</span>
                        {videoRecording.frame_count > 0 && (
                          <span className="text-xs text-gray-500">
                            ({videoRecording.frame_count} frames)
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Audit Button */}
            <Button
              className="w-full"
              size="lg"
              onClick={handleAudit}
              disabled={
                loading ||
                !selectedSession ||
                (auditMode === 'screenshot' && !selectedFile) ||
                (auditMode === 'url' && !urlToAudit) ||
                (auditMode === 'video' && (!selectedVideo || !isPremium))
              }
              agent-handle="audit-button-submit"
            >
              {loading ? (
                auditMode === 'video' ? 'Processing Video...' : 'Analyzing...'
              ) : (
                auditMode === 'video' ? 'Run Interactive Audit' : 'Run Audit'
              )}
            </Button>

            {error && (
              <div className="p-4 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          <div>
            {videoResult ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Interactive UX Audit Results</CardTitle>
                    <div
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        videoResult.summary.errors === 0
                          ? 'bg-green-100 text-green-800'
                          : videoResult.summary.errors <= 3
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {videoResult.summary.total_violations} violations
                    </div>
                  </div>
                  <CardDescription>
                    Analyzed {videoResult.summary.frames_analyzed} frames
                    {videoResult.duration_ms && ` over ${(videoResult.duration_ms / 1000).toFixed(1)}s`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {videoResult.summary.total_violations === 0 ? (
                    <div className="text-center py-8 text-green-600">
                      <p className="text-xl mb-2">No UX violations found!</p>
                      <p className="text-sm text-gray-500">
                        Your interaction meets all UX principles.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-6" agent-handle="video-audit-results-list">
                      {/* Summary Stats */}
                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="p-2 bg-red-50 rounded">
                          <div className="text-lg font-bold text-red-600">{videoResult.summary.errors}</div>
                          <div className="text-xs text-red-500">Errors</div>
                        </div>
                        <div className="p-2 bg-yellow-50 rounded">
                          <div className="text-lg font-bold text-yellow-600">{videoResult.summary.warnings}</div>
                          <div className="text-xs text-yellow-500">Warnings</div>
                        </div>
                        <div className="p-2 bg-blue-50 rounded">
                          <div className="text-lg font-bold text-blue-600">{videoResult.summary.temporal_metrics_count}</div>
                          <div className="text-xs text-blue-500">Temporal Metrics</div>
                        </div>
                      </div>

                      {/* Temporal Violations */}
                      {videoResult.temporal_violations.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                            Temporal Issues ({videoResult.temporal_violations.length})
                          </h4>
                          <div className="space-y-2">
                            {videoResult.temporal_violations.map((v: InteractiveAuditViolation, i: number) => (
                              <div key={i} className={`p-3 rounded-lg border ${getSeverityColor(v.severity)}`}>
                                <div className="flex justify-between items-start mb-1">
                                  <span className="font-medium text-sm">{v.rule_id}</span>
                                  <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded">
                                    {v.measured_value}ms / {v.threshold}ms
                                  </span>
                                </div>
                                <p className="text-sm">{v.message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Spatial Violations */}
                      {videoResult.spatial_violations.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                            Spatial Issues ({videoResult.spatial_violations.length})
                          </h4>
                          <div className="space-y-2">
                            {videoResult.spatial_violations.map((v: InteractiveAuditViolation, i: number) => (
                              <div key={i} className={`p-3 rounded-lg border ${getSeverityColor(v.severity)}`}>
                                <span className="text-xs opacity-70">{v.rule_id}</span>
                                <p className="text-sm">{v.message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Behavioral Violations */}
                      {videoResult.behavioral_violations.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                            Behavioral Issues ({videoResult.behavioral_violations.length})
                          </h4>
                          <div className="space-y-2">
                            {videoResult.behavioral_violations.map((v: InteractiveAuditViolation, i: number) => (
                              <div key={i} className={`p-3 rounded-lg border ${getSeverityColor(v.severity)}`}>
                                <span className="text-xs opacity-70">{v.rule_id}</span>
                                <p className="text-sm">{v.message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Pattern Violations (Dark Patterns) */}
                      {videoResult.pattern_violations.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                            Dark Pattern Detections ({videoResult.pattern_violations.length})
                          </h4>
                          <div className="space-y-2">
                            {videoResult.pattern_violations.map((v: InteractiveAuditViolation, i: number) => (
                              <div key={i} className={`p-3 rounded-lg border ${getSeverityColor(v.severity)}`}>
                                <span className="text-xs opacity-70">{v.rule_id}</span>
                                <p className="text-sm">{v.message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={() => {
                      setVideoResult(null);
                      setVideoRecording(null);
                      setSelectedVideo(null);
                    }}
                    agent-handle="audit-button-reaudit-video"
                  >
                    Audit Another Video
                  </Button>
                </CardContent>
              </Card>
            ) : result ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Audit Results</CardTitle>
                    <div
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        result.score >= 80
                          ? 'bg-green-100 text-green-800'
                          : result.score >= 60
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      Score: {result.score}%
                    </div>
                  </div>
                  <CardDescription>{result.summary}</CardDescription>
                </CardHeader>
                <CardContent>
                  {result.violations.length === 0 ? (
                    <div className="text-center py-8 text-green-600">
                      <p className="text-xl mb-2">No violations found!</p>
                      <p className="text-sm text-gray-500">
                        Your UI matches your style profile.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4" agent-handle="audit-results-list">
                      {['error', 'warning', 'info'].map((severity) => {
                        const violations = groupedViolations?.[severity];
                        if (!violations?.length) return null;
                        return (
                          <div key={severity}>
                            <h4 className="font-medium mb-2 capitalize">
                              {severity}s ({violations.length})
                            </h4>
                            <div className="space-y-2">
                              {violations.map((v, i) => (
                                <div
                                  key={i}
                                  className={`p-3 rounded-lg border ${getSeverityColor(v.severity)}`}
                                >
                                  <div className="flex justify-between items-start mb-1">
                                    <span className="font-medium">{v.property}</span>
                                    <span className="text-xs opacity-70">{v.rule_id}</span>
                                  </div>
                                  <p className="text-sm mb-2">{v.message}</p>
                                  <div className="text-xs space-y-1">
                                    <p>
                                      <span className="opacity-70">Expected:</span>{' '}
                                      <code className="bg-white/50 px-1 rounded">{v.expected}</code>
                                    </p>
                                    <p>
                                      <span className="opacity-70">Found:</span>{' '}
                                      <code className="bg-white/50 px-1 rounded">{v.found}</code>
                                    </p>
                                    <p className="mt-2 italic">{v.suggestion}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <Button
                    variant="outline"
                    className="w-full mt-4"
                    onClick={() => {
                      setResult(null);
                      setSelectedFile(null);
                      setPreviewUrl(null);
                    }}
                    agent-handle="audit-button-reaudit"
                  >
                    Audit Another Screenshot
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center py-16 text-gray-400">
                  <p className="text-lg mb-2">No results yet</p>
                  <p className="text-sm">
                    {auditMode === 'video'
                      ? 'Upload a video and run the audit to check interactive UX rules'
                      : 'Upload a screenshot and run the audit to see violations'}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
