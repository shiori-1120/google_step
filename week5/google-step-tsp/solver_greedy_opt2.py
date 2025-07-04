#!/usr/bin/env python3

import sys
import math
import codecs
import random

from common import print_tour, read_input

# 2点間の距離を測る
def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def generate_dist_list(cities):
    N = len(cities)
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    
    return dist

# 貪欲法
def greedy(cities, dist):
    # N次元配列に各点の距離を入れていく
    N = len(cities)

    # 今いるcityを初期化
    current_city = 0
    # 訪れていないcityをsetにいれる
    unvisited_cities = set(range(1, N))
    # ここに道順を入れる
    tour = [current_city]

    # 訪れていないcityが無くなるまで繰り返す
    while unvisited_cities:
        # 今いるcityから一番距離が近いcityを次の行き先に指定
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        # setから訪れたcityを削除
        unvisited_cities.remove(next_city)
        # 道順に次のcityを追加
        tour.append(next_city)
        # 今いるcityを更新
        current_city = next_city
        
    return tour

# 挿入法
# 新しい都市を今の順回路のどこに入れるのがいいか計算
def insertion(cities, dist):
    # N次元配列に各点の距離を入れていく
    N = len(cities)

    # 初期設定
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]
    
    # 初期パスを作成
    next_city = min(unvisited_cities,key=lambda city: dist[current_city][city])
    unvisited_cities.remove(next_city)
    tour.append(next_city)
    count=0
    # 次の順路が一番短くなるところに挿入する
    while unvisited_cities:
        # print('insertion')
        # 近くの都市を選ぶ(index)
        next_city = min(unvisited_cities, key=lambda city: dist[current_city][city])
        # setから訪れたcityを削除
        unvisited_cities.remove(next_city)
        
        # [i番目の後に入れる, i → next → i+1の長さ]
        min_diff = [None, float('inf')]
        
        for i in range(len(tour)-1):
            new_dist = dist[tour[i]][next_city] + dist[next_city][tour[i+1]]
            if min_diff[1] > new_dist:
                min_diff = [i, new_dist]
        
        # 間に挿入する
        tour.insert(min_diff[0], next_city)
        # if count%100 ==0:
        #     tour = two_opt(tour, dist)
        
        # 更新
        current_city = next_city
        
    return tour
# 2-optを実装
def random_two_opt(tour, dist):
    N = len(tour)
    new_tour = tour
    count = 0
    while not count > 1e3:
        print("距離",calculate_cost(new_tour, dist), count)
        # ランダムに二つ選ぶ
        # 0 ~ len(tour)-1 最初から最後まで
        i_1 = random.randint(0, len(tour)-1)
        j_1 = random.randint(0, len(tour)-1)
        while abs(i_1 - j_1) < 2:
            j_1 = random.randint(0, len(tour)-1)
            
        if i_1 == len(tour)-1:
            i_2 = 0
        else:
            i_2 = i_1 + 1
            
        if j_1 == len(tour)-1:
            j_2 = 0
        else:
            j_2 = j_1 + 1
        # 今の距離と、その2つの間を入れ替えた時の距離を測る
        curr_dist = dist[new_tour[i_1]][new_tour[i_2]] + dist[new_tour[j_1]][new_tour[j_2]]
        update_dist = dist[new_tour[i_1]][new_tour[j_1]] + dist[new_tour[i_2]][new_tour[j_2]]
        # print(curr_dist, update_dist)
        # 入れ替えた時に距離が短くなるなら入れ替える
        if curr_dist > update_dist:
            new_tour[i_2:j_2] = new_tour[i_2:j_2][::-1]
            print("距離",calculate_cost(new_tour, dist), count)
        count += 1
    
    return new_tour

# 2-optを実装
def two_opt(tour, dist):
    N = len(tour)
    new_tour = tour
    
    complete = False
    # ある程度ループが回った時、無限ループを検知する
    # （無限ループでなくとも同じところを入れ替えようとしたら終了する）
    loop_check = []
    count = 0
    while not complete:
        if count%10 == 0:
            new_tour = random_two_opt(new_tour, dist)
        print("距離",calculate_cost(new_tour, dist), count)
        # 以下の操作を入れ替えて短くなるところがなくなるまで繰り返す
        tmp = new_tour
        complete = True
        # tourの最初から2つずつ選ぶ(0, 1), (1, 2), (2, 3), ..., (N-4, N-3)
        # その次の2つを選ぶ(2, 3), (3, 4), (4, 5), ..., (N-2, N-1)
        for i in range(N-2):
            for j in range(i+2, N-1):
                # 今の距離と、その2つの間を入れ替えた時の距離を測る
                curr_dist = dist[new_tour[i]][new_tour[i+1]] + dist[new_tour[j]][new_tour[j+1]]
                update_dist = dist[new_tour[i]][new_tour[j]] + dist[new_tour[i+1]][new_tour[j+1]]
                # 入れ替えた時に距離が短くなるなら入れ替える
                if curr_dist > update_dist:
                    tmp = new_tour[i+1:j+1][::-1]
                    new_tour[i+1:j+1] = tmp
                    complete = False
                    count += 1
                    if count >2*N:
                        # print("十分にループが回っています", count)
                        if [i+1, j+1] in loop_check:
                            return new_tour
                        else:
                            loop_check.append([i+1, j+1])
                    break
            if not complete:
                break
        if complete:
            # 最初と最後と交わってるところがあるかどうか
            for i in range(1, N-2):
                curr_dist = dist[new_tour[0]][new_tour[N-1]] + dist[new_tour[i]][new_tour[i+1]]
                update_dist = dist[new_tour[0]][new_tour[i]] + dist[new_tour[N-1]][new_tour[i+1]]
                # 入れ替えた時に距離が短くなるなら入れ替える
                if curr_dist > update_dist:
                    tmp = new_tour[i+1:][::-1]
                    new_tour[i+1:] = tmp
                    complete = False
                    count += 1
                    if count >2*N:
                        # print("十分にループが回っています", count)
                        if [i+1, N-1] in loop_check:
                            return new_tour
                        else:
                            loop_check.append([i+1, N-1])
                    break
    return new_tour


# 2-optを実装
def three_opt(tour, dist):
    pass

# 焼きなまし法
def simulated_annealing(tour, dist):
    current_tour = tour # 初期パス
    current_cost = calculate_cost(current_tour, dist)
    best_tour = current_tour # 見つけた中で一番良い解を保存
    best_cost = current_cost
    alpha = 0.99

    initial_temp = current_cost * 0.1
    temperature =  initial_temp# 初期温度

    while temperature > initial_temp*1e-4: # 最終的な温度より大きいとき繰り返す
        print(temperature)
        print('距離', calculate_cost(best_tour , dist))
        # 各温度での繰り返し回数 (inner_loop_iterations) だけ近傍探索を行う
        for _ in range(len(tour)):
            # (A) 近傍解の生成
            new_tour = two_opt(current_tour, dist)
            new_cost = calculate_cost(current_tour, dist)
            # (B) 新しい解の評価
            delta_e = new_cost - current_cost
            # print("delta_e", delta_e)
            # (C) 受容判定と解の更新
            p = math.exp(-delta_e/temperature)
            # print("p", p)
            # (D) 最良解の更新 (オプションだが重要)
            if random.random() < p:
                best_tour = new_tour
                best_cost = new_cost
            
        current_tour = new_tour
        current_cost = new_cost
        # 温度の降下
        temperature = temperature * alpha
    return best_tour

# 今のパスの距離を返す
def calculate_cost(tour, dist):
    path_len = 0
    for i in range(len(tour)-1):
        path_len += dist[tour[i]][tour[i+1]]
    path_len += dist[tour[0]][tour[-1]]
    
    return path_len

def solve(cities):
    dist = generate_dist_list(cities)
    
    tour = insertion(cities, dist)
    print('finish insertion')
    print(calculate_cost(tour, dist))
    # tour = simulated_annealing(tour, dist)
    tour = two_opt(tour, dist)
    print(len(tour))
    print(calculate_cost(tour, dist))
    return tour

def divide_solve(cities):
    dist = generate_dist_list(cities)
    
    #分割して解く
    tour_1, tour_2, tour_3, tour_4 = [], [], [], []
    c_1, c_2, c_3, c_4 = [], [], [], []
    i_1, i_2, i_3, i_4 = [], [], [], []
    max_x = max_x = max(city[0] for city in cities)
    max_y = max_x = max(city[1] for city in cities)
    # print(max_x)
    # print(max_y)
    
    for i in range(len(cities)):
        cities
        # 右上
        if max_x/2 <= cities[i][0] and max_y/2 <= cities[i][1]:
            c_1.append(cities[i])
            i_1.append(i)
        # 左上
        elif 0 <= cities[i][0] <= max_x/2 and max_y/2 <= cities[i][1]:
            c_2.append(cities[i])
            i_2.append(i)
        # 左下
        elif 0 <= cities[i][0] <= max_x/2 and  0 <= cities[i][1] <= max_y/2:
            c_3.append(cities[i])
            i_3.append(i)
        # 右下
        elif max_x/2 <= cities[i][0] and 0 <= cities[i][1] <= max_y/2:
            c_4.append(cities[i])
            i_4.append(i)
    
    dist_1 = generate_dist_list(c_1)
    dist_2 = generate_dist_list(c_2)
    dist_3 = generate_dist_list(c_3)
    dist_4 = generate_dist_list(c_4)
    
    print('1', len(c_1))
    tour_1 = insertion(c_1, dist_1)
    tour_1 = two_opt(tour_1 ,dist_1)
    print('2',len(c_2))
    tour_2 = insertion(c_2, dist_2)
    tour_2 = two_opt(tour_2 ,dist_2)
    print('3', len(c_3))
    tour_3 = insertion(c_3, dist_3)
    tour_3 = two_opt(tour_3 ,dist_3)
    print('4',len(c_4))
    tour_4 = insertion(c_4, dist_4)
    tour_4 = two_opt(tour_4 ,dist_4)

    print('here')
    
    new_tour_1 = []
    for x in tour_1:
        new_tour_1.append(i_1[x])
        
    new_tour_2 = []
    for x in tour_2:
        new_tour_2.append(i_2[x])
        
    new_tour_3 = []
    for x in tour_3:
        new_tour_3.append(i_3[x])
        
    new_tour_4 = []
    for x in tour_4:
        new_tour_4.append(i_4[x])
    
    print('here2')
    # tour = simulated_annealing(cities, dist)
    tour = new_tour_1 + new_tour_2 + new_tour_3 + new_tour_4
    tour = two_opt(tour, dist)
    print(len(tour))
    print(calculate_cost(tour, dist))
    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print(*['index']+tour, sep="\n", file=codecs.open('output.csv', 'w', 'utf-8'))
    # print_tour(tour)
    
