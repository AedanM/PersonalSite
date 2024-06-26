from django.contrib import admin

from .models import Education, Employment, SkillsAndTools


class ResumeAdmin(admin.ModelAdmin):
    empty_value_display = "-Not Set-"


# Register your models here.
admin.site.register(Education, ResumeAdmin)
admin.site.register(Employment, ResumeAdmin)
admin.site.register(SkillsAndTools, ResumeAdmin)
