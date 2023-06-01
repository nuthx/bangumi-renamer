import wx
import os
import re
import ctypes  # 高分屏适配
import asyncio  # 异步IO

from module import function

# ctypes.windll.shcore.SetProcessDpiAwareness(1)
# ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="renamer", size=(1000, 650), 
            style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
        self.Center()
        self.SetBackgroundColour(wx.Colour(248, 248, 248))

        # 创建列表而非集合，方便排序
        self.file_path_exist = []
        
        # 修正窗口实际宽度
        win_width, win_height = self.GetClientSize()
        rule_width = win_width - 30

        # ListView 表格
        self.list_ctrl = wx.ListView(self, 
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_EDIT_LABELS)
        self.list_ctrl.SetMinSize((rule_width, 260))
        self.list_ctrl.InsertColumn(0, "文件名")
        self.list_ctrl.InsertColumn(1, "动画名（本季）")
        self.list_ctrl.InsertColumn(2, "动画名（首季）")
        self.list_ctrl.InsertColumn(3, "重命名")
        self.list_ctrl.SetColumnWidth(0, 280)
        self.list_ctrl.SetColumnWidth(1, 180)
        self.list_ctrl.SetColumnWidth(2, 180)
        self.list_ctrl.SetColumnWidth(3, 330)
        
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.list_selected)
        self.list_ctrl.SetDropTarget(DropFolder(self.list_ctrl, self.file_path_exist))
        
        # 标签容器
        self.edit_frame = wx.StaticBox(self, label="编辑关联条目", size=(rule_width,0))

        # 图片
        img_url = "img/default.jpg"
        self.image = wx.Image(img_url, wx.BITMAP_TYPE_ANY)
        self.scaled = self.image.Scale(145, 210, wx.IMAGE_QUALITY_HIGH)
        self.bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.scaled))

        # 分割线
        # self.vline = wx.StaticLine(self, style=wx.LI_VERTICAL)

        # 标签
        label_width = win_width - 295
        self.lbt_file_name = wx.StaticText(self, label="文件名", style=wx.ALIGN_LEFT)
        self.lbt_file_name.SetMinSize((60, -1))
        self.lb_file_name = wx.StaticText(self, label="[Moozzi2] Tensei Oujo to Tensai Reijou no Mahou Kakumei BD-BOX [ x265-10Bit Ver. ] - TV + SP", style=wx.ALIGN_LEFT)
        self.lb_file_name.SetMinSize((label_width, -1))

        self.lbt_a_jp_name = wx.StaticText(self, label="动画名", style=wx.ALIGN_LEFT)
        self.lbt_a_jp_name.SetMinSize((60, -1))
        self.lb_a_jp_name = wx.StaticText(self, label="balabala", style=wx.ALIGN_LEFT)

        # 进度条
        self.progress_bar = wx.Gauge(self, range=100)
        process_bar_width = rule_width - 345
        self.progress_bar.SetMinSize((process_bar_width, 20))

        # 清除按钮
        self.clear_button = wx.Button(self, label="清除全部")
        self.clear_button.SetMinSize((100, 32))
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_list)

        # 识别按钮
        self.analysis_button = wx.Button(self, label="开始识别")
        self.analysis_button.SetMinSize((100, 32))
        self.analysis_button.Bind(wx.EVT_BUTTON, self.start_analysis)

        # 重命名按钮
        self.rename_button = wx.Button(self, label="重命名全部")
        self.rename_button.SetMinSize((100, 32))
        
        # 排列窗口
        WINDOW = wx.BoxSizer(wx.VERTICAL)
        WINDOW.Add(self.list_ctrl, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=15)

        LABEL_FRAME_1 = wx.BoxSizer(wx.HORIZONTAL)
        LABEL_FRAME_1.Add(self.lbt_file_name, 0, wx.TOP | wx.BOTTOM, border=5)
        LABEL_FRAME_1.Add(self.lb_file_name, 0, wx.TOP | wx.BOTTOM, border=5)

        LABEL_FRAME_2 = wx.BoxSizer(wx.HORIZONTAL)
        LABEL_FRAME_2.Add(self.lbt_a_jp_name, 0, wx.TOP | wx.BOTTOM, border=5)
        LABEL_FRAME_2.Add(self.lb_a_jp_name, 0, wx.TOP | wx.BOTTOM, border=5)

        LABEL_FRAME = wx.BoxSizer(wx.VERTICAL)
        LABEL_FRAME.Add(LABEL_FRAME_1, 0)
        LABEL_FRAME.Add(LABEL_FRAME_2, 0)
        
        EDIT_FRAME = wx.StaticBoxSizer(self.edit_frame, wx.HORIZONTAL)
        EDIT_FRAME.Add(self.bitmap, 0, wx.ALL, border=10)
        # EDIT_FRAME.Add(self.vline, 0, wx.EXPAND | wx.ALL, border=10)
        EDIT_FRAME.Add(LABEL_FRAME, 0, wx.TOP | wx.LEFT, border=10)

        CTRL_FRAME = wx.BoxSizer(wx.HORIZONTAL)
        CTRL_FRAME.Add(self.progress_bar, 0, wx.CENTER)
        CTRL_FRAME.Add(self.clear_button, 0, wx.LEFT, border=15)
        CTRL_FRAME.Add(self.analysis_button, 0, wx.LEFT, border=15)
        CTRL_FRAME.Add(self.rename_button, 0, wx.LEFT, border=15)

        WINDOW.Add(EDIT_FRAME, 0, wx.ALIGN_CENTER)
        WINDOW.Add(CTRL_FRAME, 0, wx.TOP | wx.LEFT, border=15)

        self.SetSizer(WINDOW)
        print("窗口创建完成，实际宽度" + str(rule_width) + "像素")

    def list_selected(self, event):
        # 选择文件夹时输出当前选择的文件名
        selected_item = event.GetItem()
        file_name = self.list_ctrl.GetItemText(selected_item.GetId(), 0)
        print(f"当前选择文件夹: {file_name}")

    def start_analysis(self, event):
        # 调用获取到的文件路径列表
        file_path_exist = self.list_ctrl.GetDropTarget().file_path_exist

        # 判断列表是否为空
        if file_path_exist == set():
            print("请先拖入文件夹")
            # 禁用按钮
            # self.analysis_button.Enable(False)
        else:
            # 创建列表，写入所有抓取的数据
            anime_list = []

            # 循环开始：分析每个文件
            list_id = 0
            for file_path in file_path_exist:

                # 通过文件路径 file_path 获取数据，合并入列表 anime_list
                this_anime_dict = function.get_anime_info(list_id, file_path)
                anime_list.append(this_anime_dict)
                print(anime_list)

                # 写入listview
                # 如果没有 b_originate_name 说明没有执行到最后一步
                # 重写 file_file 并展示在 listview 避免错位
                this_anime = anime_list[list_id]
                if "b_originate_name" in this_anime:
                    file_name = anime_list[list_id]["file_name"]
                    b_cn_name = anime_list[list_id]["b_cn_name"]
                    b_originate_name = anime_list[list_id]["b_originate_name"]
                    self.list_ctrl.SetItem(list_id, 0, file_name)
                    self.list_ctrl.SetItem(list_id, 1, b_cn_name)
                    self.list_ctrl.SetItem(list_id, 2, b_originate_name)
                else:
                    print("该动画未获取到内容，已跳过")
                
                # 进入下一轮前修改 ID
                list_id += 1

    def on_clear_list(self, event):
        self.list_ctrl.DeleteAllItems()
        self.file_path_exist = []
        print("已清除所有文件夹")


class DropFolder(wx.FileDropTarget):
    def __init__(self, window, file_path_exist):
        super().__init__()
        self.window = window
        self.file_path_exist = file_path_exist

    def OnDropFiles(self, x, y, file_path_list):
        for file_path in file_path_list:
            # 判断是否为文件夹
            if os.path.isdir(file_path):
                file_name = os.path.basename(file_path)

                # 判断是否存在相同文件夹，并写入 file_path_exist 列表
                if file_path not in self.file_path_exist:
                    self.window.InsertItem(self.window.GetItemCount(), file_name)
                    self.file_path_exist.append(file_path)
                    print(f"新增了{file_name}")
                    # print(f"总路径列表：{self.file_path_exist}")
                else:
                    print(f"{file_name}已存在")
            else:
                print(f"已过滤文件{file_path}")
 
                # 调整第一列宽度以适应内容
                # width, height = self.window.GetTextExtent(file_name)
                # width = width + 20
                # if width > 280:
                #     self.window.SetColumnWidth(0, width)
        return True