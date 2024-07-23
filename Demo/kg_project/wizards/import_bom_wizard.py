import base64
import xlrd
import tempfile
import binascii

from odoo import models, fields, modules
from odoo.exceptions import UserError



class ImportBOM(models.TransientModel):
    _name = "import.bom.wizard"
    _description = 'Importing the BOM'


    data_file = fields.Binary(string="Template File", required=True)
    filename = fields.Char(string="Filename", track_visibility="onchange", default='bom_template.xls')

    # def get_import_templates(self):
    #     print('haiiii')
    #     with open(modules.get_module_resource('kg_casio', 'static/xls', 'customer_template.xls'),'rb') as f:
    #         return base64.b64encode(f.read())

    def export_file(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.data_file))
            fp.seek(0)
            fp.close
        except:
            raise UserError("Invalid File!")

        workbook = xlrd.open_workbook(fp.name, on_demand=True)
        sheet = workbook.sheet_by_index(0)

        if sheet.ncols == 0:
            return

        first_row = []
        for col in range(sheet.ncols):
            first_row.append(sheet.cell_value(0, col))

        import_lines = []
        for row in range(1, sheet.nrows):
            line = {}
            for col in range(sheet.ncols):
                line[first_row[col]] = sheet.cell_value(row, col)
            import_lines.append(line)

        print(import_lines)

        # bom_line_ids = []
        # if self.data_file:
        #     print(self.data_file,'sssssssssssssssssssssssssssssssssssssssss')
        #     with open(modules.get_module_resource('kg_project', 'static/xls', 'customer_template.xls'), 'rb') as f:
        #         return base64.b64encode(f.read())