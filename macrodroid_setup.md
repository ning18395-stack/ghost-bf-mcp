# Macrodroid 配置

## 1. 安装
应用商店搜 "Macrodroid"，免费版够用。

## 2. 新建宏

打开 Macrodroid → 右下 "+" → 添加宏

### 触发器
- 类别：**应用程序**
- 选项：**应用打开/关闭**
- 选择：**任何应用程序被打开**

### 动作
- 类别：**连接**
- 选项：**HTTP 请求**
- 配置：
  - URL: `http://127.0.0.1:8000/phone/activity` (Termux本地)
  - 方法：`POST`
  - 内容类型：`application/json`
  - 自定义请求头：
    ```
    X-Auth-Token: change-me-to-something-random-abc123
    ```
    （跟 config.toml 里的 phone.secret 一致）
  - 请求体：
    ```
    {"app": "[fg_app_name]", "event": "switch"}
    ```

### 约束（可选）
加 "屏幕开启" 约束，避免黑屏时也上报。

## 3. 保存 + 后台权限

- 保存宏
- 设置 → 电池 → 关闭 Macrodroid 的电池优化
- 给后台运行权限

## 4. 测试

切几个 APP，然后在 Termux 里访问：
```bash
curl http://127.0.0.1:8000/activity
```
应该能看到上报的活动。
