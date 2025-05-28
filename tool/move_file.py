import os
import json
import shutil # 用於移動檔案

# --- 配置 ---
source_folder = './articles/unlabeled_articles' # 來源資料夾路徑
destination_folder = './articles/training_articles'
# --- 配置結束 ---

def move_json_file(filename, source_folder = source_folder, destination_folder = destination_folder):
    """移動單一 JSON 檔案（如果已經標記）"""
    source_path = os.path.join(source_folder, filename)
    destination_path = os.path.join(destination_folder, filename)

    # **檢查檔案是否存在**
    if not os.path.exists(source_path):
        print(f"⚠️ 錯誤：'{filename}' 不存在於 {source_folder}")
        return False

    try:
        # **讀取 JSON 檔案內容**
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # **確認是否有 "category"**
        if isinstance(data, dict) and 'category' in data:
            shutil.move(source_path, destination_path)
            print(f"✅ 移動 '{filename}' 至 {destination_folder}")
            return True
        else:
            print(f"⚠️ '{filename}' 未標記，無法移動。")
            return False

    except json.JSONDecodeError:
        print(f"⚠️ 錯誤：'{filename}' 無法解析，可能格式錯誤。")
        return False
    except Exception as e:
        print(f"⚠️ 移動 '{filename}' 時發生錯誤：{e}")
        return False

def move_json_with_category(src_folder, dest_folder):
    """遍歷所有 JSON 檔案，並使用 `move_single_json_file()` 進行移動"""
    moved_count = 0
    processed_count = 0
    error_count = 0

    print("\n開始掃描來源資料夾...")

    for filename in os.listdir(src_folder):
        source_path = os.path.join(src_folder, filename)

        if os.path.isfile(source_path) and filename.lower().endswith('.json'):
            processed_count += 1
            try:
                success = move_json_file(filename,src_folder, dest_folder)
                if success:
                    moved_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"⚠️ 處理 '{filename}' 時發生錯誤：{e}")
                error_count += 1

    print("\n--- 移動完成 ---")
    print(f"總共掃描的 JSON 檔案數: {processed_count}")
    print(f"成功移動的檔案數: {moved_count}")
    print(f"發生錯誤的檔案數: {error_count}")

# --- 主程式執行 ---
if __name__ == "__main__":
    # 呼叫函數，開始執行移動
    move_json_with_category(source_folder, destination_folder)