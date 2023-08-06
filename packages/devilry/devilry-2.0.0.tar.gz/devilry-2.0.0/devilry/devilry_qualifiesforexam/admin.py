from django.contrib import admin
from devilry.devilry_qualifiesforexam.models import Status, QualifiesForFinalExam


class QualifiesForFinalExamInline(admin.TabularInline):
    model = QualifiesForFinalExam
    fields = ['relatedstudent', 'qualifies']
    readonly_fields = ['relatedstudent', 'qualifies']
    extra = 0


class StatusAdmin(admin.ModelAdmin):
    inlines = [QualifiesForFinalExamInline]
    list_display = (
        'id',
        'period',
        'getStatusText',
        'createtime',
        'message',
    )
    search_fields = [
        'id',
        'period__short_name',
        'period__long_name',
        'period__parentnode__short_name',
        'period__parentnode__long_name',
        'message',
    ]
    readonly_fields = [
        'period',
        'createtime',
        'message',
        'user',
        'plugin',
        'exported_timestamp',
        'status'
    ]

    def get_queryset(self, request):
        return super(StatusAdmin, self).get_queryset(request)\
            .select_related(
                'period', 'period__parentnode')

    # def admins_as_string(self, obj):
    #     return ', '.join([user.username for user in obj.admins.all()])
    # admins_as_string.short_description = "Admins"

admin.site.register(Status, StatusAdmin)
