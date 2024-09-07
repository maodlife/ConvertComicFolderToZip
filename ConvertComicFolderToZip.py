#!/usr/bin/env python3

# 递归处理漫画文件夹
# 预期是整理成每个文件夹里有 xx.zip压缩包 和 /png /webp 等图片文件夹
import os
import shutil
import subprocess
import zipfile

# 递归处理文件夹
def literate_handle_dir(dir_path : str):
    # 首先检查这是不是漫画文件夹
    if check_is_comic_dir(dir_path):
        print("找到漫画文件夹: " + dir_path)
        handle_comic_dir(dir_path)
    else:
        # 递归处理每一个子文件夹
        list = os.listdir(dir_path)
        for sub_dir in list:
            sub_dir_path = os.path.join(dir_path, sub_dir)
            if os.path.isdir(sub_dir_path):
                literate_handle_dir(sub_dir_path)
    return

# 检查是不是漫画文件夹
def check_is_comic_dir(dir_path : str):
    if os.path.isdir(dir_path) == False:
        return False
    # 列出当前目录中的所有文件和文件夹
    list = os.listdir(dir_path)
    for item in list:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            if item_path.endswith(".zip"):
                return True
        if check_is_image_file(item_path):
            return True
    return False

# 判断一个文件是不是图片
# 直接用后缀判断了
def check_is_image_file(item_path):
    if item_path.endswith("png")\
        or item_path.endswith("jpg")\
        or item_path.endswith("webp")\
        or item_path.endswith("jpeg"):
        return True
    else:
        return False

# 处理漫画文件夹
def handle_comic_dir(dir_path : str):
    print("    把图片文件放入子文件夹中...")
    move_image_files_to_sub_dir(dir_path)
    print("    转换webp文件夹...")
    conver_webp_folder(dir_path)
    print("    开始生成zip文件")
    create_zip_file(dir_path)

# 把图片文件放入子文件夹中
def move_image_files_to_sub_dir(dir_path : str):
    image_item_list = []
    image_ext_list = []
    # 遍历文件
    file_list = os.listdir(dir_path)
    for item in file_list:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path) and check_is_image_file(item_path):
            image_item_list.append(item_path)
            _, image_file_extension = os.path.splitext(item_path)
            ext = image_file_extension[1:]  # 跳过开头的 .
            if (ext in image_ext_list) == False:
                image_ext_list.append(ext)
    if len(image_ext_list) >= 1:
        print("    有%d种图片文件，开始移动到子文件夹中..." % len(image_ext_list))
        for ext in image_ext_list:
            target_dir_name = os.path.join(dir_path, ext)
            if (ext in file_list) and (len(os.listdir(target_dir_name)) > 0):
                print("    已经存在命名为" + target_dir_name + "的文件，且文件夹有内容，请检查")
            else:
                if (ext in file_list) == False:
                    os.mkdir(ext)
                # 移动这种类型的图片文件到新建的文件夹中
                for image in image_item_list:
                    if image.endswith(ext):
                        shutil.move(image, target_dir_name)
    # 删除空文件夹
    file_list = os.listdir(dir_path)
    for item in file_list:
        if os.path.isdir(item) and len(os.listdir(os.path.join(dir_path, item))) == 0:
            print("    发现空文件夹：" + os.path.join(dir_path, item))
            os.rmdir(os.path.join(dir_path, item))
            print("    已删除")

# 转换webp文件夹
def conver_webp_folder(dir_path : str):
    file_list = os.listdir(dir_path)
    image_folder_cnt = 0  # 图片文件夹计数
    have_webp_folder = False
    for image_folder in file_list:
        if (os.path.isdir(image_folder) and check_is_image_file(os.path.join(dir_path, image_folder))):
            image_folder_cnt += 1
            if image_folder == "webp":
                have_webp_folder = True
    if have_webp_folder and image_folder_cnt == 1:
        print("    仅存在webp文件夹, 开始转换..." + dir_path)
        os.mkdir("png")
        webp_dir_path = os.path.join(dir_path, "webp")
        png_dir_path = os.path.join(dir_path, "png")
        webp_file_list = os.listdir(webp_dir_path)
        for webp_file in webp_file_list:
            webp_basename = os.path.basename(webp_file)
            webp_file_name, _ = os.path.splitext(webp_basename)
            new_png_file_name = os.path.join(png_dir_path, webp_file_name+".png")
            # print(new_png_file_name)
            command = ['dwebp', os.path.join(webp_dir_path, webp_file), '-o', new_png_file_name]
            try:
                # 使用 subprocess.run() 运行命令
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                print(f"命令执行失败: {e}")
                print("错误信息:", e.stderr.decode())
        print("    转换webp结束...")

def create_zip_file(dir_path : str):
    file_list = os.listdir(dir_path)
    # 用文件夹的basename作为压缩包名字
    dir_basename = os.path.basename(dir_path)
    zip_file_name = os.path.join(dir_path, dir_basename + ".zip")
    # 已存在zip
    if (dir_basename + ".zip") in file_list:
        print("    已存在压缩包：" + zip_file_name)
        return
    # 优先寻找png文件夹，然后找一个不是webp的文件夹
    found = ""
    for file in file_list:
        file_path = os.path.join(dir_path, file)
        if os.path.isdir(file_path) and check_is_image_file(file_path) and file == "png":
            found = file_path
            break
        if os.path.isdir(file_path) and check_is_image_file(file_path) and file != "webp":
            found = file_path
            break
    if found == "":
        print("    没有找到图片文件夹, 请检查: " + dir_path)
        return
    # 开始压缩
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹中的所有文件
        for root, dirs, files in os.walk(found):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 将文件添加到 ZIP 文件中，不包括文件夹路径
                zipf.write(file_path, file)

# 获取当前工作目录
current_directory = os.getcwd()
print("start handle: " + current_directory)
literate_handle_dir(current_directory)
print("success!")
