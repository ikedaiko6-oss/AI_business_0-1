---
name: lean-coding
description: 無駄のないコーディング原則集(トークン消費の最小化も含む)。Torvalds・Carmack・Pike・Beck・Ousterhout・Metz・grug ら著名エンジニアの流儀のいいとこどり。コードを書く・直す・レビューするときに常に適用する。Use when writing, refactoring, or reviewing any code - eliminates waste such as premature abstraction/optimization, needless complexity, speculative generality, oversized diffs, and token-wasteful AI workflows (full-file rewrites, unnecessary reads, boilerplate output).
---

# 無駄のないコーディング (Lean Coding)

**「動く最小のコード」を「読み手に伝わる形」で書く。**
無駄 = 今必要ないコード・複雑さ・抽象・最適化・大きすぎるdiff・浪費トークン。
迷ったら「複雑性は悪魔 (complexity very, very bad — grug)」。足すより削る側に倒す。

「何を書くか」の原則はこのスキル。「どの順番で動くか」は [fast-build](../fast-build/SKILL.md) を参照。

## 0. 基本姿勢 — この順番を守る

**Make it work → Make it right → Make it fast.** (Kent Beck)
①まず動かす(汚くてよい) ②意図が読める形に整える ③速くするのは計測でボトルネックだと証明されてから(大抵やらない)。

## 1. 書く前に決める

**データ構造が先、コードは後** (Torvalds / Pike)
> "Bad programmers worry about the code. Good programmers worry about data structures and their relationships." — Linus Torvalds

- 実装前に「どんなデータをどんな形で持つか」を決める。正しいデータ構造を選べばコードは自明になる。if が多いのはデータの持ち方が悪いサイン。
- 手戻り(書き直し)が最大の無駄。ここで1分考えるのが一番の節約。

**YAGNI — 今日使わないものは書かない**
- 「後で必要かも」の引数・オプション・設定・汎用化・拡張ポイントは全部無駄。必要になった日に足す方が安い。
- 「no」は魔法の言葉 (grug)。機能・ライブラリ・抽象レイヤーは足す前に「無しで済まないか」を問う。数行で書ける処理に依存を増やさない。

## 2. 書くときのルール

**特殊ケースを設計で消す — "good taste"** (Torvalds)
- if で特殊ケースを潰さず、特殊ケースが「普通のケース」に溶ける書き方を探す。例: 連結リストの先頭削除は間接ポインタで全ケース同一になる。None を許さず空リストで統一する。
- レビュー観点:「この if は設計を変えれば消えないか?」

**状態を最小化する** (Carmack)
> "A large fraction of the flaws in software development are due to programmers not fully understanding all the possible states their code may execute in." — John Carmack

- 可能な限り純粋関数に。グローバル状態・遠くからの mutation を減らす。変数は再代入しない(const/final)。フラグ変数は最後の手段。

**関数は「呼ばれる回数」と「純粋さ」で分ける** (Carmack / grug)
- 1回しか呼ばれない処理を見栄えのために細切れ関数にしない。上から下へ一本で読める方が、ファイル中を飛び回るより分かりやすい。
- 切り出すのは ①2箇所以上から呼ばれる ②純粋関数として独立できる ③明確に別責務、のとき。
- 短さと読みやすさが衝突したら読みやすさを取る。ワンライナー曲芸は無駄。

**深いモジュール** (Ousterhout)
- インターフェースは小さく、実装は深く(手本: Unix の open/read/write/close)。素通しラッパー・引数を横流しするだけの層・転送するだけのクラスは shallow module = 無駄。層を1枚削れないか問う。

**抽象化は3回目まで待つ** (Metz / Abramov / Dodds)
> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

- 2回の重複ではまだ抽象化しない。3回目でパターンが確定してから括り出す(Rule of Three / AHA)。
- 合わなくなった抽象は引数と if で延命せず、いったん重複に戻して正しい形を見つけ直す。

**最適化は計測してから** (Pike)
- ボトルネックは推測できない。プロファイル前のチューニング禁止。n は大抵小さく、単純なアルゴリズム+単純なデータ構造が勝つ。

**名前とコードで意図を語る** (Beck)
- 説明コメントを書きたくなったら、まず名前と構造で説明できないか試す。コメントは「なぜ・外部制約・落とし穴」だけ。「次の行が何をするか」コメントは無駄。

## 3. 書いた後に削る

- **Fewest elements** (Beck): 未使用の関数・引数・import・分岐は消す。「将来のため」は理由にならない(git で戻せる)。
- **The best code is no code at all** (Atwood): 行数ではなく「書かずに済んだ量」を誇る。
- **Tidy First** (Beck): 整理(リネーム・移動・整形)と振る舞いの変更を同じコミットに混ぜない。
- **小さい diff** (Google): 1コミット=1意図。レビューできる大きさに保つ。

## 4. テスト

- テストは「動くことの証明」(Beck 第一条)。主要経路から書く。
- 費用対効果の最良点は、実際の動きを検証する統合テスト (grug)。モックに癒着したユニットテストはリファクタのたびに壊れる無駄。実装の形ではなく、外から見える振る舞いをテストする。

## 5. トークンも無駄のうち — AI協働ルール

リーンなコードはそのままトークン節約(YAGNI・fewest elements・小さい diff = 出力削減)。加えて:

- **差分編集**: 全文再生成せず該当箇所だけ Edit。編集後の確認再読・チャットへのコード再掲をしない。
- **読むのは必要な範囲だけ**: Grep/Glob で位置を特定してから該当行だけ Read。ファイル全読み・リポジトリ総なめをしない。
- **最大の浪費は手戻り**: §1(データ構造と方針を先に決める)がトークン節約の本丸。試行錯誤ループに入ったら手を止めて設計に戻る。
- **頼まれていない出力をしない**: ボイラープレート・自明コメント・雛形・余分なテスト・長い説明を生成しない。
- **ただし可読性は削らない**: 変数名を縮めても節約は誤差で、読めないコストの方が高い。「書く量を減らす」で節約し、「圧縮して読みにくくする」では節約しない。
- **深いモジュールはコンテキストも節約**(§2): インターフェースだけ読めば使えるコードは、次に AI が読み込む量も減らす。

## 6. コミット前チェックリスト

- [ ] 今日使わないコード・引数・汎用化を足していない (YAGNI)
- [ ] 設計変更で消える if / 特殊ケースが残っていない (good taste)
- [ ] 1〜2回しか使われない抽象を作っていない (Rule of Three)
- [ ] 計測せずに「速くするコード」を書いていない (Pike)
- [ ] 素通しラッパー・薄い層を足していない (deep modules)
- [ ] 消せるもの(未使用コード・自明コメント)は消した
- [ ] diff は1意図。整理と機能変更が混ざっていない (Tidy First)
- [ ] テストは振る舞いを検証している(実装の形ではなく)
- [ ] 全文再生成・不要な再読をしていない(トークン)

出典・原典リンク一覧: [references/sources.md](references/sources.md)(必要なときだけ参照)
