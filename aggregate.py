import re
import datetime
import calendar

# 4段階目アンケート結果の読み込み
# 「{'1物': ['player1', 'player2'], '2魔': ['player1', 'player3'], ...}」形式のdictを返却します
def import_questionnaire_phase4() -> dict:
    print('4段階目アンケート結果を読み込んでいます...')
    result = {}

    with open('#4段階目アンケート結果.txt', 'r', encoding='utf-8') as f:
        key = None
        for line in f:
            key_line = re.match('^[0-9]+\. \[(.+)\].+$', line)
            if key_line:
                # 「1. [1物]ゴブグレ」形式の行をタイトル行として読み込み
                key = key_line.group(1)
            elif key is not None:
                # タイトル行の直後の行をアンケート結果行として読み込み
                result[key] = line.rstrip(' \r?\n').split(' ')
                key = None

    # debug
    # print(result)

    return result

# 初日4段階目参加メンバーを取得
def import_questionnaire_first_day() -> list:
    print('初日アンケート結果を読み込んでいます...')
    result = []

    with open('#初日アンケート結果.txt', 'r', encoding='utf-8') as f:
        is_phase4_line = False
        for line in f:
            # 初日アンケートの「5. 4段階目」「6. 朝活貫通」を初日4段階目参加メンバーとしてカウントする
            key_line = re.match('^[56]\..+$', line)
            if key_line:
                is_phase4_line = True
            elif is_phase4_line:
                # 4段階目タイトル行の直後の行を4段階目参加メンバーとしてカウント
                result += line.rstrip(' \r?\n').split(' ')
                is_phase4_line = False

    return list(set(result))

# 本日の凸状況の読み込み
# 「{'player1': ['1物', '2魔', '5物'], ...}」形式のdictを返却します
def import_today_route() -> dict:
    print('本日の凸状況を読み込んでいます...')
    result = {}

    with open('#本日の凸状況.txt', 'r', encoding='utf-8') as f:
        for line in f:
            route_line = re.match('^(.+) ([1-5][物魔].+|－)/([1-5][物魔].+|－)/([1-5][物魔].+|－) .+$', line)
            if route_line:
                # プレイヤー名はアンケート結果にあわせ、utf-8換算で13byte目以降切り捨て
                key = route_line.group(1).encode('utf-8')[0:12].decode('utf-8', errors='ignore')
                # 1凸目/2凸目/3凸目の本凸先を取得
                route1 = route_line.group(2)[0:2]
                route2 = route_line.group(3)[0:2]
                route3 = route_line.group(4)[0:2]
                result[key] = [route1, route2, route3]

    # debug
    # print(result)

    return result

# 現在の周回数の読み込み
def import_current_lap() -> list:
    print('現在の周回数を読み込んでいます...')

    with open('#現在の周回数.txt', 'r', encoding='utf-8') as f:
        return [line.rstrip('\r|\n') for line in f.readlines()]

# 現在のクラバト日付（1-5日目）を取得します
def get_current_day() -> int:
    # 5:00を基準とした現在日付を取得します
    # たとえば「6/27 4:50」は6/26として扱われます
    now = (datetime.datetime.now() - datetime.timedelta(hours=5))
    # today = now.day
    # ★debug
    today = 27
    _, lastday = calendar.monthrange(now.year, now.month)

    result = today + 6 - lastday

    # debug
    # print(result)

    return result

# 凸先変更情報の読み込み
def import_route_change_info():
    print('凸先変更情報を読み込んでいます...')
    return {}

questionnaire_phase4 = import_questionnaire_phase4()
questionnaire_first_day = import_questionnaire_first_day()
temporary_route = import_route_change_info()
today_route = import_today_route()
current_lap = import_current_lap()
current_day = get_current_day()

# 以下デバッグ



