import random


def find_change(s1, s2):
    """
    :param s1: parent str
    :param s2: child str
    :return: find whether s1 can match s2
    """
    n = len(s1) + 1
    m = len(s2) + 1
    dp = [[0] * m for _ in range(n)]
    for i in range(1, n):
        for j in range(1, m):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i][j - 1], dp[i - 1][j])
    return dp[-1][-1]
print(find_change('lyx', 'lyx_1'))