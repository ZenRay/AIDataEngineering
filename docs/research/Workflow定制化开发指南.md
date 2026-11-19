# Workflow 定制化开发指南

> **文档定位**：本文档介绍如何定制化开发 Workflow，以满足特定场景的需求。适用于需要复用和优化 workflow 的场景。

---

## 一、Workflow 基础概念

### 1.1 什么是 Workflow？

Workflow 是一种**多 Agent 编排工具**，可以：
- 协调多个 Agent 并行或串行工作
- 管理复杂的数据流和决策点
- 支持阶段化执行和错误处理
- 提供可复用的工作流模板

### 1.2 Workflow 的两种使用方式

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| **预定义 Workflow** | 使用内置的 workflow（如 deep-research） | 通用场景、快速验证 |
| **自定义 Workflow** | 编写自己的 workflow 脚本 | 特定场景、需要定制 |

### 1.3 预定义 Workflow 示例

```javascript
// 使用预定义的 deep-research workflow
Workflow({
  name: "deep-research",
  args: "研究问题：如何从 Java 代码中提取状态机？"
})
```

**特点**：
- ✅ 开箱即用
- ✅ 经过验证
- ❌ 灵活性有限
- ❌ 难以针对特定场景优化

---

## 二、自定义 Workflow 的优势

### 2.1 为什么需要定制化？

**预定义 workflow 的局限**：
- 固定的流程，难以调整
- 通用的验证策略，可能不适用于特定领域
- 输出格式固定，可能不符合需求
- 难以针对特定场景优化

**自定义 workflow 的优势**：
- ✅ **完全灵活**：可以设计任意流程
- ✅ **场景优化**：针对特定领域优化
- ✅ **可控性强**：完全掌控每个阶段
- ✅ **可复用**：保存为文件，多次使用
- ✅ **可迭代**：持续优化和改进

### 2.2 定制化场景示例

| 场景 | 定制化需求 | 预定义 workflow 能否满足 |
|------|-----------|------------------------|
| **代码分析 deep research** | 针对代码分析优化搜索角度和验证策略 | ❌ 部分满足 |
| **多阶段代码解析** | 服务依赖 → 结构化提取 → 业务规则 → 图谱构建 | ❌ 不满足 |
| **质量检查 workflow** | 完整性 → 一致性 → 准确率 → 报告生成 | ❌ 不满足 |
| **定制化报告生成** | 特定的输出格式和结构 | ❌ 部分满足 |

---

## 三、自定义 Workflow 的核心概念

### 3.1 Workflow 脚本结构

```javascript
// 1. 元数据定义
export const meta = {
  name: 'my-workflow',
  description: '工作流描述',
  phases: [
    { title: '阶段 1', detail: '详细说明' },
    { title: '阶段 2', detail: '详细说明' }
  ]
}

// 2. 主函数
async function main() {
  // 工作流逻辑
  return result
}
```

### 3.2 核心 API

#### agent() - 创建 Agent

```javascript
// 基本用法
const result = await agent("任务描述", {
  label: "agent-label",
  phase: "阶段名称"
})

// 高级用法
const result = await agent("任务描述", {
  label: "agent-label",
  phase: "阶段名称",
  model: "qwen3.7-plus[1m]",  // 模型选择
  tools: ['WebSearch', 'WebFetch'],  // 工具限制
  schema: { /* 输出 schema */ }  // 输出格式
})
```

#### parallel() - 并行执行

```javascript
// 并行执行多个 agent
const results = await parallel(
  tasks.map(task => 
    agent(`处理：${task}`, { label: `task-${task.id}` })
  )
)

// 带限制条件的并行
const results = await parallel(
  items.map(item => 
    () => agent(`处理：${item}`, { label: `item-${item.id}` })
  ),
  { concurrency: 5 }  // 最多 5 个并发
)
```

#### pipeline() - 串行执行

```javascript
// 串行执行多个阶段
const result = await pipeline(
  stages,
  async (stage) => {
    return await agent(`执行阶段：${stage.name}`, {
      label: `stage-${stage.name}`
    })
  }
)
```

#### phase() - 阶段定义

```javascript
// 定义带详细信息的阶段
await phase("数据收集", "收集所有相关数据", async () => {
  // 阶段逻辑
  return data
})
```

### 3.3 数据流管理

```javascript
async function main() {
  // 阶段 1：收集数据
  const data = await agent("收集数据", { label: "collect" })
  
  // 阶段 2：处理数据（并行）
  const processed = await parallel(
    data.items.map(item =>
      agent(`处理：${item}`, { label: `process-${item.id}` })
    )
  )
  
  // 阶段 3：综合结果
  const result = await agent(
    `综合结果：${JSON.stringify(processed)}`,
    { label: "synthesize" }
  )
  
  return result
}
```

---

## 四、实战：定制化 Deep Research

### 4.1 需求分析

**场景**：针对代码分析的 deep research

**定制化需求**：
- 搜索角度针对代码分析优化
- 验证策略针对技术结论优化
- 输出格式针对学习笔记优化

### 4.2 Workflow 设计

```javascript
export const meta = {
  name: 'code-analysis-research',
  description: '针对代码分析的定制化 deep research',
  phases: [
    { 
      title: 'Scope', 
      detail: '分解研究问题为 5 个代码分析相关的角度' 
    },
    { 
      title: 'Search', 
      detail: '并行搜索，聚焦代码分析工具和最佳实践' 
    },
    { 
      title: 'Verify', 
      detail: '3 票验证，针对技术结论优化验证策略' 
    },
    { 
      title: 'Synthesize', 
      detail: '综合结果，生成学习笔记格式的文档' 
    }
  ]
}
```

### 4.3 完整实现

```javascript
export const meta = {
  name: 'code-analysis-research',
  description: '针对代码分析的定制化 deep research',
  phases: [
    { title: 'Scope', detail: '分解研究问题' },
    { title: 'Search', detail: '并行搜索' },
    { title: 'Verify', detail: '技术验证' },
    { title: 'Synthesize', detail: '综合报告' }
  ]
}

async function main() {
  // 阶段 1：Scope（针对代码分析优化）
  const scope = await agent(`
    分解研究问题为 5 个代码分析相关的角度：
    1. 学术/技术深度：代码分析的理论基础
    2. 工具实现：具体的代码分析工具和框架
    3. 工程实践：业界最佳实践和案例
    4. 局限性与挑战：当前技术的局限性
    5. 未来方向：新兴技术和研究方向
    
    输出 JSON 格式：
    {
      "angles": [
        { "label": "...", "query": "...", "rationale": "..." }
      ]
    }
  `, {
    label: 'scope',
    phase: 'Scope',
    schema: {
      type: 'object',
      properties: {
        angles: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              label: { type: 'string' },
              query: { type: 'string' },
              rationale: { type: 'string' }
            }
          }
        }
      }
    }
  })
  
  // 阶段 2：Search（并行搜索）
  const searchResults = await parallel(
    scope.angles.map(angle =>
      agent(`
        搜索角度：${angle.label}
        查询：${angle.query}
        
        使用 WebSearch 搜索相关信息，返回：
        {
          "results": [
            { "url": "...", "title": "...", "snippet": "...", "relevance": "high|medium|low" }
          ]
        }
      `, {
        label: `search:${angle.label}`,
        phase: 'Search',
        tools: ['WebSearch'],
        schema: {
          type: 'object',
          properties: {
            results: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  url: { type: 'string' },
                  title: { type: 'string' },
                  snippet: { type: 'string' },
                  relevance: { enum: ['high', 'medium', 'low'] }
                }
              }
            }
          }
        }
      })
    )
  )
  
  // 阶段 3：Verify（技术结论验证）
  const allClaims = searchResults.flatMap(r => r.claims || [])
  
  const verified = await parallel(
    allClaims.slice(0, 25).map(claim =>
      agent(`
        验证技术结论：
        ${claim}
        
        进行 3 票验证：
        - 2-1 或 3-0：确认
        - 1-2 或 0-3：反驳
        
        输出 JSON：
        {
          "claim": "...",
          "vote": "3-0|2-1|1-2|0-3",
          "confidence": "high|medium|low",
          "evidence": "...",
          "sources": ["..."]
        }
      `, {
        label: `verify:${claim.id}`,
        phase: 'Verify',
        tools: ['WebSearch', 'WebFetch'],
        schema: {
          type: 'object',
          properties: {
            claim: { type: 'string' },
            vote: { enum: ['3-0', '2-1', '1-2', '0-3'] },
            confidence: { enum: ['high', 'medium', 'low'] },
            evidence: { type: 'string' },
            sources: { type: 'array', items: { type: 'string' } }
          }
        }
      })
    )
  )
  
  // 阶段 4：Synthesize（生成学习笔记）
  const report = await agent(`
    综合所有验证结果，生成学习笔记格式的文档：
    
    验证结果：
    ${JSON.stringify(verified, null, 2)}
    
    输出格式：
    # 标题
    
    ## 核心发现
    
    ### 1. 结论 1
    **结论**：...
    **置信度**：高/中/低（X-Y 投票）
    **证据**：...
    **来源**：...
    
    ## 验证状态总表
    
    | 结论 | 验证方式 | 绑定版本 | 失效风险 | 复核动作 |
    |------|---------|---------|---------|---------|
    | ... | ... | ... | ... | ... |
    
    ## 延展方向
    
    ## 参考资源
  `, {
    label: 'synthesize',
    phase: 'Synthesize'
  })
  
  return {
    scope: scope,
    search: searchResults,
    verified: verified,
    report: report
  }
}
```

### 4.4 使用方式

```javascript
// 方式 1：直接传入脚本内容
const scriptContent = `...`  // 上面的完整代码
Workflow({
  script: scriptContent,
  name: 'code-analysis-research',
  args: '研究问题：如何从 Java 代码中提取状态机？'
})

// 方式 2：保存为文件，通过 scriptPath 调用
// 先保存为 custom-deep-research.js
Workflow({
  scriptPath: './custom-deep-research.js',
  args: '研究问题：如何从 Java 代码中提取状态机？'
})
```

---

## 五、进阶：多阶段代码解析 Workflow

### 5.1 需求

**场景**：多阶段代码解析

**阶段**：
1. 服务依赖识别
2. 结构化提取
3. 业务规则提取
4. 知识图谱构建
5. 质量检查

### 5.2 Workflow 设计

```javascript
export const meta = {
  name: 'code-analysis-pipeline',
  description: '多阶段代码解析 workflow',
  phases: [
    { title: '服务依赖识别', detail: '识别微服务间的调用关系' },
    { title: '结构化提取', detail: '提取代码结构（类、方法、字段）' },
    { title: '业务规则提取', detail: '提取业务规则和状态机' },
    { title: '知识图谱构建', detail: '构建 Neo4j 知识图谱' },
    { title: '质量检查', detail: '检查完整性和一致性' }
  ]
}

async function main() {
  const codebase = args.codebase_path
  
  // 阶段 1：服务依赖识别
  const dependencies = await agent(`
    分析代码库：${codebase}
    识别微服务间的调用关系（RPC、HTTP、MQ）
    输出服务依赖图
  `, {
    label: 'dependency-identification',
    phase: '服务依赖识别'
  })
  
  // 阶段 2：结构化提取（并行处理多个服务）
  const structures = await parallel(
    dependencies.services.map(service =>
      agent(`
        提取服务 ${service.name} 的代码结构：
        - 类、接口、枚举
        - 方法、字段
        - 注解、配置
      `, {
        label: `structure-${service.name}`,
        phase: '结构化提取'
      })
    )
  )
  
  // 阶段 3：业务规则提取（并行处理）
  const businessRules = await parallel(
    structures.map(structure =>
      agent(`
        从以下代码结构中提取业务规则：
        ${JSON.stringify(structure)}
        
        提取：
        - 状态机和状态转换
        - 验证规则和约束
        - 业务逻辑规则
      `, {
        label: `rules-${structure.service}`,
        phase: '业务规则提取'
      })
    )
  )
  
  // 阶段 4：知识图谱构建
  const knowledgeGraph = await agent(`
    构建 Neo4j 知识图谱：
    
    服务依赖：${JSON.stringify(dependencies)}
    代码结构：${JSON.stringify(structures)}
    业务规则：${JSON.stringify(businessRules)}
    
    使用 Symbol-centric Schema：
    - Symbol 节点（类、方法、字段）
    - 关系（CALLS、CONTAINS、DEPENDS_ON）
    - semantic-impact 关系（连接代码到业务概念）
    
    生成 Cypher 语句
  `, {
    label: 'graph-construction',
    phase: '知识图谱构建'
  })
  
  // 阶段 5：质量检查
  const qualityReport = await agent(`
    检查知识图谱的质量：
    ${JSON.stringify(knowledgeGraph)}
    
    检查项：
    1. 完整性：所有服务和类是否都已提取？
    2. 一致性：关系是否正确？
    3. 准确性：业务规则是否准确？
    4. 覆盖率：关键业务过程是否覆盖？
    
    生成质量报告
  `, {
    label: 'quality-check',
    phase: '质量检查'
  })
  
  return {
    dependencies,
    structures,
    businessRules,
    knowledgeGraph,
    qualityReport
  }
}
```

---

## 六、最佳实践

### 6.1 设计原则

1. **单一职责**：每个 Agent 只做一件事
2. **清晰的数据流**：明确每个阶段的输入输出
3. **错误处理**：考虑失败场景和回退策略
4. **可测试性**：每个阶段可以独立测试
5. **可复用性**：设计通用的组件和模式

### 6.2 常见模式

#### 模式 1：扇出-汇入（Fan-out/Fan-in）

```javascript
// 扇出：并行处理多个任务
const results = await parallel(
  items.map(item => agent(`处理：${item}`, { label: `process-${item.id}` }))
)

// 汇入：综合所有结果
const summary = await agent(`综合结果：${JSON.stringify(results)}`, {
  label: 'synthesize'
})
```

#### 模式 2：管道（Pipeline）

```javascript
// 串行执行多个阶段
const result = await pipeline(
  stages,
  async (stage, context) => {
    const output = await agent(`执行阶段：${stage.name}`, {
      label: `stage-${stage.name}`
    })
    return { ...context, [stage.name]: output }
  }
)
```

#### 模式 3：条件分支

```javascript
const result = await agent("分析数据", { label: "analyze" })

if (result.needsMoreProcessing) {
  const processed = await agent("进一步处理", { label: "process" })
  return processed
} else {
  return result
}
```

### 6.3 性能优化

1. **并行化**：尽可能并行执行独立任务
2. **缓存**：缓存中间结果，避免重复计算
3. **批处理**：批量处理相似任务
4. **限制并发**：避免过多的并发导致资源耗尽

```javascript
// 限制并发数
const results = await parallel(
  tasks.map(task => () => agent(`处理：${task}`, { label: `task-${task.id}` })),
  { concurrency: 5 }  // 最多 5 个并发
)
```

### 6.4 错误处理

```javascript
async function main() {
  try {
    const result = await agent("任务", { label: "task" })
    return result
  } catch (error) {
    // 错误处理
    console.error("任务失败:", error)
    
    // 尝试回退策略
    const fallback = await agent("回退任务", { label: "fallback" })
    return fallback
  }
}
```

---

## 七、保存和复用

### 7.1 保存 Workflow 脚本

```bash
# 保存为文件
cat > custom-workflow.js << 'EOF'
export const meta = { ... }
async function main() { ... }
EOF
```

### 7.2 复用 Workflow

```javascript
// 通过 scriptPath 调用
Workflow({
  scriptPath: './custom-workflow.js',
  args: { ... }
})
```

### 7.3 迭代优化

```javascript
// 1. 首次运行
Workflow({ script: scriptContent, name: 'v1' })

// 2. 根据结果优化脚本
// 编辑 custom-workflow.js

// 3. 重新运行
Workflow({ scriptPath: './custom-workflow.js' })
```

---

## 八、学习资源

### 8.1 官方文档

- **Workflow Authoring Skill**：加载 `workflow-authoring` skill 学习完整指南
- **API 参考**：`agent()`, `parallel()`, `pipeline()`, `phase()`
- **示例**：查看 `.claude/workflows/` 目录下的示例

### 8.2 实践建议

1. **从简单开始**：先创建简单的 workflow，逐步复杂化
2. **参考现有实现**：学习 `deep-research` 等预定义 workflow
3. **小步迭代**：每次只改进一个方面
4. **充分测试**：在小数据集上测试 workflow
5. **记录经验**：记录成功和失败的经验

### 8.3 常见问题

**Q: 如何调试 workflow？**
A: 使用 `verbose: true` 参数，查看详细日志

**Q: 如何处理大量数据？**
A: 使用批处理和分页，避免一次性处理过多数据

**Q: 如何保证 workflow 的可靠性？**
A: 添加错误处理、重试机制和回退策略

**Q: 如何优化 workflow 的性能？**
A: 并行化、缓存、限制并发、批处理

---

## 九、总结

### 9.1 核心要点

- ✅ Workflow 支持高度定制化
- ✅ 可以编写自己的 workflow 脚本
- ✅ 可以保存和复用 workflow
- ✅ 提供了强大的 Agent 编排能力

### 9.2 适用场景

- **定制化 Deep Research**：针对特定领域优化
- **多阶段处理**：代码解析、数据处理等
- **复杂工作流**：需要多 Agent 协作的场景
- **可复用流程**：需要多次执行的流程

### 9.3 下一步

1. **学习 workflow-authoring skill**：深入了解 API 和最佳实践
2. **分析现有 workflow**：学习 `deep-research` 等实现
3. **设计自己的 workflow**：从简单场景开始
4. **实践和优化**：不断迭代改进

---

**文档维护**：本文档介绍 Workflow 定制化开发方法，可根据实践经验持续更新

**最后更新**：2026-11-06  
**维护者**：数据团队 + AI Agent
