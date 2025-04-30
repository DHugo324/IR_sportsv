import os
import json
import shutil # 用於移動檔案，比 os.rename 更強大

# --- 配置 ---
# 請將 '你的來源資料夾路徑' 替換成實際的來源資料夾路徑
source_folder = './articles/unlabeled_articles' # 來源資料夾路徑
# 請將 '你的目標資料夾路徑' 替換成實際要存放檔案的目標資料夾路徑
destination_folder = './articles/training_articles'
# destination_folder = './articles/unlabeled_articles'
# --- 配置結束 ---

def move_json_without_category(src_folder, dest_folder):
    moved_count = 0
    processed_count = 0
    error_count = 0

    print("\n開始掃描來源資料夾...")

    # 3. 遍歷來源資料夾中的所有項目 (檔案和子資料夾)
    for filename in os.listdir(src_folder):
        source_path = os.path.join(src_folder, filename)

        # 4. 檢查是否為檔案以及是否為 .json 檔案 (忽略大小寫)
        if os.path.isfile(source_path) and filename.lower().endswith('.json'):
            processed_count += 1
            print(f"\n正在檢查檔案: {filename}")
            try:
                # 5. 開啟並讀取 JSON 檔案內容
                # 使用 utf-8 編碼讀取，這是 JSON 常用的編碼
                with open(source_path, 'r', encoding='utf-8') as f:
                    data = json.load(f) # 解析 JSON

                if isinstance(data,dict) and 'category' in data:
                    destination_path = os.path.join(dest_folder, filename)
                    print(f"  -> 偵測到 'category' 鍵。準備移動至: {destination_path}")
                    try:
                        shutil.move(source_path, destination_path)
                        moved_count += 1
                        print(f"  -> 檔案已成功移動。")
                    except Exception as move_e:
                        print(f"  -> 錯誤：移動檔案 '{filename}' 時發生錯誤: {move_e}")
                        error_count += 1

                # 可選：如果 JSON 根不是物件，或包含 category 鍵，則印出訊息
                elif not isinstance(data, dict):
                     print(f"  -> JSON 根目錄不是物件 (dictionary)，略過 '{filename}'。")
                else:
                    print(f"  -> 不包含 'category' 鍵，檔案保留在來源資料夾。")

            except json.JSONDecodeError:
                print(f"  -> 錯誤：無法解析 JSON 檔案 '{filename}'。檔案可能已損毀或格式不正確。")
                error_count += 1
            except FileNotFoundError:
                 print(f"  -> 錯誤：嘗試讀取時找不到檔案 '{filename}' (可能在處理過程中已被移動或刪除)。")
                 error_count += 1
            except PermissionError:
                print(f"  -> 錯誤：沒有權限讀取或移動檔案 '{filename}'。")
                error_count += 1
            except Exception as e:
                # 捕捉其他可能的錯誤，例如讀取錯誤、編碼錯誤等
                print(f"  -> 處理檔案 '{filename}' 時發生未預期錯誤: {e}")
                error_count += 1
        # 如果需要，可以取消下面註解來查看非 JSON 檔案
        # elif os.path.isfile(source_path):
        #     print(f"略過非 JSON 檔案: {filename}")


    print("\n--- 處理完成 ---")
    print(f"總共掃描的 JSON 檔案數: {processed_count}")
    print(f"成功移動的檔案數: {moved_count}")
    print(f"處理過程中發生錯誤的檔案數: {error_count}")
def move_file():
    move_json_without_category(source_folder, destination_folder)
# --- 主程式執行 ---
if __name__ == "__main__":
    # 呼叫函數，開始執行移動操作
    move_json_without_category(source_folder, destination_folder)