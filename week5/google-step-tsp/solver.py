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
    while not count > 1e10:
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
            print("距離",calculate_cost(new_tour, dist), 'rondom')
        count += 1
    
    return new_tour

# 2-optを実装
def two_opt(tour, dist):
    N = len(tour)
    new_tour = tour
    
    complete = False
    # ある程度ループが回った時、無限ループを検知する
    # （無限ループでなくとも同じところを入れ替えようとしたら終了する）
    count = 0
    while not count > 5e2:
        if count%5 == 0:
            new_tour = random_two_opt(new_tour, dist)
        print(*['index']+new_tour, sep="\n", file=codecs.open('output.csv', 'w', 'utf-8'))
        print("距離",calculate_cost(new_tour, dist), count)
        # 以下の操作を入れ替えて短くなるところがなくなるまで繰り返す
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
                    new_tour[i+1:j+1] = new_tour[i+1:j+1][::-1]
                    complete = False
                    count += 1
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
                    new_tour[i+1:] = new_tour[i+1:][::-1]
                    complete = False
                    count += 1
                    break
    return new_tour

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
    tour = random_two_opt(tour, dist)
    print(len(tour))
    print(calculate_cost(tour, dist))
    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print(*['index']+tour, sep="\n", file=codecs.open('output.csv', 'w', 'utf-8'))
    # print_tour(tour)
    
