


    # 读取配置
    def load_text(self):
        config_file = QtCore.QFileInfo("config.ini")
        settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

        # 如果不存在配置文件，则创建
        if not config_file.exists():
            open(config_file.filePath(), "w").write("")  # 创建配置文件，并写入空内容
            name_type = "{b_initial_name}/[{b_typecode}] [{b_release_date}] {b_jp_name}"  # 默认格式
            settings.setValue("type", name_type)

        input_text = settings.value("type", "")
        self.type_input.setText(str(input_text))





    # 显示选中动画的详情
    @QtCore.Slot()
    def show_select_list(self, current):
        select_order = self.tree.indexOfTopLevelItem(current)
        order_count = len(self.anime_list)

        # 选中了未分析的项目
        if order_count <= select_order:
            self.info_jp_name.setText("动画：")
            self.info_cn_name.setText("中文名：")
            self.b_initial_name.setText("动画系列：")
            self.info_type.setText("动画类型：")
            self.info_release_date.setText("放送日期：")
            self.info_file_name.setText("文件名：")
            self.info_final_name.setText("重命名结果：")
            pixmap = QtGui.QPixmap("img/default.png")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)
            return

        # 选中行是否存在 b_initial_id 证明分析完成
        if "b_initial_id" in self.anime_list[select_order]:
            b_jp_name = self.anime_list[select_order]["b_jp_name"]
            self.info_jp_name.setText(f"动画：{b_jp_name}")

            b_cn_name = self.anime_list[select_order]["b_cn_name"]
            self.info_cn_name.setText(f"中文名：{b_cn_name}")

            b_initial_name = self.anime_list[select_order]["b_initial_name"]
            self.b_initial_name.setText(f"动画系列：{b_initial_name}")

            b_type = self.anime_list[select_order]["b_type"]
            self.info_type.setText(f"动画类型：{b_type}")

            b_release_date = self.anime_list[select_order]["b_release_date"]
            b_release_date = arrow.get(b_release_date, "YYMMDD")
            b_release_date = b_release_date.format("YYYY年M月D日")
            self.info_release_date.setText(f"放送日期：{b_release_date}")

            file_name = self.anime_list[select_order]["file_name"]
            self.info_file_name.setText(f"文件名：{file_name}")

            final_name = self.anime_list[select_order]["final_name"]
            final_name = final_name.replace("/", " / ")
            self.info_final_name.setText(f"重命名结果：{final_name}")

            b_image_name = self.anime_list[select_order]["b_image_name"]
            pixmap = QtGui.QPixmap(f"img/{b_image_name}")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)
        else:
            self.info_jp_name.setText("动画：")
            self.info_cn_name.setText("中文名：")
            self.b_initial_name.setText("动画系列：")
            self.info_type.setText("动画类型：")
            self.info_release_date.setText("放送日期：")
            self.info_file_name.setText("文件名：")
            self.info_final_name.setText("重命名结果：")
            pixmap = QtGui.QPixmap("img/default.png")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)



    # 开始命名
    @QtCore.Slot()
    def start_rename(self):
        # anime_list 是否有数据
        if not self.anime_list:
            print("请先拖入文件或开始分析")
            return

        # 列出有 anime_list 中有 final_name 的索引
        final_name_order = []
        for index, dictionary in enumerate(self.anime_list):
            if "final_name" in dictionary:
                final_name_order.append(index)

        # 如果没有能命名的文件，退出
        if not final_name_order:
            print("当前没有需要重命名的文件夹")
            return
        else:
            print(f"即将重命名下列ID：{final_name_order}")

        # 开始命名
        for order in final_name_order:
            this_anime_dict = self.anime_list[order]

            # 拆分 final_name 的前后文件夹
            final_name = this_anime_dict['final_name']
            if '/' in final_name:
                final_name_list = final_name.split('/')
                final_name_1 = final_name_list[0]
                final_name_2 = final_name_list[1]
                print(final_name_1)
                print(final_name_2)
            else:
                final_name_1 = ""
                final_name_2 = final_name
                print(final_name_2)

            # 更名当前文件夹
            file_path = this_anime_dict['file_path']
            file_dir = os.path.dirname(file_path)
            final_path_2 = os.path.join(file_dir, final_name_2)
            os.rename(file_path, final_path_2)

            # 判断是否有父文件夹，
            if final_name_1 == "":
                return

            # 创建父文件夹
            final_path_1 = os.path.join(file_dir, final_name_1)
            if not os.path.exists(final_path_1):
                os.makedirs(final_path_1)

            # 修改 / 为当前系统下的正确分隔符
            separator = os.path.sep
            final_name = final_name.replace('/', separator)

            # 移动至父文件夹
            final_path = os.path.join(file_dir, final_name)
            shutil.move(final_path_2, final_path)
            b_cn_name = this_anime_dict['b_cn_name']
            print(f"{b_cn_name}重命名成功")

        # 输出结果
        self.state.setText("重命名完成")

