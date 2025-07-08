import sys
import collections
import numpy as np
from scipy.sparse import csr_matrix

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):
        self.titles = {}
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file, encoding="utf-8") as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                self.titles[id] = title
                self.links[id] = [] # Initialize links for all pages
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file, encoding="utf-8") as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                if src in self.titles and dst in self.titles: # Ensure both source and destination exist
                    self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Helper function to convert title to ID and vice versa
    def find_start_goal_id(self, start_title, goal_title):
        # Create reverse mapping for efficiency if not already present
        if not hasattr(self, '_title_to_id'):
            self._title_to_id = {v: k for k, v in self.titles.items()}
        
        start_id = self._title_to_id.get(start_title)
        goal_id = self._title_to_id.get(goal_title)
        
        if start_id is None:
            print(f"Error: Start page '{start_title}' not found.")
        if goal_id is None:
            print(f"Error: Goal page '{goal_title}' not found.")
            
        return start_id, goal_id

    def id_to_title_path(self, id_path):
        if not id_path:
            return []
        return [self.titles.get(node_id, str(node_id)) for node_id in id_path]


    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1: # Exclude titles with underscores (often internal pages)
                print(titles[index])
                count += 1
            index += 1
        print()

    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = collections.defaultdict(int)
        for src_id in self.links:
            for dst_id in self.links[src_id]:
                link_count[dst_id] += 1

        if not link_count:
            print("No linked pages found.")
            return

        print("The most linked pages are:")
        # Find max count to handle pages with same max links
        link_count_max = max(link_count.values())
        for dst_id in sorted(link_count.keys(), key=lambda k: link_count[k], reverse=True)[:10]: # Top 10 most linked
            print(self.titles.get(dst_id, str(dst_id)), link_count[dst_id])
        print()


    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_shortest_path(self, start, goal):
        start_id, goal_id = self.find_start_goal_id(start, goal)
        if start_id is None or goal_id is None:
            return None
                
        id_shortest_path = self.bfs(start_id, goal_id)
        if id_shortest_path:
            title_shortest_path = self.id_to_title_path(id_shortest_path)
            print(f"Shortest path found: {title_shortest_path}, Length: {len(title_shortest_path)}")
        else:
            print(f"Cannot find shortest path from '{start}' to '{goal}'.")
        
        return id_shortest_path

    def bfs(self, start_id, goal_id):
        path_dict = {}
        q = collections.deque()
        visited = set()
        
        q.append(start_id)
        visited.add(start_id) # Mark as visited when added to queue
        
        while q:
            new_node = q.popleft() # BFS uses popleft()
                
            if new_node == goal_id:
                path = [new_node]
                curr = new_node
                while curr != start_id:
                    curr = path_dict[curr]
                    path.append(curr)
                return path[::-1] # Return path in correct order
            else:
                for child in self.links.get(new_node, []): # Use .get() to handle missing keys
                    if child not in visited:
                        q.append(child)
                        visited.add(child)
                        path_dict[child] = new_node
                            
        return None # Path not found


    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        # 1. IDマッピングとNの取得
        all_page_ids = sorted(list(self.titles.keys()))
        id_to_idx = {page_id: i for i, page_id in enumerate(all_page_ids)}
        idx_to_id = {i: page_id for i, page_id in enumerate(all_page_ids)}
        N = len(all_page_ids)

        damping_factor = 0.85
        tolerance = 1e-6 # 収束閾値 (0.01は少し大きいので、より小さい値に)

        # 2. 遷移行列 M_T の構築
        rows, cols, data = [], [], []
        dangling_nodes_idx = [] 

        for src_id in all_page_ids:
            src_idx = id_to_idx[src_id]
            
            if src_id in self.links and self.links[src_id]:
                out_degree = len(self.links[src_id])
                for dst_id in self.links[src_id]:
                    if dst_id in id_to_idx:
                        dst_idx = id_to_idx[dst_id]
                        rows.append(dst_idx)
                        cols.append(src_idx)
                        data.append(1.0 / out_degree)
            else:
                dangling_nodes_idx.append(src_idx)
        
        M_T = csr_matrix((data, (rows, cols)), shape=(N, N), dtype=np.float64)

        # 3. PageRankベクトルの初期化
        pagerank_vector = np.full(N, 1.0 / N, dtype=np.float64) 

        # 4. べき乗法による反復計算
        iteration_count = 0
        while True:
            iteration_count += 1
            
            new_pagerank_propagated = M_T.dot(pagerank_vector)

            sum_of_dangling_pageranks = np.sum(pagerank_vector[dangling_nodes_idx])
            dangling_distribution_vector = np.full(N, sum_of_dangling_pageranks / N, dtype=np.float64)
            
            random_jump_vector = np.full(N, 1.0 / N, dtype=np.float64)

            new_pagerank_vector = (
                damping_factor * (new_pagerank_propagated + dangling_distribution_vector) + 
                (1.0 - damping_factor) * random_jump_vector
            )
            
            variance = np.sum((new_pagerank_vector - pagerank_vector)**2)
            
            if variance < tolerance:
                break
            
            pagerank_vector = new_pagerank_vector

        # 5. 結果の並び替えとトップ10の取得
        sorted_indices = np.argsort(pagerank_vector)[::-1]

        most_popular_titles = []
        for i in range(10):
            if i >= N:
                break
            page_id = idx_to_id[sorted_indices[i]]
            most_popular_titles.append(self.titles[page_id])
        
        print("Finished PageRank calculation.")
        print('Top 10 most popular pages:', most_popular_titles)
        return most_popular_titles


    # Homework #3 (optional): Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    
    # 単純経路を見つけるためのDFS (再帰なし)
    # avoid_nodes_set: この探索では通ってはいけないノードの集合
    def dfs_for_longest_path(self, start_id, goal_id, avoid_nodes_set=None):
        if avoid_nodes_set is None:
            avoid_nodes_set = set()

        path_dict = {}
        q = collections.deque() # スタックとして使用 (pop()で末尾から取り出す)
        
        q.append(start_id)
        visited_in_sub_path = {start_id} # このDFS探索での訪問済みノード

        while q:
            current_node = q.pop()
            
            if current_node == goal_id:
                path = [current_node]
                curr = current_node
                while curr != start_id:
                    curr = path_dict[curr]
                    path.append(curr)
                return path[::-1]
            
            for child in self.links.get(current_node, []):
                # ゴールノードは常に訪問可能
                # それ以外は、現在の探索で未訪問かつ避けるべきノードではない
                if child == goal_id or (child not in visited_in_sub_path and child not in avoid_nodes_set):
                    q.append(child)
                    visited_in_sub_path.add(child)
                    path_dict[child] = current_node
                    
        return None

    # 既存のパスの中間を置き換えるための探索
    def find_other_path(self, start_id, goal_id, main_path_nodes_to_avoid_set, min_required_length):
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
                
                # パスが min_required_length より長く、かつ開始と終了ノード以外を含む場合のみ有効
                if len(new_id_path) > min_required_length and len(new_id_path) > 2: 
                    return new_id_path
                return None
            else:
                for child in self.links.get(new_node, []):
                    # childがゴールか、(訪問済みでなく AND 避けるべきノードでない)
                    if child == goal_id or (child not in visited and child not in main_path_nodes_to_avoid_set):
                        q.append(child)
                        visited.add(child)
                        path_dict[child] = new_node
        return None

    # 最長経路を探索するメイン関数
    def find_longest_path(self, start, goal):
        start_id, goal_id = self.find_start_goal_id(start, goal)
        if start_id is None or goal_id is None:
            return []

        # 最初のパス (dfs_for_longest_path を使用)
        id_longest_path = self.dfs_for_longest_path(start_id, goal_id)
        
        if not id_longest_path:
            print("Path from start to goal not found.")
            return []

        print(f"Initial path length: {len(id_longest_path)}")

        while True:
            path_updated = False
            current_path_length = len(id_longest_path)
            
            for i in range(current_path_length - 1):
                count_no_improvement = 0 
                for j in range(i + 1, current_path_length):
                    sub_start_id = id_longest_path[i]
                    sub_goal_id = id_longest_path[j]
                    
                    # 探索時に避けるべきノードのセット (サブパスの端点以外)
                    nodes_to_avoid = set(id_longest_path[:i] + id_longest_path[j+1:])
                    
                    tmp_path = self.find_other_path(sub_start_id, sub_goal_id, nodes_to_avoid, j - i + 1)
                    
                    if tmp_path:
                        new_id_longest_path = id_longest_path[:i] + tmp_path + id_longest_path[j+1:] 
                        
                        # 新しいパスが単純経路であることを最終確認
                        if len(new_id_longest_path) == len(set(new_id_longest_path)):
                            id_longest_path = new_id_longest_path
                            path_updated = True
                            print(f"Path updated. New length: {len(id_longest_path)}") 
                            break 
                    else:
                        count_no_improvement += 1
                        if count_no_improvement >= 10:
                            break
            
            if not path_updated:
                print(f"No further path extension found.")
                break
        
        final_title_path = self.id_to_title_path(id_longest_path)
        print('Final longest path length:', len(final_title_path))
        print(final_title_path)
        return final_title_path


# --- メイン実行ブロック ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python wikipedia_optimized.py pages_file links_file")
        sys.exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])

    # Homework #1 Example
    # print("\n--- Homework #1: Shortest Path ---")
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # wikipedia.find_shortest_path("東京タワー", "東京駅")

    # Homework #2 Example (Optimized PageRank)
    # print("\n--- Homework #2: Most Popular Pages (PageRank) ---")
    # wikipedia.find_most_popular_pages()

    # Homework #3 (optional) Example: Longest Path
    print("\n--- Homework #3: Longest Path ---")
    wikipedia.find_longest_path("渋谷", "池袋")
    # wikipedia.find_longest_path("日本", "アメリカ合衆国")