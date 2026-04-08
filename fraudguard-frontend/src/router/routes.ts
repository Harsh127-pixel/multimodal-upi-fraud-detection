import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/DashboardPage.vue') },
      { path: 'verify', component: () => import('pages/VerifyUPI.vue') },
      { path: 'report', component: () => import('pages/ReportFraud.vue') },
      { path: 'alerts', component: () => import('pages/AlertsPage.vue') },
      { path: 'settings', component: () => import('pages/ProfilePage.vue') },
      { path: 'advanced', component: () => import('pages/AdvancedAnalysis.vue') },
      { path: 'analytics', component: () => import('pages/AnalyticsPage.vue') },
      { path: 'mobile', component: () => import('pages/MobileDefense.vue') },
      { path: 'graph', component: () => import('pages/GraphSandbox.vue') },
      { path: 'community', component: () => import('pages/CommunityWatch.vue') },
      { path: 'soc', component: () => import('pages/SOCDashboard.vue') },
      { path: 'cases', component: () => import('pages/CaseManager.vue') },
      { path: 'scanner', component: () => import('pages/BulkScanner.vue') },
      { path: 'playbook', component: () => import('pages/PlaybookExecutor.vue') },
      { path: 'riskmap', component: () => import('pages/RiskMap.vue') }
    ],
  },
  {
    path: '/login',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: '', name: 'login', component: () => import('pages/LoginPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
