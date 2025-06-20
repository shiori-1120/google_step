import sys
import collections

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file, encoding="utf-8") as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file, encoding="utf-8") as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()


    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()


    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_shortest_path(self, start, goal):
        start_id, goal_id = self.find_start_goal_id(start, goal)
                
        id_shortest_path = self.bfs(start_id, goal_id)
        title_shortest_path = self.id_to_title_path(id_shortest_path)
        print(title_shortest_path)
        
        return id_shortest_path


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

#small
# 
# midium
# ['英語', 'ISBN', '2006年', '2005年', '2007年', '東京都', '昭和', '2004年', '2003年', '2000年']
# large
# ['英語', '日本', 'VIAF_(識別子)', 'バーチャル国際典拠ファイル', 'アメリカ合衆国', 'ISBN', 'ISNI_(識別子)', '国際標準名称識別子', '地理座標系', 'SUDOC_(識別子)']


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
    

    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    
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

        # longest path 311238


    def id_to_title_path(self, id_path):
        if not id_path:
            return
        title_path = []
        for id in id_path:
            title_path += [self.titles[id]]
        return title_path
    
    def find_start_goal_id(self, start, goal):
        start_id, goal_id = '', ''
        
        for key, value in self.titles.items():
            if value == start:
                start_id = key
            elif value == goal:
                goal_id = key
                
        return start_id, goal_id

    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])
                


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    # wikipedia.find_longest_titles()

    # Example
    # wikipedia.find_most_linked_pages()

    # Homework #1
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # wikipedia.find_shortest_path("A", "B")
    # wikipedia.find_shortest_path("A", "C")
    # wikipedia.find_shortest_path("A", "D")
    # wikipedia.find_shortest_path("A", "E")
    # wikipedia.find_shortest_path("A", "F")

    # Homework #2
    # wikipedia.find_most_popular_pages()

    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")
    # wikipedia.find_longest_path("A", "F")
    
