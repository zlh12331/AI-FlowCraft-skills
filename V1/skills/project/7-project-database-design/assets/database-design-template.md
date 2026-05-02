# 数据库设计文档

> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}
> **需求来源**：`specs/产品需求文档.md`、`specs/数据模型字段约定.md`、`specs/系统架构设计.md`

---

## 1. 数据库概述

### 1.1 数据库基本信息

| 配置项 | 值 |
|--------|-----|
| 数据库类型 | {{如：MySQL 8.0 / PostgreSQL 15 / MongoDB 6.0}} |
| 字符集 | {{如：utf8mb4 / UTF8}} |
| 排序规则 | {{如：utf8mb4_general_ci / en_US.UTF-8}} |
| 存储引擎 | {{如：InnoDB / PostgreSQL 原生存储}} |
| ORM | {{如：Prisma / TypeORM / Drizzle / SQLAlchemy / Django ORM / GORM / JPA-Hibernate}} |
| 连接池配置 | {{如：最大连接数 100，最小空闲连接 10}} |

### 1.2 设计原则

<!-- 列出本数据库设计的核心原则 -->

1. {{原则 1}}：{{说明}}
2. {{原则 2}}：{{说明}}

### 1.3 命名规范

<!-- 引用数据模型字段约定中的命名规范，确保一致性 -->

| 对象 | 命名规则 | 示例 |
|------|---------|------|
| 表名 | {{如：小写下划线，单数/复数形式}} | {{如：users, order_items}} |
| 字段名 | {{如：小写下划线}} | {{如：created_at, user_id}} |
| 主键名 | {{如：id（不添加实体前缀）}} | {{如：id}} |
| 外键名 | {{如：关联表名单数_id}} | {{如：user_id, todo_id}} |
| 索引名 | {{如：idx_表名_字段名}} | {{如：idx_users_email}} |
| 唯一索引名 | {{如：uk_表名_字段名}} | {{如：uk_users_email}} |
| 外键约束名 | {{如：fk_表名_关联表名_字段名}} | {{如：fk_todos_users_user_id}} |

---

## 2. ER 图

<!-- 使用 Mermaid erDiagram 表达所有核心实体及其关系 -->

```mermaid
erDiagram
    {{实体A}} ||--o{ {{实体B}} : "关系说明"
    {{实体A}} {
        {{类型}} {{主键字段}} PK
        {{类型}} {{字段2}}
        {{类型}} {{字段3}}
    }
    {{实体B}} {
        {{类型}} {{主键字段}} PK
        {{类型}} {{外键字段}} FK
        {{类型}} {{字段2}}
    }
```

### 2.1 关系说明

| 关系 | 类型 | ORM 关系标识 | 说明 |
|------|------|----------------|------|
| {{实体A}} - {{实体B}} | 一对多 | {{如：UserProjects}} | {{关系说明}} |
| {{实体C}} - {{实体D}} | 多对多 | {{如：UserRoles}} | {{关系说明，通过中间表实现}} |

> **ORM 关系标识**：在 ER 图中标注的每个关系，在后续代码生成时需要使用对应 ORM 的关系声明语法。请为每对关系指定一个唯一的标识名称，并注明使用的 ORM（如 Prisma 的 `@relation("名称")`、JPA 的 `@OneToMany`、GORM 的 `gorm:"foreignKey:UserID"`、SQLAlchemy 的 `relationship(back_populates="...")`、Django ORM 的 `related_name="..."` 等）。

---

## 3. 表结构定义

<!-- 每个表包含：用途说明、字段定义表、索引定义、建表 SQL -->

### 3.1 {{表名}}

<!-- 表的用途说明 -->

#### 3.1.1 字段定义

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | {{类型}} | PK, AUTO_INCREMENT | - | 主键 |
| {{字段名}} | {{类型}} | {{约束}} | {{默认值}} | {{说明}} |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 3.1.2 索引定义

| 索引名 | 索引类型 | 字段 | 查询场景 |
|--------|---------|------|---------|
| PRIMARY | 主键索引 | id | 主键查询 |
| idx_{{名称}} | 普通索引 | {{字段}} | {{查询场景说明}} |
| uk_{{名称}} | 唯一索引 | {{字段}} | {{唯一性约束说明}} |

#### 3.1.3 建表 SQL

<!-- 填写指引：请根据 specs/技术栈.md 中的数据库选型选择对应语法。 -->

**MySQL 语法示例**：

```sql
-- {{表名}}：{{表用途说明}}
CREATE TABLE {{表名}} (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    {{字段名}} {{类型}} {{约束}} DEFAULT {{默认值}} COMMENT '{{说明}}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_{{名称}} ({{字段}}) COMMENT '{{索引用途}}',
    UNIQUE KEY uk_{{名称}} ({{字段}}) COMMENT '{{唯一约束说明}}'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{{表注释}}';
```

**PostgreSQL 语法示例**：

```sql
-- {{表名}}：{{表用途说明}}
CREATE TABLE {{表名}} (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 业务字段
    {{字段名}} {{类型}} {{约束}} DEFAULT {{默认值}},

    -- 审计字段
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- 约束
    CONSTRAINT fk_{{表名}}_{{关联表}}_{{字段}} FOREIGN KEY ({{字段}})
        REFERENCES {{关联表}}(id)
        ON DELETE CASCADE
);

-- 表注释
COMMENT ON TABLE {{表名}} IS '{{表注释}}';

-- 字段注释
COMMENT ON COLUMN {{表名}}.id IS '主键，UUID v4，自动生成';
COMMENT ON COLUMN {{表名}}.{{字段名}} IS '{{说明}}';

-- 索引
CREATE INDEX idx_{{名称}} ON {{表名}} ({{字段}});
COMMENT ON INDEX idx_{{名称}} IS '{{索引用途}}';
```

**PostgreSQL 自动更新 `updated_at` 触发器**：

> PostgreSQL 没有 MySQL 的 `ON UPDATE CURRENT_TIMESTAMP` 语法，需要通过触发器函数实现 `updated_at` 的自动更新。以下触发器函数只需定义一次，然后为每个包含 `updated_at` 字段的表创建对应触发器即可。

```sql
-- 自动更新 updated_at 的触发器函数（全局只需定义一次）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为每个包含 updated_at 字段的表创建触发器
CREATE TRIGGER update_{{table_name}}_updated_at
    BEFORE UPDATE ON {{table_name}}
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

<!-- 重复以上结构定义每个表 -->

---

## 4. 分库分表策略

<!-- 仅当数据量预估较大、需要分库分表时填写本章节。如果不需要，删除此节。 -->

### 4.1 分片评估

| 表名 | 预估数据量 | 增长速度 | 是否需要分片 | 分片策略 |
|------|-----------|---------|------------|---------|
| {{表名}} | {{如：千万级/亿级}} | {{如：日均增长 10 万}} | 是/否 | {{如：按 user_id 哈希取模}} |

### 4.2 分片规则

<!-- 描述分库分表的具体规则 -->

- **分片键**：{{如：user_id}}
- **分片算法**：{{如：哈希取模 / 范围分片 / 一致性哈希}}
- **分片数量**：{{如：16 个分表}}
- **路由规则**：{{如：user_id % 16}}

### 4.3 跨分片查询

<!-- 描述跨分片查询的处理方案 -->

| 查询场景 | 处理方案 |
|---------|---------|
| {{场景 1}} | {{方案说明}} |
| {{场景 2}} | {{方案说明}} |

---

## 5. 数据迁移方案

<!-- 仅当涉及已有系统的数据迁移时填写本章节。如果不涉及，删除此节。 -->

### 5.1 迁移概述

| 项目 | 说明 |
|------|------|
| 迁移范围 | {{需要迁移的表和数据}} |
| 预估数据量 | {{总数据量}} |
| 停机窗口 | {{是否需要停机，停机时长}} |
| 回滚方案 | {{迁移失败时的回滚策略}} |

### 5.2 迁移步骤

1. {{步骤 1}}：{{详细说明}}
2. {{步骤 2}}：{{详细说明}}
3. {{步骤 3}}：{{详细说明}}

### 5.3 数据校验

<!-- 描述迁移后的数据校验方案 -->

| 校验项 | 校验方式 | 通过标准 |
|--------|---------|---------|
| {{校验项 1}} | {{校验方式}} | {{通过标准}} |
| {{校验项 2}} | {{校验方式}} | {{通过标准}} |

---

## 6. 慢查询预防策略

### 6.1 索引优化建议

| 表名 | 查询场景 | 建议索引 | 说明 |
|------|---------|---------|------|
| {{表名}} | {{查询场景描述}} | {{索引定义}} | {{优化原理}} |

### 6.2 查询优化规则

<!-- 定义全局查询优化规则，供开发团队遵循 -->

1. **禁止 SELECT ***：查询必须明确指定所需字段，避免读取无用数据。
2. **大表分页优化**：超过 {{如：100 页}} 的深度分页，使用 {{如：基于游标的分页}} 替代 OFFSET。
3. **避免全表扫描**：WHERE 条件必须命中索引，禁止对大表进行无索引条件的查询。
4. **JOIN 优化**：JOIN 的关联字段必须有索引，避免多表大 JOIN。
5. **子查询优化**：复杂的子查询改写为 JOIN，提升查询性能。
6. **批量操作**：批量插入/更新使用批量语句，避免循环单条操作。

### 6.3 监控与告警

| 监控项 | 阈值 | 告警方式 |
|--------|------|---------|
| 慢查询 | {{如：执行时间 > 500ms}} | {{如：钉钉告警}} |
| 连接数 | {{如：使用率 > 80%}} | {{如：邮件告警}} |
| 锁等待 | {{如：等待时间 > 5s}} | {{如：短信告警}} |

---

## 7. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
