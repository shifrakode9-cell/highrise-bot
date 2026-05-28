import os
import sys

# نقوم بتشغيل المكتبة كأمر نظام مباشرة
# هذا يتجاوز تماماً مشكلة AttributeError
os.system(f"python -m highrise {os.getenv('ROOM_ID')} {os.getenv('API_KEY')}")
