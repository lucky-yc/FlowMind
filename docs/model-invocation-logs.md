# 模型调用日志功能

## 概述

模型调用日志功能用于记录 FlowMind 系统中所有 LLM 模型的调用详情，便于排查问题和审计追踪。

## 功能特性

- 记录完整的模型调用请求和响应
- 支持按智能体、工作流、执行任务过滤
- Token 使用量统计
- 调用延迟监控
- 错误记录和追踪
- 按模型、来源、状态的多维度统计

## 数据库表结构

`model_invocation_logs` 表包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| agent_id | Integer | 智能体ID |
| workflow_id | Integer | 工作流ID |
| execution_id | Integer | 执行ID |
| node_id | String | 工作流节点ID |
| model_provider | String | 模型提供商 (openai, anthropic, custom) |
| model_id | String | 模型ID (gpt-4, claude-3 等) |
| model_name | String | 用户定义的模型名称 |
| temperature | Float | 温度参数 |
| max_tokens | Integer | 最大token数 |
| request_params | JSON | 其他请求参数 |
| system_prompt | Text | 系统提示词 |
| input_messages | JSON | 输入消息列表 |
| output_content | Text | 模型输出内容 |
| response_metadata | JSON | 响应元数据 |
| prompt_tokens | Integer | 提示词token数 |
| completion_tokens | Integer | 生成token数 |
| total_tokens | Integer | 总token数 |
| latency_ms | Integer | 请求耗时(毫秒) |
| status | String | 状态 (success, error, timeout, pending) |
| error_message | Text | 错误信息 |
| error_code | String | 错误代码 |
| source_type | String | 调用来源 (agent, workflow, api) |
| source_name | String | 来源名称 |
| created_at | DateTime | 创建时间 |

## API 接口

### 获取日志列表

```
GET /api/v1/model-invocation-logs/
```

查询参数：
- `agent_id` - 按智能体过滤
- `workflow_id` - 按工作流过滤
- `execution_id` - 按执行任务过滤
- `model_id` - 按模型ID模糊搜索
- `source_type` - 按来源类型过滤 (agent, workflow, api)
- `status` - 按状态过滤 (success, error)
- `start_date` - 开始日期
- `end_date` - 结束日期
- `page` - 页码 (默认 1)
- `page_size` - 每页数量 (默认 20)

### 获取统计信息

```
GET /api/v1/model-invocation-logs/stats
```

返回：
- 总调用次数
- 成功/失败次数
- Token 使用统计
- 平均延迟
- 按模型、来源、状态分组统计

### 获取单条日志

```
GET /api/v1/model-invocation-logs/{log_id}
```

### 删除日志

```
DELETE /api/v1/model-invocation-logs/{log_id}
```

## 代码集成

### 在智能体调用中使用

```python
from app.services.llm import chat_completion

# 调用时传入日志参数
result = await chat_completion(
    model=model,
    messages=messages,
    db=db,
    user_id=current_user.id,
    agent_id=agent.id,
    source_type="agent",
    source_name=agent.name,
)
```

### 在工作流节点中使用

```python
result = await chat_completion(
    model=model,
    messages=messages,
    db=db,
    user_id=user_id,
    workflow_id=workflow_id,
    execution_id=execution_id,
    node_id=node_id,
    source_type="workflow",
    source_name=workflow_name,
)
```

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── model_invocation_log.py  # 数据库模型
│   ├── schemas/
│   │   └── model_invocation_log.py  # Pydantic Schema
│   ├── api/
│   │   └── model_invocation_logs.py # API 路由
│   └── services/
│       ├── invocation_log.py        # 日志服务
│       └── llm.py                   # LLM 服务（已集成日志）
```
