# coding:utf-8
import autoit
import time


class test_cloudmusic(object):

    # 定义相关参数
    cloudmusic_path = "C:\Program Files (x86)\Netease\CloudMusic\cloudmusic.exe"
    cloudmusic_title = "[CLASS:OrpheusBrowserHost]"
    song = u"红玫瑰"

    def test_search(self):
        # 运行网易云音乐
        autoit.run(self.cloudmusic_path)
        time.sleep(5)

        # 等待网易云音乐窗口激活
        autoit.win_wait_active(self.cloudmusic_title)

        # 按5下TAB切换至搜索框
        autoit.send("{TAB 5}")

        # 搜索歌曲
        autoit.send(self.song)
        time.sleep(1)

        # 按3下向下键选择第一首歌曲
        autoit.send("{DOWN 3}")
        time.sleep(1)

        # 按回车键播放歌曲
        autoit.send("{ENTER}")
        time.sleep(1)

        # 校验当前窗口标题是否含有搜索歌曲名
        title = autoit.win_get_title(self.cloudmusic_title)
        assert self.song in title, self.song.encode('utf-8') + ' not in ' + title.encode('utf-8')

        # 关闭窗口
        autoit.win_close(self.cloudmusic_title)
