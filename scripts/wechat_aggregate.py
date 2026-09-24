#!/usr/bin/env python3
"""汇总分类结果 results/batch_*.json → leads_master.csv（含姓名，仅本机）、leads_summary.json、needs_anonymized.md（不含姓名，可交给机会生成 agent）。
用法：wechat_aggregate.py <输出目录>
无聊天导出时：使用者按分类字段手填 ≤30 人存为 results/batch_manual.json 也能跑（contacts_stats.jsonl 可以不存在）。"""
import csv, glob, json, os, sys
from collections import Counter, defaultdict
D=sys.argv[1]
sp=os.path.join(D,"contacts_stats.jsonl")
stats={json.loads(l)["file"]:json.loads(l) for l in open(sp,encoding="utf-8")} if os.path.exists(sp) else {}
rows=[]
for p in sorted(glob.glob(os.path.join(D,"results","batch_*.json"))):
    data=json.load(open(p,encoding="utf-8"))
    if isinstance(data,dict): data=data.get("contacts") or data.get("results") or list(data.values())[0]
    for c in data:
        s=stats.get(c.get("file"),{})
        for k in ("total","first","last","msgs_12m","msgs_24m","mine","theirs","biz_hits","ai_hits","kind"): c[k]=s.get(k)
        rows.append(c)
order={"A":0,"B":1,"C":2,"none":3}
rows.sort(key=lambda c:(order.get(c.get("lead_tier"),9),-(c.get("warmth") or 0),-(c.get("msgs_24m") or 0)))
cols=["lead_tier","name","decision_maker","role_guess","industry","business_desc","size_signal","relationship","warmth","ai_signal","stated_need","need_hypothesis","last","msgs_12m","msgs_24m","total","biz_hits","ai_hits","kind","evidence","file"]
with open(os.path.join(D,"leads_master.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(cols)
    for c in rows: w.writerow([json.dumps(c.get(k),ensure_ascii=False) if isinstance(c.get(k),(list,dict)) else c.get(k) for k in cols])
AB=[c for c in rows if c.get("lead_tier") in ("A","B")]
ind=defaultdict(Counter)
for c in AB: ind[c.get("industry","未知")][c["lead_tier"]]+=1
summary=dict(classified=len(rows),lead_tier=dict(Counter(c.get("lead_tier","none") for c in rows)),
    relationship=dict(Counter(c.get("relationship","unknown") for c in rows)),
    decision_makers_warm=sum(1 for c in AB if c.get("decision_maker") in ("yes","likely") and (c.get("warmth") or 0)>=2),
    stated_need_n=sum(1 for c in rows if c.get("stated_need")),
    candidates=sum(sum(1 for _ in open(p,encoding="utf-8")) for p in glob.glob(os.path.join(D,"batches","batch_*.jsonl"))),
    missing_batches=[os.path.basename(p)[:-6] for p in glob.glob(os.path.join(D,"batches","batch_*.jsonl")) if not os.path.exists(os.path.join(D,"results",os.path.basename(p)[:-6]+".json"))],
    industry_x_tier_AB={k:dict(v) for k,v in sorted(ind.items(),key=lambda kv:-sum(kv[1].values()))})
summary["coverage"]=round(summary["classified"]/summary["candidates"],3) if summary["candidates"] else None
json.dump(summary,open(os.path.join(D,"leads_summary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
with open(os.path.join(D,"needs_anonymized.md"),"w",encoding="utf-8") as f:
    f.write("# A/B 档线索的匿名需求清单（不含姓名，供机会生成用）\n\n")
    for t in ("A","B"):
        f.write(f"## {t} 档\n\n")
        for c in rows:
            if c.get("lead_tier")==t:
                f.write(f"- [{c.get('industry')}|{c.get('size_signal')}|warmth={c.get('warmth')}|ai={c.get('ai_signal')}|{'亲口说过' if c.get('stated_need') else '仅推断'}] {c.get('role_guess') or ''}；{c.get('business_desc') or ''}；需求假设：{c.get('need_hypothesis') or '—'}\n")
        f.write("\n")
print(json.dumps(summary,ensure_ascii=False,indent=2))
