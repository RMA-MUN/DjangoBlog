from django.apps import AppConfig


class AuthorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'author'
    
    def ready(self):
        # 导入signals以确保它们被注册
        import author.signals
