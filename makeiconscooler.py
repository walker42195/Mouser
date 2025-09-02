from PIL import Image, ImageDraw

SIZES = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]

def draw_deer_silhouette(draw, bbox, pose="standing"):
    x0, y0, x1, y1 = bbox
    w = x1 - x0
    h = y1 - y0
    cx = x0 + w/2
    cy = y0 + h/2
    s = min(w, h)

    # proportioner (relativt s) för en hjort
    body_w = s * (0.60 if pose=="standing" else 0.70)
    body_h = s * (0.40 if pose=="standing" else 0.35)
    head_w = s * 0.20
    head_h = s * 0.18
    neck_h = s * 0.18
    leg_h = s * 0.45
    antler_w = s * 0.35
    antler_h = s * 0.30

    if pose == "standing":
        # kropp (oval)
        body_cx = cx
        body_cy = cy + s*0.05
        body = [
            (body_cx - body_w/2, body_cy - body_h/2),
            (body_cx + body_w/2, body_cy + body_h/2)
        ]
        draw.ellipse(body, fill=(255,255,255,255))

        # hals / huvud (rektangel + cirkel)
        neck_top_x = body_cx - body_w/2 + s*0.15
        neck_top_y = body_cy - body_h/2 - neck_h*0.1
        neck = [
            (neck_top_x, neck_top_y),
            (neck_top_x + head_w*0.35, neck_top_y + neck_h)
        ]
        draw.rectangle(neck, fill=(255,255,255,255))

        head_cx = neck[1][0] + head_w*0.2
        head_cy = neck_top_y + head_h*0.2
        head = [
            (head_cx - head_w/2, head_cy - head_h/2),
            (head_cx + head_w/2, head_cy + head_h/2)
        ]
        draw.ellipse(head, fill=(255,255,255,255))

        # öron (trianglar)
        ear1 = [(head_cx + head_w*0.10, head_cy - head_h*0.50),
                (head_cx + head_w*0.30, head_cy - head_h*0.70),
                (head_cx + head_w*0.00, head_cy - head_h*0.30)]
        ear2 = [(head_cx - head_w*0.20, head_cy - head_h*0.50),
                (head_cx - head_w*0.00, head_cy - head_h*0.70),
                (head_cx - head_w*0.30, head_cy - head_h*0.30)]
        draw.polygon(ear1, fill=(255,255,255,255))
        draw.polygon(ear2, fill=(255,255,255,255))

        # horn (greniga för hjort)
        antler_base_x = head_cx + head_w*0.20
        antler_base_y = head_cy - head_h*0.35
        a1 = [(antler_base_x, antler_base_y),
              (antler_base_x + antler_w*0.50, antler_base_y - antler_h*0.70),
              (antler_base_x + antler_w*0.30, antler_base_y - antler_h*0.50),
              (antler_base_x + antler_w*0.20, antler_base_y - antler_h*0.30)]
        a2 = [(antler_base_x - antler_w*0.05, antler_base_y - antler_h*0.10),
              (antler_base_x + antler_w*0.45, antler_base_y - antler_h*0.60),
              (antler_base_x + antler_w*0.25, antler_base_y - antler_h*0.40)]
        draw.polygon(a1, fill=(255,255,255,255))
        draw.polygon(a2, fill=(255,255,255,255))

        # ben — rektanglar
        leg_w = max(1, int(s*0.06))
        leg_x = body_cx - body_w/2 + leg_w
        for i in range(4):
            lx = leg_x + i*(body_w/4)
            ly_top = body_cy + body_h/2 - s*0.02
            ly_bottom = ly_top + leg_h
            draw.rectangle([(lx, ly_top), (lx + leg_w*1.4, ly_bottom)], fill=(255,255,255,255))

    else:
        # liggande — kropp större och huvud åt vänster-liggande
        body_cx = cx
        body_cy = cy + s*0.04
        body = [
            (body_cx - body_w/2, body_cy - body_h/2),
            (body_cx + body_w/2, body_cy + body_h/2)
        ]
        draw.ellipse(body, fill=(255,255,255,255))

        head_cx = body_cx - body_w/2 - head_w*0.20
        head_cy = body_cy - body_h*0.20
        head = [
            (head_cx - head_w/2, head_cy - head_h/2),
            (head_cx + head_w/2, head_cy + head_h/2)
        ]
        draw.ellipse(head, fill=(255,255,255,255))

        # öron
        ear = [(head_cx - head_w*0.05, head_cy - head_h*0.45),
               (head_cx + head_w*0.08, head_cy - head_h*0.62),
               (head_cx + head_w*0.18, head_cy - head_h*0.32)]
        draw.polygon(ear, fill=(255,255,255,255))

        # horn bakåtriktade
        antler = [(head_cx + head_w*0.15, head_cy - head_h*0.20),
                  (head_cx + antler_w*0.10, head_cy - antler_h*0.20),
                  (head_cx + antler_w*0.05, head_cy - antler_h*0.10)]
        draw.polygon(antler, fill=(255,255,255,255))

        # vikta ben under kroppen
        leg_w = max(1, int(s*0.06))
        lx1 = body_cx - body_w*0.20
        lx2 = body_cx + body_w*0.25
        ly_top = body_cy + body_h/4
        draw.rectangle([(lx1, ly_top), (lx1 + leg_w*1.4, ly_top + leg_w*3)], fill=(255,255,255,255))
        draw.rectangle([(lx2, ly_top), (lx2 + leg_w*1.4, ly_top + leg_w*3)], fill=(255,255,255,255))

def make_icon_image(size, pose="standing"):
    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # svart rund bakgrund
    margin = max(1, int(size[0]*0.04))
    draw.ellipse([margin, margin, size[0]-margin-1, size[1]-margin-1], fill=(0,0,0,255))
    # ritområde (inre cirkel)
    pad = int(size[0]*0.08)
    inner = (margin+pad, margin+pad, size[0]-margin-pad, size[1]-margin-pad)
    draw_deer_silhouette(draw, inner, pose=pose)
    return img

def save_icons(base_active="deer_active_silhouette", base_idle="deer_idle_silhouette"):
    sizes = SIZES
    active_256 = make_icon_image((256,256), pose="standing")
    idle_256 = make_icon_image((256,256), pose="lying")
    active_256.save(f"{base_active}.ico", format="ICO", sizes=sizes)
    idle_256.save(f"{base_idle}.ico", format="ICO", sizes=sizes)
    for s in sizes:
        make_icon_image(s, pose="standing").save(f"{base_active}_{s[0]}x{s[1]}.png")
        make_icon_image(s, pose="lying").save(f"{base_idle}_{s[0]}x{s[1]}.png")

if __name__ == "__main__":
    save_icons()
    print("Skapade silhuett-hjortar: deer_active_silhouette.ico, deer_idle_silhouette.ico och PNG-varianter.")