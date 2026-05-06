# persistence 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| JSON | 状態ファイル形式 | 人間が読めてデバッグしやすい。Python 標準ライブラリで扱える |
| Path.home() / .image_viewer_state.json | 保存先 | ユーザーホームは確実に書き込み可能で OS 横断的に使える |

## アーキテクチャ

```
state_manager.py
  ├── save(state: dict) → ~/.image_viewer_state.json
  └── load() → dict | {}  (エラー時は空 dict)

MainWindow.closeEvent
  └── tabs.get_state() → state_manager.save(state + window geometry)

MainWindow._restore_state
  └── state_manager.load() → tabs.restore_state(state) + window geometry
```

## インターフェース

```python
# state_manager.py
def save(state: dict) -> None: ...
def load() -> dict: ...   # 失敗時は {} を返す

# AppTabWidget
def get_state(self) -> dict: ...
def restore_state(self, state: dict) -> None: ...

# TabContent
def get_state(self) -> dict: ...
def restore_state(self, state: dict) -> None: ...
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| Python 標準 json | JSON シリアライズ/デシリアライズ |
| Python 標準 pathlib.Path | ファイルパス操作 |
