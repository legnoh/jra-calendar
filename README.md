# jra-calendar

- **https://jra.event.lkj.io/graderaces.ics**
  - 全情報入り: https://jra.event.lkj.io/graderaces.ics
    - JRA国内競争のみ: https://jra.event.lkj.io/graderaces_jra.ics
    - NARダートグレード競争のみ: https://jra.event.lkj.io/graderaces_dirtgrade.ics
    - 日本馬参加の海外競争のみ: https://jra.event.lkj.io/graderaces_overseas.ics
  - 全情報入り(JSON): https://jra.event.lkj.io/graderaces.json
    - JRA国内競争のみ(JSON): https://jra.event.lkj.io/graderaces_jra.json
    - NARダートグレード競争のみ(JSON): https://jra.event.lkj.io/graderaces_dirtgrade.json
    - 日本馬参加の海外競争のみ(JSON): https://jra.event.lkj.io/graderaces_overseas.json

[![Netlify Status](https://api.netlify.com/api/v1/badges/1813c971-2e32-4d0f-844b-e8e9a8a95c67/deploy-status)](https://app.netlify.com/sites/jra-calendar/deploys)

<img width="600" alt="sample" src="https://github.com/user-attachments/assets/c672a941-a698-4544-b6ba-9cd288d9fe03" />

- 中央競馬とダートグレード競走と日本馬参加の海外競走の開催予定カレンダーです。
  - 外部カレンダーなどで登録することで、自動的にカレンダーを読み込めます。
    - iCloud: [iCloud の照会カレンダーを使う - Apple サポート (日本)](https://support.apple.com/ja-jp/HT202361)
    - Googleカレンダー: [リンクを使用して一般公開のカレンダーを追加する \- Google カレンダー ヘルプ](https://support.google.com/calendar/answer/37100?hl=ja&co=GENIE.Platform%3DDesktop#:~:text=リンクを使用して一般公開のカレンダーを追加する)
- JRA, NAR提供のものに比べ、以下の利点があります。
  - 確定している発走時刻を自動で取得し、発走時刻にイベント時刻を合わせます。
  - 公式サイトの分析ページのURL、NetkeibaのURL、地方競馬の配信URLなど、さまざまな情報にリンクしやすくなります。

## Disclaim / 免責事項

- 当スクリプトは、JRA、並びにNARからは非公認のものです。
  - これらを利用したことによるいかなる損害についても当方では責任を負いかねます。
- 当スクリプトはこれらのサイトに対し、負荷をかけることを目的として制作したものではありません。
  - 利用の際は常識的な範囲でのアクセス頻度に抑えてください。
- 先方に迷惑をかけない範囲での利用を強く推奨します。
- 全データは取得できる最古のものを取得していますが、先方の更新によってデータが失われることがあります。
