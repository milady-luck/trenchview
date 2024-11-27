from datetime import datetime

from trenchview.custom_types import CoinCall, UnparsedRickbotCall
from trenchview.parsing import (
    ParsedCoinCallResp,
    find_ticker,
    parse_coin_call,
    parse_coin_call_resp,
)


class TestFindTicker:
    def test_single_dollar(self):
        ticker_line = "foo bar $WIF"
        ticker = find_ticker(ticker_line)
        assert ticker == "WIF"

    def test_multi_dollar(self):
        for i in range(10):
            prefix = "$" * i
            ticker = find_ticker(f"foo bar ${prefix}WIF")
            assert ticker == prefix + "WIF"


class TestRickRespParse:
    def test_k_fdv(self):
        s = """🔥 I CHOOSE RICH EVERYTIME! [694.0K/53.3K%] $NICK
🌐 Solana @ Raydium
💰 USD: $0.0006939
💎 FDV: $694.0K 
💦 Liq: $44.7K [x31.0] 
📊 Vol: $318K 🕰️ Age: 1h
⛰️ ATH: $694.0K 
🚀 1H: 3.1K% | $280.3K 🅑 1161 🅢 809
👥 TH: 5.0 | 5.0 | 3.4 | 3.4 | 3.4 [37%]
🖨️ Mint: ✅ | LP: 🔥

G3q2zUkuxDCXMnhdBPujjPHPw9UTMDbXqzcc2UHM3jiy
BAN | BNK | DEX | BRD | DT | JUP | RAY
UNI | STB | PHO | EXP | RUG | SOC | TW
CAL | MNZ | MAG | ORC | FLX | SRM

🏆 [redacted] @ 15.6K 👀 211
⚔️ TIP: Farm Cambria Duel Arena"""
        parsed = parse_coin_call_resp(s)
        expected = ParsedCoinCallResp(
            "NICK", "Solana", 694_000.0, "G3q2zUkuxDCXMnhdBPujjPHPw9UTMDbXqzcc2UHM3jiy"
        )

        assert parsed == expected

    def test_m_fdv(self):
        s = """💊 Nailong [25.7M/52.1%] $NAILONG 🔼
🌐 Solana @ Raydium
💰 USD: $0.02571
💎 FDV: $25.7M 
💦 Liq: $1.1M 🐡 [x46.5] 
📊 Vol: $3M 🕰️ Age: 1mo
⛰️ ATH: $27.8M [6d ago] 
📈 1H: 38.9% ⋅ $658K 🅑 251 🅢 382
👥 TH: 2.3⋅2.1⋅2.1⋅2.1⋅1.8 [18%]
🖨️ Mint: ✅ ⋅ LP: 🔥
🧰 More: 📊 🫧 🎨 💪 💬 🌍 🐦 [♺]

mkvXiNBpa8uiSApe5BrhWVJaT87pJFTZxRy7zFapump
MAE⋅BAN⋅BNK⋅SHU⋅PEP⋅MVX⋅DEX
TRO⋅STB⋅PHO⋅BLX⋅GMG⋅EXP⋅TW

🏆 lasercat397 @ 1.3M⋅19x⋅1mo 👀 8.6K
📈 TIP: Trade pump.fun on Photon"""
        parsed = parse_coin_call_resp(s)
        expected = ParsedCoinCallResp(
            "NAILONG",
            "Solana",
            25_700_000.0,
            "mkvXiNBpa8uiSApe5BrhWVJaT87pJFTZxRy7zFapump",
        )

        assert parsed == expected

    def test_b_fdv(self):
        s = """🟡 dogwifhat [1.7B/-0.7%] $$WIF 🔼
🌐 Solana @ Orca Wp
💰 USD: $1.75
💎 FDV: $1.7B 
� Liq: $1.7M 🐡 [x2033.5] 
�📊 Vol: $24M 🕰️ Age: 4mo
⛰️ ATH: $3.4B [3mo ago] 
📉 1H: -0.9% ⋅ $664.6K 🅑 682 🅢 624
🖨️ Mint: ✅ | LP: ‼️
🧰 More: 📊 🫧 💪 💬 TG⋅X⋅WEB

EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm
MAE⋅BAN⋅BNK⋅SHU⋅PEP⋅DEX⋅BRD
TRO⋅STB⋅PHO⋅BLX⋅EXP⋅RUG⋅TW

🏆 rightcalibre @ 1.7B⋅2mo 👀 1950  # noqa: W29150
📢 AD: Snipe, trade & win 10 $SOL - DEX3"""
        parsed = parse_coin_call_resp(s)
        expected = ParsedCoinCallResp(
            "$WIF",
            "Solana",
            1_700_000_000,
            "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        )

        assert parsed == expected

    def test_missed_coins(self):
        s1 = """💊 SIGMA - $SIGMA
💎 FDV: 69.7M ✅ 🕰️ 4mo ⋅ 👑
👀 Hits: 66 ⋅ last seen: 1mo
💬 Comments: 303 ⋅ last reply: 1h
🧑‍💻 sigmaonsol ⋅ TG ⋅ 𝕏 [♺] ⋅ Web ⋅ /dp: ✅
🧬 $BETA [474K] ⋅ $PBJ ⋅ $STICKY ⋅ $BAG [21]
👥 TH: 2.3⋅1.8⋅1.6⋅1.5⋅1.4 [14%]
🧰 More: 🫧 🎨

5SVG3T9CNQsm2kEwzbRq6hASqh1oGfjqTtLXYUibpump
MAE⋅BAN⋅BNK⋅SHU⋅PEP⋅MVX⋅DEX
TRO⋅STB⋅PHO⋅BLX⋅GMG⋅EXP⋅TW
"""
        # TODO: change these tests to deduce chain from ca
        parsed = parse_coin_call_resp(s1)
        expected = ParsedCoinCallResp(
            "SIGMA", None, 69_700_000, "5SVG3T9CNQsm2kEwzbRq6hASqh1oGfjqTtLXYUibpump"
        )
        assert parsed == expected

        s2 = """💊 PopipoPopipoPopipoPo.. - $POPIPO
💎 FDV: 95.7K 🕰️ 13m ⋅ 👑
👀 Hits: 46 🔥 #4 ⋅ last seen: 1s
💬 Comments: 43 ⋅ last reply: 2m
🧑‍💻 DEV ⋅ /dp: No
🧬 $DWD [1]
👥 TH: 6.3⋅4.2⋅3.9⋅3.2⋅3.1 [31%]
🧰 More: 🫧 🎨

vdK7t1fBTYJFkxizPWpgGZS5RCsw4yGmT4AXsR6pump
MAE⋅BAN⋅BNK⋅SHU⋅PEP⋅MVX⋅DEX
TRO⋅STB⋅PHO⋅BLX⋅GMG⋅EXP⋅TW

💨 You are first in this chat @ 95.7K
🚀 TIP: Trade faster with Photon
"""
        parsed = parse_coin_call_resp(s2)
        expected = ParsedCoinCallResp(
            "POPIPO", None, 95_700, "vdK7t1fBTYJFkxizPWpgGZS5RCsw4yGmT4AXsR6pump"
        )
        assert parsed == expected

    def test_base_ca(self):
        s = """🟢 Dolphin Zone [1.5M/-51.3%] $EEEEEEEEE 🔼
🌐 Base @ Uniswap V3
💰 USD: $0.00001469
💎 FDV: $1.5M 
💦 Liq: $532K [x5.5] 
📊 Vol: $869K 🕰️ Age: 3d
⛰️ ATH: $5M [1d ago] 
📈 1H: 15% ⋅ $33.4K 🅑 26 Ⓢ 27
🧰 More: 📊 🫧 🎨 💪 💬 SOC

SIM: ✅ ⋅ HP: ✅ ⋅ T: 0/0
TH: 525 ⋅ AT: 0 ⋅ GAS: 103K
TOP: 20.1⋅1.6⋅1.6⋅1.4⋅1.3⋅1.1 [31%]

0x00ddE4d2F08497bcEC6F5E0666F63e14B3a1Dab9
BAN⋅MAE⋅SGM⋅ALF⋅DEX⋅DT⋅UNI
SHU⋅PHO⋅BLX⋅GMG⋅EXP⋅TW⋅SOC

🏆 memetic_power @ 1.6M⋅2d 👀 645
💊 TIP: Try Memescope on Photon
"""
        parsed = parse_coin_call_resp(s)
        expected = ParsedCoinCallResp(
            "EEEEEEEEE", "Base", 1_500_000, "0x00ddE4d2F08497bcEC6F5E0666F63e14B3a1Dab9"
        )
        assert parsed == expected


class TestParseCoinCall:
    # E2E test that mostly serves to make sure we're running both methods properly

    def test_e2e(self):
        rickbot_msg = """💊 Nailong [25.7M/52.1%] $NAILONG 🔼
🌐 Solana @ Raydium
💰 USD: $0.02571
💎 FDV: $25.7M 
💦 Liq: $1.1M 🐡 [x46.5] 
📊 Vol: $3M 🕰️ Age: 1mo
⛰️ ATH: $27.8M [6d ago] 
📈 1H: 38.9% ⋅ $658K 🅑 251 🅢 382
👥 TH: 2.3⋅2.1⋅2.1⋅2.1⋅1.8 [18%]
🖨️ Mint: ✅ ⋅ LP: 🔥
🧰 More: 📊 🫧 🎨 💪 💬 🌍 🐦 [♺]

mkvXiNBpa8uiSApe5BrhWVJaT87pJFTZxRy7zFapump
MAE⋅BAN⋅BNK⋅SHU⋅PEP⋅MVX⋅DEX
TRO⋅STB⋅PHO⋅BLX⋅GMG⋅EXP⋅TW

🏆 lasercat397 @ 1.3M⋅19x⋅1mo 👀 8.6K
📈 TIP: Trade pump.fun on Photon"""
        dt = datetime.now()
        caller = "milady"
        unparsed = UnparsedRickbotCall(caller, rickbot_msg, dt)

        parsed = parse_coin_call(unparsed)
        expected = CoinCall(
            caller=caller,
            ticker="NAILONG",
            chain="Solana",
            fdv=25_700_000.0,
            dt=dt,
            ca="mkvXiNBpa8uiSApe5BrhWVJaT87pJFTZxRy7zFapump",
        )

        assert parsed == expected
