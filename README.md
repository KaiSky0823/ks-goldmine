# ks-goldmine · 本机金矿挖掘

对**自己电脑**里的全部内容做只读、地毯式盘点，找出你真正擅长的点、真正感兴趣的点，把二者交叉，再用市场证据和三路对抗红队压成有实质商业回报的个性化赚钱路径 Top N，附可直接动手的行动方案与交付物。

由一次真实的完整跑（5 个 workflow、130+ agent）蒸馏而成；方法、模板、脚本、教训全在仓库里。**通用版**：编排词是抽象的，SKILL.md 开头的「宿主适配」表告诉你在 Claude Code / Codex / 其他助手里各对应什么。

## 安装

```bash
# Claude Code
git clone https://github.com/KaiSky0823/ks-goldmine.git ~/.claude/skills/ks-goldmine
# Codex
git clone https://github.com/KaiSky0823/ks-goldmine.git ~/.agents/skills/ks-goldmine
```

`scripts/` 需要 Python 3.9+ 与 bash（macOS / Linux；Windows 在 WSL 里跑）。可选配套：`ks-100`、`ks-agent-team-review`、`ks-deep-claim-audit`、`ks-anything-to-pdf`。

## 用法

告诉助手你的目标与约束，例如：

> 用 ks-goldmine 从我电脑里找 3 个月内合法月入 ≥5000 美元的路径。本金 10 万、每周 8 小时、人在上海、有公司主体、不做 X。

它会先问清约束并告知量级（标准档很贵，有轻量档），然后按六个阶段跑：只读盘点 → 机主画像（擅长/兴趣/交叉）→ 授权后本地分析人脉 → 外部赛道证据 → 多视角融合 + 评委 + 红队 + 反方 → Top N 报告与三审 → Top 1 的交付包。

## 你需要知道的

- **只读**：不改你机器上任何文件，不碰生产系统，不对外发任何东西；产物全部写在一个新建的项目目录里。
- **凭据与隐私**：不打开密钥/证书/cookie 类文件；第三方姓名只留在本机线索文件，报告里一律角色化。
- **聊天导出分析是可选的，须你明确授权**：统计在本地，但分类时每人姓名与最多 26 条短片段会发给模型。不授权就手填一份「可能付钱的人」清单，后续照跑。
- **结论只用保守口径**，会给概率和算式；用过程指标（发出几份报价）代替金额指标。

## 目录

`SKILL.md` 方法总纲 ｜ `templates/` 六个阶段的 agent prompt ｜ `scripts/` 本机扫描、聊天导出统计、评分表生成 ｜ `references/` 实战教训与产物布局
