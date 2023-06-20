import re
import csv
import datetime
import calendar

# 4段階目ボスのHP
boss_hp = [
    20000,
    21000,
    23000,
    24000,
    25000,
]

def import_questionnaire_phase4(expect_damages: dict) -> list:
    """
    4段階目アンケート結果の読み込み

    Args:
        expect_damages (dict): 各ボスの想定ダメージ
    Returns:
        list: [['1魔', 'player1'], ['2物', 'player2'], ...]
    """
    print('4段階目アンケート結果を読み込んでいます...')
    result = []

    with open('#4段階目アンケート結果.txt', 'r', encoding='utf-8') as f:
        is_player_line = False
        for line in f:
            key_line = re.match('^[0-9]+\..*\[([1-5][物魔])\].+$', line)
            if key_line:
                # 「1. ゴブグレ[1物]」形式の行をタイトル行として読み込み
                boss = key_line.group(1)
                is_player_line = True
            elif is_player_line:
                # タイトル行の直後の行をアンケート結果行として読み込み
                result += [[boss, player, expect_damages[boss]] for player in line.rstrip(' \r?\n').split(' ')]
                is_player_line = False

    # debug
    # print(result)

    return result

def import_questionnaire_first_day() -> list:
    """
    初日4段階目参加メンバーを取得

    Returns:
        list: ['player1', 'player2']
    """
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

def import_today_route() -> list:
    """
    本日の凸状況の読み込み

    Returns:
        list: [['player1', '1物'], ...}
    """
    print('本日の凸状況を読み込んでいます...')
    result = []

    with open('#本日の凸状況.txt', 'r', encoding='utf-8') as f:
        for line in f:
            route_line = re.match('^(.+) ([1-5][物魔].+|－)/([1-5][物魔].+|－)/([1-5][物魔].+|－) .+$', line)
            if route_line:
                # プレイヤー名はアンケート結果にあわせ、utf-8換算で13byte目以降切り捨て
                player = route_line.group(1).encode('utf-8')[0:12].decode('utf-8', errors='ignore')
                # 1凸目/2凸目/3凸目の本凸先を取得
                route1 = route_line.group(2)[0:2]
                if route1 != '－':
                    result += [[player, route1]]
                
                route2 = route_line.group(3)[0:2]
                if route2 != '－':
                    result += [[player, route2]]

                route3 = route_line.group(4)[0:2]
                if route3 != '－':
                    result += [[player, route3]]

    return result

def import_current_lap() -> list:
    """
    現在の周回数の読み込み

    Returns:
        list: [30.2, 31.0, ...]
    """
    print('現在の周回数を読み込んでいます...')

    with open('#現在の周回数.txt', 'r', encoding='utf-8') as f:
        return [float(line.rstrip('\r|\n')) for line in f.readlines()]

def get_current_day() -> int:
    """
    現在のクラバト日付（1-5日目）を取得します

    Returns:
        int: 1-5
    """
    # 5:00を基準とした現在日付を取得します
    # たとえば「6/27 4:50」は6/26として扱われます
    now = (datetime.datetime.now() - datetime.timedelta(hours=5))
    today = now.day

    # 今月最終日を取得します
    # たとえば6月の場合、30を取得します
    _, lastday = calendar.monthrange(now.year, now.month)

    # 現在日付と今月最終日から、クラバト日付を取得します
    result = today + 6 - lastday

    return result

def import_route_change_info():
    """
    凸先変更情報の読み込み

    Returns:
        list: [[2, 'player1', '2物', '3物'], [3, 'player2', '2物', '3物']]
    """
    result = []

    print('凸先変更情報を読み込んでいます...')

    with open('#凸先変更情報.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            c_line = re.match('^([1-5]) ([^ ]+) ([1-5][物魔]) ([1-5][物魔])$', line)
            if c_line:
                day = int(c_line.group(1))
                player = c_line.group(2)
                before = c_line.group(3)
                after = c_line.group(4)
                result += [[day, player, before, after]]
            elif line[0] != '#':
                print(f'[WARN]読み込みスキップ: {line}')
        
        return result

def import_expect_damages() -> dict:
    """
    各編成の平均ダメージの読み込み

    Returns:
        dict: {'1物': 5800, '2物': 4800}
    """
    print('各編成の平均ダメージを読み込んでいます...')

    with open('#各編成の平均ダメージ.txt', 'r', encoding='utf-8') as f:
        return {line[:2]: int(line[3:].rstrip('\r|\n')) for line in f.readlines() if re.match('^[1-5][物魔] [0-9]+$', line)}
 
def get_expects(current_day: int) -> list:
    """
    凸予定情報を作成します

    Args:
        current_day (int): 現在のクラバト日付(1-5)
    Returns:
        list: [[1, '1魔', 'player1'], [1, '2物', 'player2'], ...]
    """
    result = []

    # 各編成の平均ダメージの読み込み
    expect_damages = import_expect_damages()
    # 4段階目アンケート結果の読み込み
    questionnaire_phase4 = import_questionnaire_phase4(expect_damages)

    if current_day == 1:
        # クラバト初日の場合、初日4段階目参加メンバーを取得
        questionnaire_first_day = import_questionnaire_first_day()

        # 初日4段階目予定を結果リストに追加
        for player in questionnaire_first_day:
            result += [[1] + phase4 + [''] for phase4 in questionnaire_phase4 if phase4[1] == player]
        
    # 現在のクラバト日付以降の4段階目凸予定を結果リストに追加
    for day in range(max(current_day, 2), 6):
        result += [[day] + phase4 + [''] for phase4 in questionnaire_phase4]

    # 凸先変更情報の読み込み
    route_change_info = import_route_change_info()
    # 凸先変更情報の反映
    for change in route_change_info:
        org_exists = False
        for org in result:
            # クラバト日付、プレイヤー名、変更前凸先が存在する場合
            # org[day, boss, player, damage]
            # change[day, player, before(boss), after(boss)]
            if org[0] == change[0] and org[2] == change[1] and org[1] == change[2]:
                # 凸予定を書き換え
                org[1] = change[3] # 凸先
                org[3] = expect_damages[org[1]]
                org_exists = True
                break
        if not org_exists:
            print(f'[WARN]変更前の凸予定が存在しません. #凸先変更情報.txtの内容を確認してください: {change}')

    return result

def get_results(expects: list, actuals: list) -> list:
    for actual in actuals:
        expect_exists = False
        for expect in expects:
            # 凸予定と凸実績を突合する
            # expect[day, boss, player, damage]
            # actual[player, boss]
            if expect[0] == current_day and expect[2] == actual[0] and expect[1] == actual[1]:
                expect[4] = '済'
                expect_exists = True
                break
        if not expect_exists:
            print(f'[WARN]凸予定にない凸実績が存在します. 各テキストファイルの内容を確認してください. 実績: {actual}')
    
    expects.sort(key = lambda x: x[4])

    return expects

def aggregate_today(results: list, current_day: int, current_lap: list, boss_hp: list) :
    # [1, '1魔', 'player1', 5600, '済']
    aggregate_results = [0, 0, 0, 0, 0]
    for result in results:
        if result[0] == current_day and result[4] == '':
            aggregate_results[int(result[1][0]) -1] += result[3]

    return [round(aggregate_results[i] / boss_hp[i], 1) + current_lap[i] for i in range(0, 5)]

def aggregate_all(results: list, current_lap: list, boss_hp: list) :
    # [1, '1魔', 'player1', 5600, '済']
    aggregate_results = [0, 0, 0, 0, 0]
    for result in results:
        if result[4] == '':
            aggregate_results[int(result[1][0]) -1] += result[3]

    return [round(aggregate_results[i] / boss_hp[i], 1) + current_lap[i] for i in range(0, 5)]

################################################################################
# 処理本体
################################################################################
# 現在のクラバト日付を取得
current_day = get_current_day()
# 本日以降の凸予定リストを取得
expects = get_expects(current_day)
# 本日の凸実績を取得
actuals = import_today_route()
# 現在周回数を取得
current_lap = import_current_lap()

# 全日程の凸消化状況を取得
results = get_results(expects, actuals)

# 本日着地見込みを取得
aggregate_today_result = aggregate_today(results, current_day, current_lap, boss_hp)
# 最終着地見込みを取得
aggregate_all_result = aggregate_all(results, current_lap, boss_hp)

print()
with open('本日凸消化状況.csv', 'w') as f:
    print('本日凸消化状況.csvを出力しました.')
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows([result for result in results if result[0] == current_day])

with open('全日程凸消化状況.csv', 'w') as f:
    print('全日程凸消化状況.csvを出力しました.')
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(results)

print()
print(f'本日着地見込み: {aggregate_today_result}')
print(f'最終着地見込み: {aggregate_all_result}')
