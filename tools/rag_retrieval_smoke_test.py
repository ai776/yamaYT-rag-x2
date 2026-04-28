#!/usr/bin/env python3
"""Smoke-test Yamamoto RAG routing and local retrieval.

This is intentionally dependency-free. It does not try to replace the Claude
Code workflow; it checks whether representative themes can pull plausible
source files from `insights/` and whether routing references are valid.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "insights" / "_routing.md"
INSIGHTS = ROOT / "insights"


@dataclass(frozen=True)
class Case:
    name: str
    query: str
    expected_category: str
    expected_files: tuple[str, ...]
    accepted_categories: tuple[str, ...] = ()
    note: str = ""


CASES = (
    Case(
        name="outsourcing",
        query="社員を増やさず外注とクラウドディレクターで業務委託チームを作りたい",
        expected_category="外注・業務委託・クラウドディレクター",
        expected_files=(
            "ホリエモンスペシャル対談外注だけで年商40億円知らないと損する最強の外注活用術_analysis.txt",
            "優秀な外注の見つけ方もう迷わないプロのクラウドディレクター活用術_analysis.txt",
            "保存版外注だけで年商40億円外注500名で運営する外注業務内容公開外注組織化スマート経営事例紹介_analysis.txt",
        ),
    ),
    Case(
        name="ai_efficiency",
        query="AI議事録 マインドマップ GPTs ChatGPT 業務効率化で生産性を上げる",
        expected_category="AI活用・業務効率化",
        expected_files=(
            "AIマインドマップで議事録作成業務効率を劇的にアップする方法_analysis.txt",
            "AI革命最新のビジネス自動化とコスト削減術_analysis.txt",
            "ChatGPTで業務効率化書籍制作ビジネスモデルをGPTsで生み出す方法_analysis.txt",
        ),
    ),
    Case(
        name="marketing_funnel",
        query="広告代理店 ファネル リスト集客 LP 後発でも勝てるマーケティング",
        expected_category="マーケティング・広告・ファネル",
        expected_files=(
            "後発でも勝てる広告代理店ビジネスで他社と差別化して成功する秘訣を特別に公開します_analysis.txt",
            "知らなきゃ損高い再現性で10億円売り上げるマーケティングファネル設計とは_analysis.txt",
            "全ての経営者が学ぶべきゼロから売上を爆増させる広告運用方法とはリスト集客_analysis.txt",
        ),
    ),
    Case(
        name="influencer",
        query="ナノインフルエンサー DM アンバサダー契約 SNSで口コミを広げる",
        expected_category="SNS・インフルエンサー",
        expected_files=(
            "初心者必見ナノインフルエンサーで成功するインフルエンサーマーケティングの極意_analysis.txt",
            "インフルエンサーマーケティングDMのコツとアンバサダー契約の秘訣_analysis.txt",
            "AI外注ショート動画自動生成でSNS運用_analysis.txt",
        ),
    ),
    Case(
        name="sales",
        query="営業代行 クロージング 商談 成約率 BtoBの提案を強くしたい",
        expected_category="営業・クロージング・営業代行",
        expected_files=(
            "営業が苦手な方必見クロージングのコツ大公開今すぐ試せる成功率がアップするテクニック3選_analysis.txt",
            "営業代行で無限のビジネスチャンス1対1マーケティングで成果を出す秘訣_analysis.txt",
            "入会金1000万円REALVALUECLUB入会してみたBtoBビジネスでの成功方法リアルバリュークラブRVCとは_analysis.txt",
        ),
    ),
    Case(
        name="media_pr",
        query="書籍を無料配布してテレビ出演やPRにつなげて信頼を作る",
        expected_category="出版・メディア・PR",
        expected_files=(
            "書籍を無料配布して売上爆上げ誰も知らない出版マーケティングを解説します_analysis.txt",
            "無料でテレビに出演できる絶対に役立つマスコミメディア対策の裏技を伝授します_analysis.txt",
            "ニュースレターの威力無料配布から売上600万円デジタル時代にあえてアナログを取り入れる理由_analysis.txt",
        ),
    ),
    Case(
        name="new_business",
        query="認知症ビジネス AI診断 10億円を狙う新規事業モデルを考える",
        expected_category="新規事業・ビジネスモデル",
        expected_files=(
            "認知症ビジネスで10億円を達成するための事業戦略_analysis.txt",
            "AI診断で年商10億円個性心理学を活用したオンライン診断ビジネス成功術_analysis.txt",
            "10億を売り上げるビジネスはこう作るビジネスモデル設計で大事なポイントを解説_analysis.txt",
        ),
    ),
    Case(
        name="community_networking",
        query="異業種交流会 RVC 経営者コミュニティ 人脈からBtoBの新規事業につなげたい",
        expected_category="人脈・異業種交流・コミュニティ",
        expected_files=(
            "チャンスを掴む異業種交流会で10億円の収益を生む立ち回り方_analysis.txt",
            "入会金1000万円REALVALUECLUB入会してみたBtoBビジネスでの成功方法リアルバリュークラブRVCとは_analysis.txt",
            "営業代行で無限のビジネスチャンス1対1マーケティングで成果を出す秘訣_analysis.txt",
        ),
    ),
    Case(
        name="analog_newsletter",
        query="デジタル時代にあえて紙のニュースレターを無料配布して売上につなげる",
        expected_category="マーケティング・広告・ファネル",
        expected_files=(
            "ニュースレターの威力無料配布から売上600万円デジタル時代にあえてアナログを取り入れる理由_analysis.txt",
            "圧倒的に反応が違うライバルが少ないアナログマーケティングで10億円稼ぐ方法を伝授_analysis.txt",
            "書籍を無料配布して売上爆上げ誰も知らない出版マーケティングを解説します_analysis.txt",
        ),
        accepted_categories=("出版・メディア・PR",),
        note="ニュースレターはカテゴリ3と7の両方にあるため、売上導線なら3、無料配布/PRなら7も許容。",
    ),
    Case(
        name="product_boom",
        query="グリークヨーグルトや相席寿司みたいな商品ブーム 店舗トレンドが伸びる理由",
        expected_category="マーケティング・広告・ファネル",
        expected_files=(
            "ヒカキンが購入した400万円の純金ハンドスピナーの話も5ヶ月で2億円売ったマーケティングの裏話を特別に公開_analysis.txt",
            "知らなきゃ損高い再現性で10億円売り上げるマーケティングファネル設計とは_analysis.txt",
            "デジタルマーケティング完全ガイドChatGPT活用で見込み客を獲得する方法_analysis.txt",
        ),
    ),
    Case(
        name="ai_plus_outsourcing",
        query="AIでショート動画を自動生成して外注チームでSNS運用を回す",
        expected_category="AI活用・業務効率化",
        expected_files=(
            "AI外注ショート動画自動生成でSNS運用_analysis.txt",
            "AI革命最新のビジネス自動化とコスト削減術_analysis.txt",
            "業務効率化年商40億の経営者が使う生産性を上げるAIサービスとは_analysis.txt",
        ),
        accepted_categories=("SNS・インフルエンサー",),
        note="AI、外注、SNSが混ざる境界ケース。AI自動化を主題にするなら2、SNS運用を主題にするなら4。",
    ),
    Case(
        name="high_ticket_b2b",
        query="高単価BtoBコミュニティで紹介営業を作り営業代行につなげる",
        expected_category="営業・クロージング・営業代行",
        expected_files=(
            "入会金1000万円REALVALUECLUB入会してみたBtoBビジネスでの成功方法リアルバリュークラブRVCとは_analysis.txt",
            "営業代行で無限のビジネスチャンス1対1マーケティングで成果を出す秘訣_analysis.txt",
            "プロの力を借りる年商1億円以上の企業がプロ人材外注活用で成長スピードを一気に加速_analysis.txt",
        ),
    ),
)


def normalize(text: str) -> str:
    return text.lower().replace("　", " ")


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+|[一-龥ぁ-んァ-ンー]+", normalize(text))
    expanded: list[str] = []
    for token in tokens:
        expanded.append(token)
        if re.search(r"[一-龥ぁ-んァ-ンー]", token):
            expanded.extend(token[i : i + 2] for i in range(max(0, len(token) - 1)))
            expanded.extend(token[i : i + 3] for i in range(max(0, len(token) - 2)))
    return [t for t in expanded if len(t) >= 2]


def parse_routing() -> dict[str, dict[str, list[str]]]:
    text = ROUTING.read_text(encoding="utf-8")
    categories: dict[str, dict[str, list[str]]] = {}
    current: str | None = None
    section: str | None = None

    for raw in text.splitlines():
        line = raw.strip()
        match = re.match(r"##\s+\d+\.\s+(.+)", line)
        if match:
            current = match.group(1).strip()
            categories[current] = {"keywords": [], "files": []}
            section = None
            continue
        if current is None:
            continue
        if line.startswith("### "):
            section = line.removeprefix("### ").strip()
            continue
        if section == "反応キーワード" and line and not line.startswith("-"):
            categories[current]["keywords"].extend(
                [part.strip() for part in re.split(r"[、,]", line) if part.strip()]
            )
        if section == "優先して読むファイル" and line.startswith("- `"):
            file_match = re.search(r"`([^`]+)`", line)
            if file_match:
                categories[current]["files"].append(file_match.group(1))
    return categories


def route_category(query: str, categories: dict[str, dict[str, list[str]]]) -> tuple[str, int]:
    query_norm = normalize(query)
    scored: list[tuple[int, str]] = []
    for category, data in categories.items():
        score = 0
        for keyword in data["keywords"]:
            key = normalize(keyword)
            if key and key in query_norm:
                score += 10 + len(key)
        scored.append((score, category))
    scored.sort(reverse=True)
    return scored[0][1], scored[0][0]


def load_documents() -> list[tuple[Path, str]]:
    docs = []
    for path in sorted(INSIGHTS.glob("*_analysis.txt")):
        docs.append((path, normalize(path.name + "\n" + path.read_text(encoding="utf-8"))))
    return docs


def score_doc(query: str, doc_text: str) -> int:
    score = 0
    for token in tokenize(query):
        count = doc_text.count(token)
        if count:
            score += min(count, 12) * (4 if len(token) >= 4 else 1)
    return score


def retrieve(query: str, docs: list[tuple[Path, str]], limit: int) -> list[tuple[int, Path]]:
    ranked = [(score_doc(query, text), path) for path, text in docs]
    ranked.sort(key=lambda item: (item[0], item[1].name), reverse=True)
    return [item for item in ranked[:limit] if item[0] > 0]


def check_routing_files(categories: dict[str, dict[str, list[str]]]) -> list[str]:
    errors = []
    for category, data in categories.items():
        for rel in data["files"]:
            if not (ROOT / rel).exists():
                errors.append(f"{category}: missing {rel}")
    return errors


def run(limit: int) -> int:
    categories = parse_routing()
    docs = load_documents()
    missing = check_routing_files(categories)

    failures = 0
    if missing:
        failures += len(missing)
        print("Routing file reference failures:")
        for error in missing:
            print(f"  FAIL {error}")
        print()

    for case in CASES:
        routed, route_score = route_category(case.query, categories)
        top = retrieve(case.query, docs, limit)
        top_names = [path.name for _, path in top]
        expected_hit = [name for name in case.expected_files if name in top_names]
        accepted = (case.expected_category, *case.accepted_categories)
        route_ok = routed in accepted and route_score > 0
        retrieval_ok = bool(expected_hit)
        status = "PASS" if route_ok and retrieval_ok else "FAIL"
        if (
            status == "PASS"
            and routed != case.expected_category
            and routed in case.accepted_categories
        ):
            status = "WARN"
        if status == "FAIL":
            failures += 1

        print(f"{status} {case.name}")
        print(f"  query: {case.query}")
        print(f"  route: {routed} (expected: {case.expected_category})")
        if case.accepted_categories:
            print(f"  accepted also: {', '.join(case.accepted_categories)}")
        if case.note:
            print(f"  note: {case.note}")
        print(f"  expected hit: {expected_hit[0] if expected_hit else '-'}")
        print(f"  top {limit} results:")
        for score, path in top:
            print(f"    {score:4d}  {path.name}")
        print()

    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=5, help="number of retrieved files to inspect")
    args = parser.parse_args()
    return run(args.top)


if __name__ == "__main__":
    sys.exit(main())
