# Claude Code 制約事項

## 編集可能ファイル
Claude Codeは以下のファイルのみ編集可能です：
- README.md
- DEVELOPMENT_GUIDE.md
- .amazonq/ 以下のすべてのファイル

## 編集禁止ファイル
以下のファイルは Amazon Q が管理するため、Claude Codeは編集しないでください：
- src/ 以下のすべてのPythonファイル
- tests/ 以下のすべてのテストファイル
- config/ 以下の設定ファイル
- requirements.txt
- main.py
- その他のゲーム実装ファイル

## 役割分担
- **Claude Code**: ドキュメント管理、プロジェクト設定、開発ガイドライン
- **Amazon Q**: 実際のゲーム実装、テストコード、設定ファイル

## 重要な注意事項
もしゲーム実装に関する質問や修正依頼があった場合は、以下のように対応してください：
1. 「このファイルは Amazon Q が管理しています」と説明
2. DEVELOPMENT_GUIDE.md に実装ガイドラインを追記
3. .amazonq/rules/ に必要なルールを追加