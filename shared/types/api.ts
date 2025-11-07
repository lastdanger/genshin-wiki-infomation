// API 请求和响应类型定义

// 通用响应结构
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 分页响应
export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

// 通用查询参数
export interface BaseQueryParams {
  page?: number;
  per_page?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// 角色查询参数
export interface CharacterQueryParams extends BaseQueryParams {
  element?: string;
  weapon_type?: string;
  rarity?: number;
  region?: string;
}

// 武器查询参数
export interface WeaponQueryParams extends BaseQueryParams {
  weapon_type?: string;
  rarity?: number;
}

// 圣遗物查询参数
export interface ArtifactQueryParams extends BaseQueryParams {
  domain_name?: string;
}

// 怪物查询参数
export interface MonsterQueryParams extends BaseQueryParams {
  monster_type?: string;
  category?: string;
  element?: string;
}

// 游戏机制查询参数
export interface GameMechanicQueryParams extends BaseQueryParams {
  category?: string;
  difficulty_level?: string;
}

// 图片上传参数
export interface ImageUploadParams {
  entity_type: 'character' | 'weapon' | 'artifact' | 'monster';
  entity_id: number;
  image_type: 'portrait' | 'icon' | 'splash' | 'card' | 'user_upload';
}

// 数据源状态
export interface DataSourceStatus {
  source_name: string;
  status: 'online' | 'offline' | 'error';
  last_sync: string;
  next_sync?: string;
  error_message?: string;
}

// 搜索结果
export interface SearchResult {
  type: 'character' | 'weapon' | 'artifact' | 'monster' | 'game_mechanic';
  id: number;
  name: string;
  description?: string;
  thumbnail?: string;
  match_score: number;
}

// 统计数据
export interface StatsResponse {
  characters_count: number;
  weapons_count: number;
  artifacts_count: number;
  monsters_count: number;
  game_mechanics_count: number;
  images_count: number;
}