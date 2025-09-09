import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/train', label: 'Train Model', icon: '🎯' },
    { path: '/models', label: 'Model Management', icon: '🤖' },
    { path: '/predict', label: 'Make Prediction', icon: '🔮' },
    { path: '/history', label: 'Prediction History', icon: '📋' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav style={{
      background: '#343a40',
      padding: '1rem 0',
      borderBottom: '2px solid #007bff'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center' }}>
        <div style={{ 
          color: 'white', 
          fontSize: '24px', 
          fontWeight: 'bold', 
          marginRight: '2rem',
          padding: '0 1rem'
        }}>
          🧠 ML Prediction Platform
        </div>
        
        <ul style={{ 
          display: 'flex', 
          listStyle: 'none', 
          margin: 0, 
          padding: 0, 
          gap: '0.5rem',
          flex: 1
        }}>
          {navItems.map(item => (
            <li key={item.path}>
              <Link
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  color: isActive(item.path) ? '#fff' : '#adb5bd',
                  textDecoration: 'none',
                  borderRadius: '4px',
                  background: isActive(item.path) ? '#007bff' : 'transparent',
                  transition: 'all 0.2s ease',
                  fontSize: '14px',
                  fontWeight: isActive(item.path) ? '600' : '400'
                }}
                onMouseOver={(e) => {
                  if (!isActive(item.path)) {
                    (e.target as HTMLElement).style.background = '#495057';
                    (e.target as HTMLElement).style.color = '#fff';
                  }
                }}
                onMouseOut={(e) => {
                  if (!isActive(item.path)) {
                    (e.target as HTMLElement).style.background = 'transparent';
                    (e.target as HTMLElement).style.color = '#adb5bd';
                  }
                }}
              >
                <span style={{ marginRight: '0.5rem', fontSize: '16px' }}>
                  {item.icon}
                </span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;