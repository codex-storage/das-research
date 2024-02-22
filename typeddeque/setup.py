from distutils.core import setup, Extension

def main():
    setup(name="typeddeque",
          version="0.0.1",
          description="typed deque classes",
          author="<Csaba Kiraly>",
          author_email="csaba.kiraly@gmail.com",
          ext_modules=[Extension("typeddeque", ["_collectionsmodule.c"])])

if __name__ == "__main__":
    main()