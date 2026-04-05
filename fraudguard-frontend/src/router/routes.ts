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
      { path: 'profile', component: () => import('pages/ProfilePage.vue') },
      { path: 'advanced', component: () => import('pages/AdvancedAnalysis.vue') },
      { path: 'analytics', component: () => import('pages/AnalyticsPage.vue') }
    ],
  },
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue')
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
