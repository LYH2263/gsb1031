import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import { Button, Spin } from 'antd';
import Login from './pages/Login';
import BookList from './pages/BookList';
import MyBooks from './pages/MyBooks';
import { AuthContext, AuthProvider } from './context/AuthContext';
import { BookOutlined, UserOutlined, LogoutOutlined, MenuOutlined, CloseOutlined } from '@ant-design/icons';

const PrivateRoute = ({ children }: { children: React.ReactElement }) => {
  const { user, isLoading } = useContext(AuthContext);
  const location = useLocation();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen"><Spin size="large" /></div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

const AppContent: React.FC = () => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  return (
    <div className="min-h-screen flex flex-col">
      {user && (
        <header className="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-white/20 shadow-sm transition-all duration-300">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer" onClick={() => window.location.href='/'}>
                   <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-ios-blue to-ios-cyan flex items-center justify-center text-white font-bold shadow-lg shadow-ios-blue/30">
                     L
                   </div>
                   <span className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
                     图书馆
                   </span>
                </div>
                <nav className="hidden md:ml-10 md:flex md:space-x-8">
                  <Link 
                    to="/" 
                    className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-all duration-200 ${location.pathname === '/' ? 'border-ios-blue text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                  >
                    图书大厅
                  </Link>
                  <Link 
                    to="/my-books" 
                    className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-all duration-200 ${location.pathname === '/my-books' ? 'border-ios-blue text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                  >
                    我的图书
                  </Link>
                </nav>
              </div>
              <div className="flex items-center gap-4">
                 <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100/50 backdrop-blur-md border border-white/20">
                   <UserOutlined className="text-gray-500" />
                   <span className="text-sm font-medium text-gray-700 hidden sm:block" title={user.phone}>{user.phone}</span>
                   {user.role === 'admin' && <span className="text-xs bg-ios-blue/10 text-ios-blue px-2 py-0.5 rounded-full">Admin</span>}
                 </div>
                 <Button 
                   type="text" 
                   icon={<LogoutOutlined />} 
                   onClick={logout} 
                   className="text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-full w-10 h-10 flex items-center justify-center transition-all duration-200"
                 />
                 <div className="md:hidden flex items-center">
                    <Button
                      type="text"
                      icon={isMobileMenuOpen ? <CloseOutlined /> : <MenuOutlined />}
                      onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                      className="text-gray-500 hover:text-gray-900"
                    />
                 </div>
              </div>
            </div>
          </div>
          
          {isMobileMenuOpen && (
            <div className="md:hidden absolute top-16 left-0 w-full bg-white/95 backdrop-blur-xl border-b border-white/20 shadow-lg z-40 animate-fade-in">
              <div className="px-4 pt-2 pb-4 space-y-1">
                <Link 
                  to="/" 
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-xl text-base font-medium transition-colors ${location.pathname === '/' ? 'bg-ios-blue/10 text-ios-blue' : 'text-gray-700 hover:bg-gray-50'}`}
                >
                  <div className="flex items-center gap-2">
                    <BookOutlined />
                    <span>图书大厅</span>
                  </div>
                </Link>
                <Link 
                  to="/my-books" 
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-xl text-base font-medium transition-colors ${location.pathname === '/my-books' ? 'bg-ios-blue/10 text-ios-blue' : 'text-gray-700 hover:bg-gray-50'}`}
                >
                  <div className="flex items-center gap-2">
                    <UserOutlined />
                    <span>我的图书</span>
                  </div>
                </Link>
              </div>
            </div>
          )}
        </header>
      )}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <BookList />
              </PrivateRoute>
            }
          />
          <Route
            path="/my-books"
            element={
              <PrivateRoute>
                <MyBooks />
              </PrivateRoute>
            }
          />
        </Routes>
      </main>
      <footer className="bg-white/30 backdrop-blur-md border-t border-white/20 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>图书馆管理系统 ©2026 Designed with Glassmorphism</p>
        </div>
      </footer>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
