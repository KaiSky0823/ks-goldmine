#!/usr/bin/env python3
"""从阶段 3 workflow 的结构化返回生成附录 A（评分表）与附录 B（红队裁决表）。
用法：score_table.py <workflow结果.json> <输出.md>
输入 JSON 需含：candidates[{cid,title,type}]、judges[{judge,scores[{cid,speed,hit_target,ceiling,unfair_advantage,leverage,safety,forcing_function,delight,comment}],portfolio[]}]、
redteam[{cid,reviews[{lens,verdict,adjusted_month3_conservative}]}]。delight 只在该候选前七项三位评委均值都 ≥5 时计入，否则记 0 并标 *。"""
import json, sys
W = {'speed': .18, 'hit_target': .18, 'ceiling': .10, 'unfair_advantage': .14, 'leverage': .10, 'safety': .10, 'forcing_function': .12, 'delight': .08}
d = json.load(open(sys.argv[1], encoding='utf-8'))
rows = []
for c in d['candidates']:
    per = [s for j in d['judges'] for s in j.get('scores', []) if s.get('cid') == c['cid']]
    if not per: continue
    avg = {k: sum(s.get(k, 0) for s in per) / len(per) for k in W}
    gate = all(avg[k] >= 5 for k in W if k != 'delight')
    if not gate: avg['delight'] = 0
    total = sum(avg[k] * W[k] for k in W)
    rows.append((total, c, avg, gate, [s.get('comment', '') for s in per]))
rows.sort(key=lambda r: -r[0])
L = ['## 附录 A　候选评分表（评委均值，1–10；delight 仅在前七项均值都 ≥5 时计入，否则记 0 并标 *）', '',
     '| 排名 | 编号 | 候选 | 类型 | 总分 | 速度 | 达标 | 天花板 | 独特 | 杠杆 | 安全 | 逼报价 | 眼前一亮 |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for i, (t, c, a, g, _) in enumerate(rows, 1):
    L.append(f"| {i} | {c['cid']} | {c['title']} | {c.get('type','')} | **{t:.2f}** | " + ' | '.join(f"{a[k]:.1f}" for k in list(W)[:7]) + f" | {a['delight']:.1f}{'' if g else '*'} |")
L += ['', '评委各自的三件套：'] + [f"- {j['judge']}：{' + '.join(j.get('portfolio', []))}" for j in d['judges']]
vm = {'survive': '通过', 'survive_with_changes': '改了才能活', 'kill': '否决'}
L += ['', '## 附录 B　红队裁决', '', '| 编号 | 视角 | 裁决 | 第 3 个月保守收入（首句） |', '|---|---|---|---|']
for r in d.get('redteam', []):
    for v in r.get('reviews', []):
        s = str(v.get('adjusted_month3_conservative', '')).split('（')[0].split('(')[0].split('；')[0][:60]
        L.append(f"| {r['cid']} | {v.get('lens','')} | {vm.get(v.get('verdict'), v.get('verdict'))} | {s} |")
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('ok', len(rows), 'candidates')
