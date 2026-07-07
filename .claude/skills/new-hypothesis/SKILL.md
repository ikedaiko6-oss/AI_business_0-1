---
name: new-hypothesis
description: Evaluate a new business hypothesis for this repo (AI_business_0-1) with live research before presenting it — never vibes-only. Use whenever the user proposes a new business idea, asks something like "この事業どう思う"/"〜って稼げる？", or explicitly invokes /new-hypothesis. Runs WebSearch for real competitors, pricing, and demand evidence (plus counter-evidence), fills the mandatory 11-item template from CLAUDE.md, appends it to research/hypothesis-log.md, and commits+pushes to the designated branch.
---

# 事業仮説の即時リサーチ＆評価スキル

新しい事業アイデアが話題に出たら、雰囲気で良し悪しを言わず、その場でリサーチしてから `CLAUDE.md` の11項目テンプレートを埋めて記録する。`/new-hypothesis <アイデア>` の形でも、会話の中でアイデアが出た時にも使う。argsが空なら直前の会話で出たアイデアを対象にする。

Make a todo list for the steps below and work through them one at a time.

## 1. 前提を読む

- `CLAUDE.md` の「仮説とリサーチの原則」「新しい事業仮説を出す型」を確認する
- `research/strength-profile.md` で強み適合の軸（現場力・AI・中京圏・開業済み）を確認する
- `research/hypothesis-log.md` が既にあれば読み、同じ/似た仮説が評価済みでないか確認する（あれば重複させず追記・更新で対応）

## 2. リサーチする（CLAUDE.md 原則1・2を厳守）

WebSearchで必ず次を調べる。既存の `research/` ファイルで確実に裏付けが取れる部分は再利用してよいが、新規要素は必ず検索する。

- **実在する競合**：社名・サービス名が具体的に出るまで検索する。「競合がいない」と書きたくなったら、まだ探し方が甘いと疑う
- **価格帯・相場**：出典URLが取れるものを優先する
- **需要の一次情報**：可能な限り官公庁統計・業界団体データを優先する
- **反証**：都合の悪い情報（レッドオーシャン化の兆候、規制、撤退・廃業事例、自動化による陳腐化リスク）を積極的に探す。良い情報だけ集めない

一次情報が取れない数値は「要検証」と明記する。数値には出典URLを添える。

## 3. 11項目テンプレートを埋める

`CLAUDE.md` の表と同じ11項目を埋める：事業仮説／根拠／強み適合／競合／価格帯／レッドオーシャン度／残っている隙間／参入コスト／日10万円への道筋／次に検証すべき質問／判定。

- 判定（S/A/B/C）は `research/2026-07-06-100k-per-day-worldwide-map.md` のランク定義（S=今月着手、A=90日以内、B=6〜12ヶ月、C=やらないと決める）に揃える
- 「日10万円への道筋」は**単発の10万円か、ストック化した平均10万円かを必ず明記**する
- 「残っている隙間」に「競合がいない」等の確定的な表現は使わない。競合の経済合理性が向いていない理由・その隙間がいつまで続くかを書く
- 項目が埋まらない場合は、埋まっていないこと自体を明記する（隠さない）

## 4. 記録する

- `research/hypothesis-log.md` に日付見出し（`## YYYY-MM-DD <事業仮説名>`）で追記する（ファイルがなければ作成し、README.mdの目次にも追加する）
- S/Aランクが付いた場合のみ、専用の深掘りファイル（`S1-*.md` のような形式）を作るかどうかユーザーに確認する。B/Cランクはログに留め、深掘りファイルは作らない

## 5. コミット・プッシュ

`CLAUDE.md` 原則5の通り、都度の許可待ちをせずコミットして指定ブランチにプッシュする。

## 6. 報告

ユーザーには埋めた11項目の表そのものと、一言の要約（判定＋理由）だけ返す。リサーチ過程の検索クエリや細かい試行錯誤は出さない。

## 注意

- 既存ファイルの結論と矛盾する情報が見つかったら、`CLAUDE.md` 原則4の通り隠さず訂正として明記し、該当ファイルも更新する
- 「確定」「絶対」「〜が最適」等の断定語を使う前に、反証を探したかどうかを自問する
