from interface import info_retrieval


def main():
    s = info_retrieval()
    # s.create_index()
    s.load_inverted_index()
    query = input("请输入想要查询的内容：")
    expand, all_check_result = s.spell_check(query)
    if expand:
        print("你可能想要查询的是：(根据序号选择你想要查询的内容，输入 0 则继续查询 " + query + " )")
        for i, result in enumerate(all_check_result):
            print(i+1, ''.join(result))
        num = eval(input("查询内容：(0~n)："))
        if num != 0 and num <= len(all_check_result):
            query = ''.join(all_check_result[num - 1])
    score = s.info_search(query)
    print("总共检索到" + str(len(score)) + "个结果")
    for i in range(len(score)):
            print(score[i]["file"])



if __name__ == "__main__":
    main()
