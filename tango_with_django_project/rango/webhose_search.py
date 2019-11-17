import json
import urllib.parse
import urllib.request
import os


def read_webhose_key():
    """
    从search.key 文件中读取webhose API 密钥
    返回None(未找到密钥)，或者密钥的字符串形式
    注意：把search.key 写入 .gitignore 文件，禁止提交
    """
    # 参见 Python Anti-Patterns 小书，这是一份十分优秀的资料
    12  # 使用 with 打开文件
    13  # http://docs.quantifiedcode.com/python-anti-patterns/maintainability/
    webhose_api_key = None

    try:
        path = 'search.key'
        if not os.path.isfile(path):
            path = '../search.key'

        with open(path, 'r') as f:
            webhose_api_key = f.readline().strip()
    except:
        raise IOError('search.key file not found')

    return webhose_api_key


def run_query(search_terms, size=0):
    """
    26 指定搜索词条和结果数量（默认为 10），把 Webhose API 返回的结果存入列表
    27 每个结果都有标题、链接地址和摘要
    28
    """
    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('Webhose key not found')

    # Webhose API 的基 URL
    root_url = 'http://webhose.io/search'

    # 处理查询字符串，转义特殊字符
    query_string = urllib.parse.quote(search_terms)

    # 使用字符串格式化句法构建完整的 API URL
    # search_url 是一个多行字符串
    search_url = ('{root_url}?token={key}&format=json&q={query}'
                  '&sort=relevancy&size={size}').format(root_url=root_url,
                                                        key=webhose_api_key,
                                                        query=query_string,
                                                        size=size)

    results = []

    try:
        # 连接 webhose API 把响应转为 Python 字典
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)

        # 迭代结果
        for post in json_response['posts']:
            results.append({'title': post['title'],
                            'link': post['url'],
                            'summary': post['text'][:200]})

    except:
        print("Error when querying the Webhose API")

    return results


def main():
    search_term = input("请输入搜索字符串")
    results = run_query(search_term)
    for post in results:
        print("title: %s, summary: %s" % (post['title'], post['summary']))


if __name__ == '__main__':
    main()
