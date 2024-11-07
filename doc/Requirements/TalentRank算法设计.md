# TalentRank 算法设计

TalentRank 算法用于衡量开发者在技术社区中的综合表现。通过个人和公司两个维度的权重系统，算法能够更全面地评估开发者的技术能力和影响力。该算法的用户评分包含 **个人影响力**、**个人贡献活跃度** 和 **参与项目的重要性** 三大主要因素。

## 1. 用户个人权重

用户个人权重衡量开发者的技术能力和社区影响力，从以下几个方面进行评估：

### 1.1 个人影响力

个人影响力指标评估开发者在社区中的知名度和受欢迎程度，主要包括：

- **Star 数**：反映项目的受欢迎程度，可作为开发者影响力的一个基本指标。
- **Fork 数**：表示项目的传播程度和社区接受度。
- **粉丝数（Followers）**：直接反映开发者的受欢迎程度和影响力。

#### 个人影响力得分公式
将 Star 数、Fork 数和粉丝数设定权重，计算总得分：

$$
\text{个人影响力得分} = (w_{\text{star}} \times \text{Star 数}) + (w_{\text{fork}} \times \text{Fork 数}) + (w_{\text{followers}} \times \text{粉丝数})
$$

- **权重建议**：由于粉丝数直接代表个人影响力，建议 $w_{\text{followers}}$权重大于 $w_{\text{fork}}$ 和 $w_{\text{star}}$。例如：
  -  $w_{\text{star}} = 0.3 $
  -  $w_{\text{fork}} = 0.2$ 
  -  $w_{\text{followers}} = 0.5$ 

### 1.2 个人贡献活跃度

个人贡献活跃度评估开发者在项目中的技术投入和活跃程度，主要包括：

- **提交次数（Commits）**：衡量开发者在项目中的代码贡献频率。
- **拉取请求（PR）**：反映贡献质量，考虑 PR 的数量和被接受率（例如，被合并的 PR 比重高的用户得分更高）。
- **问题参与度（Issues）**：包括创建和回复的 Issue 数量，评估开发者解决问题的能力。

#### 个人贡献得分公式
给不同的活动赋予权重，计算总得分：
$$
\text{个人贡献得分} = (w_{\text{commits}} \times \text{提交次数}) + (w_{\text{pr}} \times \text{PR 数} \times \text{PR 接受率}) + (w_{\text{issues}} \times \text{Issues 数})
$$


- **权重建议**：PR 质量通常比纯提交次数更重要，因此建议 `w_pr` 大于 `w_commits` 和 `w_issues`。例如：
  - $ w_{\text{commits}} = 0.2 $
  - $ w_{\text{pr}} = 0.5$
  - $w_{\text{issues}} = 0.3 $

### 1.3 参与项目的重要性

参与项目的重要性反映了开发者所参与项目的整体影响力和受欢迎程度，通过项目的 Star 和 Fork 数量来衡量。

#### 参与项目的重要性得分公式
将每个项目的 Star 数和 Fork 数分别加权后累加得到总分：

$$
\text{项目重要性得分} = \sum_{\text{repo}} \left( w_{\text{repoStar}} \times \text{repoStar} + w_{\text{repoFork}} \times \text{repoFork} \right)
$$


- **权重建议**：项目的 Star 数通常比 Fork 数更能代表受欢迎程度，因此建议$w_{\text{repoStar}}$高于 $w_{\text{repoFork}}$。例如：
  - $w_{\text{repoStar}} = 0.6$
  - $w_{\text{repoFork}} = 0.4 $

## 2. 综合 TalentRank 计算

将上述三个部分的得分加权组合成最终的 TalentRank 得分。为确保 TalentRank 分数的合理分布，建议给每部分分数设定最高值，并进行归一化计算。

### TalentRank 得分公式

$$
\text{TalentRank} = w_{\text{personal\_influence}} \times \text{个人影响力得分} + w_{\text{personal\_contribution}} \times \text{个人贡献得分} + w_{\text{project\_importance}} \times \text{项目重要性得分}
$$

- **权重建议**：如个人贡献活跃度比个人影响力和项目重要性更重要，可以设定 $w_{\text{personal\_contribution}}$ 更高，例如：
  - $w_{\text{personal\_influence}} = 0.3$
  - $w_{\text{personal\_contribution}} = 0.5 $
  - $ w_{\text{project\_importance}} = 0.2$

