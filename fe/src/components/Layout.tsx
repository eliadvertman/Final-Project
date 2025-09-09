import React from 'react';
import Navigation from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
      <Navigation />
      <main style={{ minHeight: 'calc(100vh - 80px)' }}>
        {children}
      </main>
    </div>
  );
};

export default Layout;