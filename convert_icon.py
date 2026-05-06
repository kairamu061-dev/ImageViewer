import sys
try:
    from PIL import Image
except ImportError:
    print("エラー: Pillowライブラリがインストールされていません。")
    print("以下のコマンドを実行してインストールしてください: pip install Pillow")
    sys.exit(1)

def main():
    # 入力ファイル名（新しい六角形の画像）
    input_path = "app_icon_hexagon.png"
    output_ico = "app_icon.ico"
    output_png = "app_icon_256.png"

    try:
        img = Image.open(input_path)
    except FileNotFoundError:
        print(f"エラー: {input_path} が見つかりません。")
        sys.exit(1)

    # RGBA形式に変換（透過に対応するため）
    img = img.convert("RGBA")

    # 白い背景を透過させる処理
    # (R, G, B) がすべて一定以上（白に近い）の場合、アルファ値（透過度）を0にする
    data = img.getdata()
    new_data = []
    threshold = 240 # この閾値以上の明るさのピクセルを透明にします
    for item in data:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0)) # 透明化
        else:
            new_data.append(item)
    img.putdata(new_data)

    # 透過部分を基準にして、アイコンの実体部分だけを含む最小の矩形（バウンディングボックス）で切り抜く
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # アスペクト比を維持して正方形にするための処理（ICOは通常正方形）
    # 最大辺の長さに合わせた透明な正方形のキャンバスを作成し、中央に配置する
    max_size = max(img.size)
    square_img = Image.new("RGBA", (max_size, max_size), (255, 255, 255, 0))
    paste_pos = ((max_size - img.width) // 2, (max_size - img.height) // 2)
    square_img.paste(img, paste_pos)

    # ICOファイルとして保存 (Windows等でそのまま使える形式)
    icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    square_img.save(output_ico, format='ICO', sizes=icon_sizes)
    print(f"アイコンを保存しました: {output_ico}")

    # 標準的な256x256サイズのPNGとしても保存
    img_256 = square_img.resize((256, 256), Image.Resampling.LANCZOS)
    img_256.save(output_png)
    print(f"PNG画像を保存しました: {output_png}")

if __name__ == "__main__":
    main()
