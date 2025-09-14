import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import AuthApp from './components/AuthApp';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AuthApp />
  </React.StrictMode>
);
