import asyncio
from highrise import Highrise

async def main():
    hr = Highrise()
    # طباعة كل الدوال المتاحة في الكائن للبحث عن الدالة الصحيحة
    print("--- الدوال المتاحة في Highrise هي: ---")
    print(dir(hr))

if __name__ == "__main__":
    asyncio.run(main())
