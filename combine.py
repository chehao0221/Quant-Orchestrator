import os

def combine_files(output_file="all_code0101.txt"):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk("."):
            # 排除掉不需要的資料夾
            if any(x in root for x in [".git", "__pycache__", "venv", ".github"]):
                continue
            for file in files:
                if file.endswith((".py", ".txt", ".yaml")): # 只抓代碼和配置
                    file_path = os.path.join(root, file)
                    outfile.write(f"\n{'='*20}\nFILE: {file_path}\n{'='*20}\n")
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        outfile.write(f.read())
    print(f"完成！請把 {output_file} 的內容貼給我或上傳。")

combine_files()
