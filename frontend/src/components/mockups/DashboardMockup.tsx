/**
 * Dashboard mockup using extracted user preferences.
 * Demonstrates sidebar navigation, stats cards, tables, and charts.
 */
import { MockupProps } from './types';

export default function DashboardMockup({ colors, typography }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  const stats = [
    { label: 'Total Users', value: '12,847', change: '+12%' },
    { label: 'Revenue', value: '$48,352', change: '+8%' },
    { label: 'Active Projects', value: '164', change: '+24%' },
    { label: 'Conversion', value: '3.2%', change: '+2%' },
  ];

  const recentItems = [
    { name: 'Project Alpha', status: 'Active', progress: 75 },
    { name: 'Beta Launch', status: 'Pending', progress: 45 },
    { name: 'Marketing Campaign', status: 'Active', progress: 90 },
    { name: 'User Research', status: 'Complete', progress: 100 },
  ];

  return (
    <div
      className="w-full min-h-[800px] flex"
      style={{ backgroundColor: colors.background, fontFamily: bodyFont }}
    >
      {/* Sidebar */}
      <aside
        className="w-64 min-h-full p-4 flex flex-col"
        style={{ backgroundColor: colors.primary }}
      >
        <div
          className="text-xl font-bold mb-8 px-2"
          style={{ color: colors.background, fontFamily: headingFont }}
        >
          Dashboard
        </div>
        <nav className="flex-1">
          {['Overview', 'Analytics', 'Projects', 'Team', 'Settings'].map((item, i) => (
            <div
              key={item}
              className="px-4 py-3 rounded-lg mb-1 cursor-pointer transition-all"
              style={{
                backgroundColor: i === 0 ? `${colors.background}20` : 'transparent',
                color: colors.background,
                opacity: i === 0 ? 1 : 0.7,
              }}
            >
              {item}
            </div>
          ))}
        </nav>
        <div
          className="px-4 py-3 rounded-lg cursor-pointer"
          style={{ color: colors.background, opacity: 0.7 }}
        >
          Logout
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1
              className="text-2xl font-bold"
              style={{ color: colors.primary, fontFamily: headingFont }}
            >
              Welcome back, Alex
            </h1>
            <p style={{ color: colors.secondary }}>
              Here's what's happening with your projects today.
            </p>
          </div>
          <button
            className="px-4 py-2 rounded-lg font-medium"
            style={{ backgroundColor: colors.accent, color: colors.background }}
          >
            + New Project
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {stats.map((stat, i) => (
            <div
              key={i}
              className="p-6 rounded-xl shadow-sm"
              style={{
                backgroundColor: colors.background,
                border: `1px solid ${colors.primary}15`,
              }}
            >
              <p className="text-sm mb-1" style={{ color: colors.secondary }}>
                {stat.label}
              </p>
              <div className="flex items-end justify-between">
                <span
                  className="text-2xl font-bold"
                  style={{ color: colors.primary, fontFamily: headingFont }}
                >
                  {stat.value}
                </span>
                <span
                  className="text-sm font-medium"
                  style={{ color: colors.accent }}
                >
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-3 gap-6">
          {/* Projects Table */}
          <div
            className="col-span-2 rounded-xl shadow-sm overflow-hidden"
            style={{
              backgroundColor: colors.background,
              border: `1px solid ${colors.primary}15`,
            }}
          >
            <div
              className="px-6 py-4 border-b"
              style={{ borderColor: `${colors.primary}15` }}
            >
              <h2
                className="font-semibold"
                style={{ color: colors.primary, fontFamily: headingFont }}
              >
                Recent Projects
              </h2>
            </div>
            <div className="p-4">
              {recentItems.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-3 border-b last:border-0"
                  style={{ borderColor: `${colors.primary}10` }}
                >
                  <div>
                    <p style={{ color: colors.primary }} className="font-medium">
                      {item.name}
                    </p>
                    <p className="text-sm" style={{ color: colors.secondary }}>
                      {item.status}
                    </p>
                  </div>
                  <div className="w-32">
                    <div
                      className="h-2 rounded-full overflow-hidden"
                      style={{ backgroundColor: `${colors.primary}20` }}
                    >
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${item.progress}%`,
                          backgroundColor:
                            item.progress === 100 ? colors.accent : colors.primary,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Feed */}
          <div
            className="rounded-xl shadow-sm"
            style={{
              backgroundColor: colors.background,
              border: `1px solid ${colors.primary}15`,
            }}
          >
            <div
              className="px-6 py-4 border-b"
              style={{ borderColor: `${colors.primary}15` }}
            >
              <h2
                className="font-semibold"
                style={{ color: colors.primary, fontFamily: headingFont }}
              >
                Recent Activity
              </h2>
            </div>
            <div className="p-4">
              {[
                'New user signed up',
                'Project completed',
                'Payment received',
                'Comment added',
              ].map((activity, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 py-3 border-b last:border-0"
                  style={{ borderColor: `${colors.primary}10` }}
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: colors.accent }}
                  />
                  <span style={{ color: colors.secondary }} className="text-sm">
                    {activity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
