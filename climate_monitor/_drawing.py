"""Simple OLED drawing primitives retained from the original program."""

OLED_WIDTH = 128

def centered_x(draw, text, font):
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    return max(0, (OLED_WIDTH - text_width) // 2)


def draw_temperature_icon(draw, status):
    # 右上角の左側に、温度状態の小さいアイコンを描く。
    # 特殊文字フォントに依存しないよう、図形だけで描画する。
    cx = 106
    cy = 7

    if status == "cold":
        # 雪の結晶
        draw.line((cx, 2, cx, 12), fill=255, width=1)
        draw.line((101, cy, 111, cy), fill=255, width=1)
        draw.line((102, 3, 110, 11), fill=255, width=1)
        draw.line((110, 3, 102, 11), fill=255, width=1)

    elif status == "hot":
        # 太陽
        draw.ellipse((103, 4, 109, 10), outline=255, fill=255)
        draw.line((106, 1, 106, 2), fill=255)
        draw.line((106, 12, 106, 13), fill=255)
        draw.line((100, 7, 101, 7), fill=255)
        draw.line((111, 7, 112, 7), fill=255)
        draw.line((102, 3, 103, 4), fill=255)
        draw.line((109, 10, 110, 11), fill=255)
        draw.line((109, 4, 110, 3), fill=255)
        draw.line((102, 11, 103, 10), fill=255)

    elif status == "comfortable":
        # チェックマーク
        draw.line((101, 7, 104, 10), fill=255, width=2)
        draw.line((104, 10, 111, 2), fill=255, width=2)


def draw_humidity_icon(draw, status):
    # 右上角の右側に、湿度状態の小さいアイコンを描く。
    # dry: 空の水滴 / comfortable: 満ちた水滴 / humid: 二つの水滴

    if status == "dry":
        # 空の水滴
        points = [(121, 1), (117, 7), (117, 10), (119, 12),
                  (121, 13), (123, 12), (125, 10), (125, 7), (121, 1)]
        draw.line(points, fill=255, width=1)

    elif status == "comfortable":
        # 一つの満ちた水滴
        points = [(121, 1), (117, 7), (117, 10), (119, 12),
                  (121, 13), (123, 12), (125, 10), (125, 7)]
        draw.polygon(points, fill=255)

    elif status == "humid":
        # 湿度が高い場合は二つの小さい水滴
        left_drop = [(119, 2), (116, 7), (116, 9), (117, 11),
                     (119, 12), (121, 11), (122, 9), (122, 7)]
        right_drop = [(124, 4), (122, 8), (122, 10), (123, 12),
                      (124, 13), (126, 12), (127, 10), (127, 8)]
        draw.polygon(left_drop, fill=255)
        draw.polygon(right_drop, fill=255)
