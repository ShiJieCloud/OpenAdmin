# OpenAdmin 🚀
轻量级、开箱即用的前后端分离后台管理系统，基于 FastAPI + Vue3 构建，专注于高效开发、易扩展、低门槛，适合中小企业后台、个人项目、快速开发场景。

## 📂 项目结构
```
OpenAdmin/
├── server/           # 后端代码目录（基于 FastAPI）
├── web/              # 前端代码目录（基于 Vue3）
├── .gitignore        # Git 忽略文件
├── LICENSE           # 许可证
└── README.md         # 项目文档
```

## 🛠️ 技术栈
---
### 🔧 后端技术栈（FastAPI）
| 技术 | 版本要求 | 作用 |
|------|---------|------|
| Python | ≥3.9 | 后端开发核心语言 |
| FastAPI | ≥0.100 | 高性能异步Web框架，自动生成接口文档、类型校验 |
| SQLAlchemy | ≥2.0 | Python现代化ORM框架，封装数据库读写操作 |
| Pydantic | ≥2.0 | 请求参数校验、模型序列化，减少数据错误 |
| PyJWT | 最新 | 无状态Token登录、接口权限鉴权，保障系统安全 |
| MySQL | ≥5.7/8.0 | 系统主数据库，存储所有业务数据 |
| Redis | ≥7.0 | 缓存（可选），提升接口响应速度、存储Token黑名单 |

### 🎨 前端技术栈（Vue3）
| 技术 | 版本要求 | 作用 |
|------|---------|------|
| Vue3 | ≥3.3 | 前端核心框架，实现MVVM架构，高效渲染页面 |
| Vite | ≥5.0 | 前端构建工具，实现极速热更新、高效打包 |
| Element Plus | ≥2.4 | Vue3专属UI组件库，提供后台管理所需全部组件 |
| Pinia | ≥2.0 | Vue3状态管理工具，替代Vuex，简化全局状态管理 |
| Axios | ≥1.0 | 前端HTTP请求库，实现前后端接口通信、请求拦截 |

## 📄 许可证
本项目采用 [MIT License](LICENSE) 许可证开源。

## 🙏 鸣谢
感谢以下开源项目的支持：
- FastAPI：https://fastapi.tiangolo.com/
- Vue3：https://vuejs.org/
- Element Plus：https://element-plus.org/
- SQLAlchemy：https://www.sqlalchemy.org/

## 📞 联系作者
如果有问题、建议或合作需求，欢迎提交 Issue 到项目仓库。

---
⭐️ 如果你觉得这个项目有用，请给个 Star 支持一下！