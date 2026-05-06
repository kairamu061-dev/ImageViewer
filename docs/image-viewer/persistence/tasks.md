# persistence タスク

## 実装タスク一覧

- [x] state_manager.py 実装（save/load）
- [x] MainWindow.closeEvent で状態保存
- [x] MainWindow._restore_state で状態復元
- [x] TabContent.get_state / restore_state 実装
- [x] AppTabWidget.get_state / restore_state 実装
- [x] FavoritesTab のスプリッターサイズ保存/復元
- [x] スワップモード保存/復元
- [x] ウィンドウ位置・サイズ保存/復元

## 依存関係

- TabContent.get_state → AppTabWidget.get_state
- FavoritesModel.to_json / from_json → AppTabWidget.get_state / restore_state
- すべて → MainWindow.closeEvent / _restore_state
