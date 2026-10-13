# 项目交付与维护说明

## 当前结论

Secret Fire 的长期问题不是功能数量，而是职责边界曾经不够清楚：源码、常驻运行目录和本地存档会各自留下一份状态；百科又同时读取“基础物品类别”和“具体百科条目”，却只靠页面里的特殊判断连接。这会造成看似已经写入、实际运行版本未更新，或分类显示为零的情况。

本次整理后，源码目录是唯一可编辑来源。运行版只能由发布脚本从源码生成；个人存档始终在源码外；百科分类明确声明自己的数据来源。

## 目录与职责

| 位置 | 负责内容 | 不负责内容 |
| --- | --- | --- |
| `public/` | 页面、交互、展示状态 | 存档事实与规则裁定 |
| `server.mjs` | 本地 HTTP 边界、单回合模型调用、输入校验 | 长期世界记忆 |
| `engine.py` | SQLite、世界、人物、地点、分支、物品与资源事实 | 调用模型 |
| `data/` | 可版本化的固定世界观、物品类别、法术目录 | 玩家存档 |
| `data/world_bible_manifest.json` | 固定百科的完整清单与顺序 | 玩家自定义条目 |
| `tools/` | 导入、发布、交付打包 | 游戏运行时状态 |
| `~/.codex-rpg-memory/campaign.sqlite3` | 当前电脑的个人存档 | 项目源码或固定世界观源文件 |

百科有两种受控数据源：物品栏内的常态类别来自 `item_types.json`；世界观、介绍和“物品 -> 魔法”内的具体页面来自 SQLite 中导入的固定百科。每一个页面分类都在 `public/app.js` 的配置中声明 `source`，不再靠“某个分类例外”的条件判断。

固定百科同时是一个只读数据库。`universe_lore_entries.record_json` 保存每条记录的稳定 `record_id`、`source_id`、`record_type`、规范名称、别名、摘要、状态、区域、标签、检索词、关系和自定义字段；正文只是给玩家阅读的叙述层。`data/world_bible_database_records.json` 提供地点、机构、规则、事件、异常和传闻等可直接查询的实体记录。百科页面的类型、状态、区域筛选和全文搜索都读取这些结构化字段，叙事 brief 也会同时使用正文与记录元数据。

## 日常开发流程

1. 只修改本项目源码目录。
2. 运行 `npm test`。测试同时覆盖 Python 引擎、导入、存档迁移和前端关键结构。
3. 固定百科有修改时执行 `npm run canon:import`，它会把 `data/world_bible_manifest.json` 中的全部资料同步到目标本地数据库。
4. 需要更新常驻版本时执行 `npm run runtime:publish`。它先在同级临时目录构建完整运行版，再替换运行目录并重启服务。
5. 用浏览器打开 `http://127.0.0.1:4179/` 做一次关键路径检查：百科三大类、魔法条目计数、新建/读取存档和一回合故事。

## 固定百科的稳定性

每条 `world_bible_*.json` 记录都具有 `source_id`。导入时优先按这个标识更新，因此可以安全修改标题、正文、排序和玩家可见分类。旧数据库中没有 `source_id` 的条目只会走一次兼容匹配，成功后即获得稳定标识。第 7 个 SQLite 迁移为此添加了唯一索引。

新增固定百科时必须同时完成三件事：为每条记录添加永不复用的 `source_id`；将文件加入 `world_bible_manifest.json`；补充或更新测试。不要直接编辑个人数据库来维护固定世界观。

## 数据安全与交付

`tools/create_delivery_package.py` 只打包源码、文档、数据、测试和项目技能说明，并写入 `SHA256SUMS.txt`。它会排除 `backups/`、`node_modules/`、缓存和全部 SQLite 文件，避免把个人故事、账户相关运行数据或旧存档一并交付。

打包命令：

```bash
python3 tools/create_delivery_package.py --output /absolute/path/Secret-Fire-Project.zip
```

运行版发布与交付包都不会修改或删除 `~/.codex-rpg-memory/campaign.sqlite3`。存档迁移、备份和删除仍必须通过游戏内的存档功能完成。
