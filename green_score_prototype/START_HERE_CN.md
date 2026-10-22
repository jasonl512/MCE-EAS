# 先看这里

这是你们这周新做出的 Green Score 基础评分原型。里面已经有能运行的 Python 代码和我运行产生的结果。

## 下载之后做什么

1. 解压下载的 ZIP。
2. 打开里面的 `green_score_prototype` 文件夹。
3. 先打开 `demo_results` 里的 `scores.csv`，可以用 Excel 查看。所有地区名以 DEMO 开头，都是模拟测试数据。
4. 把整个 `green_score_prototype` 文件夹放进电脑上的 MCE-EAS 仓库文件夹，不要覆盖原来的 `energy_cleaning` 文件夹。
5. 在 GitHub Desktop 查看新增文件，提交说明可以写 `Add first Green Score prototype and synthetic tests`，然后 Push origin。这个包目前还没有替你上传 GitHub。

## 这个结果表怎么看

- `pm25_score`、`tree_cover_score`、`hvi_score`、`site_eui_score` 是四项转换后的分数，越高表示模型中越好。
- `equal_score` 是四项各占 0.25 时的总分。
- `air_priority_score` 是空气项占 0.55、其余各占 0.15 的测试情景。不是最终确定的权重。
- `rank` 是对应情景的排名，1 最高；只给有总分的行排名。
- `issues` 解释为什么不计算总分，`warnings` 说明参考范围截断等需要注意的情况。

几个可以展示的例子：

| 模拟输入 | 相同权重总分 | 空气优先总分 | 说明 |
| --- | ---: | ---: | --- |
| DEMO_A | 39.31 | 59.58 | 空气比较好，其他项较低 |
| DEMO_B | 66.81 | 52.08 | 其他项比较好，空气项较低 |
| DEMO_C | 50.00 | 50.00 | 四项都在参考范围中点 |
| DEMO_D_MISSING | 留空 | 留空 | 缺少 PM2.5，程序没有编造总分 |

A 和 B 的顺序会随权重变化。这只说明程序能按不同权重计算，不代表曼哈顿的真实地区结果。

## 在你的电脑重新运行

需要 Python 3，不需要额外安装任何 Python 包。

在文件资源管理器中进入 `green_score_prototype` 文件夹，点击上方地址栏，输入 `cmd`，按回车。然后输入：

```text
py green_score.py
```

看到 `SYNTHETIC data: 4 scored; 3 blocked` 就表示示例运行完成。结果保存在 `demo_results`。

测试代码的命令：

```text
py -m unittest -v
```

看到 `Ran 11 tests` 和 `OK` 表示这些软件测试通过。如果电脑提示找不到 `py`，可以试 `python` 替换 `py`；两者都找不到时需要先安装 Python。

## 现在能向老师说什么

我们这周完成了评分计算代码、模拟输入输出和软件测试。我们检查了缺失值、无效数值、年份不一致和改变权重的情况。

真实的四项社区数据尚未对齐；现有能源文件仍然是物业记录，不能直接塞进这个社区评分表。模拟数据的参考上下限也是测试用假设，不能称为真实环境标准。

预算优化、最低成本模式、地图以及项目之间的影响关系还没有实现。下一步要继续对齐真实数据，并和搭档整理的项目成本与收益资料衔接。
