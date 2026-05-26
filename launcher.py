import asyncio
from highrise.__main__ import main
import sys

if __name__ == "__main__":
    # تعديل المعاملات الداخلية لتشمل معرف العالم والتوكن ومعرف الغرفة الفرعية
    sys.argv = [
        "highrise",
        "bot:MyBot",
        "6894bd39e3e4a405517cb530" # معرف العالم الرئيسي (World ID)
    ]
    
    # حقن المتغيرات الحساسة مباشرة للبيئة لتتعرف عليها واجهة واجهة برمجة التطبيقات للعبة لعام 2026
    import os
    os.environ["HIGHRISE_API_TOKEN"] = "a2d28756193cd5d27e1ce58108a8d6ad44529721d2536c2248c67b7eca4006b5"
    os.environ["HIGHRISE_ROOM_ID"] = "6a04970a90ee23ef0aaff651" # معرف غرفتك المباشرة المأهولة باللاعبين
    
    main()
