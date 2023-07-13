


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

