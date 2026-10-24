# Freebie Board

A page that lists free PC games, DLC, loot, drops and playtests you can claim right now.

- **Live page:** https://xxld.github.io/freebie-board/
- **Data:** Epic's free-games feed (Germany), the [GamerPower](https://www.gamerpower.com/) giveaway API and a hand-checked list in `extra.json` (Prime Gaming, GOG, Steam, itch.io, Twitch drops and more). A GitHub Action rebuilds `data.js` every day at about 06:17 UTC and whenever `extra.json` changes.
- **Region:** the Epic list is for Germany and some offers are region-locked or need a Prime membership. Mark the ones that do not work for you with "Can't claim".
- **Your ticks** (claimed, can't claim) and the store filter are saved in your own browser only.
- **Add your own offers:** put them in `extra.json` as `[{"title":"...","store":"...","kind":"game","url":"https://..."}]`.
- **Run it yourself:** `python update.py`, then open `index.html`.
- **Epic region:** change `COUNTRY` at the top of `update.py`.

No accounts, keys or secrets are used.
