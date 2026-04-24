# Base Mod 验证计划

## 目标

先验证一个最小 CS2 Base Mod 是否可行，而不是直接承诺完整资产生成。

最小验证目标：

1. 读取外部 `Asset Spec` 配置文件
2. 校验配置是否合法
3. 生成确定性的站点运行计划
4. 在 CS2 Code Mod 中加载该运行计划
5. 后续再将运行计划映射到真实 prefab、Editor 资产或模板模块

## 当前仓库已提供的内容

1. `schemas/asset-spec.schema.json`
2. `examples/asset-specs/minimal-harbor-station.json`
3. `template-library/stations/minimal-train-station.template.json`
4. `base-mod/src/AiGameModStudio.BaseMod.Core`
5. `base-mod/src/AiGameModStudio.SpecProbe`
6. `base-mod/src/AiGameModStudio.CS2Runtime`

## 本地验证步骤

安装 .NET SDK 8 后运行：

```bash
dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- examples/asset-specs/minimal-harbor-station.json
```

成功标准：

1. 进程返回 `0`
2. 没有 `Error` 级别校验问题
3. 输出包含 `module_instances`
4. 输出中的实例数量等于示例配置中模块数量总和

验证外部运行时目录：

```bash
mkdir -p /tmp/ai-game-mod-studio
cp examples/asset-specs/minimal-harbor-station.json /tmp/ai-game-mod-studio/active-asset.json
dotnet run --project base-mod/src/AiGameModStudio.SpecProbe -- --data-dir /tmp/ai-game-mod-studio
```

成功标准：

1. 进程返回 `0`
2. 输出 `state` 为 `Loaded`
3. 目录下生成 `runtime-status.log`
4. 目录下生成 `runtime-status.json`

## 游戏内验证步骤

1. 在 `Cities: Skylines II` 中安装官方 Code Mod 工具链
2. 使用官方模板创建一个新的 Code Mod 项目
3. 引用 `base-mod/src/AiGameModStudio.BaseMod.Core`
4. 将 `base-mod/src/AiGameModStudio.CS2Runtime` 中的文件复制进官方模板项目
5. 定义 `CITIES_SKYLINES_2` 编译符号
6. 通过官方模板构建并让工具链部署到游戏 Mod 目录
7. 将示例配置复制为运行时读取路径下的 `active-asset.json`
8. 启动游戏并查看日志

自动生成官方模板集成项目：

```powershell
base-mod\tools\Install-CS2OfficialTemplate.ps1 `
  -RepoRoot E:\vscode\code\AI_Game_model `
  -GamePath "E:\SteamLibrary\steamapps\common\Cities Skylines II" `
  -Force `
  -Build
```

如果官方工具链尚未在游戏内完成初始化，可先运行 compile-only 预检：

```powershell
base-mod\tools\Install-CS2OfficialTemplate.ps1 `
  -RepoRoot E:\vscode\code\AI_Game_model `
  -GamePath "E:\SteamLibrary\steamapps\common\Cities Skylines II" `
  -Force `
  -Build `
  -CompileOnly
```

运行时默认读取路径：

```text
<LocalApplicationData>/Colossal Order/Cities Skylines II/ModsData/AiGameModStudio/active-asset.json
```

运行时状态文件：

```text
<LocalApplicationData>/Colossal Order/Cities Skylines II/ModsData/AiGameModStudio/runtime-status.log
<LocalApplicationData>/Colossal Order/Cities Skylines II/ModsData/AiGameModStudio/runtime-status.json
```

首轮游戏内成功标准：

1. Mod 能加载
2. 日志显示找到了 `active-asset.json`
3. 日志显示配置校验通过
4. 日志显示生成了站点 runtime plan
5. 修改或替换 `active-asset.json` 后，日志显示触发热重载

这一轮不要求真的生成可见车站。可见实例化是下一轮。

## 下一轮验证

下一轮才进入 CS2 具体 prefab / asset 绑定：

1. 找到一个可复用的官方或 Editor 生成的站点 prefab
2. 将 `RuntimeModuleInstance` 映射到 prefab 或 sub-object
3. 验证名称、颜色、入口数、站台数等参数能影响游戏内结果
4. 再评估是否需要转向 Asset Editor 生成资产包，而不是纯运行时实例化

## 官方资料依据

Paradox 的 Code Mod 说明确认了官方工具链会安装 Unity、Burst、ECS 等依赖，并提供代码 Mod 项目模板、依赖和 post-build 动作。官方资料也说明 CS2 更推荐创建自己的系统并注册到更新循环，而不是依赖脆弱的补丁式修改。

Paradox 的 Custom Assets 说明确认了自定义资产通过 Editor 导入 mesh、texture，设置 prefab preset，并通过场景内编辑、路径、功能参数和 Paradox Mods 分享完成资产流程。因此本项目的安全路径是：Base Mod 先读取 `Asset Spec`，后续再决定映射到运行时 prefab，还是驱动 Editor 资产模板。

参考：

1. https://www.paradoxinteractive.com/games/cities-skylines-ii/modding/dev-diary-3-code-modding
2. https://www.paradoxinteractive.com/zh-CN/games/cities-skylines-ii/news/adding-custom-assets
