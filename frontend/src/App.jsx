/**
 * 原神游戏信息网站 - 主应用组件
 *
 * 提供路由配置和全局布局结构
 */
import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// 布局组件
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import { GlobalErrorBoundary } from './components/ErrorBoundary';

// 懒加载页面组件
const HomePage = React.lazy(() => import('./pages/HomePage'));
const CharacterListPage = React.lazy(() => import('./pages/CharacterListPage'));
const CharacterDetailPage = React.lazy(() => import('./pages/CharacterDetailPage'));
const WeaponListPage = React.lazy(() => import('./pages/WeaponListPage'));
const WeaponDetailPage = React.lazy(() => import('./pages/WeaponDetailPage'));
const ArtifactListPage = React.lazy(() => import('./pages/ArtifactListPage'));
const ArtifactDetailPage = React.lazy(() => import('./pages/ArtifactDetailPage'));
const MonsterListPage = React.lazy(() => import('./pages/MonsterListPage'));
const MonsterDetailPage = React.lazy(() => import('./pages/MonsterDetailPage'));
const GameMechanicsPage = React.lazy(() => import('./pages/GameMechanicsPage'));
const ImageGalleryPage = React.lazy(() => import('./pages/ImageGalleryPage'));
const SearchResultsPage = React.lazy(() => import('./pages/SearchResultsPage'));
const AdminPage = React.lazy(() => import('./pages/AdminPage'));
const AdminCharactersPage = React.lazy(() => import('./pages/admin/AdminCharactersPage'));
const AdminWeaponsPage = React.lazy(() => import('./pages/admin/AdminWeaponsPage'));
const AdminArtifactsPage = React.lazy(() => import('./pages/admin/AdminArtifactsPage'));
const AdminMonstersPage = React.lazy(() => import('./pages/admin/AdminMonstersPage'));
const NotFoundPage = React.lazy(() => import('./pages/NotFoundPage'));

function App() {
  return (
    <GlobalErrorBoundary>
      <Router>
        <div className="App">
          <Layout>
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                {/* 首页 */}
                <Route path="/" element={<HomePage />} />

                {/* 角色相关路由 */}
                <Route path="/characters" element={<CharacterListPage />} />
                <Route path="/characters/:id" element={<CharacterDetailPage />} />

                {/* 武器相关路由 */}
                <Route path="/weapons" element={<WeaponListPage />} />
                <Route path="/weapons/:id" element={<WeaponDetailPage />} />

                {/* 圣遗物相关路由 */}
                <Route path="/artifacts" element={<ArtifactListPage />} />
                <Route path="/artifacts/:id" element={<ArtifactDetailPage />} />

                {/* 怪物相关路由 */}
                <Route path="/monsters" element={<MonsterListPage />} />
                <Route path="/monsters/:id" element={<MonsterDetailPage />} />

                {/* 游戏机制路由 */}
                <Route path="/game-mechanics" element={<GameMechanicsPage />} />
                <Route path="/game-mechanics/:category" element={<GameMechanicsPage />} />

                {/* 图片画廊 */}
                <Route path="/gallery" element={<ImageGalleryPage />} />
                <Route path="/gallery/:type" element={<ImageGalleryPage />} />

                {/* 搜索结果 */}
                <Route path="/search" element={<SearchResultsPage />} />

                {/* 管理后台 */}
                <Route path="/admin" element={<AdminPage />} />
                <Route path="/admin/characters" element={<AdminCharactersPage />} />
                <Route path="/admin/weapons" element={<AdminWeaponsPage />} />
                <Route path="/admin/artifacts" element={<AdminArtifactsPage />} />
                <Route path="/admin/monsters" element={<AdminMonstersPage />} />

                {/* 重定向和404 */}
                <Route path="/home" element={<Navigate to="/" replace />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Suspense>
          </Layout>
        </div>
      </Router>
    </GlobalErrorBoundary>
  );
}

export default App;