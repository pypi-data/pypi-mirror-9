from django.contrib import admin

#import local models
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, StagingTable, StagingBatch, StagingQueue, ReferenceColumn

#Register models
admin.site.register(State)
admin.site.register(DataSource)
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(Column)
admin.site.register(ImportQueue)

class ImportQueueInline(admin.StackedInline):
    model = ImportQueue
    fields = ['file']
    extra = 3

class ImportBatchAdmin(admin.ModelAdmin):
    inlines = [ImportQueueInline]

admin.site.register(ImportBatch, ImportBatchAdmin)
admin.site.register(StagingTable)
admin.site.register(StagingQueue)

class StagingQueueInline(admin.StackedInline):
    model = StagingQueue
    #fields = ['file']
    extra = 3

class StagingBatchAdmin(admin.ModelAdmin):
    inlines = [StagingQueueInline]

admin.site.register(StagingBatch, StagingBatchAdmin)
admin.site.register(ReferenceColumn)