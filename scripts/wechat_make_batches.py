#!/usr/bin/env python3
"""把阶段A候选联系人切成 30 人一批的 jsonl，供分类 agent 逐批处理（纯本地）。用法：wechat_make_batches.py <输出目录>"""
import json, os, sys
D=sys.argv[1]
rows=[json.loads(l) for l in open(os.path.join(D,"contacts_stats.jsonl"),encoding="utf-8")]
cand=[r for r in rows if (r["msgs_24m"]>=5 or r["biz_hits"]>=5 or r["ai_hits"]>=1) and r["total"]>=10]
cand.sort(key=lambda r:r["file"])
keep=["file","name","kind","total","first","last","msgs_12m","msgs_24m","mine","theirs","biz_hits","ai_hits","ask_hits","snip_ai","snip_biz","tail"]
os.makedirs(os.path.join(D,"batches"),exist_ok=True); os.makedirs(os.path.join(D,"results"),exist_ok=True)
for i in range(0,len(cand),30):
    with open(os.path.join(D,"batches",f"batch_{i//30+1:02d}.jsonl"),"w",encoding="utf-8") as f:
        for r in cand[i:i+30]: f.write(json.dumps({k:r[k] for k in keep},ensure_ascii=False)+"\n")
print("candidates",len(cand),"batches",(len(cand)+29)//30)
