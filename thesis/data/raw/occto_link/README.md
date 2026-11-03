# 北海道本州間連系設備（北本連系線）の運用容量とマージン（OCCTO の公表資料）

著者が2026-11-03 に OCCTO のサイトから取得した PDF。モデルでは model/params.py の LINK_MARGIN・OPCAP_EAST_PLAN・OPCAP_WEST・OPCAP_EAST に使う。

| ファイル | 資料 | 使う頁 |
|:--|:--|:--|
| 1_2023_2032_unyouyouryou.pdf | 2023〜2032年度の連系線の運用容量（年間・長期） | p.3〜10（年間）、p.12（長期） |
| oshirase_1_2024-2033_unyouyouryou.pdf | 2024〜2033年度の連系線の運用容量（年間・長期） | p.3〜10、p.12 |
| oshirase_1_2025-2034_unyouyouryou.pdf | 2025〜2034年度の連系線の運用容量（年間・長期） | p.3〜10、p.12 |
| oshirase_1_2026-2035_unyouyouryou.pdf | 2026〜2035年度の連系線の運用容量（年間・長期）別紙1（2026-03-01） | p.3〜18（年間）、p.20（長期） |
| 20230301_margin_1_nenkan.pdf | 2023・2024年度の連系線のマージン（年間）別紙1 | p.4（北本・通常時）、p.5（作業時） |
| 20240301_margin_1_nenkan.pdf | 2024・2025年度の連系線のマージン（年間）別紙1 | p.4、p.5 |
| 20250301_margin_1_nenkan.pdf | 2025・2026年度の年間マージン 別紙1 | p.4、p.5 |
| 20260301_margin_1_nenkan.pdf | 2026・2027年度の年間マージン 別紙1 | p.4、p.5、p.11〜12（内訳） |
| 20260301_margin_2_thouki.pdf | 2028〜2035年度の長期マージン 別紙2 | p.2〜3 |

出典の URL（取得元）:
- 運用容量 2026〜2035: https://www.occto.or.jp/assets/renkeisenriyou/oshirase/2025/files/oshirase_1_2026-2035_unyouyouryou.pdf
- 年間マージン 2026-03-01: https://www.occto.or.jp/assets/news/renkeisenriyou/20260301_margin_1_nenkan.pdf
- 長期マージン 2026-03-01: https://www.occto.or.jp/assets/news/renkeisenriyou/20260301_margin_2_thouki.pdf
- 年間マージン 2025-03-01: https://www.occto.or.jp/assets/renkeisenriyou/oshirase/2024/files/20250301_margin_1_nenkan.pdf
- 年間マージン 2024-03-01: https://www.occto.or.jp/assets/renkeisenriyou/oshirase/2023/files/20240301_margin_1_nenkan.pdf
- 年間マージン 2023-03-01: https://www.occto.or.jp/assets/renkeisenriyou/oshirase/2022/files/20230301_margin_1_nenkan.pdf

読み方の注:
- 昼間帯は8〜22時、夜間帯は0〜8時と22〜24時（年間マージン 別紙1 p.2）。【】は作業時の最小運用容量（運用容量の PDF）。
- スポットで使える量は「運用容量−マージン（−計画潮流）」（JEPX 取引規程 第18条第4項、OCCTO の空容量の式）。北海道向（東北⇒北海道）のマージンは区分 B1（北海道の最大の単一電源の脱落）と C1 の大きい方。
- 年間マージン p.4 の値（通常時）は model/params.py の LINK_MARGIN と一致することを確かめた（2026-11-03）。作業の日（p.5）はモデルに入れていない。
