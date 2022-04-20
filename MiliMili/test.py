def find_change(s1, s2):
    """
    :param s1: parent str
    :param s2: child str
    :return: find whether s1 can match s2
    """
    n = len(s1)
    m = len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    index_list = []
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i][j - 1], dp[i - 1][j])
    step = dp[-1][-1]
    for i in range(n, 0, -1):
        for j in range(m, 0, -1):
            if dp[i][j] == step and dp[i][j - 1] == dp[i - 1][j] == dp[i - 1][j - 1] == step - 1:
                step -= 1
                index_list.append([i - 1, i])
                m = j
                break

    return index_list, dp[-1][-1]

print(find_change('lyxxxx', 'yx'))