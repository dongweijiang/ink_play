# 墨痕登塔（Inkbound Spire）

原创单机 Roguelike 卡牌游戏。当前完成第 2 轮：桌面工程骨架可演示主菜单、设置、暂停与安全退出；无界面的纯规则战斗引擎可模拟完整战斗。

## 环境

- Python 3.12
- Windows 10/11 为首要平台

## 运行

```powershell
python -m pip install -r requirements.txt
python main.py
```

## 测试

```powershell
python -m pytest
```

运行不依赖 pygame 窗口的战斗模拟：

```powershell
python -m tools.simulate_combat
```

## 当前操作

- 鼠标或方向键选择菜单，Enter 确认。
- F11 切换全屏。
- 在骨架演示场景按 Esc 打开暂停菜单。
- 暂停菜单可继续、返回主菜单或退出游戏。

完整设计见 `docs/`。在线绘图识别尚未接入，不需要 API Key。正式战斗 HUD 将在第 4 轮制作。
