# import logging
# from django.apps import apps
# from django.core.exceptions import AppRegistryNotReady

# class DatabaseHandler(logging.Handler):
#     def emit(self, record):
#         try:
#             if not apps.ready:
#                 return
#             print('test')
#             LogEntry = apps.get_model('settings', 'LogEntry')
#             log_entry = LogEntry(
#                 level=record.levelname,
#                 module=record.module,
#                 message=record.getMessage()
#             )
#             log_entry.save()
#         except AppRegistryNotReady:
#             pass  # Avoid logging within the handler
#         except Exception as e:
#             pass  # Avoid logging within the handler
