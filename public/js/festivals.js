// 花火大会プリセット（デモ用データ）
// 打上座標・最大玉サイズは公式情報ではなく概略値です。自由に追加・修正してください。
// 「カスタム」を選ぶと地図クリックで任意の打上地点を設定できます。
(function () {
  const FW = (window.FW = window.FW || {});

  // 号数ごとの標準的な打上（開花）高度と開花直径の目安 [m]
  FW.SHELL_SPECS = {
    "3":  { key: "3",  label: "3号玉（高度約120m・直径約60m）",        height: 120, diameter: 60 },
    "4":  { key: "4",  label: "4号玉（高度約160m・直径約130m）",       height: 160, diameter: 130 },
    "5":  { key: "5",  label: "5号玉（高度約190m・直径約150m）",       height: 190, diameter: 150 },
    "7":  { key: "7",  label: "7号玉（高度約250m・直径約240m）",       height: 250, diameter: 240 },
    "10": { key: "10", label: "10号玉・尺玉（高度約330m・直径約320m）", height: 330, diameter: 320 },
    "20": { key: "20", label: "20号玉・二尺玉（高度約500m・直径約480m）", height: 500, diameter: 480 },
    "30": { key: "30", label: "30号玉・三尺玉（高度約600m・直径約550m）", height: 600, diameter: 550 },
  };

  FW.FESTIVALS = [
    { id: "sumida1", name: "隅田川花火大会（第一会場）",   pref: "東京都",  lat: 35.7176, lng: 139.8023, shell: "5",  note: "桜橋〜言問橋間の川上から打上" },
    { id: "sumida2", name: "隅田川花火大会（第二会場）",   pref: "東京都",  lat: 35.7043, lng: 139.7947, shell: "5",  note: "駒形橋〜厩橋間の川上から打上" },
    { id: "edogawa", name: "江戸川区花火大会",             pref: "東京都",  lat: 35.7126, lng: 139.9066, shell: "7",  note: "江戸川河川敷（篠崎公園先）" },
    { id: "jingu",   name: "神宮外苑花火大会",             pref: "東京都",  lat: 35.6753, lng: 139.7174, shell: "4",  note: "神宮球場・秩父宮ラグビー場" },
    { id: "nagaoka", name: "長岡まつり大花火大会",         pref: "新潟県",  lat: 37.4455, lng: 138.8355, shell: "30", note: "信濃川河川敷・正三尺玉で有名" },
    { id: "omagari", name: "大曲の花火（全国花火競技大会）", pref: "秋田県",  lat: 39.4440, lng: 140.4590, shell: "10", note: "雄物川河畔" },
    { id: "suwa",    name: "諏訪湖祭湖上花火大会",         pref: "長野県",  lat: 36.0530, lng: 138.1063, shell: "10", note: "諏訪湖上（初島）から打上・周囲は山" },
    { id: "atami",   name: "熱海海上花火大会",             pref: "静岡県",  lat: 35.0930, lng: 139.0798, shell: "7",  note: "熱海湾の海上から打上" },
    { id: "biwako",  name: "びわ湖大花火大会",             pref: "滋賀県",  lat: 35.0110, lng: 135.8705, shell: "10", note: "大津港沖の湖上" },
    { id: "yodogawa",name: "なにわ淀川花火大会",           pref: "大阪府",  lat: 34.7148, lng: 135.4886, shell: "10", note: "淀川河川敷（十三側）" },
    { id: "tenjin",  name: "天神祭奉納花火",               pref: "大阪府",  lat: 34.7050, lng: 135.5230, shell: "4",  note: "桜之宮公園・川崎公園周辺" },
  ];
})();
