import os

def combine_files(target_directory, output_file="all_code0101.txt"):
    # 檢查路徑是否存在
    if not os.path.exists(target_directory):
        print(f"錯誤：找不到路徑 {target_directory}")
        return

    # 切換到目標資料夾
    os.chdir(target_directory)
    print(f"正在掃描資料夾：{os.getcwd()}")

    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk("."):
            # 排除不需要的資料夾
            if any(x in root for x in [".git", "__pycache__", "venv", ".github", "node_modules"]):
                continue
            
            for file in files:
                # 只抓代碼、配置檔與說明檔
                if file.endswith((".py", ".txt", ".yaml", ".yml", ".json", ".md")):
                    # 避免自己讀取到自己生成的 output_file
                    if file == output_file:
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        outfile.write(f"\n{'='*30}\nFILE: {file_path}\n{'='*30}\n")
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            outfile.write(f.read())
                            outfile.write("\n")
                    except Exception as e:
                        print(f"讀取 {file_path} 時出錯: {e}")

    print(f"--- 完成！ ---")
    print(f"總結檔案已生成：{os.path.join(target_directory, output_file)}")

# 在這裡指定你的資料夾路徑
combine_files(r"E:\QuantProject")
