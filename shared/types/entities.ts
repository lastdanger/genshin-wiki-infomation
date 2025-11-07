// 原神游戏信息网站 - 共享实体类型定义

export type ElementType =
  | 'Pyro' | 'Hydro' | 'Anemo' | 'Electro'
  | 'Dendro' | 'Cryo' | 'Geo';

export type WeaponType =
  | 'Sword' | 'Claymore' | 'Polearm' | 'Bow' | 'Catalyst';

export type RegionType =
  | 'Mondstadt' | 'Liyue' | 'Inazuma' | 'Sumeru' | 'Fontaine' | 'Natlan' | 'Snezhnaya';

export type SkillType =
  | 'normal_attack' | 'elemental_skill' | 'elemental_burst' | 'passive';

export type ArtifactPieceType =
  | 'flower' | 'plume' | 'sands' | 'goblet' | 'circlet';

export type MonsterCategory =
  | 'Common' | 'Elite' | 'Boss' | 'Weekly_Boss';

export type DifficultyLevel =
  | 'beginner' | 'intermediate' | 'advanced';

// 基础实体接口
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

// 角色实体
export interface Character extends BaseEntity {
  name: string;
  name_en?: string;
  element: ElementType;
  weapon_type: WeaponType;
  rarity: 4 | 5;
  region?: RegionType;
  base_stats: {
    hp: number;
    atk: number;
    def: number;
  };
  ascension_stats?: {
    stat: string;
    value: number;
  };
  description?: string;
  birthday?: string;
  constellation_name?: string;
  title?: string;
  affiliation?: string;
}

// 角色技能
export interface CharacterSkill extends BaseEntity {
  character_id: number;
  skill_type: SkillType;
  name: string;
  description: string;
  scaling_stats: Record<string, any>;
  cooldown?: number;
  energy_cost?: number;
  level_scaling: Record<string, any>[];
}

// 角色天赋
export interface CharacterTalent extends BaseEntity {
  character_id: number;
  talent_type: 'passive' | 'ascension';
  name: string;
  description: string;
  unlock_condition: string;
  effects: Record<string, any>;
}

// 武器实体
export interface Weapon extends BaseEntity {
  name: string;
  name_en?: string;
  weapon_type: WeaponType;
  rarity: 3 | 4 | 5;
  base_atk: number;
  secondary_stat?: {
    stat: string;
    value: number;
  };
  passive_name?: string;
  passive_description?: string;
  passive_values: Record<string, any>[];
  ascension_costs: Record<string, any>[];
  description?: string;
  lore?: string;
}

// 圣遗物实体
export interface Artifact extends BaseEntity {
  set_name: string;
  set_name_en?: string;
  rarity_range: string;
  two_piece_effect?: string;
  four_piece_effect?: string;
  domain_name?: string;
  domain_location?: string;
}

// 圣遗物部件
export interface ArtifactPiece extends BaseEntity {
  artifact_id: number;
  piece_type: ArtifactPieceType;
  piece_name: string;
  main_stats: string[];
  description?: string;
}

// 怪物实体
export interface Monster extends BaseEntity {
  name: string;
  name_en?: string;
  monster_type: string;
  category?: MonsterCategory;
  level_range?: string;
  element?: ElementType;
  resistances?: Record<string, number>;
  immunities?: string[];
  hp_scaling?: Record<string, any>;
  attack_patterns?: Record<string, any>;
  weak_points?: string;
  drops?: Record<string, any>;
  locations?: string[];
  description?: string;
  strategy_tips?: string;
}

// 游戏机制
export interface GameMechanic extends BaseEntity {
  title: string;
  category: 'basic' | 'advanced' | 'combat' | 'elemental';
  difficulty_level: DifficultyLevel;
  summary: string;
  content: string;
  formulas?: Record<string, any>;
  examples?: Record<string, any>;
  related_entities?: {
    characters?: string[];
    weapons?: string[];
    artifacts?: string[];
  };
  tags?: string;
  priority: number;
}

// 图片实体
export interface Image extends BaseEntity {
  entity_type: 'character' | 'weapon' | 'artifact' | 'monster';
  entity_id: number;
  image_type: 'portrait' | 'icon' | 'splash' | 'card' | 'user_upload';
  url: string;
  filename: string;
  file_size: number;
  mime_type: string;
  width: number;
  height: number;
  is_official: boolean;
  upload_user_id?: number;
  moderation_status: 'pending' | 'approved' | 'rejected';
  moderation_notes?: string;
}

// 推荐关系实体
export interface CharacterWeaponRecommendation extends BaseEntity {
  character_id: number;
  weapon_id: number;
  rating: 1 | 2 | 3 | 4 | 5;
  explanation: string;
  build_type: 'dps' | 'support' | 'hybrid';
}

export interface CharacterArtifactRecommendation extends BaseEntity {
  character_id: number;
  artifact_id: number;
  rating: 1 | 2 | 3 | 4 | 5;
  explanation: string;
  main_stats_priority: Record<ArtifactPieceType, string[]>;
  sub_stats_priority: string[];
  build_type: 'dps' | 'support' | 'hybrid';
}