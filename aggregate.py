import re

# 4段階目アンケート結果の読み込み
# 「{'1物': ['player1', 'player2'], '2魔': ['player1', 'player3'], ...}」形式のdictを返却します
def import_questionnaire_phase4() -> dict:
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

    return result

# 初日アンケート結果の読み込み
def import_questionnaire_first_day():
    return {}

# 臨時対応状況の読み込み
def import_temporary_route():
    return {}

# 本日の凸状況の読み込み
# 「{'player1': ['1物', '2魔', '5物'], ...}」形式のdictを返却します
def import_today_route() -> dict:
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

    return result

# 現在の周回数の読み込み
def import_current_lap():
    with open('#現在の周回数.txt', 'r', encoding='utf-8') as f:
        return [line.rstrip('\r|\n') for line in f.readlines()]
        
print('4段階目アンケート結果を読み込んでいます...')
questionnaire_phase4 = import_questionnaire_phase4()

print('初日アンケート結果を読み込んでいます...')
questionnaire_first_day = import_questionnaire_first_day()

print('臨時対応状況を読み込んでいます...')
temporary_route = import_temporary_route()

print('本日の凸状況を読み込んでいます...')
today_route = import_today_route()

print('現在の周回数を読み込んでいます...')
current_lap = import_current_lap()

# 以下デバッグ
print()
print('本日の凸状況')
# print(today_route)

print()
print('4段階目アンケート結果')
print(questionnaire_phase4)

print()
print('現在の周回数')
# print(current_lap)

