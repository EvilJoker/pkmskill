#!/bin/bash
#
# PKM Agent 守护脚本
# 功能：轮询契约文件，调用 OpenClaw 执行任务，监控心跳，断线自动重跑
#

set -e

# ========== 配置 ==========
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
CONTRACTS_DIR="${PKM_HOME}/contracts"
HEARTBEAT_DIR="${PKM_HOME}/heartbeat"
LOG_DIR="${PKM_HOME}/logs"
PID_FILE="${PKM_HOME}/agent/agent.pid"

# 轮询间隔（秒）
POLL_INTERVAL="${POLL_INTERVAL:-30}"
# 心跳超时（秒）
HEARTBEAT_TIMEOUT="${HEARTBEAT_TIMEOUT:-300}"
# 最大重试次数
MAX_RETRIES="${MAX_RETRIES:-3}"
# OpenClaw 命令
OPENCLAW_CMD="openclaw"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_DIR}/agent.log"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "${LOG_DIR}/agent.log"
}

# ========== 信号处理 ==========
cleanup() {
    log "收到退出信号，正在优雅退出..."
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGHUP

# ========== 辅助函数 ==========

# 获取任务状态
get_task_status() {
    local contract_file="$1"
    if [ ! -f "$contract_file" ]; then
        echo "missing"
        return
    fi
    grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$contract_file" | sed 's/.*"\([^"]*\)"$/\1/' | head -1
}

# 更新任务状态
update_task_status() {
    local contract_file="$1"
    local new_status="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    if [ -f "$contract_file" ]; then
        # 使用 sed 更新状态（简单替换）
        if grep -q '"status"' "$contract_file"; then
            sed -i "s/\"status\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"status\": \"$new_status\"/" "$contract_file"
        fi
        # 更新时间戳
        if grep -q '"lastRunTime"' "$contract_file"; then
            sed -i "s/\"lastRunTime\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"lastRunTime\": \"$timestamp\"/" "$contract_file"
        fi
    fi
}

# 记录执行结果
record_result() {
    local contract_file="$1"
    local exit_code="$2"
    local output="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    if [ -f "$contract_file" ]; then
        # 构建结果 JSON
        local result_json="\"result\": {\"exitCode\": $exit_code, \"completedAt\": \"$timestamp\"}"
        
        # 追加或更新结果
        if grep -q '"result"' "$contract_file"; then
            # 简单处理：追加到文件末尾（实际生产环境应该用 jq）
            echo "," >> "$contract_file"
            echo "  $result_json" >> "$contract_file"
            echo "}" >> "$contract_file"
        fi
    fi
}

# 检查心跳是否存活
check_heartbeat() {
    local heartbeat_file="$1"
    if [ ! -f "$heartbeat_file" ]; then
        echo "missing"
        return
    fi
    
    local last_time=$(stat -c %Y "$heartbeat_file" 2>/dev/null || stat -f %m "$heartbeat_file" 2>/dev/null)
    local now=$(date +%s)
    local age=$((now - last_time))
    
    if [ $age -gt $HEARTBEAT_TIMEOUT ]; then
        echo "timeout"
    else
        echo "alive"
    fi
}

# 创建心跳文件
touch_heartbeat() {
    local heartbeat_file="$1"
    mkdir -p "$(dirname "$heartbeat_file")"
    touch "$heartbeat_file"
}

# 刷新心跳
refresh_heartbeat() {
    local heartbeat_file="$1"
    if [ -f "$heartbeat_file" ]; then
        touch "$heartbeat_file"
    fi
}

# 从契约文件获取执行命令
get_execution_command() {
    local contract_file="$1"
    # 简单解析：提取 command 字段
    grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' "$contract_file" | sed 's/.*"\([^"]*\)"$/\1/'
}

# 从契约文件获取任务ID
get_task_id() {
    local contract_file="$1"
    grep -o '"taskId"[[:space:]]*:[[:space:]]*"[^"]*"' "$contract_file" | sed 's/.*"\([^"]*\)"$/\1/'
}

# 调用 OpenClaw 执行任务
execute_task() {
    local contract_file="$1"
    local command=$(get_execution_command "$contract_file")
    local task_id=$(get_task_id "$contract_file")
    local heartbeat_file="${HEARTBEAT_DIR}/${task_id}.heartbeat"
    
    log "开始执行任务: $task_id"
    log "执行命令: $command"
    
    # 创建心跳文件
    touch_heartbeat "$heartbeat_file"
    
    # 更新状态为 running
    update_task_status "$contract_file" "running"
    
    # 执行命令（后台运行，持续更新心跳）
    local output_file="${LOG_DIR}/${task_id}_output.log"
    
    # 启动执行子进程
    (
        # 子进程：持续更新心跳
        while true; do
            refresh_heartbeat "$heartbeat_file"
            sleep 10
        done
    ) &
    HEARTBEAT_PID=$!
    
    # 执行实际命令
    local exit_code=0
    eval "$command" > "$output_file" 2>&1 || exit_code=$?
    
    # 终止心跳更新
    kill $HEARTBEAT_PID 2>/dev/null || true
    
    # 记录结果
    local output=$(cat "$output_file")
    record_result "$contract_file" "$exit_code" "$output"
    
    if [ $exit_code -eq 0 ]; then
        update_task_status "$contract_file" "completed"
        log "任务完成: $task_id (exit code: $exit_code)"
    else
        # 检查是否需要重试
        local retry_count=$(grep -o '"retryCount"[[:space:]]*:[[:space:]]*[0-9]*' "$contract_file" | grep -o '[0-9]*' || echo "0")
        if [ $retry_count -lt $MAX_RETRIES ]; then
            update_task_status "$contract_file" "pending"
            # 增加重试计数（简化处理）
            log "任务，准备失败重试: $task_id (retry: $retry_count/$MAX_RETRIES            update_task_status)"
        else
 "failed"
            log "任务失败 "$contract_file": $task_id (已达到最大重试次数)"
        fi
    fi
    
    return $exit_code
}

# 处理单个契约文件
process_contract() {
    local contract_file="$1"
    local filename=$(basename "$contract_file")
    
    # 跳过非 JSON 文件
    [[ "$filename" != *.json ]] && return
    
    local status=$(get_task_status "$contract_file")
    local task_id=$(get_task_id "$contract_file")
    
    case "$status" in
        "pending")
            log "发现待执行任务: $task_id"
            execute_task "$contract_file"
            ;;
        "running")
            # 检查心跳
            local heartbeat_file="${HEARTBEAT_DIR}/${task_id}.heartbeat"
            local hb_status=$(check_heartbeat "$heartbeat_file")
            
            if [ "$hb_status" = "timeout" ]; then
                error "检测到任务超时: $task_id，尝试重新执行"
                # 可以选择自动重跑或标记失败
                execute_task "$contract_file"
            else
                log "任务运行中: $task_id (心跳: $hb_status)"
            fi
            ;;
        "completed"|"failed")
            # 跳过已完成/失败的任务
            ;;
        *)
            # 未知状态，跳过
            ;;
    esac
}

# 主循环
main_loop() {
    log "PKM Agent 守护进程启动"
    log "轮询间隔: ${POLL_INTERVAL}s"
    log "心跳超时: ${HEARTBEAT_TIMEOUT}s"
    log "最大重试: ${MAX_RETRIES}次"
    
    while true; do
        # 确保目录存在
        mkdir -p "$CONTRACTS_DIR" "$HEARTBEAT_DIR" "$LOG_DIR"
        
        # 遍历所有契约文件
        for contract_file in "$CONTRACTS_DIR"/*.json; do
            [ -f "$contract_file" ] || continue
            process_contract "$contract_file"
        done
        
        # 等待下一个轮询周期
        sleep "$POLL_INTERVAL"
    done
}

# ========== 命令处理 ==========

start_daemon() {
    if [ -f "$PID_FILE" ]; then
        local old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "Agent 已在运行 (PID: $old_pid)"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    mkdir -p "$LOG_DIR"
    
    # 后台启动
    nohup "$0" run >> "${LOG_DIR}/agent.log" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    log "Agent 已启动 (PID: $PID)"
    echo "Agent 已启动 (PID: $PID)"
}

stop_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Agent 未运行"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm -f "$PID_FILE"
        log "Agent 已停止"
        echo "Agent 已停止"
    else
        rm -f "$PID_FILE"
        echo "Agent 未运行（PID 文件过期）"
    fi
}

status_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Agent 未运行"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "Agent 正在运行 (PID: $pid)"
        
        # 显示最近的活动
        echo ""
        echo "=== 最近日志 ==="
        tail -20 "${LOG_DIR}/agent.log" 2>/dev/null || echo "无日志"
        
        # 显示运行中的任务
        echo ""
        echo "=== 运行中的任务 ==="
        for hb in "${HEARTBEAT_DIR}"/*.heartbeat; do
            [ -f "$hb" ] || continue
            local task_id=$(basename "$hb" .heartbeat)
            local status=$(check_heartbeat "$hb")
            echo "  - $task_id: $status"
        done
        
        return 0
    else
        rm -f "$PID_FILE"
        echo "Agent 未运行（PID 文件过期）"
        return 1
    fi
}

show_logs() {
    if [ -f "${LOG_DIR}/agent.log" ]; then
        tail -50 "${LOG_DIR}/agent.log"
    else
        echo "暂无日志"
    fi
}

# 单次运行（用于手动触发）
run_once() {
    log "单次执行模式"
    for contract_file in "$CONTRACTS_DIR"/*.json; do
        [ -f "$contract_file" ] || continue
        process_contract "$contract_file"
    done
}

# ========== 主入口 ==========

case "${1:-help}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    status)
        status_daemon
        ;;
    logs)
        show_logs
        ;;
    run)
        main_loop
        ;;
    execute)
        # 单次执行指定契约文件
        if [ -z "$2" ]; then
            echo "用法: $0 execute <契约文件>"
            exit 1
        fi
        process_contract "$2"
        ;;
    *)
        echo "PKM Agent 守护脚本"
        echo ""
        echo "用法: $0 <命令>"
        echo ""
        echo "命令:"
        echo "  start         启动守护进程"
        echo "  stop          停止守护进程"
        echo "  restart       重启守护进程"
        echo "  status        查看状态"
        echo "  logs          查看日志"
        echo "  run           运行主循环（后台）"
        echo "  execute <file> 执行单个契约文件"
        echo ""
        echo "环境变量:"
        echo "  POLL_INTERVAL    轮询间隔（秒，默认30）"
        echo "  HEARTBEAT_TIMEOUT 心跳超时（秒，默认300）"
        echo "  MAX_RETRIES      最大重试次数（默认3）"
        ;;
esac
