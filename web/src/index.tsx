import { Theme } from '@radix-ui/themes';
import '@radix-ui/themes/styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Routes } from 'routes';
import App from './App';
import './index.css';
import NotFound from './NotFound';
import SimulateForm from './SimulateForm';

const router = createBrowserRouter([
  {
    path: Routes.FORM,
    element: <SimulateForm />,
    errorElement: <NotFound />,
  },
  {
    path: Routes.SIMULATION,
    element: <App />,
  },
]);

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    {/* Theme: https://www.radix-ui.com/themes/docs/theme/overview */}
    <Theme appearance='dark' accentColor='iris' grayColor='mauve' radius='small'>
      <RouterProvider router={router} />
    </Theme>
  </React.StrictMode>
);
