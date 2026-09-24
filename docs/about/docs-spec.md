# 开源项目 Docs 目录结构规范（Diátaxis 标准）
> 文件路径：`docs/about/docs-spec.md`
> 适用：OpenAdmin 开源项目，单仓库朴素 Monorepo，**文档框架无关**，不绑定任何静态文档生成工具。
> 目标：统一所有贡献者新增文档的存放位置、写作定位与命名规则。

## 1. 概述
本文档规定本项目 `docs/` 的目录结构、文档分类、写作边界、命名约定。
文档体系遵循 **Diátaxis** 文档四象限方法论，将文档分成 4 大类核心文档，外加独立的贡献开发文档与附加信息。

> 仓库整体结构：
> - `web/`：前端源码工程目录（工程实体目录名）
> - `server/`：后端源码工程目录（工程实体目录名）
> - `docs/`：Markdown 文档源码、图片与图表资源

> 核心原则：
> **源码目录使用 `web/server`；文档描述架构分层时，统一使用 `frontend/backend`。**
> 工程实体和架构概念解耦，避免歧义。

> Diátaxis 核心思想：文档按照**读者目标**划分，而不是按代码模块划分。
> - Tutorials：用于**学习**
> - How-to guides：用于**完成任务**
> - Reference：用于**查阅**
> - Explanation：用于**理解**

> `development/` 不属于 Diátaxis 四象限，是独立的贡献者文档。

## 2. 文档类型定义
### 2.1 Tutorials｜教程（学习）
**定位：引导新手系统性学习，从零上手。**
面向第一次接触项目的读者。采用循序渐进的教学叙事，带读者完成一整条完整流程，目标是**建立基础认知**，不一定解决读者真实业务需求。

特点：
- 叙事风格，一步一步跟着操作；
- 侧重建立概念，适合入门；
- 不深入底层原理，不罗列全部配置。

关键词：安装、首次启动、入门课程、从零创建示例。

### 2.2 How-to｜实操指南（做事）
**定位：指导读者完成一个具体任务。**
面向已经掌握基础使用的读者。读者已经知道自己想要达成什么目标，只需要可执行的步骤。
包含自定义配置、功能启用、场景改造、故障排查。

特点：
- 任务导向；标题常用「如何……」；
- 聚焦目标，不讲解底层原理；
- troubleshooting（故障排查）归类在此。

关键词：配置、自定义、开启功能、修改样式、排查报错。

### 2.3 Reference｜参考手册（查阅）
**定位：字典式参考，客观陈述，无教学叙事。**
供读者查找准确信息。只陈述事实，不写教程、不解释设计动机。是“查找资料”而不是“阅读学习”。

特点：
- 清单、表格、字段定义；
- 描述参数、类型、取值、默认值；
- 不写长流程，不解释为什么这么设计。

关键词：API、配置项、CLI 参数、组件属性 Props、数据库表结构。

### 2.4 Explanation｜原理解析（理解）
**定位：解释背景、架构、设计取舍、底层实现。**
面向需要深入理解项目的二次开发者、源码阅读者。回答**为什么**，而不是怎么做。
可以包含方案对比、权衡、设计决策、核心流程拆解。

特点：
- 讲思想、取舍、约束；
- 可以附带源码解析、流程图；
- 不教部署，不教基础使用。

关键词：架构、原理、实现解析、设计决策、技术选型。

### 2.5 Development｜开发贡献文档（独立分类）
不属于 Diátaxis 四类。面向**希望向本仓库提交代码/文档的贡献者**。
内容：本地开发环境搭建、构建、测试、代码规范、提交规范、PR 流程。
> ⚠️ 注意区分：`development/` 讲**如何参与项目开发**；`explanation/` 讲**项目本身内部原理**。二者不可混淆。

## 3. 目录树
```
docs
├── index.md                  # 文档首页
├── tutorials/                # 【学习】教程
│   ├── overview.md           # 教程总览
│   ├── getting-started/      # 快速入门
│   │   ├── install.md
│   │   └── quickstart.md
│   └── basic-course/         # 基础学习课程
├── how-to/                   # 【做事】实操指南
│   ├── frontend/             # 前端场景任务
│   ├── backend/             # 后端场景任务
│   └── troubleshooting/      # 故障排查
├── reference/                # 【查阅】参考手册
│   ├── frontend/             # 前端组件、指令、配置参考
│   ├── backend/              # 后端API、CLI、数据库结构
│   └── global-config.md      # 全局配置总参考
├── explanation/              # 【理解】原理解析
│   ├── architecture/         # 整体架构
│   ├── frontend/             # 前端底层原理与实现解析
│   └── backend/              # 后端核心逻辑原理
├── development/              # 贡献者开发指南（非Diátaxis）
│   ├── contributing.md
│   ├── dev-env.md
│   ├── build.md
│   ├── test.md
│   └── code-style.md
├── assets/                   # 静态资源：图片、图表
│   ├── images/
│   └── diagrams/
└── about/                    # 附加信息
    ├── faq.md
    ├── license.md
    ├── thanks.md
    └── docs-spec.md          # 👉 本文档（目录规范）
```

## 4. 命名规范（强制）
### 4.1 目录命名约定
- 在 `docs/` 内部所有文档分类目录，区分前后端时使用：`frontend` / `backend`
- 仓库源码根目录使用：`web/` 和 `server/`
> 在文档写源码链接时，链接路径写 `web/xxx.vue` / `server/xxx.py`，和仓库源码路径保持一致。

### 4.2 Markdown 文件命名
全部文件采用 **kebab-case**：小写英文字母，单词之间用短横线 `-`。
- ✅ `theme-ripple-animation.md`
- ❌ `themeRippleAnimation.md`、`theme_ripple.md`、`主题扩散动画.md`

禁止中文文件名、空格、驼峰、下划线。

### 4.3 静态资源规范
图片、截图、mermaid 导出图、示意图统一放在 `docs/assets/`。
可继续按模块建立子目录，例如 `assets/images/frontend/`。
图片不要和 md 文件放在同一目录。
图片尽量压缩，不提交大体积原图。

> 资源路径示例：`../assets/images/frontend/theme-ripple.png`

## 5. 文档归类对照表（示例）
| 文档位置 | 文档示例 | 读者 |
|---|---|---|
| `tutorials/getting-started/install.md` | 安装部署 OpenAdmin，启动第一个实例 | 首次使用项目的新用户 |
| `how-to/frontend/enable-dark-mode.md` | 如何开启深色主题功能 | 项目使用者，做配置 |
| `reference/frontend/components.md` | 前端组件全部属性、事件定义 | 需要查阅参数的开发者 |
| `explanation/frontend/theme-ripple-animation.md` | 主题切换圆形扩散动画实现原理 | 读源码、二次深度开发 |
| `development/contributing.md` | 如何Fork、提交PR、代码提交规范 | 想给项目贡献代码的开发者 |

### 关键区分示例
1. `how-to/frontend/enable-dark-mode.md`：**怎么打开深色模式（操作）**
2. `explanation/frontend/theme-ripple-animation.md`：**切换动画底层是怎么实现的（原理）**

> 不要把原理写进 How-to；不要把操作步骤写进 Explanation。

## 6. 写作边界与禁止混放规则
1. Tutorials（教程）：只写学习流程。**不粘贴完整API参考、不深入底层原理**。
2. How-to（实操）：只写完成任务的步骤。不解释大量底层设计取舍。
3. Reference（参考）：纯事实清单。**不要写教程式步骤，不要长篇原理描述**。
4. Explanation（原理）：解释设计与实现。不写部署教程，不写基础操作步骤。
5. `development/` 是贡献指南，**不属于 explanation**，不能把提交PR、本地构建文档放到 explanation。

> 一条文档只承担**一个目的**。如果一段文字既是教程又是原理，拆成两个文档分别放在对应目录。

## 7. 站点导航推荐顺序
如果文档站点生成菜单，推荐顺序遵循读者认知流：
1. 首页
2. 教程（Tutorials）
3. 实操指南（How-to）
4. 参考手册（Reference）
5. 原理解析（Explanation）
6. 开发贡献（Development）
7. 关于（About）

> 这是推荐顺序，不是强制文件系统顺序；文档工具如有侧边栏限制，可酌情调整，但尽量维持阅读认知顺序。

## 8. 工程约定
1. `docs/` 仅保存 Markdown 源码、图片、图表资源。
2. 静态站点构建产出的 HTML/CSS/JS 等产物**不提交到 Git**，由 CI 在构建时生成。
3. 文档中链接到源码时，使用仓库主分支的路径，指向仓库根目录下的 `web/`、`server/`。
4. 目录结构一旦稳定，尽量避免大规模重构；重构需要在版本更新中明确说明，防止外部链接失效。

## 9. 一句话总结
> **源码看工程目录（web/server），文档看架构分层（frontend/backend）；新手看 tutorials，用户看 how-to，开发查 reference，源码读 explanation，贡献看 development。**
