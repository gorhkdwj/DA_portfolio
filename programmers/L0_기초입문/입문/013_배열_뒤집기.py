# 배열 뒤집기
# 프로그래머스 L0 (기초·입문)
# 문제 링크: https://school.programmers.co.kr/learn/courses/30/lessons/120821
# 알고리즘: 기초
# 작성자: 김재천
# 작성일: 2026. 01. 16. 09:11:18

# def solution(num_list):
#     answer = []
#     n = len(num_list)
#     answer=[num_list[i] for i in range(n-1,-1,-1)]
#     return answer

def solution(num_list):
    answer = []
    answer = num_list[::-1]
    return answer