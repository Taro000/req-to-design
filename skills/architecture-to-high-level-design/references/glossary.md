# Glossary

Use these terms for the working language. For a language not listed, or a term missing from the list, choose one translation the first time you need it, prefer the plain everyday word, and use it everywhere after that, in every stage.

## Chain and process terms

| English | 日本語 |
|---|---|
| quality chain (the skills that write docs/quality/) | 品質チェーン |
| issues for the quality chain | 品質チェーンへの課題 |
| design stage | 設計の段 |
| design context | 設計の与件 |
| finding | 指摘 |
| severity: critical / major / minor | 重さ: 重大 / 中 / 軽微 |
| finding status: open / accepted / rejected | 指摘の状態: 未解決 / 受け入れ / 退ける |
| fresh context (for a review) | 別の文脈 |
| review | レビュー |
| risk / non-risk | リスク / リスクでないもの |
| basis: stated / inferred / assumed / confirmed | 根拠: 入力 / 推定 / 仮定 / 確認済み |
| status: active / retired | 状態: 有効 / 廃止 |
| report status: draft / answers applied | 報告書の状態: 下書き / 回答反映済み |
| inputs as of (the commit the inputs were read at) | 入力の基準 |
| detailed design status: not started / draft / answers applied | 詳細設計の状態: 未着手 / 下書き / 回答反映済み |
| business decision | 事業の判断 |
| decisions (the questions asked and the answers in effect) | 決めたこと |
| assumption (a judgment made without asking) | 仮定 |
| assumption kind: judgment / decision | 仮定の種類: 判断 / 暫定の決定 |
| assumption status: open / confirmed / overturned / retired | 仮定の状態: 未確認 / 確認済み / 覆った / 廃止 |
| breadth / severity of a point: high / medium / low | 影響の広さ / 重大さ: 高 / 中 / 低 |
| premises (what an item depends on) | 前提 |
| design input (a design decision the quality chain found in its input and passed on: DIN) | 設計への申し送り |
| decision depth: full / bounds / hand-off | 決める深さ: 確定 / 枠 / 申し送り |
| full-depth kinds (what a stage decides in full) | 確定の種類 |
| deferral (leaving a point for a later stage, implementation or an event to decide) | 先送り |
| hand-off (HND: a point a design stage leaves to a later stage or to implementation) | 申し送り |
| hand-off parts: what / to / trigger / bounds / origin | 申し送りの中身: 何を / 宛先 / 契機 / 守る枠 / 由来の項目 |
| hand-off status: open / decided / retired | 申し送りの状態: 未決定 / 決定済み / 廃止 |
| decide a hand-off / pass it on | 申し送りを決める / 先へ送る |
| implementation (the coding that follows stage 4) | 実装 |
| hand-off to implementation (the section of the detailed design index that coding agents read first) | 実装への申し送り |
| open gaps | 未解決の点 |
| out of scope | 範囲外 |
| placeholder (for a number not yet decided) | 未定の値 |
| traceability | トレーサビリティ |

## Inputs and drivers

| English | 日本語 |
|---|---|
| stakeholder | 利害関係者 |
| concern | 関心事 |
| concern kinds: function / quality / constraint / change / organization | 関心事の種類: 機能 / 品質 / 制約 / 変更 / 組織 |
| technology constraint: mandated / prohibited / platform / external service | 技術制約: 使う / 使わない / 基盤 / 外部サービス |
| project constraints (budget, deadline, team) | 費用・納期・体制の制約 |
| team structure | チームの構成 |
| anticipated change | 将来の変更 |
| current structure (of an existing system) | 今の構造 |
| as-is: keep / change / new / remove | 今の構造との差分: 残す / 変える / 新設 / 廃止 |
| architecture driver | 設計を動かす要求 |
| driver kinds: quality / change / constraint / function / observability / security / principle | 設計を動かす要求の種類: 品質 / 変更 / 制約 / 機能 / 観測 / セキュリティ / 原則 |
| primary driver | 主な設計を動かす要求 |
| quality scenario / change scenario | 品質のシナリオ / 変更のシナリオ |
| scenario parts: source / stimulus / artifact / environment / response / measure | シナリオの要素: 出どころ / 刺激 / 対象 / 環境 / 応答 / 応答の測定量 |
| negotiable / non-negotiable | 交渉できる / 交渉できない |
| principle (system-wide) | 全体の原則 |
| business priority | 事業の優先度 |
| design difficulty | 設計上の難しさ |
| high / medium / low | 高 / 中 / 低 |
| ranking table | 順位表 |
| conflict (between drivers) | 競合 |

## Architecture

| English | 日本語 |
|---|---|
| design decision | 設計の決定 |
| question (that a decision answers) | 問い |
| option / chosen option / rejected option | 案 / 選んだ案 / 退けた案 |
| rationale | 決めた理由 |
| gains / costs | 得るもの / 失うもの |
| sensitive point | 応答を左右する点 |
| trade-off | 引き換え |
| assumption (what a decision takes as given, in DEC `assumptions`) | 想定 |
| design mechanism | 設計の手立て |
| design parameter | 設計上の値 |
| technical debt | 技術的負債 |
| overall structure | 全体の構造 |
| design concerns (the eight) | 設計の観点 |
| concurrency | 並行性 |
| control and event handling | 制御とイベント処理 |
| data persistence | データの永続化 |
| distribution | 分散 |
| error handling and fault tolerance | エラー処理と障害許容 |
| integration and interoperability | 統合と相互運用 |
| assurance, security and safety | 保証・セキュリティ・安全 |
| variability | 可変性 |
| element: component / data store / external system / node | 要素: コンポーネント / データの置き場所 / 外部のシステム / 実行環境 |
| responsibility | 責務 |
| view | ビュー |
| views: context / runtime / deployment / information / code structure | ビュー: 外部との関係 / 実行時の構成 / 配置 / 情報 / コードの分け方 |
| walkthrough | 通し確認 |
| threat model | 脅威のモデル |
| trust boundary | 信頼の境界 |

## High-level and detailed design

| English | 日本語 |
|---|---|
| interface | インタフェース |
| interface kinds: http / event / file / screen / batch | インタフェースの種類: HTTP / イベント / ファイル / 画面 / バッチ |
| provider / consumer | 提供側 / 利用側 |
| operation / message | 操作 / メッセージ |
| error contract | エラーの決まり |
| idempotency / idempotency key | 冪等性 / 冪等キー |
| unknown outcome / settle it | 結果が分からない状態 / 結果を確定させる |
| reconciliation | 照合 |
| circuit breaker | サーキットブレーカー |
| percentile | パーセンタイル |
| error budget volume | 許容される失敗の件数 |
| timing: timeout / ordering / delivery | 順序と時間: タイムアウト / 順序 / 届け方 |
| versioning | 版の扱い |
| end-to-end flow | 端から端の流れ |
| failure path | 失敗したときの流れ |
| latency budget | 遅延の予算 |
| screen flow | 画面の移り変わり |
| data entity | データの実体 |
| owner (of a data entity) | 持ち主 |
| consistency | 整合の取り方 |
| retention | 保持期間 |
| classification: public / internal / personal / payment | 扱いの区分: 公開 / 社内 / 個人情報 / 決済情報 |
| shared conventions | 共通の約束事 |
| module | モジュール |
| visibility: public / internal | 公開範囲: 公開 / 内部 |
| module depth: full / bounds (designed in detail / its inside left to implementation) | モジュールの深さ: 確定 / 枠 |
| contract summary (the contract of a module at bounds depth) | 契約の要約 |
| dependency | 依存 |
| precondition / postcondition / invariant | 事前条件 / 事後条件 / 不変条件 |
| state diagram | 状態遷移図 |
| decision table | 判断表 |
| verification approach | 確かめ方 |
| detailed design index | 詳細設計の索引 |

## Terms of the quality chain that designs refer to

| English | 日本語 |
|---|---|
| user / primary user / secondary user / indirect user | 利用者 / 一次利用者 / 二次利用者 / 間接利用者 |
| data producer | データを作る人 |
| CUJ (critical user journey) / CUJ step | CUJ / CUJ の手順 |
| context of use | 利用状況 |
| quality-in-use requirement | 利用時の品質要求 |
| functional requirement / acceptance criteria | 機能要件 / 受け入れ基準 |
| quality requirement | 品質要求 |
| product quality / data quality | 製品の品質 / データの品質 |
| handling: emphasized / minimum line / excluded (this cycle) | 扱い: 重視 / 最低限守る線 / 今期は対象外 |
| entry point (a requirement that does not come from users) | 入口 |
| conflict (between quality requirements) | 競合 |
| non-functional requirement | 非機能要件 |
| SLI / SLO / error budget | SLI / SLO / エラーバジェット |
| vantage (where an SLI's events are observed): user-side / system-boundary / synthetic / data | 見る位置: 利用者の側 / システムの境界 / 模擬の利用 / データ |
| SLI binding (where an SLI's events come from) | SLI の出どころ |
| unit event (of an SLI) | 数える単位の出来事 |
| counting rule | 数え方の規則 |
| existing source (telemetry that already exists) | 既存の出どころ |
| blind spot | 見えないもの（測定の制約） |
| platforms and device support | プラットフォームと対応する端末 |
| shared facts (of the quality chain: CON, EXT, OPF) | 共有する事実 |
| operational facts | 運用の事実 |
