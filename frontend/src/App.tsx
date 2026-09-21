import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { Navigation, type ActiveTab } from './components/layout/Navigation';
import { Footer } from './components/layout/Footer';
import { OverviewDashboard } from './features/overview/OverviewDashboard';
import { CohortSimulation } from './features/cohort/CohortSimulation';
import { AdvisorRecommender } from './features/recommendation/AdvisorRecommender';
import { AdvisorsDirectory } from './features/advisors/AdvisorsDirectory';
import { BenchmarkAnalytics } from './features/analytics/BenchmarkAnalytics';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-indigo-500 selection:text-white">
      <Header />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'overview' && <OverviewDashboard onNavigate={setActiveTab} />}
        {activeTab === 'cohort' && <CohortSimulation />}
        {activeTab === 'recommend' && <AdvisorRecommender />}
        {activeTab === 'advisors' && <AdvisorsDirectory />}
        {activeTab === 'analytics' && <BenchmarkAnalytics />}
      </main>

      <Footer />
    </div>
  );
}

export default App;
