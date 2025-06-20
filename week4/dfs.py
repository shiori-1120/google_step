#! /usr/bin/python3
import collections


# An example graph structure
links = {"A": ["B","E","G"],
        "B": ["C"],
        "C": ["D"],
        "D": ["E"],
        "E": ["B","F"],
        "F": [],
        "G": ["F"]}


# A helper function to find a path.
def find_path(goal, previous):
    path = []
    node = goal
    path.append(node)
    while previous[node]:
        node = previous[node]
        path.append(node)
    path.reverse()
    return path


# dfs_with_recursion finds A -> B -> C -> D -> E -> F first.
def dfs_with_recursion(start, goal):
    print("dfs_with_recursion:")
    visited = {}
    previous = {}

    visited[start] = True
    previous[start] = None
    recursion(start, goal, visited, previous)

    if goal in previous:
        print(" -> ".join(find_path(goal, previous)))
    else:
        print("Not found")

def recursion(node, goal, visited, previous):
    if node == goal:
        return True
    for child in links[node]:
        if not child in visited:
            visited[child] = True
            previous[child] = node
            if recursion(child, goal, visited, previous):
                return True
    return False


# dfs_with_stack finds A -> G -> F first.
def dfs_with_stack(start, goal):
    print("dfs_with_stack:")
    stack = collections.deque()
    visited = {}
    previous = {}

    stack.append(start)
    visited[start] = True
    previous[start] = None
    while len(stack):
        node = stack.pop()
        if node == goal:
            break
        for child in links[node]:
            if not child in visited:
                stack.append(child)
                visited[child] = True
                previous[child] = node

    if goal in previous:
        print(" -> ".join(find_path(goal, previous)))
    else:
        print("Not found")


# Challenge quiz: Implement DFS using a stack that visits nodes and edges
# in the same order as dfs_with_recursion. In other words, implement DFS that
# finds A -> B -> C -> D -> E -> F first using a stack.
def dfs_with_stack_in_the_recursion_order(start, goal):
    print("dfs_with_stack_in_the_recursion_order:")
    stack1, stack2 = collections.deque(), collections.deque()
    visited, previous = {}, {}

    stack1.append(start)
    visited[start], previous[start] = True, None
    
    node = start
    while stack1 or stack2:
        first = True
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


dfs_with_recursion("A", "F")
dfs_with_stack("A", "F")
dfs_with_stack_in_the_recursion_order("A", "F")
