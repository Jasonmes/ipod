import os
import shutil
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3

def is_valid_text(text):
    """
    检查文本是否包含乱码
    """
    try:
        # 检查是否为空
        if not text or text.isspace():
            return False
            
        # 检查是否能正确编解码
        text.encode('utf-8').decode('utf-8')
        
        # 扩展乱码特征列表
        invalid_chars = [
            # ASCII 扩展字符
            'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï',
            'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', '×', 'Ø', 'Ù', 'Ú', 'Û',
            'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç',
            'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó',
            'ô', 'õ', 'ö', '÷', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ',
            
            # 特殊符号
            '¡', '¢', '£', '¤', '¥', '¦', '§', '¨', '©', 'ª', '«', '¬',
            '®', '¯', '°', '±', '²', '³', '´', 'µ', '¶', '·', '¸', '¹',
            'º', '»', '¼', '½', '¾', '¿',
            
            # 常见乱码组合
            '╈', '╉', '╊', '╋', '═', '║', '╒', '╓', '╔', '╕', '╖', '╗',
            '╘', '╙', '╚', '╛', '╜', '╝', '╞', '╟', '╠', '╡', '╢', '╣',
            '╤', '╥', '╦', '╧', '╨', '╩', '╪', '╫', '╬',
            
            # 其他常见乱码字符
            '¤', '¦', '¨', '¯', '´', '¸', '¹', 'º', '¼', '½', '¾',
            '‗', '―', '‖', '‰', '※', '‹', '›', '‼', '‾', '⁄', '⁊',
            '₧', '₪', '₫', '€', '₭', '₮', '₯', '₰', '₱', '₲', '₳', '₴',
            '₵', '₶', '₷', '₸', '₹', '₺', '₻', '₼', '₽', '₾', '₿',
            
            # 控制字符
            '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
            '\x08', '\x0b', '\x0c', '\x0e', '\x0f', '\x10', '\x11', '\x12',
            '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a',
            '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', '\x7f'
        ]
        
        # 检查是否包含乱码特征
        if any(char in text for char in invalid_chars):
            return False
            
        # 检查连续的特殊字符
        special_chars_count = 0
        valid_special_chars = ['-', '(', ')', '[', ']', '&', '.', "'", ',', ' ', '_', '+']
        for c in text:
            if not c.isalnum() and c not in valid_special_chars:
                special_chars_count += 1
                if special_chars_count > 2:  # 如果连续超过2个特殊字符
                    return False
            else:
                special_chars_count = 0
        
        return True
    except:
        return False

def get_audio_title(file_path):
    """
    获取音频文件的标题，支持多种格式
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.mp3']:
            audio = EasyID3(file_path)
            return audio.get('title', [''])[0]
            
        elif ext in ['.m4a', '.m4p', '.aac', '.alac']:
            audio = MP4(file_path)
            return audio.get('©nam', [''])[0]
            
        elif ext in ['.wav', '.aif', '.aiff']:
            # 如果需要支持其他格式，可以在这里添加
            # 需要引入相应的库
            return os.path.splitext(os.path.basename(file_path))[0]
            
    except:
        # 如果无法读取元数据，返回文件名（不含扩展名）
        return os.path.splitext(os.path.basename(file_path))[0]

def get_audio_duration(file_path):
    """
    获取音频文件的时长（秒）
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.mp3':
            audio = MP3(file_path)
            return int(audio.info.length)
            
        elif ext in ['.m4a', '.m4p', '.aac', '.alac']:
            audio = MP4(file_path)
            return int(audio.info.length)
            
        elif ext in ['.wav', '.aif', '.aiff']:
            # 如果需要支持其他格式，可以在这里添加相应的处理
            return 0
            
    except:
        return 0

def format_duration(seconds):
    """
    将秒数转换为时分秒格式
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def export_clean_songs(music_path, output_file, problem_file):
    """
    导出所有可读的音乐文件标题到文本文件，并导出问题文件信息
    """
    total_count = 0
    found_count = 0
    empty_title_count = 0
    invalid_title_count = 0
    error_count = 0
    total_duration = 0  # 总时长（秒）
    supported_formats = ['.mp3', '.m4a', '.m4p', '.aac', '.alac', '.wav', '.aif', '.aiff']
    
    with open(output_file, 'w', encoding='utf-8') as f, \
         open(problem_file, 'w', encoding='utf-8') as pf:
        
        # 写入正常文件头部
        f.write("歌曲标题列表\n")
        f.write("-" * 50 + "\n")
        
        # 写入问题文件头部
        pf.write("问题文件列表\n")
        pf.write("-" * 50 + "\n")
        pf.write("\n1. 空标题文件:\n")
        pf.write("-" * 30 + "\n")
        
        for folder in sorted(os.listdir(music_path)):
            if not folder.startswith('F'):
                continue
                
            folder_path = os.path.join(music_path, folder)
            if not os.path.isdir(folder_path):
                continue
                
            for file in os.listdir(folder_path):
                if file.startswith('._'):
                    continue
                    
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_formats:
                    continue
                    
                total_count += 1
                full_path = os.path.join(folder_path, file)
                duration = get_audio_duration(full_path)
                
                try:
                    title = get_audio_title(full_path)
                    
                    if not title:
                        empty_title_count += 1
                        pf.write(f"文件: {file}\n")
                        pf.write(f"路径: {full_path}\n")
                        pf.write(f"时长: {format_duration(duration)}\n")
                        pf.write("-" * 20 + "\n")
                        continue
                        
                    if not is_valid_text(title):
                        if invalid_title_count == 0:
                            pf.write("\n2. 乱码标题文件:\n")
                            pf.write("-" * 30 + "\n")
                        invalid_title_count += 1
                        pf.write(f"文件: {file}\n")
                        pf.write(f"标题: {title}\n")
                        pf.write(f"路径: {full_path}\n")
                        pf.write(f"时长: {format_duration(duration)}\n")
                        pf.write("-" * 20 + "\n")
                        continue
                        
                    found_count += 1
                    total_duration += duration
                    f.write(f"{title} [{format_duration(duration)}]\n")
                except Exception as e:
                    if error_count == 0:
                        pf.write("\n3. 读取错误���件:\n")
                        pf.write("-" * 30 + "\n")
                    error_count += 1
                    pf.write(f"文件: {file}\n")
                    pf.write(f"错误: {str(e)}\n")
                    pf.write(f"路径: {full_path}\n")
                    pf.write(f"时长: {format_duration(duration)}\n")
                    pf.write("-" * 20 + "\n")
                    continue

    total_hours = total_duration // 3600
    print(f"\n文件统计:")
    print("-" * 30)
    print(f"总文件数: {total_count}")
    print(f"成功导出: {found_count}")
    print(f"空标题数: {empty_title_count}")
    print(f"乱码标题: {invalid_title_count}")
    print(f"读取错误: {error_count}")
    print(f"总时长: {total_hours}小时 {format_duration(total_duration)}")
    print(f"\n正常文件保存到: {output_file}")
    print(f"问题文件保存到: {problem_file}")



def find_and_copy_song(music_path, dest_path, search_keyword):
    """
    搜索并复制标题中包含关键词的音乐文件
    """
    found_count = 0
    supported_formats = ['.mp3', '.m4a', '.m4p', '.aac', '.alac', '.wav', '.aif', '.aiff']
    
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    
    for folder in sorted(os.listdir(music_path)):
        if not folder.startswith('F'):
            continue
            
        folder_path = os.path.join(music_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        for file in os.listdir(folder_path):
            if file.startswith('._'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_formats:
                continue
                
            try:
                full_path = os.path.join(folder_path, file)
                title = get_audio_title(full_path)
                
                if title and search_keyword in title:
                    print(f"找到文件: {title}")
                    print(f"文件路径: {full_path}")
                    shutil.copy2(full_path, os.path.join(dest_path, file))
                    found_count += 1
            except:
                continue
    
    if found_count == 0:
        print(f"未找到标题包含 '{search_keyword}' 的文件")
    else:
        print(f"\n总共找到并复制了 {found_count} 个文件")
    return found_count > 0


def find_songs_without_artist(music_path, output_file):
    """
    查找并导出所有没有艺术家信息的音乐文件
    """
    found_count = 0
    supported_formats = ['.mp3', '.m4a', '.m4p', '.aac', '.alac', '.wav', '.aif', '.aiff']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("没有艺术家信息的歌曲列表\n")
        f.write("-" * 50 + "\n")
        
        for folder in sorted(os.listdir(music_path)):
            if not folder.startswith('F'):
                continue
                
            folder_path = os.path.join(music_path, folder)
            if not os.path.isdir(folder_path):
                continue
                
            for file in os.listdir(folder_path):
                if file.startswith('._'):
                    continue
                    
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_formats:
                    continue
                    
                try:
                    full_path = os.path.join(folder_path, file)
                    title = ""
                    artist = ""
                    
                    if ext == '.mp3':
                        audio = EasyID3(full_path)
                        title = audio.get('title', [''])[0]
                        artist = audio.get('artist', [''])[0]
                    elif ext in ['.m4a', '.m4p', '.aac', '.alac']:
                        audio = MP4(full_path)
                        title = audio.get('©nam', [''])[0]
                        artist = audio.get('©ART', [''])[0]
                    else:
                        continue
                    
                    if title and is_valid_text(title) and not artist:
                        found_count += 1
                        f.write(f"标题: {title}\n")
                        f.write(f"文件路径: {full_path}\n")
                        f.write("-" * 30 + "\n")
                except:
                    continue

    print(f"\n总共找到 {found_count} 首没有艺术家信息的歌曲")
    return found_count > 0

def count_total_songs(music_path):
    """
    统计所有音频文件的数量
    """
    total_count = 0
    supported_formats = ['.mp3', '.m4a', '.m4p', '.aac', '.alac', '.wav', '.aif', '.aiff']
    file_types = {}  # 用于统计每种格式的文件数量
    
    for folder in sorted(os.listdir(music_path)):
        if not folder.startswith('F'):
            continue
            
        folder_path = os.path.join(music_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        for file in os.listdir(folder_path):
            if file.startswith('._'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_formats:
                continue
                
            total_count += 1
            file_types[ext] = file_types.get(ext, 0) + 1
    
    # 打印统计信息
    print("\n音频文件统计:")
    print("-" * 30)
    print(f"总文件数: {total_count}")
    print("\n各格式文件数:")
    for ext, count in sorted(file_types.items()):
        print(f"{ext}: {count}")
    
    return total_count



def backup_all_songs(music_path, backup_path):
    """
    将所有音频文件备份到指定目录，保持原始文件名
    """
    total_count = 0
    error_count = 0
    supported_formats = ['.mp3', '.m4a', '.m4p', '.aac', '.alac', '.wav', '.aif', '.aiff']
    
    # 确保备份目录存在
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    
    print(f"开始备份音乐文件到: {backup_path}")
    print("正在复制...")
    
    for folder in sorted(os.listdir(music_path)):
        if not folder.startswith('F'):
            continue
            
        folder_path = os.path.join(music_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        for file in os.listdir(folder_path):
            if file.startswith('._'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_formats:
                continue
                
            try:
                src_path = os.path.join(folder_path, file)
                dest_path = os.path.join(backup_path, file)
                
                # 如果文件已存在，添加数字后缀
                if os.path.exists(dest_path):
                    name, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{name}_{counter}{ext}"
                        dest_path = os.path.join(backup_path, new_filename)
                        counter += 1
                
                shutil.copy2(src_path, dest_path)
                total_count += 1
                
                # 显示进度
                if total_count % 100 == 0:
                    print(f"已复制: {total_count} 个文件")
                    
            except Exception as e:
                error_count += 1
                print(f"复制失败: {file}")
                print(f"错误信息: {str(e)}")
                continue
    
    print("\n备份完成!")
    print("-" * 30)
    print(f"成功复制: {total_count} 个文件")
    if error_count > 0:
        print(f"复制失败: {error_count} 个文件")
    
    return total_count


if __name__ == "__main__":
    music_path = "/Volumes/“ADMINISTR/iPod_Control/Music/"
    dest_path = "/Users/jasonmes/Documents/CodeSpace/ipod/"
    output_file = "/Users/jasonmes/Documents/CodeSpace/ipod/songs_list_clean.txt"
    songs_without_artist_file = "/Users/jasonmes/Downloads/songs_without_artist.txt"
    problem_file = "/Users/jasonmes/Documents/CodeSpace/ipod/problem_songs.txt"
    
    # 先导出干净的歌曲列表
    # print("开始导出所有可读的音乐文件信息...")
    # export_clean_songs(music_path, output_file)
    # export_clean_songs(music_path, output_file, problem_file)
    
    # 然后搜索并复制特定文件
    # search_keyword = "20170324 072259"
    # print(f"\n开始搜索标题包含 '{search_keyword}' 的音乐文件...")
    # find_and_copy_song(music_path, dest_path, search_keyword)


    # print("开始查找没有艺术家信息的音乐文件...")
    # find_songs_without_artist(music_path, songs_without_artist_file)


    # print("开始统计音频文件...")
    # total_songs = count_total_songs(music_path)

    backup_path = "/Volumes/books/backmusic"
    
    print("开始备份所有音乐文件...")
    backup_all_songs(music_path, backup_path)