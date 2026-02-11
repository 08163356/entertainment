# 篮球记分功能配图提示词

## 1. 主背景图（两侧装饰）

**用途**：首页和房间页背景，中间会被内容遮挡，重点是两侧有篮球元素

**尺寸建议**：1920 x 1080 或更大

**提示词（中文）**：
```
深色篮球主题背景，左右两侧各有一个篮球和篮筐元素，中间留空透明或纯深色，霓虹灯光效果，橙色和蓝色渐变光晕，科技感，游戏UI风格，暗色调，适合作为APP背景，4K高清
```

**提示词（英文）**：
```
Dark basketball themed background, basketball and hoop elements on left and right sides, empty or solid dark center area, neon light effects, orange and blue gradient glow, tech style, game UI design, dark tone, suitable for app background, 4K HD, digital art
```

**负面提示词**：
```
bright, white background, text, watermark, blurry, low quality
```

---

## 2. 空状态插画

**用途**：当"进行中的比赛"列表为空时显示

**尺寸建议**：400 x 300

**提示词（中文）**：
```
可爱卡通风格，一个橙色篮球躺在地上休息，旁边有一个迷你篮筐，简约扁平插画风格，透明背景，柔和的阴影，轻松有趣的氛围，适合空状态提示
```

**提示词（英文）**：
```
Cute cartoon style, an orange basketball resting on the ground, a mini basketball hoop beside it, simple flat illustration style, transparent background, soft shadows, relaxed and fun atmosphere, empty state illustration, vector art
```

---

## 3. 玩家卡片装饰 - 篮球图标

**用途**：玩家卡片角落装饰

**尺寸建议**：64 x 64

**提示词（中文）**：
```
3D篮球图标，橙色篮球，黑色纹路清晰，轻微发光效果，透明背景，游戏道具风格，高清渲染
```

**提示词（英文）**：
```
3D basketball icon, orange basketball, clear black texture lines, slight glow effect, transparent background, game item style, high quality render, PNG
```

---

## 4. 领先玩家特效 - 火焰效果

**用途**：领先玩家卡片底部装饰

**尺寸建议**：200 x 100

**提示词（中文）**：
```
卡通火焰效果，橙色和黄色渐变火焰，从底部向上燃烧，透明背景，游戏特效风格，动感，适合作为装饰元素
```

**提示词（英文）**：
```
Cartoon fire effect, orange and yellow gradient flames, burning upward from bottom, transparent background, game effect style, dynamic, decorative element, PNG
```

---

## 5. 结算页面 - 冠军奖杯

**用途**：结算弹窗中冠军展示区域

**尺寸建议**：200 x 200

**提示词（中文）**：
```
金色篮球冠军奖杯，3D渲染风格，奖杯上镶嵌一个小篮球，金光闪闪，透明背景，庆祝胜利氛围，游戏成就图标风格
```

**提示词（英文）**：
```
Golden basketball champion trophy, 3D render style, small basketball embedded on trophy, shiny gold, transparent background, victory celebration mood, game achievement icon style, PNG
```

---

## 6. 结算页面 - 金币/转账图标

**用途**：转账明细区域装饰

**尺寸建议**：64 x 64

**提示词（中文）**：
```
3D金币图标，金色硬币堆叠，闪光效果，透明背景，游戏货币风格，卡通渲染
```

**提示词（英文）**：
```
3D gold coin icon, stacked golden coins, sparkle effect, transparent background, game currency style, cartoon render, PNG
```

---

## 7. 历史记录页 - 头部装饰

**用途**：历史记录页面顶部装饰条

**尺寸建议**：800 x 150

**提示词（中文）**：
```
篮球数据统计风格横幅，深色背景，左侧有篮球剪影，右侧有数据图表线条装饰，橙色和蓝色霓虹光效，科技感，游戏UI风格
```

**提示词（英文）**：
```
Basketball statistics style banner, dark background, basketball silhouette on left, data chart line decorations on right, orange and blue neon glow, tech style, game UI design, wide format
```

---

## 8. 高命中率装饰 - 星星效果

**用途**：命中率超过 80% 的玩家卡片装饰

**尺寸建议**：80 x 80

**提示词（中文）**：
```
金色五角星图标，3D立体效果，闪闪发光，透明背景，游戏成就星星风格，高清
```

**提示词（英文）**：
```
Golden five-pointed star icon, 3D effect, sparkling shine, transparent background, game achievement star style, high quality, PNG
```

---

## 图片存放位置

生成后请将图片放在以下目录：
```
frontend/src/assets/basketball/
├── bg-main_3.png          # 主背景图
├── empty-state.png      # 空状态插画
├── ball-icon.png        # 篮球图标
├── fire-effect.png      # 火焰效果
├── trophy.png           # 冠军奖杯
├── coins.png            # 金币图标
├── history-banner.png   # 历史记录横幅
└── star.png             # 星星效果
```

---

## 注意事项

1. **背景图**：需要确保中间区域较暗或留空，两侧元素不要太亮
2. **透明背景**：除主背景外，其他图片最好是 PNG 透明背景
3. **色调**：整体偏深色，主色调为橙色（篮球色）+ 蓝色/紫色（科技感）
4. **风格统一**：建议使用同一个 AI 工具生成，保持风格一致性

生成完成后告诉我，我来帮你把图片配置到代码中！
