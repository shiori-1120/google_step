#!/usr/bin/env python3

import sys
import math
import codecs

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

# 2-optを実装
def two_opt(tour, dist):
    N = len(tour)
    
    complete = False
    loop_check = []
    counter = 0
    while not complete:
        print(loop_check)
    # 以下の操作を入れ替えて短くなるところがなくなるまで繰り返す
        complete = True
        # tourの最初から2つずつ選ぶ(0, 1), (1, 2), (2, 3), ..., (N-4, N-3)
        # その次の2つを選ぶ(2, 3), (3, 4), (4, 5), ..., (N-2, N-1)
        for i in range(N-2):
            for j in range(i+2, N-1):
                # 今の距離と、その2つの間を入れ替えた時の距離を測る
                curr_dist = dist[tour[i]][tour[i+1]] + dist[tour[j]][tour[j+1]]
                update_dist = dist[tour[i]][tour[j]] + dist[tour[i+1]][tour[j+1]]
                # 入れ替えた時に距離が短くなるなら入れ替える
                if curr_dist > update_dist + 1e-9:
                    print(i+1, j+1)
                    tour[i+1:j+1] = tour[i+1:j+1][::-1]
                    complete = False
                    counter += 1
                    if counter > N:
                        if [i+1, j+1] in loop_check:
                            return tour
                        else:
                            loop_check.append([i+1, j+1])
                    break
            if not complete:
                break
        if complete:
            # 最初と最後と交わってるところがあるかどうか
            for i in range(1, N-2):
                curr_dist = dist[tour[0]][tour[N-1]] + dist[tour[i]][tour[i+1]]
                update_dist = dist[tour[0]][tour[i]] + dist[tour[N-1]][tour[i+1]]
                # 入れ替えた時に距離が短くなるなら入れ替える
                if curr_dist > update_dist:
                    print(i+1, N-1)
                    tour[i+1:N-1] = tour[i+1:N-1][::-1]
                    complete = False
                    counter += 1
                    if counter > N:
                        if [i+1, j+1] in loop_check:
                            return tour
                        else:
                            loop_check.append([i+1, N-1])
                    break
    
    return tour

def solve(cities):
    dist = generate_dist_list(cities)
    
    tour = greedy(cities, dist)
    tour = two_opt(tour ,dist)
    
    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print(*['index']+tour, sep="\n", file=codecs.open('output.csv', 'w', 'utf-8'))
    print_tour(tour)
