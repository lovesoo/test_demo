# coding:utf-8
import requests
import re
import json
from bs4 import BeautifulSoup
import jieba
from wordcloud import WordCloud
from concurrent import futures


def getUsers():
    # 获取推荐博客列表
    r = requests.get('https://www.cnblogs.com/aggsite/UserStats')

    # 使用BeautifulSoup解析
    soup = BeautifulSoup(r.text, 'lxml')
    users = [(i.text, i['href']) for i in soup.select('#blogger_list > ul > li > a') if 'AllBloggers.aspx' not in i['href'] and 'expert' not in i['href']]

    # 也可以使用使用正则表达式
    # user_re=re.compile('<a href="(http://www.cnblogs.com/.+)" target="_blank">(.+)</a>')
    # users=[(name,url) for url,name in re.findall(blog_re,r.text) if 'AllBloggers.aspx' not in url and 'expert' not in url]

    return users


def getPostsDetail(Posts):
    # 获取文章详细信息：标题，次数，URL
    post_re = re.compile('\d+\. (.+)\((\d+)\)')
    soup = BeautifulSoup(Posts, 'lxml')
    return [list(re.search(post_re, i.text).groups()) + [i['href']] for i in soup.find_all('a')]


def getViews(user):
    # 获取博客阅读排行榜，评论排行榜及推荐排行榜信息
    url = 'http://www.cnblogs.com/mvc/Blog/GetBlogSideBlocks.aspx'
    blogApp = user
    showFlag = 'ShowTopViewPosts,ShowTopFeedbackPosts,ShowTopDiggPosts'
    payload = dict(blogApp=blogApp, showFlag=showFlag)
    r = requests.get(url, params=payload)

    TopViewPosts = getPostsDetail(r.json()['TopViewPosts'])
    TopFeedbackPosts = getPostsDetail(r.json()['TopFeedbackPosts'])
    TopDiggPosts = getPostsDetail(r.json()['TopDiggPosts'])

    return dict(TopViewPosts=TopViewPosts, TopFeedbackPosts=TopFeedbackPosts, TopDiggPosts=TopDiggPosts)


def getCategory(user):
    # 获取博客随笔分类
    category_re = re.compile('(.+)\((\d+)\)')
    url = 'http://www.cnblogs.com/{0}/mvc/blog/sidecolumn.aspx'.format(user)
    blogApp = user
    payload = dict(blogApp=blogApp)
    r = requests.get(url, params=payload)
    soup = BeautifulSoup(r.text, 'lxml')
    category = [re.search(category_re, i.text).groups() for i in soup.select('.catListPostCategory > ul > li') if re.search(category_re, i.text)]

    return dict(category=category)


def getTotal(url):
    # 获取博客全部信息，包括分类及排行榜信息
    # 初始化博客用户名
    print 'Spider blog:\t{0}'.format(url)
    user = url.split('/')[-2]
    return dict(getViews(user), **getCategory(user))


def mutiSpider(max_workers=4):
    try:
        # with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:  # 多线程
        with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:  # 多进程
            for blog in executor.map(getTotal, [i[1] for i in users]):
                blogs.append(blog)
    except Exception as e:
        print e


def countCategory(category, category_name):
    # 合并计算目录数
    n = 0
    for name, count in category:
        if name.lower() == category_name:
            n += int(count)
    return n


def wordcloud(words, file_name):
    # 首先按照列表中的数目值进行排序，再对列表中的文本进行分词处理，生成词云
    words = sorted(words, key=lambda i: int(i[1]), reverse=True)
    print json.dumps(words[:10], ensure_ascii=False)

    # 拼接为长文本
    contents = ' '.join([i[0] for i in words])
    # 使用结巴分词进行中文分词
    cut_texts = ' '.join(jieba.cut(contents))
    # 设置字体为黑体，最大词数为2000，背景颜色为白色，生成图片宽1000，高667
    cloud = WordCloud(font_path='C:\Windows\Fonts\simhei.ttf', max_words=2000, background_color="white", width=1000, height=667, margin=2)
    # 生成词云
    wordcloud = cloud.generate(cut_texts)
    # 保存图片
    wordcloud.to_file('wordcloud\{0}.png'.format(file_name))
    # 展示图片
    wordcloud.to_image().show()


if __name__ == '__main__':
    blogs = []

    # 获取推荐博客列表
    users = getUsers()
    print json.dumps(users, ensure_ascii=False)

    # 多线程/多进程获取博客信息
    mutiSpider()

    # 获取所有分类目录信息
    category = [category for blog in blogs if blog['category'] for category in blog['category']]
    # 合并相同目录
    new_category = {}
    for name, count in category:
        # 全部转换为小写
        name = name.lower()
        if name not in new_category:
            new_category[name] = countCategory(category, name)

    # 获取所有排行榜文章信息
    TopViewPosts = [post for blog in blogs for post in blog['TopViewPosts']]
    TopFeedbackPosts = [post for blog in blogs for post in blog['TopFeedbackPosts']]
    TopDiggPosts = [post for blog in blogs for post in blog['TopDiggPosts']]

    # 排序并生成词云
    wordcloud(new_category.items(), 'category')
    wordcloud(TopViewPosts, 'TopViewPosts')
    wordcloud(TopFeedbackPosts, 'TopFeedbackPosts')
    wordcloud(TopDiggPosts, 'TopDiggPosts')
