import os

def set_env():
    os.environ.setdefault('DEVELOPMENT', 'True')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-%(dkfxmq46r$mryz#80q)i6&(r=e9w&4hk_lvy@416$7)hjl!1')

if __name__ == "__main__":
    set_env()
