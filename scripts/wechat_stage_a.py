#!/usr/bin/env python3
"""微信导出 · 阶段A：纯本地元数据 + 关键词统计（不联网、不改源文件、不输出聊天正文）。
用法：wechat_stage_a.py <导出目录> <输出目录>
输入：<导出目录>/{private_friends,private_unknown,groups_md}/*.md，每条消息一行：- [YYYY-MM-DD HH:MM[:SS]] 发送人: 内容
输出：contacts_stats.jsonl、contacts_overview.csv、groups_overview.csv、stage_a_summary.json
关键词表 BIZ/AI/ASK 按自己的行业改。"""
import csv, json, os, re, sys
from collections import Counter
from datetime import datetime, timedelta

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
LINE = re.compile(r"^- \[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}(?::\d{2})?)\] ([^:]{1,60}?): (.*)$")
BIZ = re.compile(r"我们公司|我司|公司|团队|员工|招聘|招人|融资|投资人|股东|合伙|创始人|CEO|老板|董事|总经理|开店|门店|工厂|订单|客户|供应商|渠道|代理|经销|报价|合同|发票|对公|甲方|乙方|招标|预算|营收|利润|业绩|销售|获客|转化|私域|直播|投放|小程序|APP|系统|软件|数字化|ERP|CRM|SaaS|项目", re.I)
AI = re.compile(r"\bAI\b|人工智能|大模型|GPT|ChatGPT|Claude|DeepSeek|豆包|Kimi|通义|智能体|Agent|自动化|提效|降本|AIGC|Midjourney|数字人|提示词|prompt|RPA|工作流|Coze|扣子|Dify|n8n|Cursor|Codex", re.I)
ASK = re.compile(r"怎么用|能不能|帮我|教我|请教|培训|课程|咨询|方案|报价|多少钱|合作|有空|聊聊|见面|约个|推荐")

def scan(path, is_group=False):
    name=None; n=0; senders=Counter(); first=last=None; by_year=Counter(); biz=ai=ask=0; s_ai=[]; s_biz=[]; tail=[]
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if name is None and raw.startswith("# 聊天记录:"): name=raw.split(":",1)[1].strip(); continue
            m=LINE.match(raw)
            if not m: continue
            d,t,sender,text=m.group(1),m.group(2),m.group(3).strip(),m.group(4).strip()
            n+=1; senders[sender]+=1; first=first or d; last=d; by_year[d[:4]]+=1
            st=text[:400]; b=bool(BIZ.search(st)); a=bool(AI.search(st))
            biz+=b; ai+=a; ask+=bool(ASK.search(st))
            if not is_group:
                item=f"[{d}] {sender}: {st[:140]}"
                if a: s_ai.append(item)
                elif b and len(st)>=12: s_biz.append(item)
                tail.append(item); tail=tail[-12:]
    return dict(name=name or os.path.basename(path), file=os.path.basename(path), total=n, first=first, last=last,
                by_year=dict(by_year), senders=senders, biz_hits=biz, ai_hits=ai, ask_hits=ask,
                snip_ai=s_ai[-8:], snip_biz=s_biz[-10:], tail=tail[-8:])

def recent_counts(path, cut12, cut24):
    c12=c24=0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if raw.startswith("- [") and len(raw)>13:
                d=raw[3:13]
                if d>=cut24:
                    c24+=1
                    if d>=cut12: c12+=1
    return c12,c24

priv=[]
for sub in ("private_friends","private_unknown"):
    d=os.path.join(SRC,sub)
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md"): r=scan(os.path.join(d,fn)); r["kind"]=sub; priv.append(r)
appear=Counter(s for r in priv for s in r["senders"])
if not appear: sys.exit("未匹配到任何消息行：需要 <导出目录>/private_friends/*.md，每行形如 '- [YYYY-MM-DD HH:MM] 发送人: 内容'（ASCII 冒号）。其他工具的导出请先转换成这个格式。")
me,me_files=appear.most_common(1)[0]   # 出现在最多文件里的发送人=本人
ref=max((r["last"] for r in priv if r["last"]), default="2000-01-01"); refd=datetime.strptime(ref,"%Y-%m-%d")
cut12=(refd-timedelta(days=365)).strftime("%Y-%m-%d"); cut24=(refd-timedelta(days=730)).strftime("%Y-%m-%d")
rows=[]
with open(os.path.join(OUT,"contacts_stats.jsonl"),"w",encoding="utf-8") as jf:
    for r in priv:
        c12,c24=recent_counts(os.path.join(SRC,r["kind"],r["file"]),cut12,cut24)
        mine=r["senders"].get(me,0); r.update(msgs_12m=c12,msgs_24m=c24,mine=mine,theirs=r["total"]-mine)
        r["senders"]=dict(r["senders"].most_common(3)); jf.write(json.dumps(r,ensure_ascii=False)+"\n"); rows.append(r)
rows.sort(key=lambda x:(x["msgs_24m"],x["total"]),reverse=True)
cols=["name","kind","total","first","last","msgs_12m","msgs_24m","mine","theirs","biz_hits","ai_hits","ask_hits","file"]
with open(os.path.join(OUT,"contacts_overview.csv"),"w",encoding="utf-8-sig",newline="") as cf:
    w=csv.writer(cf); w.writerow(cols); [w.writerow([r[k] for k in cols]) for r in rows]
groups=[]; gd=os.path.join(SRC,"groups_md")
if os.path.isdir(gd):
    for fn in sorted(os.listdir(gd)):
        if fn.endswith(".md"):
            r=scan(os.path.join(gd,fn),True); c12,c24=recent_counts(os.path.join(gd,fn),cut12,cut24)
            groups.append(dict(name=r["name"],file=fn,total=r["total"],first=r["first"],last=r["last"],msgs_12m=c12,msgs_24m=c24,
                               unique_senders=len(r["senders"]),mine=r["senders"].get(me,0),biz_hits=r["biz_hits"],ai_hits=r["ai_hits"]))
groups.sort(key=lambda x:x["msgs_12m"],reverse=True)
gcols=["name","total","first","last","msgs_12m","msgs_24m","unique_senders","mine","biz_hits","ai_hits","file"]
with open(os.path.join(OUT,"groups_overview.csv"),"w",encoding="utf-8-sig",newline="") as gf:
    w=csv.writer(gf); w.writerow(gcols); [w.writerow([g[k] for k in gcols]) for g in groups]
summary=dict(me_appears_in_files=me_files,private_chats=len(priv),ref_last_date=ref,cut12=cut12,cut24=cut24,
    active_12m_ge1=sum(r["msgs_12m"]>=1 for r in rows),active_12m_ge20=sum(r["msgs_12m"]>=20 for r in rows),
    active_24m_ge1=sum(r["msgs_24m"]>=1 for r in rows),biz_hits_ge5=sum(r["biz_hits"]>=5 for r in rows),
    ai_hits_ge1=sum(r["ai_hits"]>=1 for r in rows),groups=len(groups),groups_active_12m=sum(g["msgs_12m"]>=1 for g in groups))
json.dump(summary,open(os.path.join(OUT,"stage_a_summary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
