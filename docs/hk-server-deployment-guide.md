# 香港服务器测试部署指南

## 1. 先明确边界

不能把 ChatGPT / Codex 这种托管模型本体“安装”到你的香港服务器上离线运行。

正确方式是：

1. 你的香港服务器部署产品后端、数据库、文件存储、任务队列和 Agent 编排逻辑
2. 后端通过 OpenAI API 调用模型
3. 模型输出 `Asset Spec`
4. 你的后端校验 `Asset Spec`，生成导出包
5. CS2 `Base Mod` 在玩家本机读取导出包

也就是说，香港服务器跑的是你的应用，不是 OpenAI 模型权重。

## 2. 推荐测试架构

```mermaid
flowchart TD
    A["Browser / Web UI"] --> B["Hong Kong Server"]
    B --> C["Backend API"]
    C --> D["AI Orchestrator"]
    D --> E["OpenAI API"]
    C --> F["PostgreSQL"]
    C --> G["Object Storage / Local Files"]
    C --> H["Asset Spec Validator"]
    C --> I["Package Builder"]
    I --> J["Downloadable Asset Package"]
    J --> K["Player PC"]
    K --> L["CS2 Base Mod"]
```

## 3. 最小服务器配置

测试阶段建议：

1. Ubuntu 22.04 或 24.04
2. 2 vCPU
3. 4 GB RAM
4. 40 GB SSD
5. 公网 IP
6. HTTPS 域名

如果后续要做图像处理、3D 预览或资产转码，再升级机器。

## 4. 服务器需要安装的组件

最小测试环境：

1. `git`
2. `docker`
3. `docker compose`
4. `nginx`
5. `certbot`

应用组件：

1. `frontend`: Next.js Web UI
2. `backend`: FastAPI / Python API
3. `postgres`: 项目、用户、版本、日志
4. `worker`: 异步生成任务
5. `storage`: 本地文件夹或 S3 兼容对象存储

## 5. OpenAI API 接入

服务器上只需要保存 API Key：

```bash
export OPENAI_API_KEY="your_api_key_here"
```

生产环境不要把 API Key 写进前端，也不要提交到 GitHub。建议放在：

1. `.env`
2. Docker secret
3. 云厂商 Secret Manager
4. 服务器环境变量

后端调用模型时，推荐先使用 Responses API 生成结构化 `Asset Spec`。后续如果需要多步骤编排、工具调用、审核和追踪，再引入 Agents SDK。

## 6. 最小测试流程

第一轮不需要完整网站，建议只跑后端接口。

### 6.1 输入

用户请求：

```text
我想做一个香港风格的中型火车站，有玻璃大厅、两个岛式站台、双语标识。
```

### 6.2 后端调用模型

模型输出：

```json
{
  "spec_version": "0.1",
  "game": "cities_skylines_2",
  "asset_type": "train_station",
  "title": "Hong Kong Glass Transit Station",
  "style": {
    "theme": "modern_transit",
    "regional_inspiration": "hong_kong",
    "materials": ["glass", "steel", "concrete"]
  },
  "footprint": {
    "width": 64,
    "length": 128,
    "height_class": "midrise"
  },
  "modules": [
    {
      "module_id": "station.platform.island.medium",
      "count": 2
    },
    {
      "module_id": "station.concourse.glass_hall",
      "count": 1
    },
    {
      "module_id": "station.entrance.corner",
      "count": 2
    }
  ],
  "connections": {
    "rail_tracks": 4,
    "road_access": 2,
    "pedestrian_entries": 3
  },
  "decor": {
    "sign_language": ["zh-HK", "en"],
    "color_palette": ["#C8102E", "#E6E6E6", "#333333"]
  },
  "runtime_constraints": {
    "template_only": true,
    "requires_base_mod": true,
    "base_mod_min_version": "0.1.0"
  }
}
```

### 6.3 后端校验

调用本仓库已有的 `Asset Spec` schema 和后续后端 validator：

1. 字段是否完整
2. 模块 ID 是否存在
3. 尺寸是否超出 MVP 范围
4. 轨道数、站台数、入口数是否匹配
5. 颜色是否是合法 hex

### 6.4 生成导出包

输出一个 zip：

```text
asset-package.zip
├── active-asset.json
├── manifest.json
├── preview.json
└── README.md
```

玩家下载后，把 `active-asset.json` 放到 CS2 `Base Mod` 指定目录。

## 7. 推荐部署步骤

### 7.1 在服务器创建用户

```bash
adduser aigamemod
usermod -aG docker aigamemod
```

### 7.2 拉取仓库

```bash
su - aigamemod
git clone <your-github-repo-url> ai-game-mod-studio
cd ai-game-mod-studio
```

### 7.3 配置环境变量

```bash
cp .env.example .env
```

`.env` 最少需要：

```bash
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/aigamemod
APP_ENV=staging
PUBLIC_BASE_URL=https://your-domain.example
```

### 7.4 启动服务

等仓库补齐 `docker-compose.yml` 后，目标命令应是：

```bash
docker compose up -d --build
```

### 7.5 配置 HTTPS

```bash
sudo certbot --nginx -d your-domain.example
```

## 8. MVP 部署验收标准

服务器测试成功的标准：

1. 前端能打开
2. 后端健康检查通过
3. 后端能成功调用 OpenAI API
4. 输入自然语言后能生成 `Asset Spec`
5. `Asset Spec` 能通过 schema 校验
6. 能导出 `active-asset.json`
7. 本地 CS2 `Base Mod` 能读取该文件

## 9. 安全要求

必须坚持：

1. OpenAI API Key 只放后端
2. 前端不能直接调用 OpenAI API
3. 用户上传文件必须限制大小和类型
4. 生成结果必须经过 validator，不能直接信任模型输出
5. 每次生成都要记录输入、输出、校验结果和导出版本

## 10. 下一步需要补的工程文件

当前仓库还需要补：

1. `backend` 最小 FastAPI 服务
2. `POST /api/specs/generate`
3. `POST /api/specs/validate`
4. `POST /api/packages/build`
5. `docker-compose.yml`
6. `.env.example`
7. `frontend` 最小输入页面

建议先补 `backend + docker-compose`，这样香港服务器可以最快跑通第一轮闭环。
