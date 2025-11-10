# 贡献指南 | Contributing Guide

感谢你考虑为原神游戏信息网站贡献代码！

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)

---

## 行为准则

### 我们的承诺

为了营造开放和包容的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 如何贡献

### 报告 Bug

如果你发现了 bug，请[创建 Issue](https://github.com/lastdanger/genshin-wiki-infomation/issues/new) 并包含：

- **清晰的标题和描述**
- **重现步骤**
- **预期行为和实际行为**
- **截图**（如果适用）
- **环境信息**（浏览器、操作系统等）

**Bug 报告模板:**

```markdown
## 描述
简要描述 bug

## 重现步骤
1. 前往 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 预期行为
应该发生什么

## 实际行为
实际发生了什么

## 截图
如果适用，添加截图

## 环境
- 操作系统: [例如 macOS 12.0]
- 浏览器: [例如 Chrome 95]
- 版本: [例如 0.2.0]
```

### 功能请求

如果你有新功能的想法，请[创建 Issue](https://github.com/lastdanger/genshin-wiki-infomation/issues/new) 并包含：

- **功能描述**
- **使用场景**
- **可能的实现方案**
- **替代方案**

---

## 开发流程

### 1. Fork 项目

点击 GitHub 页面右上角的 "Fork" 按钮。

### 2. 克隆你的 Fork

```bash
git clone https://github.com/your-username/genshin-wiki-infomation.git
cd genshin-wiki-infomation
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/lastdanger/genshin-wiki-infomation.git
```

### 4. 创建分支

```bash
git checkout -b feature/your-feature-name
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

### 5. 设置开发环境

详见 [开发指南](./DEVELOPMENT.md)

### 6. 开始开发

- 遵循[代码规范](#代码规范)
- 编写测试
- 更新文档

### 7. 提交代码

```bash
git add .
git commit -m "feat: add new feature"
```

### 8. 保持同步

```bash
git fetch upstream
git rebase upstream/main
```

### 9. 推送代码

```bash
git push origin feature/your-feature-name
```

### 10. 创建 Pull Request

在 GitHub 上创建 Pull Request。

---

## 代码规范

### Python 代码规范

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)：

```python
# 好的示例
def calculate_character_damage(
    character: Character,
    enemy: Enemy,
    *,
    crit_rate: float = 0.5,
    crit_damage: float = 1.0
) -> float:
    """计算角色伤害。

    Args:
        character: 角色对象
        enemy: 敌人对象
        crit_rate: 暴击率，默认 0.5
        crit_damage: 暴击伤害，默认 1.0

    Returns:
        float: 计算后的伤害值
    """
    base_damage = character.attack * character.skill_multiplier
    defense_multiplier = calculate_defense(character.level, enemy.defense)
    damage = base_damage * defense_multiplier

    if random.random() < crit_rate:
        damage *= (1 + crit_damage)

    return damage
```

**代码检查:**

```bash
# 格式化
black src/
isort src/

# Lint 检查
flake8 src/
pylint src/

# 类型检查
mypy src/
```

### JavaScript/TypeScript 代码规范

遵循 [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)：

```javascript
// 好的示例
/**
 * 获取角色详情
 * @param {number} characterId - 角色 ID
 * @returns {Promise<Character>} 角色对象
 */
const getCharacterDetail = async (characterId) => {
  try {
    const response = await api.get(`/characters/${characterId}`);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

// 使用解构和默认参数
const CharacterCard = ({
  character,
  onClick = () => {},
  showDetails = false,
}) => (
  <div className="character-card" onClick={() => onClick(character.id)}>
    <img src={character.avatar} alt={character.name} />
    <h3>{character.name}</h3>
    {showDetails && <p>{character.description}</p>}
  </div>
);
```

**代码检查:**

```bash
# Lint 检查
npm run lint

# 自动修复
npm run lint:fix

# 格式化
npm run format
```

---

## 提交规范

### Conventional Commits

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）:**

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链
- `ci`: CI/CD 相关

**范围（scope）:**

- `api`: 后端 API
- `ui`: 前端 UI
- `db`: 数据库
- `cache`: 缓存
- `auth`: 认证
- `docs`: 文档

**示例:**

```bash
# 简单提交
git commit -m "feat(api): add character search endpoint"

# 详细提交
git commit -m "feat(api): add character search endpoint

- Add GET /api/characters/search
- Support filtering by element and weapon type
- Add pagination support
- Add unit tests

Closes #123"

# Bug 修复
git commit -m "fix(ui): correct character card image display

The character avatar was not displaying correctly on mobile devices.
This commit fixes the CSS issues.

Fixes #456"

# 破坏性变更
git commit -m "feat(api)!: change authentication to JWT

BREAKING CHANGE: Session-based auth has been replaced with JWT tokens.
Clients must update their authentication logic.

Migration guide: docs/AUTH_MIGRATION.md"
```

---

## Pull Request 流程

### PR 检查清单

提交 PR 前，确保：

- [ ] 代码遵循项目规范
- [ ] 所有测试通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交消息符合规范
- [ ] 没有合并冲突
- [ ] CI/CD 检查通过

### PR 模板

```markdown
## 描述
简要描述此 PR 的目的

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 测试

## 变更内容
- 变更 1
- 变更 2
- 变更 3

## 测试
描述测试过程和结果

## 截图
如果适用，添加截图

## 相关 Issue
Closes #123
Relates to #456

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 所有测试通过
- [ ] 添加了测试
- [ ] 更新了文档
```

### 代码审查

1. **自动检查**: CI/CD 会自动运行测试和 lint
2. **人工审查**: 至少需要一位维护者审查
3. **反馈处理**: 根据反馈修改代码
4. **合并**: 审查通过后由维护者合并

---

## 测试要求

### 后端测试

```bash
# 运行测试
pytest

# 测试覆盖率（要求 > 80%）
pytest --cov=src --cov-report=html
```

**测试示例:**

```python
def test_get_character_by_id(client, db_session):
    """测试获取角色详情"""
    # Arrange
    character = Character(name="Amber", element="Pyro")
    db_session.add(character)
    db_session.commit()

    # Act
    response = client.get(f"/api/characters/{character.id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "Amber"
```

### 前端测试

```bash
# 运行测试
npm test

# 测试覆盖率（要求 > 70%）
npm test -- --coverage
```

**测试示例:**

```javascript
describe('CharacterCard', () => {
  it('should render character information', () => {
    const character = { id: 1, name: 'Amber', element: 'Pyro' };

    render(<CharacterCard character={character} />);

    expect(screen.getByText('Amber')).toBeInTheDocument();
    expect(screen.getByAltText('Amber')).toBeInTheDocument();
  });
});
```

---

## 文档更新

### 何时更新文档

- 添加新功能时
- 修改 API 时
- 更改配置时
- 修复重要 bug 时

### 文档位置

- **API 文档**: `backend/docs/`
- **前端文档**: `frontend/docs/`
- **项目文档**: `docs/`
- **README**: 项目根目录

---

## 获取帮助

如有疑问，可以：

- 查看[开发指南](./DEVELOPMENT.md)
- 在 [GitHub Discussions](https://github.com/lastdanger/genshin-wiki-infomation/discussions) 提问
- 在 [Issue](https://github.com/lastdanger/genshin-wiki-infomation/issues) 中寻求帮助

---

## 感谢

感谢每一位贡献者的付出！你的贡献让这个项目变得更好。

---

**Happy Contributing! 🎉**
