from PIL import Image, ImageDraw, ImageFont

def create_active_icon2():
    sizes = [(16,16),(32,32),(48,48),(64,64)]
    for size in sizes:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rita svart cirkel som bakgrund
        margin = 1
        draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                    fill=(0, 0, 0, 255), outline=(0, 0, 0, 255))

        # Gul smiley ansikte (mindre än bakgrundscirkeln)
        face_margin = size[0] * 0.3
        draw.ellipse([face_margin, face_margin, size[0]-face_margin, size[1]-face_margin], 
                    fill=(0, 0, 0, 255))

        # Svarta ögon
        eye_size = size[0] * 0.08
        left_eye_x = size[0] * 0.35
        right_eye_x = size[0] * 0.65
        eye_y = size[1] * 0.4

        draw.ellipse([left_eye_x - eye_size, eye_y - eye_size, 
                     left_eye_x + eye_size, eye_y + eye_size], fill=(255,255,0))
        draw.ellipse([right_eye_x - eye_size, eye_y - eye_size, 
                     right_eye_x + eye_size, eye_y + eye_size], fill=(255,255,0))

        # Leende mun
        mouth_width = size[0] * 0.3
        mouth_height = size[1] * 0.2
        mouth_x = size[0] * 0.5
        mouth_y = size[1] * 0.65

        draw.arc([mouth_x - mouth_width/2, mouth_y - mouth_height/2,
                 mouth_x + mouth_width/2, mouth_y + mouth_height/2], 
                start=0, end=180, fill=(255,255,0), width=max(1, int(size[0]/16)))

        # Spara en egen fil för varje storlek
        filename = f"active_{size[0]}x{size[1]}.ico"
        img.save(filename, format="ICO")
        
        
        
def create_active_icon():
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rita svart cirkel som bakgrund
    margin = 1
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(0, 0, 0, 255), outline=(0, 0, 0, 255))

    # Gul smiley ansikte (mindre än bakgrundscirkeln)
    face_margin = size[0] * 0.3
    draw.ellipse([face_margin, face_margin, size[0]-face_margin, size[1]-face_margin], 
                fill=(0, 0, 0, 255))

    # Svarta ögon
    eye_size = size[0] * 0.08
    left_eye_x = size[0] * 0.35
    right_eye_x = size[0] * 0.65
    eye_y = size[1] * 0.4

    draw.ellipse([left_eye_x - eye_size, eye_y - eye_size, 
                 left_eye_x + eye_size, eye_y + eye_size], fill=(255,255,0))
    draw.ellipse([right_eye_x - eye_size, eye_y - eye_size, 
                 right_eye_x + eye_size, eye_y + eye_size], fill=(255,255,0))

    # Leende mun
    mouth_width = size[0] * 0.3
    mouth_height = size[1] * 0.2
    mouth_x = size[0] * 0.5
    mouth_y = size[1] * 0.65

    draw.arc([mouth_x - mouth_width/2, mouth_y - mouth_height/2,
             mouth_x + mouth_width/2, mouth_y + mouth_height/2], 
            start=0, end=180, fill=(255,255,0), width=max(1, int(size[0]/16)))

    # Spara som .ico med flera storlekar
    img.save(
        "active.ico",
        format="ICO",
        sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    )

def create_idle_icon():
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rita svart cirkel som bakgrund
    margin = 1
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                fill=(0, 0, 0, 255), outline=(0, 0, 0, 255))
    
    # Gul smiley ansikte (mindre än bakgrundscirkeln)
    face_margin = size[0] * 0.15
    draw.ellipse([face_margin, face_margin, size[0]-face_margin, size[1]-face_margin], 
                fill=(0, 0, 0, 255))
    
    # Slutna ögon (sovande)
    eye_width = size[0] * 0.12
    left_eye_x = size[0] * 0.35
    right_eye_x = size[0] * 0.65
    eye_y = size[1] * 0.4
    line_width = max(1, int(size[0]/16))
    
    draw.line([left_eye_x - eye_width/2, eye_y, 
              left_eye_x + eye_width/2, eye_y], fill=(255,255,0), width=line_width)
    draw.line([right_eye_x - eye_width/2, eye_y, 
              right_eye_x + eye_width/2, eye_y], fill=(255,255,0), width=line_width)
    
    # Liten sovande mun
    mouth_width = size[0] * 0.15
    mouth_y = size[1] * 0.7
    draw.ellipse([size[0]*0.5 - mouth_width/2, mouth_y - mouth_width/4,
                 size[0]*0.5 + mouth_width/2, mouth_y + mouth_width/4], 
                fill=(255,255,0))
    
    # Zzz text (utanför den svarta cirkeln)
    try:
        font = ImageFont.truetype("arial.ttf", max(8, int(size[0]/4)))
    except:
        font = ImageFont.load_default()
    
    # Placera Zzz längst upp till höger, utanför den svarta cirkeln
    text_x = size[0] * 0.7
    text_y = size[1] * 0.05
    draw.text((text_x, text_y), "Zzz", font=font, fill=(255,255,0))
    
       
    # Spara som .ico med flera storlekar
    img.save(
        "idle.ico",
        format="ICO",
        sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    )


# Skapa ikonerna
create_active_icon()
create_idle_icon()
print("Färdiga runda .ico-filer skapade: active.ico (vaken) och idle.ico (sovande)")