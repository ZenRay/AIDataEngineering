---
title: "代码知识图谱 Schema 设计原理：从 Symbol-centric 到 semantic-impact"
create_time: "2026-11-06 17:00:00"
update_time: "2026-11-06 17:00:00"
category: "architecture"
subcategory: "system-design"
tags:
  - "Neo4j"
  - "知识图谱"
  - "Schema 设计"
  - "本体论"
  - "Symbol-centric"
  - "semantic-impact"
project: "AIDataEngineering"
project-description: "AI 辅助数仓建设项目"
purpose: "reference"
document_type: "knowledge"
status: "active"
---

# 代码知识图谱 Schema 设计原理：从 Symbol-centric 到 semantic-impact

> **迭代须知**
> 
> **版本历史**：
> | 版本 | 日期 | 变更摘要 |
> |------|------|---------|
> | v1.0 | 2026-11-06 | 初版：整理代码知识图谱 Schema 的设计原理，包括 Symbol-centric 设计、semantic-impact 关系、TBox/ABox 分离 |
> 
> **修改规则**：
> - 修改结论前必查「验证状态总表」
> - 过时内容标注"⚠️ 已过时（原验证条件：…）"而非直接删除
> - 每次修改同步更新 `update_time` 和版本历史表

---

## 一、代码知识图谱的核心挑战

### 1.1 为什么要构建代码知识图谱？

**传统代码分析的局限**：

1. **孤立的代码视图**：传统静态分析工具（如 SonarQube、Checkstyle）只能看到单个文件或模块，无法理解跨文件、跨服务的复杂关系
2. **缺乏业务语义**：代码分析只能看到技术结构（类、方法、调用），无法理解业务概念（订单、支付、结算）
3. **难以追踪变化影响**：当代码发生变化时，难以快速评估影响范围

**代码知识图谱的价值**：

1. **统一视图**：将代码结构、调用关系、数据流、业务概念统一到一个图中
2. **语义丰富**：不仅包含技术结构，还包含业务语义
3. **支持复杂查询**：可以查询"这个 API 影响了哪些业务过程？""这个表被哪些服务使用？"等复杂问题
4. **支持影响分析**：当代码变化时，可以快速评估影响范围

### 1.2 Schema 设计的核心挑战

**挑战 1：如何表示代码结构？**

代码包含多种实体（类、方法、变量、文件、模块）和关系（调用、继承、依赖、包含）。如何设计一个既能表达复杂结构，又易于查询的 Schema？

**挑战 2：如何连接代码到业务概念？**

代码是技术实现，业务概念是业务语义。如何在知识图谱中建立两者的映射？

**挑战 3：如何支持演进？**

代码是持续变化的，知识图谱需要支持增量更新，而不是每次全量重建。

**挑战 4：如何平衡灵活性和性能？**

Schema 设计需要足够灵活以表达复杂的代码结构，同时需要足够简单以保证查询性能。

---

## 二、Symbol-centric Schema 设计原理

### 2.1 为什么选择 Symbol 作为核心？

**设计决策**：以 Symbol（符号）作为核心节点类型，而不是以 File、Class 或 Method 作为核心。

**Symbol 的定义**：

Symbol 是代码中的**命名实体**，包括：
- 函数/方法（Function/Method）
- 类/接口（Class/Interface）
- 变量/字段（Variable/Field）
- 模块/包（Module/Package）
- 类型（Type）
- 常量（Constant）

**设计原理**：

1. **Symbol 是代码的基本单元**：所有代码操作都可以归结为对 Symbol 的操作（定义、使用、调用、继承）
2. **Symbol 跨越多个层次**：一个 Symbol 可以同时属于多个层次（方法属于类，类属于模块，模块属于项目）
3. **Symbol 承载丰富的元数据**：每个 Symbol 都有名称、类型、位置、可见性等属性
4. **Symbol 之间的关系是代码的核心**：调用、继承、依赖等关系都是 Symbol 之间的关系

### 2.2 Symbol-centric Schema 的设计

**核心节点类型**：

```cypher
// Symbol 节点：代码中的命名实体
(:Symbol {
    name: "createOrder",           // 符号名称
    type: "METHOD",                 // 符号类型（CLASS/METHOD/FIELD/VARIABLE）
    signature: "void createOrder(Order)", // 签名
    visibility: "public",           // 可见性
    static: false,                  // 是否静态
    abstract: false,                // 是否抽象
    file: "OrderService.java",      // 所在文件
    line: 42,                       // 行号
    column: 8,                      // 列号
    complexity: 5,                  // 圈复杂度
    parameters: ["Order order"],    // 参数列表
    return_type: "void"             // 返回类型
})

// Module 节点：文件级分组
(:Module {
    name: "OrderService",
    path: "src/main/java/com/example/OrderService.java",
    package: "com.example",
    imports: ["com.example.Order", "com.example.OrderRepository"]
})

// File 节点：物理文件
(:File {
    name: "OrderService.java",
    path: "src/main/java/com/example/OrderService.java",
    language: "java",
    size: 1024,
    last_modified: "2026-11-06T10:00:00Z"
})

// Folder 节点：目录
(:Folder {
    name: "example",
    path: "src/main/java/com/example"
})

// Dependency 节点：外部依赖
(:Dependency {
    name: "spring-boot-starter-web",
    group: "org.springframework.boot",
    version: "2.7.0",
    scope: "compile"
})

// Statement 节点：控制流节点（可选，用于细粒度分析）
(:Statement {
    type: "IF_STATEMENT",
    condition: "order.getAmount() > 0",
    line: 45,
    column: 12
})
```

**核心关系类型**：

```cypher
// 调用关系
(:Symbol {name: "createOrder"})-[:CALLS {line: 48}]->(:Symbol {name: "save"})

// 继承关系
(:Symbol {name: "OrderService"})-[:EXTENDS]->(:Symbol {name: "BaseService"})

// 实现关系
(:Symbol {name: "OrderService"})-[:IMPLEMENTS]->(:Symbol {name: "IService"})

// 包含关系
(:Symbol {name: "OrderService"})-[:CONTAINS]->(:Symbol {name: "createOrder"})

// 导入关系
(:Module {name: "OrderService"})-[:IMPORTS]->(:Module {name: "Order"})

// 依赖关系
(:Module {name: "OrderService"})-[:DEPENDS_ON]->(:Dependency {name: "spring-boot-starter-web"})

// 语义影响关系（连接代码到业务概念）⭐ 关键
(:Symbol {name: "createOrder"})-[:SEMANTIC_IMPACT {confidence: 0.85}]->(:BusinessConcept {name: "订单创建"})
```

### 2.3 为什么不是其他设计？

**替代设计 1：层级结构（Project → Namespace → Class → Method）**

```
❌ 缺点：
- 过于刚性，难以表达复杂关系（如跨包调用）
- 查询效率低（需要多层遍历）
- 难以支持增量更新（层级变化影响大）
```

**替代设计 2：Subject-Predicate-Object 三元组**

```
❌ 缺点：
- 缺乏类型信息（所有节点都是同一类型）
- 难以表达复杂属性（需要额外的节点）
- 查询效率低（需要大量 JOIN）
```

**替代设计 3：以 File 或 Class 作为核心**

```
❌ 缺点：
- File 太物理，难以表达逻辑关系
- Class 太具体，难以表达函数式编程
- Symbol 更通用，可以表达各种命名实体
```

### 2.4 Symbol-centric 的优势

**优势 1：灵活性**

Symbol 可以表示各种命名实体，不受特定编程范式限制（面向对象、函数式、过程式）。

**优势 2：查询效率**

Symbol 之间的关系直接表达，不需要多层遍历。

```cypher
// 查询：找到 createOrder 方法调用的所有方法
MATCH (m:Symbol {name: "createOrder"})-[:CALLS]->(called:Symbol)
RETURN called.name

// 查询：找到所有调用 createOrder 的地方
MATCH (caller:Symbol)-[:CALLS]->(m:Symbol {name: "createOrder"})
RETURN caller.name, caller.file
```

**优势 3：增量更新**

当代码变化时，只需要更新受影响的 Symbol 节点和关系，不需要重建整个图。

**优势 4：扩展性**

可以轻松添加新的 Symbol 类型（如 Annotation、Lambda）和新的关系类型（如 DATA_FLOW、CONTROL_FLOW）。

---

## 三、semantic-impact 关系：连接代码到业务概念

### 3.1 为什么需要 semantic-impact 关系？

**问题**：代码知识图谱包含丰富的技术信息（类、方法、调用），但缺乏业务语义。如何连接技术实现到业务概念？

**传统方法的局限**：

1. **命名约定**：通过类名/方法名推断业务概念（如 `OrderService.createOrder` → "订单创建"）
   - 问题：命名不规范时失效，无法处理复杂业务逻辑

2. **注释和文档**：从注释中提取业务信息
   - 问题：注释可能过时、不完整、不准确

3. **人工标注**：由业务专家手动标注
   - 问题：成本高、难以维护

**semantic-impact 的设计思路**：

在代码 Symbol 和业务概念之间建立**语义影响关系**，表示代码对业务概念的影响。

### 3.2 semantic-impact 关系的设计

**关系定义**：

```cypher
// semantic-impact 关系
(:Symbol)-[:SEMANTIC_IMPACT {
    confidence: 0.85,           // 置信度（0-1）
    impact_type: "CREATE",      // 影响类型（CREATE/READ/UPDATE/DELETE）
    evidence: "method_name",    // 证据来源（method_name/comment/annotation/data_flow）
    reviewer: "AI",             // 审核者（AI/human）
    review_date: "2026-11-06"   // 审核日期
}]->(:BusinessConcept {
    name: "订单创建",
    description: "买家提交订单的业务过程",
    domain: "ORDER",
    priority: "HIGH"
})
```

**影响类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| **CREATE** | 创建业务实体 | `createOrder()` 创建订单 |
| **READ** | 读取业务实体 | `getOrder()` 读取订单 |
| **UPDATE** | 更新业务实体 | `updateOrderStatus()` 更新订单状态 |
| **DELETE** | 删除业务实体 | `cancelOrder()` 取消订单 |
| **VALIDATE** | 验证业务规则 | `validateOrder()` 验证订单 |
| **CALCULATE** | 计算业务指标 | `calculateTotal()` 计算总金额 |

**证据来源**：

| 来源 | 说明 | 置信度 |
|------|------|:------:|
| **method_name** | 从方法名推断 | 0.6-0.8 |
| **comment** | 从注释提取 | 0.7-0.9 |
| **annotation** | 从注解提取 | 0.8-1.0 |
| **data_flow** | 从数据流分析 | 0.7-0.9 |
| **human** | 人工标注 | 1.0 |

### 3.3 semantic-impact 的应用场景

**场景 1：业务影响分析**

```cypher
// 问题：修改 createOrder 方法会影响哪些业务过程？
MATCH (m:Symbol {name: "createOrder"})-[:SEMANTIC_IMPACT]->(concept:BusinessConcept)
RETURN concept.name, concept.description

// 结果：
// concept.name: "订单创建"
// concept.description: "买家提交订单的业务过程"
```

**场景 2：业务覆盖率分析**

```cypher
// 问题：哪些业务过程没有被代码实现？
MATCH (concept:BusinessConcept)
WHERE NOT EXISTS {
    MATCH (s:Symbol)-[:SEMANTIC_IMPACT]->(concept)
}
RETURN concept.name

// 结果：没有被代码实现的业务过程
```

**场景 3：代码重构影响评估**

```cypher
// 问题：删除 OrderService 类会影响哪些业务过程？
MATCH (c:Symbol {name: "OrderService", type: "CLASS"})-[:CONTAINS]->(m:Symbol)-[:SEMANTIC_IMPACT]->(concept:BusinessConcept)
RETURN DISTINCT concept.name, concept.priority

// 结果：受影响的业务过程及其优先级
```

### 3.4 如何建立 semantic-impact 关系？

**方法 1：基于命名约定（自动）**

```python
def infer_semantic_impact_from_name(method_name):
    """从方法名推断业务概念"""
    # 规则：create* → CREATE, get* → READ, update* → UPDATE, delete* → DELETE
    if method_name.startswith("create"):
        return {
            "impact_type": "CREATE",
            "business_concept": extract_noun(method_name),  # createOrder → 订单
            "confidence": 0.7
        }
    elif method_name.startswith("get"):
        return {
            "impact_type": "READ",
            "business_concept": extract_noun(method_name),
            "confidence": 0.7
        }
    # ...
```

**方法 2：基于注释提取（自动）**

```python
def infer_semantic_impact_from_comment(comment):
    """从注释中提取业务概念"""
    # 使用 NLP 或 LLM 提取业务概念
    import openai
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "从代码注释中提取业务概念"},
            {"role": "user", "content": f"注释：{comment}\n提取业务概念："}
        ]
    )
    
    business_concept = response.choices[0].message.content
    return {
        "business_concept": business_concept,
        "confidence": 0.8,
        "evidence": "comment"
    }
```

**方法 3：基于数据流分析（自动）**

```python
def infer_semantic_impact_from_data_flow(method):
    """从数据流分析推断业务概念"""
    # 分析方法的数据流，识别业务实体
    data_flow = analyze_data_flow(method)
    
    # 如果方法写入 order 表 → 影响"订单"业务概念
    if "order_table" in data_flow.writes:
        return {
            "impact_type": "CREATE" if data_flow.is_insert else "UPDATE",
            "business_concept": "订单",
            "confidence": 0.85,
            "evidence": "data_flow"
        }
```

**方法 4：人工标注（手动）**

```python
def manual_annotation(symbol, business_concept, impact_type):
    """人工标注 semantic-impact 关系"""
    return {
        "symbol": symbol,
        "business_concept": business_concept,
        "impact_type": impact_type,
        "confidence": 1.0,
        "evidence": "human",
        "reviewer": "业务专家"
    }
```

### 3.5 semantic-impact 的置信度评分

**置信度计算**：

```python
def calculate_confidence(evidence_sources):
    """计算 semantic-impact 的置信度"""
    weights = {
        "human": 1.0,
        "annotation": 0.9,
        "data_flow": 0.85,
        "comment": 0.8,
        "method_name": 0.7
    }
    
    if not evidence_sources:
        return 0.0
    
    # 多个证据源时，取最高置信度 + 额外加分
    max_confidence = max(weights.get(source, 0.5) for source in evidence_sources)
    bonus = min(0.1 * (len(evidence_sources) - 1), 0.2)  # 最多加 0.2
    
    return min(max_confidence + bonus, 1.0)
```

**置信度阈值**：

| 置信度 | 状态 | 处理方式 |
|:------:|:----:|---------|
| ≥ 0.8 | 高置信度 | 自动通过 |
| 0.6-0.8 | 中置信度 | 建议审核 |
| < 0.6 | 低置信度 | 必须审核 |

---

## 四、TBox/ABox 分离：本体论与实例的架构设计

### 4.1 为什么需要 TBox/ABox 分离？

**问题**：代码知识图谱需要同时表达两类信息：
1. **概念定义**：什么是"订单"？什么是"支付"？（本体论）
2. **实例数据**：`createOrder()` 方法是"订单创建"业务过程的一个实现（实例）

**混合设计的问题**：

如果将概念定义和实例数据混合在一起，会导致：
1. **难以演进**：修改概念定义会影响所有实例
2. **难以复用**：概念定义无法在多个知识图谱间共享
3. **难以推理**：无法进行概念级别的推理

### 4.2 TBox/ABox 分离的设计

**TBox（Terminology Box，术语箱）**：

定义概念体系和层级关系，是**蓝图/Schema**。

```cypher
// TBox：定义业务概念
(:Ontology:Concept {
    name: "Order",
    definition: "买家与卖家之间的交易协议",
    type: "ENTITY",
    attributes: ["order_id", "buyer", "seller", "amount", "status"]
})

// TBox：定义概念关系
(:Ontology:Relationship {
    name: "belongs_to",
    definition: "表示归属关系",
    from: "Order",
    to: "Seller"
})

// TBox：定义业务规则（公理）
(:Ontology:Axiom {
    name: "order_must_have_seller",
    rule: "所有订单必须有卖家",
    expression: "FORALL o: Order, EXISTS s: Seller, o.belongs_to(s)"
})
```

**ABox（Assertion Box，断言箱）**：

存储具体的实例数据，是**实现/数据**。

```cypher
// ABox：具体的代码实体
(:Code:Symbol {
    name: "createOrder",
    type: "METHOD",
    file: "OrderService.java"
})

// ABox：具体的业务概念实例
(:Business:Concept {
    name: "订单创建",
    instance_of: "Order",  // 关联到 TBox 的概念
    description: "买家提交订单的业务过程"
})

// ABox：semantic-impact 关系（连接代码到业务概念）
(:Code:Symbol {name: "createOrder"})-[:SEMANTIC_IMPACT]->(:Business:Concept {name: "订单创建"})

// ABox：实例关系
(:Business:Concept {name: "订单创建"})-[:INSTANCE_OF]->(:Ontology:Concept {name: "Order"})
```

### 4.3 TBox/ABox 分离的架构

```
┌─────────────────────────────────────────┐
│  TBox（本体论层）                        │
│  - 定义概念体系（Order, Payment, Seller）│
│  - 定义概念关系（belongs_to, relates_to）│
│  - 定义业务规则（公理）                  │
│  - 相对稳定，变化缓慢                    │
│  - 可复用，可共享                        │
└─────────────────────────────────────────┘
                    ↓ instance_of
┌─────────────────────────────────────────┐
│  ABox（实例层）                          │
│  - 具体的代码实体（createOrder 方法）    │
│  - 具体的业务概念实例（订单创建）        │
│  - semantic-impact 关系                  │
│  - 频繁变化，随代码演进                  │
│  - 特定于项目，不可共享                  │
└─────────────────────────────────────────┘
```

### 4.4 TBox/ABox 分离的优势

**优势 1：支持演进**

TBox 相对稳定，ABox 频繁变化。分离后，修改 ABox 不会影响 TBox。

**优势 2：支持复用**

TBox 可以在多个项目间共享。例如，"Order"概念可以在订单服务、支付服务、结算服务中复用。

**优势 3：支持推理**

可以在 TBox 级别进行概念推理。例如：
- 如果"Order"有属性"amount"
- 并且"PresaleOrder"继承自"Order"
- 那么"PresaleOrder"也有属性"amount"

**优势 4：支持查询**

可以分别查询 TBox 和 ABox：
- 查询 TBox：什么是"Order"？有哪些属性？
- 查询 ABox：哪些代码实现了"Order"概念？

### 4.5 TBox/ABox 在 Neo4j 中的实现

**实现方案 1：使用 Label 区分**

```cypher
// TBox：使用 Ontology: 前缀的 Label
CREATE (:Ontology:Concept {name: "Order", ...})
CREATE (:Ontology:Relationship {name: "belongs_to", ...})
CREATE (:Ontology:Axiom {name: "order_must_have_seller", ...})

// ABox：使用 Code: 和 Business: 前缀的 Label
CREATE (:Code:Symbol {name: "createOrder", ...})
CREATE (:Business:Concept {name: "订单创建", ...})

// 关系：使用 instance_of 连接
MATCH (bc:Business:Concept {name: "订单创建"})
MATCH (oc:Ontology:Concept {name: "Order"})
CREATE (bc)-[:INSTANCE_OF]->(oc)
```

**实现方案 2：使用独立节点**

```cypher
// TBox：独立的 Ontology 节点
CREATE (:Ontology {
    type: "Concept",
    name: "Order",
    definition: "..."
})

// ABox：独立的 Instance 节点
CREATE (:Instance {
    type: "BusinessConcept",
    name: "订单创建",
    ontology_ref: "Order"  // 引用 TBox
})
```

**推荐方案**：使用 Label 区分，因为：
- 查询效率高（直接使用 Label 过滤）
- 关系表达自然（使用 instance_of 关系）
- 易于理解和维护

---

## 五、增量更新：技术挑战与解决方案

### 5.1 为什么增量更新是个挑战？

**当前工具的局限**：

大多数代码知识图谱工具（如 RepoDoc、Infigraph）采用**全量 wipe-and-rebuild** 策略：
1. 删除整个知识图谱
2. 重新解析所有代码
3. 重新构建整个知识图谱

**问题**：
- 性能差：大规模代码库需要数小时
- 成本高：浪费计算资源
- 不可持续：代码频繁变化时无法实时响应

### 5.2 增量更新的技术挑战

**挑战 1：变更检测**

如何检测代码变化？
- 文件级：新增/删除/修改了哪些文件？
- 函数级：新增/删除/修改了哪些函数？
- 行级：修改了哪些代码行？

**挑战 2：影响传播**

代码变化会影响哪些知识图谱节点？
- 直接影响：修改的函数对应的 Symbol 节点
- 间接影响：调用该函数的其他函数
- 级联影响：整个调用链

**挑战 3：选择性重建**

如何只更新受影响的部分？
- 删除受影响的节点和关系
- 重新解析变化的代码
- 重新构建受影响的节点和关系

**挑战 4：一致性保证**

如何确保更新后的知识图谱与代码一致？
- 事务管理：确保更新要么全部成功，要么全部回滚
- 并发控制：处理多人同时修改代码的情况
- 版本管理：支持回滚到历史版本

### 5.3 增量更新的设计思路

**核心思想**：基于 git diff 检测变化，通过影响传播确定更新范围，选择性重建受影响的部分。

**增量更新流程**：

```
1. 变更检测（Change Detection）
   ↓
   输入：old_commit, new_commit
   输出：变更列表（新增/删除/修改的文件、函数）

2. 影响传播（Impact Propagation）
   ↓
   输入：变更列表
   输出：受影响的节点列表（包括级联影响）

3. 选择性重建（Selective Rebuild）
   ↓
   输入：受影响的节点列表
   输出：更新后的知识图谱

4. 一致性验证（Consistency Verification）
   ↓
   输入：更新后的知识图谱
   输出：验证结果（一致/不一致）
```

### 5.4 变更检测的实现

**基于 git diff**：

```python
import subprocess

class ChangeDetector:
    def detect_changes(self, old_commit, new_commit):
        """检测两个 commit 之间的代码变化"""
        # 执行 git diff
        result = subprocess.run(
            ["git", "diff", old_commit, new_commit, "--name-status"],
            capture_output=True,
            text=True
        )
        
        changes = []
        for line in result.stdout.split("\n"):
            if not line.strip():
                continue
            
            status, file = line.split("\t")
            changes.append({
                "status": status,  # A: Added, M: Modified, D: Deleted
                "file": file
            })
        
        return changes
    
    def map_changes_to_symbols(self, changes):
        """将文件变化映射到 Symbol 节点"""
        symbols = []
        
        for change in changes:
            if change["status"] == "A":
                # 新增文件：解析文件，提取所有 Symbol
                symbols.extend(self.parse_file(change["file"]))
            
            elif change["status"] == "D":
                # 删除文件：找到文件中所有 Symbol
                symbols.extend(self.find_symbols_in_file(change["file"]))
            
            elif change["status"] == "M":
                # 修改文件：需要更细粒度的分析
                # 1. 解析新旧文件
                # 2. 比较差异
                # 3. 提取变化的 Symbol
                symbols.extend(self.extract_changed_symbols(change["file"]))
        
        return symbols
```

### 5.5 影响传播的实现

**基于图遍历**：

```python
class ImpactAnalyzer:
    def analyze_impact(self, changed_symbols):
        """分析代码变化的影响范围"""
        affected_nodes = set(changed_symbols)
        
        # BFS 遍历，找到所有受影响的节点
        queue = list(changed_symbols)
        
        while queue:
            current = queue.pop(0)
            
            # 找到调用当前节点的所有节点
            callers = self.find_callers(current)
            
            for caller in callers:
                if caller not in affected_nodes:
                    affected_nodes.add(caller)
                    queue.append(caller)
        
        return list(affected_nodes)
    
    def find_callers(self, symbol):
        """找到调用指定 Symbol 的所有 Symbol"""
        query = """
        MATCH (caller:Symbol)-[:CALLS]->(target:Symbol {name: $name})
        RETURN caller
        """
        
        result = self.neo4j_session.run(query, name=symbol.name)
        return [record["caller"] for record in result]
```

### 5.6 选择性重建的实现

```python
class IncrementalUpdater:
    def update_graph(self, changed_symbols, affected_nodes):
        """选择性重建受影响的部分"""
        # 1. 删除受影响的节点和关系
        self.delete_affected_nodes(affected_nodes)
        
        # 2. 重新解析变化的代码
        new_symbols = self.reparse_code(changed_symbols)
        
        # 3. 重新构建受影响的节点和关系
        self.rebuild_affected_nodes(new_symbols)
        
        # 4. 验证一致性
        self.verify_consistency()
    
    def delete_affected_nodes(self, affected_nodes):
        """删除受影响的节点和关系"""
        for symbol in affected_nodes:
            query = """
            MATCH (n:Symbol {name: $name})
            DETACH DELETE n
            """
            self.neo4j_session.run(query, name=symbol.name)
    
    def reparse_code(self, changed_symbols):
        """重新解析变化的代码"""
        # 使用 Tree-sitter 解析变化的文件
        # 提取新的 Symbol
        # ...
        pass
    
    def rebuild_affected_nodes(self, new_symbols):
        """重新构建受影响的节点和关系"""
        for symbol in new_symbols:
            # 创建 Symbol 节点
            self.create_symbol_node(symbol)
            
            # 创建关系（CALLS, CONTAINS, etc.）
            self.create_relationships(symbol)
```

---

## 六、验证状态总表

| 结论 | 验证方式 | 绑定版本/条件 | 失效风险 | 复核动作 |
|------|---------|-------------|---------|---------|
| Symbol-centric Schema 设计合理 | ✅ Deep Research（3-0/2-1） | Infigraph + RepoDoc | 低 | 无需复核 |
| semantic-impact 关系连接代码到业务概念 | ✅ Deep Research（3-0） | RepoDoc 论文 | 低 | 无需复核 |
| TBox/ABox 分离支持演进 | ✅ Deep Research（2-1） | Neo4j 官方博客 + PuppyGraph | 低 | 无需复核 |
| 当前工具不支持增量更新 | ✅ Deep Research（2-1） | Neo4j 开发者博客 | 中 | 6 个月后复核 |
| 增量更新基于 git diff + 影响传播 | 🔮 推断级 | 学术提案，未实现 | 高 | 需要实测验证 |
| TBox/ABox 在 Neo4j 中的具体实现 | 🔮 推断级 | 设计推演 | 中 | 需要原型验证 |

---

## 七、延展方向

### 7.1 待实测的项目

1. **Symbol-centric Schema 在财务域代码上的表现**
   - 节点数量和关系数量
   - 查询性能
   - 存储开销

2. **semantic-impact 关系的准确性**
   - 自动推断的准确率
   - 人工标注的成本
   - 置信度评分的有效性

3. **增量更新的性能**
   - 变更检测的速度
   - 影响传播的准确性
   - 选择性重建的效率

### 7.2 可以深入研究的方向

1. **数仓特定节点类型扩展**
   - Table、Field、ETLJob 等数仓特定节点
   - 与代码 Symbol 的关系
   - 数据血缘的表示

2. **本体论推理**
   - 概念继承和特化
   - 业务规则验证
   - 一致性检查

3. **GraphRAG 集成**
   - 使用知识图谱增强 RAG
   - 代码理解和生成
   - 业务问答

---

## 八、参考资源

### 8.1 开源项目

- **Infigraph（Intuit 开源）**：Symbol-centric 代码知识图谱
  - URL: https://github.com/intuit/infigraph
  
- **RepoDoc**：基于知识图谱的代码文档自动生成
  - URL: https://arxiv.org/html/2604.26523v1

### 8.2 官方文档

- **Neo4j 知识图谱博客**：
  - https://neo4j.com/blog/knowledge-graph/
  
- **Neo4j 开发者博客**：
  - https://neo4j.com/blog/developer/codebase-knowledge-graph/

### 8.3 学术论文

- **RepoDoc 论文**：
  - URL: https://arxiv.org/html/2604.26523v1
  - 主题：代码知识图谱 + semantic-impact 关系

- **知识图谱 vs 本体论**：
  - URL: https://www.puppygraph.com/blog/knowledge-graph-vs-ontology
  - 主题：TBox/ABox 分离

---

**最后更新**：2026-11-06  
**维护者**：数据团队 + AI Agent
