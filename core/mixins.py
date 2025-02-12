from django.http import HttpResponse
from import_export.formats.base_formats import XLSX
from io import BytesIO
import zipfile
from tablib import Dataset

class ExportMixin():
    def export_selected_records(self, request, queryset):
        export_format = request.POST.get("file_format", "xlsx")
        resource = self.resource_class()
        resource.context = {"export_format": export_format}
        dataset = resource.export(queryset)
        file_format = XLSX()
        file_name = "exported_data"
        export_data = file_format.export_data(dataset)
        response = HttpResponse(export_data, content_type=file_format.get_content_type())
        response['Content-Disposition'] = f'attachment; filename="{file_name}.{file_format.get_extension()}"'

        return response

    export_selected_records.short_description = "Export Selected Records"


class ExportWithInlineMixin():
    def export_selected_records(self, request, queryset):
        export_format = request.POST.get("file_format", "xlsx")
        resource = self.resource_class()
        resource.context = {"export_format": export_format}
        file_format = XLSX()

        responses = []
        for batch in queryset:
            dataset = resource.export([batch])

            batch_name = str(batch).replace(" ", "_")
            file_name = f"{batch_name}_{batch.pk}.{file_format.get_extension()}"
            export_data = file_format.export_data(dataset)
            response = HttpResponse(
                export_data, content_type=file_format.get_content_type()
            )
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'
            responses.append((file_name, response.content))

        if len(responses) == 1:
            return HttpResponse(
                responses[0][1],
                content_type=file_format.get_content_type(),
                headers={
                    "Content-Disposition": f'attachment; filename="{responses[0][0]}"'
                },
            )
        else:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, content in responses:
                    zip_file.writestr(file_name, content)

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="exported_batches.zip"'
            return response

    export_selected_records.short_description = "Export Selected Records"


class DataSetMixin():

    def _create_dataset(self, data, headers):
        dataset = Dataset()
        dataset.headers = headers
        for row in data:
            dataset.append([row[col] for col in headers])

        return dataset
