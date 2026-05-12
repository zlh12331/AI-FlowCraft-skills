# 设计规范 (Design Spec)

> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}

## 1. 设计规范概述

*用一段话概括本项目的视觉设计方向和核心原则。*

> **设计理念**：{{在此处生成，如"简洁、专业、高效"}}
> **适用范围**：{{在此处生成，如"本项目所有前端页面和组件"}}
> **设计工具**：{{在此处生成，如"Figma / 直接编码（基于 TailwindCSS Design Token）"}}
> **技术适配**：{{在此处生成，如"所有 Design Token 命名与 TailwindCSS 命名约定兼容，可直接映射为 TailwindCSS 工具类或通过 CSS 变量在 tailwind.config.ts 中扩展使用。"}}

---

## 2. 色板 (Color Palette)

### 2.1 主色 (Primary)

*品牌核心色，用于主要按钮、链接、选中状态等。*

| 名称 | 色值 (HEX) | 色值 (HSL) | CSS 变量名 | 用途 |
|------|-----------|-----------|-----------|------|
| Primary-50 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-50` | 浅色背景 |
| Primary-100 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-100` | 悬停背景 |
| Primary-200 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-200` | 选中背景 |
| Primary-500 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-500` | 主色/品牌色 |
| Primary-600 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-600` | 悬停状态 |
| Primary-700 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-700` | 按下状态 |
| Primary-900 | `#{{HEX}}` | `{{HSL}}` | `--color-primary-900` | 深色文字 |

### 2.2 辅色 (Secondary)

*辅助色，用于次要元素、标签、图标等。*

| 名称 | 色值 (HEX) | 色值 (HSL) | CSS 变量名 | 用途 |
|------|-----------|-----------|-----------|------|
| Secondary-50 | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-50` | 浅色背景 |
| Secondary-100 | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-100` | 悬停背景 |
| Secondary-500 | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-500` | 辅色 |
| Secondary-600 | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-600` | 悬停状态 |
| Secondary-700 | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-700` | 按下状态 |

### 2.3 功能色 (Semantic)

*用于传达特定语义的颜色。*

| 名称 | 色值 (HEX) | 色值 (HSL) | CSS 变量名 | 用途 |
|------|-----------|-----------|-----------|------|
| Success | `#{{HEX}}` | `{{HSL}}` | `--color-success` | 成功状态 |
| Warning | `#{{HEX}}` | `{{HSL}}` | `--color-warning` | 警告状态 |
| Error | `#{{HEX}}` | `{{HSL}}` | `--color-error` | 错误状态 |
| Info | `#{{HEX}}` | `{{HSL}}` | `--color-info` | 信息提示 |

### 2.4 中性色 (Neutral)

*用于文字、背景、边框、分割线等基础元素。*

| 名称 | 色值 (HEX) | 色值 (HSL) | CSS 变量名 | 用途 |
|------|-----------|-----------|-----------|------|
| Neutral-0 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-0` | 纯白背景 |
| Neutral-50 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-50` | 浅灰背景 |
| Neutral-100 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-100` | 分割线/边框 |
| Neutral-200 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-200` | 禁用边框 |
| Neutral-300 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-300` | 占位符文字 |
| Neutral-400 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-400` | 次要文字 |
| Neutral-500 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-500` | 正文文字 |
| Neutral-600 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-600` | 标题文字 |
| Neutral-700 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-700` | 强调文字 |
| Neutral-900 | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-900` | 纯黑/深色 |

### 2.5 暗色模式映射表

*暗色模式下各颜色的替换映射。通过在 `:root[data-theme="dark"]` 或 `.dark` 选择器下覆盖 CSS 变量值实现主题切换。*

| 亮色模式 Token | 暗色模式替换值 (HEX) | 暗色模式替换值 (HSL) | CSS 变量名 |
|---------------|---------------------|---------------------|-----------|
| `--color-primary-50` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-50` |
| `--color-primary-100` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-100` |
| `--color-primary-200` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-200` |
| `--color-primary-500` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-500` |
| `--color-primary-600` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-600` |
| `--color-primary-700` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-700` |
| `--color-primary-900` | `#{{HEX}}` | `{{HSL}}` | `--color-primary-900` |
| `--color-secondary-50` | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-50` |
| `--color-secondary-100` | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-100` |
| `--color-secondary-500` | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-500` |
| `--color-secondary-600` | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-600` |
| `--color-secondary-700` | `#{{HEX}}` | `{{HSL}}` | `--color-secondary-700` |
| `--color-success` | `#{{HEX}}` | `{{HSL}}` | `--color-success` |
| `--color-warning` | `#{{HEX}}` | `{{HSL}}` | `--color-warning` |
| `--color-error` | `#{{HEX}}` | `{{HSL}}` | `--color-error` |
| `--color-info` | `#{{HEX}}` | `{{HSL}}` | `--color-info` |
| `--color-neutral-0` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-0` |
| `--color-neutral-50` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-50` |
| `--color-neutral-100` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-100` |
| `--color-neutral-200` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-200` |
| `--color-neutral-300` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-300` |
| `--color-neutral-400` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-400` |
| `--color-neutral-500` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-500` |
| `--color-neutral-600` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-600` |
| `--color-neutral-700` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-700` |
| `--color-neutral-900` | `#{{HEX}}` | `{{HSL}}` | `--color-neutral-900` |

> **暗色模式设计原则**：
> - 背景色和文字色进行反转，但不是简单的黑白互换，而是使用深蓝灰色系（slate）作为暗色背景，避免纯黑背景造成的视觉疲劳。
> - 功能色在暗色模式下适当提高亮度（提升 10-15%），确保在深色背景上的可读性和辨识度。

---

## 3. 字体体系 (Typography)

### 3.1 字体族 (Font Family)

| 类型 | 字体族 | 回退字体 | CSS 变量名 |
|------|-------|---------|-----------|
| 正文 (Body) | `{{字体名}}` | `{{回退字体}}` | `--font-family-body` |
| 标题 (Heading) | `{{字体名}}` | `{{回退字体}}` | `--font-family-heading` |
| 代码 (Code) | `{{字体名}}` | `{{回退字体}}` | `--font-family-code` |

### 3.2 字号梯度表 (Font Size Scale)

| 级别 | 名称 | 字号 | 行高 | 字重 | CSS 变量名 | 使用场景 |
|------|------|------|------|------|-----------|---------|
| Display | 超大标题 | `{{字号值}}px` | `{{行高值}}` | Bold (700) | `--font-size-display` | 首页 Hero |
| H1 | 一级标题 | `{{字号值}}px` | `{{行高值}}` | Bold (700) | `--font-size-h1` | 页面标题 |
| H2 | 二级标题 | `{{字号值}}px` | `{{行高值}}` | Semibold (600) | `--font-size-h2` | 区块标题 |
| H3 | 三级标题 | `{{字号值}}px` | `{{行高值}}` | Semibold (600) | `--font-size-h3` | 卡片标题 |
| H4 | 四级标题 | `{{字号值}}px` | `{{行高值}}` | Medium (500) | `--font-size-h4` | 小标题 |
| Body-LG | 大正文 | `{{字号值}}px` | `{{行高值}}` | Regular (400) | `--font-size-body-lg` | 强调正文 |
| Body | 正文 | `{{字号值}}px` | `{{行高值}}` | Regular (400) | `--font-size-body` | 正文内容 |
| Body-SM | 小正文 | `{{字号值}}px` | `{{行高值}}` | Regular (400) | `--font-size-body-sm` | 辅助说明 |
| Caption | 说明文字 | `{{字号值}}px` | `{{行高值}}` | Regular (400) | `--font-size-caption` | 标签/注释 |
| Overline | 超小文字 | `{{字号值}}px` | `{{行高值}}` | Medium (500) | `--font-size-overline` | 标签/徽章 |

### 3.3 字重规范 (Font Weight)

| 名称 | 字重值 | CSS 变量名 | 使用场景 |
|------|-------|-----------|---------|
| Regular | 400 | `--font-weight-regular` | 正文内容 |
| Medium | 500 | `--font-weight-medium` | 按钮/标签 |
| Semibold | 600 | `--font-weight-semibold` | 小标题/强调 |
| Bold | 700 | `--font-weight-bold` | 大标题/重点 |

---

## 4. 间距系统 (Spacing)

### 4.1 基础间距单位

> **基础单位**：`{{4px / 8px}}`
> **设计原则**：所有间距值为基础单位的整数倍，保持视觉节奏一致。

### 4.2 间距梯度表 (Spacing Scale)

| 级别 | Token 名 | 值 | TailwindCSS 映射 | CSS 变量名 | 使用场景 |
|------|---------|-----|-----------------|-----------|---------|
| 0 | space-0 | `0px` | `0` | `--spacing-0` | 无间距 |
| xs | space-xs | `{{间距值}}px` | `1` | `--spacing-xs` | 紧凑元素间距 |
| sm | space-sm | `{{间距值}}px` | `2` | `--spacing-sm` | 相关元素间距 |
| md | space-md | `{{间距值}}px` | `3` | `--spacing-md` | 默认间距 |
| lg | space-lg | `{{间距值}}px` | `4` | `--spacing-lg` | 区块内间距 |
| xl | space-xl | `{{间距值}}px` | `6` | `--spacing-xl` | 区块间间距 |
| 2xl | space-2xl | `{{间距值}}px` | `8` | `--spacing-2xl` | 大区块间距 |
| 3xl | space-3xl | `{{间距值}}px` | `12` | `--spacing-3xl` | 页面级间距 |
| 4xl | space-4xl | `{{间距值}}px` | `16` | `--spacing-4xl` | 页面顶部/底部 |

### 4.3 组件内外间距规则

| 组件类型 | 内间距 (Padding) | 外间距 (Margin) | 间距 Token |
|---------|-----------------|----------------|-----------|
| 按钮 (Button) | `{{间距值}}px {{间距值}}px` | — | `--spacing-sm --spacing-md` |
| 输入框 (Input) | `{{间距值}}px {{间距值}}px` | `--spacing-sm 0` | — |
| 卡片 (Card) | `--spacing-lg` | `--spacing-md 0` | — |
| 模态框 (Modal) | `--spacing-lg` | — | — |
| 列表项 (List Item) | `--spacing-md` | — | — |
| 页面容器 (Container) | `--spacing-lg --spacing-xl` | — | — |

---

## 5. 圆角规范 (Border Radius)

### 5.1 圆角梯度表

| 级别 | Token 名 | 值 | TailwindCSS 映射 | CSS 变量名 | 使用场景 |
|------|---------|-----|-----------------|-----------|---------|
| none | radius-none | `0px` | `rounded-none` | `--radius-none` | 直角元素 |
| sm | radius-sm | `{{圆角值}}px` | `rounded-sm` | `--radius-sm` | 小元素（标签、徽章） |
| md | radius-md | `{{圆角值}}px` | `rounded-lg` | `--radius-md` | 按钮、输入框 |
| lg | radius-lg | `{{圆角值}}px` | `rounded-xl` | `--radius-lg` | 卡片、弹窗 |
| xl | radius-xl | `{{圆角值}}px` | `rounded-2xl` | `--radius-xl` | 大容器 |
| full | radius-full | `9999px` | `rounded-full` | `--radius-full` | 圆形元素（头像、胶囊按钮） |

---

## 6. 阴影规范 (Box Shadow)

### 6.1 阴影梯度表

| 级别 | Token 名 | 值 | CSS 变量名 | 使用场景 |
|------|---------|-----|-----------|---------|
| none | shadow-none | `none` | `--shadow-none` | 无阴影 |
| sm | shadow-sm | `{{阴影值}}` | `--shadow-sm` | 卡片默认状态 |
| md | shadow-md | `{{阴影值}}` | `--shadow-md` | 卡片悬停/下拉菜单 |
| lg | shadow-lg | `{{阴影值}}` | `--shadow-lg` | 弹窗/模态框 |
| xl | shadow-xl | `{{阴影值}}` | `--shadow-xl` | 全屏遮罩层 |

---

## 7. 动效曲线 (Motion / Easing)

### 7.1 缓动函数 (Easing Functions)

| 名称 | 缓动值 | CSS 变量名 | 使用场景 |
|------|-------|-----------|---------|
| ease-default | `cubic-bezier({{缓动值}})` | `--ease-default` | 通用过渡 |
| ease-in | `cubic-bezier({{缓动值}})` | `--ease-in` | 元素进入 |
| ease-out | `cubic-bezier({{缓动值}})` | `--ease-out` | 元素离开 |
| ease-in-out | `cubic-bezier({{缓动值}})` | `--ease-in-out` | 循环动画 |
| ease-spring | `cubic-bezier({{缓动值}})` | `--ease-spring` | 弹性效果 |

### 7.2 时长规范 (Duration)

| 级别 | 时长 | CSS 变量名 | 使用场景 |
|------|------|-----------|---------|
| instant | `0ms` | `--duration-instant` | 即时响应 |
| fast | `{{过渡时长}}ms` | `--duration-fast` | 微交互（悬停、按下） |
| normal | `{{过渡时长}}ms` | `--duration-normal` | 通用过渡（展开、收起） |
| slow | `{{过渡时长}}ms` | `--duration-slow` | 页面切换、复杂动画 |

---

## 8. Design Token 汇总表

> **说明**：本表汇总所有 Design Token，便于前端开发者快速查阅。Token 命名遵循 `--{category}-{property}-{variant}` 格式。

| Token 名 | 值 | 用途 | CSS 变量名 |
|---------|-----|------|-----------|
| `color-primary-500` | `#{{HEX}}` | 品牌主色 | `--color-primary-500` |
| `color-secondary-500` | `#{{HEX}}` | 品牌辅色 | `--color-secondary-500` |
| `color-success` | `#{{HEX}}` | 成功状态 | `--color-success` |
| `color-warning` | `#{{HEX}}` | 警告状态 | `--color-warning` |
| `color-error` | `#{{HEX}}` | 错误状态 | `--color-error` |
| `color-info` | `#{{HEX}}` | 信息提示 | `--color-info` |
| `color-neutral-0` | `#{{HEX}}` | 纯白背景 | `--color-neutral-0` |
| `color-neutral-500` | `#{{HEX}}` | 正文文字 | `--color-neutral-500` |
| `color-neutral-900` | `#{{HEX}}` | 纯黑/深色 | `--color-neutral-900` |
| `font-family-body` | `{{字体名}}` | 正文字体 | `--font-family-body` |
| `font-family-heading` | `{{字体名}}` | 标题字体 | `--font-family-heading` |
| `font-family-code` | `{{字体名}}` | 代码字体 | `--font-family-code` |
| `font-size-body` | `{{字号值}}px` | 正文字号 | `--font-size-body` |
| `font-size-h1` | `{{字号值}}px` | 一级标题 | `--font-size-h1` |
| `font-weight-regular` | `400` | 正文字重 | `--font-weight-regular` |
| `font-weight-bold` | `700` | 标题字重 | `--font-weight-bold` |
| `spacing-md` | `{{间距值}}px` | 默认间距 | `--spacing-md` |
| `spacing-lg` | `{{间距值}}px` | 区块内间距 | `--spacing-lg` |
| `radius-md` | `{{圆角值}}px` | 按钮圆角 | `--radius-md` |
| `radius-lg` | `{{圆角值}}px` | 卡片圆角 | `--radius-lg` |
| `shadow-sm` | `{{阴影值}}` | 卡片阴影 | `--shadow-sm` |
| `shadow-lg` | `{{阴影值}}` | 弹窗阴影 | `--shadow-lg` |
| `ease-default` | `cubic-bezier(...)` | 通用缓动 | `--ease-default` |
| `duration-normal` | `{{过渡时长}}ms` | 通用时长 | `--duration-normal` |

### 8.1 图标规范

| 属性 | 规范 |
|------|------|
| 图标库 | <!-- 如：Lucide Icons / Heroicons / Material Icons --> |
| 尺寸梯度 | <!-- 如：16px / 20px / 24px / 32px --> |
| 使用场景 | <!-- 导航栏: 24px, 按钮: 20px, 内联文本: 16px --> |
| 颜色规则 | <!-- 继承当前文本颜色，或使用语义色 Token --> |

### 8.2 Z-index 层级管理

| 层级 | Z-index 范围 | 用途 |
|------|-------------|------|
| 基础内容 | 0-9 | 页面内容、卡片 |
| 下拉菜单 | 10-19 | Dropdown、Select |
| 吸顶/固定 | 20-29 | Sticky header、Fixed footer |
| 遮罩层 | 30-39 | Modal backdrop |
| 弹窗 | 40-49 | Modal、Dialog |
| Toast | 50-59 | 通知、提示 |
| Tooltip | 60-69 | 工具提示 |

---

## 9. 响应式断点

> 布局策略为"移动优先"（Mobile First），即默认编写移动端样式，通过 `md:` 和 `lg:` 前缀逐步增强桌面端体验。

| 名称 | 最小宽度 | TailwindCSS 前缀 | 使用场景 |
|------|---------|-----------------|---------|
| sm | {{例如：640px}} | `sm:` | {{例如：移动端竖屏}} |
| md | {{例如：768px}} | `md:` | {{例如：平板竖屏}} |
| lg | {{例如：1024px}} | `lg:` | {{例如：平板横屏/小桌面}} |
| xl | {{例如：1280px}} | `xl:` | {{例如：标准桌面}} |

### 9.1 响应式布局规则

| 布局元素 | 移动端 (< 768px) | 桌面端 (>= 768px) |
|---------|-----------------|------------------|
| {{元素 1}} | {{移动端布局描述}} | {{桌面端布局描述}} |
| {{元素 2}} | {{移动端布局描述}} | {{桌面端布局描述}} |

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
