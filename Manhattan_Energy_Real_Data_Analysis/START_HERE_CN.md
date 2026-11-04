# 先看这里

## 新增：能源评分方法

先打开 `OPEN_ME_Energy_Score_Method.html`。这一页使用数据中已有的官方
ENERGY STAR 1-100 分数，不再把所有不同类型的建筑放进同一个 Site EUI
最低值/最高值公式。没有官方分数的记录继续留空，不会自行填写。

给地图使用的新文件是
`results/district_official_energy_score_for_map.csv`。它同时包含每个
district 的中位数和数据覆盖率。这里的中位数只是初步地图汇总，并不是
官方 district rating，也不是完整 Green Score。

这是你们 GitHub 上真实的2024年曼哈顿能源数据分析，不是之前的模拟评分。

## 怎么打开

1. 解压整个 ZIP。
2. 用 Chrome 打开 OPEN_ME_Real_Data_Report.html，就能看报告和三张图。不用安装 Python 也能看。
3. results 文件夹里有单独的 PNG，可以放进 PPT。
4. 把 results/district_energy_for_map.csv 和 README_Methods.md 发给搭档，用于把能源结果接到社区分区地图。

## 这次完成了什么

- 核对 GitHub 中的2024年记录，以及之前的初步筛选数量。
- 新增父子物业、共享地块编号/建筑编号的审核标记。它们只是疑似重叠关系，不等于已证实重复。
- 参考 NYC DOB 建议，把 EUI <5 或 >1000 的记录暂时放入待审核名单。
- 生成真实能源分布、物业类型比较、社区分区比较三张图。
- 输出12个社区分区的记录数和能耗中位数，并提供仅住宅类型的比较。
- 提供从实际记录算出中位数的例子，以及筛选敏感性结果。

## 数量为什么变了

原来共有11,937条2024年记录。初步筛选后是10,537条。
这次不是认定其余记录都是错误，而是先把未解决的父子关系和共享编号记录暂放一边，剩7,828条。
再把39条需要核查的极端EUI暂放一边，得到7,789条用于这次探索分析的记录。
所有记录仍然保留在 input 和 record_audit.csv 中，没有覆盖原来的数据。

这是一个保守分析子集，不代表所有曼哈顿建筑，也不是“最终完全清洗完的数据”。

## 给搭档的地图文件

results/district_energy_for_map.csv：
- boro_cd：101到112。若地图字段BoroCD使用相同编码，就按这个匹配；仍需他确认实际字段。
- district_number：1到12，只能在先筛到曼哈顿之后使用。
- median_site_eui_kbtu_ft2_year：该区纳入记录的Site EUI中位数。
- analysis_records：该区纳入的报告物业记录数。
- multifamily_median_site_eui：只看Multifamily Housing时的中位数。
- multifamily_records：对应住宅记录数。
- analysis_share_of_extract：本区输入记录中有多少比例进入这次分析，不是全区建筑覆盖率。

地图标题应该是“2024 reported Site EUI, screened properties”，不能写“Green Score”。单位kBtu/ft²/year。
尚未提供或核实分区边界文件，因此本包没有声称已经完成地图连接。

## 向老师怎么解释

We used real 2024 Manhattan energy records and documented the screening steps. We compared reported Site EUI by property type and community district, and kept the excluded records for review. These are preliminary energy results, not final Green Scores.

## 怎么重跑

在这个文件夹打开终端，运行：

python -m pip install -r requirements.txt
python analyze_energy.py

脚本会从随包附带的 input CSV 重新生成结果和报告，不需要重新下载数据。
不要用本包替换旧的 green_score_prototype；建议以后作为独立的 energy_analysis 文件夹上传。
