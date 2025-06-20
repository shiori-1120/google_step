# グラフ探索アルゴリズムの宿題

## 宿題1: 最短経路の探索

`find_shortest_path()` 関数を実装し、あるページから別のページへの最短経路を出力する。例えば「渋谷」から「小野妹子」への到達経路を考える。

**ヒント:**

* BFS (幅優先探索) を工夫して最短経路を導き出す。
* `collections.deque` を使うとスタックやキューを簡単に作成できる。

### 実装

#### `find_shortest_path` 関数

```python
    def find_shortest_path(self, start, goal):
        start_id, goal_id = self.find_start_goal_id(start, goal)
                
        id_shortest_path = self.bfs(start_id, goal_id)
        title_shortest_path = self.id_to_title_path(id_shortest_path)
        print(title_shortest_path)
        
        return id_shortest_path
```

#### `bfs` 関数

```python
    def bfs(self, start_id, goal_id):
        path_dict = {}
        q = collections.deque()
        visited = set()
        
        q.append(start_id)
        
        while q:
            new_node = q.popleft()
                
            if new_node == goal_id:
                print('found shortest path')
                path = [new_node]
                while path[-1] != start_id:
                    path += [path_dict[new_node]]
                    new_node = path_dict[new_node]
                return path[::-1]
            else:
                for child in self.links[new_node]:
                    if not child in visited:
                        q.append(child)
                        visited.add(child)
                        path_dict[child] = new_node
            
        print('cannot find shortest path')
```

**`path_dict` を使った経路の記録と復元:**

`path_dict` には通った道が記録され、これを使って逆順にたどることで最短経路を生成する。

```python
path_dict = {}
path_dict[child] = new_node

id_path = [new_node]
while id_path[-1] != start_id:
    id_path += [path_dict[new_node]]
    new_node = path_dict[new_node]
```

---

## 宿題2: ページランクの計算と人気ページの特定

`find_most_popular_pages()` 関数を実装し、ページランクを計算して重要度の高いページトップ10を求める。この宿題の意図は、スライドで言葉で説明されたアルゴリズムを自分で具体化し、コードに落とし込むことにある。


**ヒント:**

* **正しさの確認方法:** ページランクの分配と更新を何回繰り返しても「全部のノードのページランクの合計値」が一定に保たれることを確認する。一定にならない場合、何かが間違っている。
* **大規模データセットへの対応:** Largeデータセットで動かすためには $O(N + E)$ のアルゴリズムが必要だ。(ページ数: $N = 2215900$, リンク数: $E = 119006494$)
* **収束条件:** ページランクの更新が「完全に」収束するには時間がかかりすぎるため、更新が十分に少なくなったら停止させる。収束条件の例: sum({new\_pagerank}[i] - {old\_pagerank}[i])^2 < 0.01

### 実装

```python
    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        old_pagerank, new_pagerank = {}, {}
        variance = 1
        
        # すべてに初期値を渡す
        for key in self.titles.keys():
            old_pagerank[key] = 1
        
        # 収束するまで繰り返す
        while variance > 0.01:
            new_pagerank = collections.defaultdict(float)
            print('variance', variance)

            n = len(self.titles)
            
            sum_of_dangling_pageranks = 0.0 
            
            # new_pagerankにpagerankを分配していく
            for key, value in self.links.items():
                # valueがあるとき、そのpageにpagerank*0.85/len(value)で分配
                if value: 
                    for child in value:
                        new_pagerank[child] += old_pagerank[key]*0.85/len(value) 

                # valueがないとき、すべてのnodeにpagerank*1で分配
                else:
                    sum_of_dangling_pageranks += old_pagerank[key]
                    
            
            add_dangling_pageranks = sum_of_dangling_pageranks*0.85/n
            for page in self.titles.keys():
                new_pagerank[page] += 0.15 + add_dangling_pageranks
            
            print('pagerank合計', sum(new_pagerank.values()))
            
            # 収束判定
            variance = 0.0
            for key in self.titles.keys():
                variance += (new_pagerank[key] - old_pagerank[key])**2
            
            old_pagerank = new_pagerank # 更新
            
        print(variance)
        # 並び替えて上から十個もってくる
        find_most_popular_pages = sorted(new_pagerank.items(), key=lambda item: item[1], reverse=True)[:10]
        find_most_popular_pages_titles = []
        for i in range(len(find_most_popular_pages)):
            find_most_popular_pages_titles.append(self.titles[find_most_popular_pages[i][0]])
        print(find_most_popular_pages_titles)
        
        return find_most_popular_pages_titles
```

**実行結果例:**

* **small:** 
* **medium:** `['英語', 'ISBN', '2006年', '2005年', '2007年', '東京都', '昭和', '2004年', '2003年', '2000年']`
* **large:** `['英語', '日本', 'VIAF_(識別子)', 'バーチャル国際典拠ファイル', 'アメリカ合衆国', 'ISBN', 'ISNI_(識別子)', '国際標準名称識別子', '地理座標系', 'SUDOC_(識別子)']`

---

## 宿題3: できるだけ長い経路の発見

Wikipediaのグラフにおいて「渋谷」から「池袋」まで、同じページを重複して通らない、できるだけ長い経路を発見する。

「最長」経路を求めることはNP困難と呼ばれる問題であり、多項式時間の計算量では解けないことが知られている。そのため、グラフ探索アルゴリズムを工夫して「できるだけ長い」経路を発見する。

**発見した経路の長さ:**

* medium: 311261

**探索方法のアイデア:**

1.  DFSで最初の経路を探す。
2.  その経路間に、より長い別の経路がないかを探す。
3.  もしあれば、その経路に更新する。

### 実装

#### `find_longest_path` 関数 (最長経路を探索するメイン関数)

```python
    # 最長経路を探索するメイン関数
    def find_longest_path(self, start, goal):
        start_id, goal_id = self.find_start_goal_id(start, goal)

        # 最初のパス
        id_longest_path = self.dfs(start_id, goal_id)
        
        if not id_longest_path:
            print("not found.")
            return

        print("Length", len(id_longest_path))
        while True:
            path_updated = False
            current_path_length = len(id_longest_path)
            print('Length', current_path_length)
            
            for i in range(current_path_length - 1):
                count = 0
                for j in range(i + 1, current_path_length):
                    
                    # 探索時に避けるべきノードのセット
                    nodes_to_avoid = set(id_longest_path[:i] + id_longest_path[j+1:])
                    
                    tmp_path = self.find_other_path(id_longest_path[i], id_longest_path[j], nodes_to_avoid, j - i + 1)
                    if tmp_path:
                        id_longest_path = id_longest_path[:i] + tmp_path + id_longest_path[j+1:] 
                        path_updated = True
                        print('Length', len(id_longest_path)) 
                        count = 0 
                    else:
                        count += 1
                        if count == 10:
                            break
                        print('else', j - i + 1, count)  

            if not path_updated:
                # ある程度、新しい経路が見つからなかったらループを抜ける
                break
        
        final_title_path = self.id_to_title_path(id_longest_path)
        print(final_title_path)
        print('Final longest path length:', len(final_title_path))
        return final_title_path
```

#### `find_other_path` 関数 (既存パスの中間を置き換えるための探索)

受け取った `start_id` と `goal_id` 間でDFSを実行する。元のノード間の距離よりも長かった場合に経路を更新する。

```python
    # 既存のパスの中間を置き換えるための探索
    def find_other_path(self, start_id, goal_id, avoid_set, path_length):
        path_dict = {}
        q = collections.deque()
        
        q.append(start_id)
        visited = {start_id} 

        while q:
            new_node = q.pop()
            if new_node == goal_id:
                new_id_path = [new_node]
                curr = new_node
                while curr != start_id:
                    curr = path_dict[curr]
                    new_id_path.append(curr)
                new_id_path.reverse()
                
                # pathがstart, goalのみの時、元のノード間の距離より短いときは更新しない
                if len(new_id_path) > path_length and len(new_id_path) > 2: 
                    return new_id_path
            else:
                for child in self.links.get(new_node, []):
                    # childがゴールか、(訪問済みでなく AND 避けるべきノードでない)
                    if child == goal_id or (child not in visited and child not in avoid_set):
                        q.append(child)
                        visited.add(child)
                        path_dict[child] = new_node
        return None
```

#### `dfs` 関数 (深さ優先探索)

```python
    def dfs(self, start_id, goal_id, id_path = []):
        path_dict = {}
        q = collections.deque()
        q.append(start_id)
        visited = set()
        
        while q:
            new_node = q.pop()
                
            if new_node == goal_id:
                id_path = [new_node]
                while id_path[-1] != start_id:
                    id_path += [path_dict[new_node]]
                    new_node = path_dict[new_node]
                return id_path[::-1]
            else:
                for child in self.links[new_node]:
                    if not child in visited and not child in id_path:
                        q.append(child)
                        visited.add(child)
                        path_dict[child] = new_node
            
        print('cannot find a long path')
        return None
```

---

## スタックを用いた再帰DFSと同じ経路の再現

スタックを2つ使用して、再帰によるDFSと同じ経路を再現する。

最初にBFSのように振る舞うとき、最初の1つだけ別のスタックに、残りを同じスタックに積む。最初の1つだけを入れるスタックには最大で1つしか入れない。

？？？？

stack1ってstackじゃなくてもいい？？？

結局最初にB, E, Gを見つけているのは変わらない？？（出力は違うけど）

```python
def dfs_with_stack_in_the_recursion_order(start, goal):
    print("dfs_with_stack_in_the_recursion_order:")
    stack1 = collections.deque()
    stack2 = collections.deque()
    visited = {}
    previous = {}
    first = True

    stack1.append(start)
    visited[start] = True
    previous[start] = None
    node = start
    while stack1 or stack2:
        if stack1:
            node = stack1.pop()
        else:
            node = stack2.pop()
        if node == goal:
            break
        for child in links[node]:
            if not child in visited:
                if first:
                    stack1.append(child)
                    first = False
                    visited[child] = True
                    previous[child] = node
                else:
                    stack2.append(child)
                    previous[child] = node
        

    if goal in previous:
        print(" -> ".join(find_path(goal, previous)))
    else:
        print("Not found")
```
