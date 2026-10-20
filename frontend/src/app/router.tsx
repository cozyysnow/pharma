import { createBrowserRouter } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { LoginPage } from '../pages/Login/LoginPage';
import { DashboardPage } from '../pages/Dashboard/DashboardPage';
import { InventoryPage } from '../pages/Inventory/InventoryPage';
import { MedicinesPage } from '../pages/Medicines/MedicinesPage';
import { MedicineDetailsPage } from '../pages/MedicineDetails/MedicineDetailsPage';
import { TransactionsPage } from '../pages/Transactions/TransactionsPage';
import { ForecastPage } from '../pages/Forecast/ForecastPage';
import { RiskPage } from '../pages/Risk/RiskPage';
import { ReplenishmentPage } from '../pages/Replenishment/ReplenishmentPage';
import { AlertsPage } from '../pages/Alerts/AlertsPage';
import { DatasetsPage } from '../pages/Datasets/DatasetsPage';
import { ReportsPage } from '../pages/Reports/ReportsPage';
import { SettingsPage } from '../pages/Settings/SettingsPage';
import { StyleguidePage } from '../pages/Styleguide/StyleguidePage';
import { NotFoundPage } from '../pages/NotFound/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'inventory',
        element: <InventoryPage />,
      },
      {
        path: 'medicines',
        element: <MedicinesPage />,
      },
      {
        path: 'medicines/:id',
        element: <MedicineDetailsPage />,
      },
      {
        path: 'transactions',
        element: <TransactionsPage />,
      },
      {
        path: 'forecast',
        element: <ForecastPage />,
      },
      {
        path: 'risk',
        element: <RiskPage />,
      },
      {
        path: 'replenishment',
        element: <ReplenishmentPage />,
      },
      {
        path: 'alerts',
        element: <AlertsPage />,
      },
      {
        path: 'datasets',
        element: <DatasetsPage />,
      },
      {
        path: 'reports',
        element: <ReportsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: '_styleguide',
        element: <StyleguidePage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);
