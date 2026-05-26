import asyncio
from highrise.cli import main
import sys

if __name__ == "__main__":
    # تمرير المعرفات بشكل صريح مع خيارات سطر الأوامر الرسمية لدعم العوالم والغرف الفرعية
    sys.argv = [
        "highrise",
        "bot:MyBot",
        "6894bd39e3e4a405517cb530", # معرف العالم الرئيسي (World ID)
        "a2d28756193cd5d27e1ce58108a8d6ad44529721d2536c2248c67b7eca4006b5", # التوكن النظيف
        "--room-id", "6a04970a90ee23ef0aaff651" # معرف الغرفة الفرعية المملوكة لك داخل العالم
    ]
    main()
