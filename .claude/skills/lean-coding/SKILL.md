---
name: lean-coding
description: 無駄のないコーディングの原則集。Torvalds・Carmack・Pike・Beck・Ousterhout・Metz・grug ら著名エンジニアが公開している流儀のいいとこどり。コードを書く・直す・レビューするときに常に適用する。Use when writing, refactoring, or reviewing any code, to eliminate waste - premature abstraction, premature optimization, needless complexity, speculative generality, and oversized diffs.
---

# 無駄のないコーディング (Lean Coding)

目的: **「動く最小のコード」を「読み手に伝わる形」で書く。**
無駄とは = 今必要ないコード・複雑さ・抽象・最適化・大きすぎるdiff のすべて。
迷ったら「複雑性は悪魔 (complexity very, very bad — grug)」に立ち返り、足すより削る側に倒す。

## 0. 基本姿勢 — この順番を守る

**Make it work → Make it right → Make it fast.** (Kent Beck)

1. まず動かす(この段階は汚くてよい)
2. 動いたら、意図が読める形に整える
3. 速くするのは、計測でボトルネックだと証明されてから(やらないことが多い)

## 1. 書く前に決めること

### データ構造が先、コードは後 (Torvalds / Pike)

> "Bad programmers worry about the code. Good programmers worry about data structures and their relationships." — Linus Torvalds

> "Data dominates. If you've chosen the right data structures and organized things well, the algorithms will almost always be self-evident." — Rob Pike (Rule 5)

- 実装に入る前に「どんなデータを、どんな形で持つか」を先に決める。
- 正しいデータ構造を選ぶと、コードは自明になり if 文が減る。if が多いのは大抵データの持ち方が悪いサイン。

### YAGNI — 今日使わないものは書かない

- 「後で必要になるかも」の引数・オプション・設定項目・汎用化・拡張ポイントはすべて無駄。必要になった日に足す方が安い。
- 「no」は魔法の言葉 (grug)。機能もライブラリも抽象レイヤーも、足す前に「無しで済まないか」を必ず問う。
- 依存ライブラリの追加は特に慎重に。数行で書けるものに依存を増やさない。

## 2. 書くときのルール

### 特殊ケースを設計で消す — "good taste" (Torvalds)

- if 文で特殊ケースを潰すのではなく、特殊ケースが「普通のケース」に溶ける書き方を探す。
- 有名な例: 連結リストの先頭削除だけ特別扱いするコードは、間接ポインタを使えば全ケース同じ処理になる。
- 一般形: `None`/空を特別扱いしない設計(空リスト・デフォルト値・番兵で統一する)。

```python
# 悪い: 呼び出し側に None の特殊ケースが漏れる
if cart is None: cart = [item]
else: cart.append(item)

# 良い: 「空のカート」を普通のケースにする(None を存在させない)
cart.append(item)
```

- レビュー観点: 「この if は、設計を変えれば消えないか?」

### 状態を最小化する (Carmack)

> "A large fraction of the flaws in software development are due to programmers not fully understanding all the possible states their code may execute in." — John Carmack

- 可能な限り純粋関数(入力→出力だけ、副作用なし)として書く。
- グローバル状態・メンバ変数への書き込み・遠くからの mutation を減らす。
- 変数はなるべく再代入しない(const / final / 単一代入)。フラグ変数は最後の手段。

### 関数は「呼ばれる回数」と「純粋さ」で分ける (Carmack / grug)

- 1回しか呼ばれない処理を、見栄えのために細切れの小関数へ分解しない。上から下へ一本で読める流れの方が、ファイル中を飛び回るより理解しやすい。
- 切り出してよいのは: ①2箇所以上から呼ばれる ②純粋関数として独立できる ③明確に別の責務、のとき。
- 短さ(concision)と読みやすさ(clarity)が衝突したら、常に読みやすさを取る。ワンライナーの曲芸は無駄。

### 深いモジュールを作る (Ousterhout)

- **インターフェースは小さく、実装は深く。** 手本は Unix の file I/O(open/read/write/close だけで背後の複雑さを全部隠す)。
- 呼び出しをほぼ素通しするラッパー・引数を横流しするだけの層・1メソッドを転送するだけのクラスは shallow module = 無駄。層を1枚削れないか常に問う。

### 抽象化は3回目まで待つ (Metz / Abramov / Kent C. Dodds)

> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

- 2回の重複ではまだ抽象化しない。3回目で共通パターンが確定してから括り出す(Rule of Three / AHA: Avoid Hasty Abstractions)。
- 既存の抽象が新しい要件に合わなくなったら、引数と if を足して延命しない。**いったん重複に戻して**、正しい形が見えてから抽象し直す。

### 最適化は計測してから (Pike Rules 1–4)

- ボトルネックの場所は推測できない。プロファイルを取るまでチューニング禁止。
- n が小さいうちは単純なアルゴリズムが勝つ。そして n は大抵小さい。凝ったアルゴリズムは定数が大きくバグも多い。
- 単純なアルゴリズム+単純なデータ構造をデフォルトにする。

### 名前とコードで意図を語る (Beck: reveals intention)

- 「何をしたいか」がコードから読めるように名付ける。説明コメントを書きたくなったら、まず名前と構造で説明できないか試す。
- コメントはコードに書けないことだけに使う: なぜこうしたか・外部制約・落とし穴。「次の行が何をするか」を書くコメントは無駄。

## 3. 書いた後に削る

- **Fewest elements** (Beck): 使われていない関数・引数・import・設定・分岐は消す。「将来のため」は残す理由にならない。バージョン管理があるので消しても戻せる。
- **The best code is no code at all** (Jeff Atwood): 書いた行数ではなく、問題を解いた上でどれだけ書かずに済んだかを誇る。
- **Tidy First** (Beck): 整理(リネーム・移動・整形)と振る舞いの変更を同じコミットに混ぜない。先に小さく整えてから、本命の変更をする。
- **小さい diff** (Google eng-practices): 1コミット=1意図。レビューできる大きさを超えたら分割する。

## 4. テスト

- テストは「動くことの証明」であり Simple Design の第一条 (Beck: passes the tests)。主要経路のテストを最初に書く。
- 費用対効果の最良点は、実際の動きを検証する統合テスト (grug)。モックだらけで実装の形に癒着したユニットテストは、リファクタのたびに壊れる無駄。
- 実装の詳細ではなく、外から見える振る舞いをテストする。

## 5. コミット前チェックリスト

- [ ] 今日使わないコード・引数・オプション・汎用化を足していないか (YAGNI)
- [ ] 設計を変えれば消える if / 特殊ケースは残っていないか (good taste)
- [ ] 1〜2回しか使われない抽象を作っていないか (Rule of Three)
- [ ] 計測せずに「速くするためのコード」を書いていないか (Pike)
- [ ] 素通しのラッパー・薄い層を足していないか (deep modules)
- [ ] 消せるもの(未使用コード・自明コメント・デッドコード)は消したか
- [ ] diff は1つの意図か。整理と機能変更が混ざっていないか (Tidy First)
- [ ] テストは振る舞いを検証しているか(実装の形ではなく)

## 出典 — いいとこどり元

| 人物 | 採用した考え方 | 原典 |
|---|---|---|
| Linus Torvalds | good taste(特殊ケースを消す)/ データ構造中心 | github.com/mkirchner/linked-list-good-taste, 2016 TED interview |
| John Carmack | 状態の最小化・純粋関数・むやみに関数分割しない | "Carmack on Inlined Code" (number-none.com) |
| Rob Pike | 計測するまで最適化しない / データが支配する | "Rob Pike's 5 Rules of Programming" |
| Kent Beck | Simple Design 4原則 / work→right→fast / Tidy First | martinfowler.com/bliki/BeckDesignRules.html |
| Sandi Metz | 間違った抽象より重複が安い | sandimetz.com "The Wrong Abstraction" |
| Dan Abramov | clean code への過剰信仰をやめる | overreacted.io "Goodbye, Clean Code" |
| Kent C. Dodds | AHA — 早まった抽象化を避ける | kentcdodds.com/blog/aha-programming |
| John Ousterhout | 深いモジュール / 複雑性=変更増幅+認知負荷 | "A Philosophy of Software Design" |
| Carson Gross | 複雑性は悪魔 / 「no」は魔法の言葉 / 統合テスト重視 | grugbrain.dev |
| Jeff Atwood | The best code is no code at all | blog.codinghorror.com |
| Google | 小さいCL / 1CL=1意図 | github.com/google/eng-practices |
