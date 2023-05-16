from odoo import fields, models,api
import xlwt
from xlwt import easyxf
from cStringIO import StringIO
import base64
import itertools
from operator import itemgetter
import operator


class ProductProduct(models.Model):
    _inherit = "product.template"
    
    location_ids1=fields.Many2many("stock.location",string="Ubicaciones")

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    location_ids1=fields.Many2many("stock.location", string="Ubicaciones",store=True,compute="_get_location")

    @api.depends("product_tmpl_id.location_ids1")
    def _get_location(self):
        for line in self:
            if line.product_tmpl_id.location_ids1:
                line.location_ids1=line.product_tmpl_id.location_ids1
            else:
                line.location_ids1=False

class StockZero(models.TransientModel):
    _name = "stockzero"
    _description = "reporte stock zero"

    
    locations_ids = fields.Many2many(
        "stock.location",
        string="Ubicacion",
    )
   
    tipo_stock=fields.Selection([
        ("z","Stock Zero"),
        ("p","Stock con existencia"),
        ("t","Todos"),],string="Tipo de reporte")

    tipo_cate=fields.Selection([
        
        ("p","Producto"),
        ("c","Categoria"),],string="Tipo de Filtro")

    categ_id=fields.Many2many("product.category",string="Categoria de productos")
    product_id=fields.Many2many("product.product",string="Productos")
    

    
    
  

    def generate(self):
        report = self.env.ref("jr_stock_zero.stock_summary_report")
        return self.env['report'].get_action(self,"jr_stock_zero.comercial")

    def get_orders(self):
        if self.tipo_stock=="z":
            obj = self.env["product.product"].search(
                [
                    ("location_ids1", "in", self.locations_ids.ids),
                    ("qty_available","<=",0),
                   
                ]
            )
            orders=[]

            for line in obj:
                for record in line.location_ids1:
                    orders.append([record.name,line.default_code,line.name,line.qty_available])

        elif self.tipo_stock=="p":
            obj= self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                    
                ]
            )
            
            orders=[]
            for line in obj:
                if not orders:
                    orders.append([line.location_id.name,line.product_id.default_code,line.product_id.name,line.qty])
                else:
                    for record in orders:
                        if line.product_id.default_code== record[1] and line.location_id.name==record[0]:
                            record[2]=record[2]+line.qty


   

            

        elif self.tipo_stock=="t":
            product= self.env["product.product"].search(
                [
                    ("location_ids1", "in", self.locations_ids.ids),
                    ("qty_available","<=",0),
                   
                ]
            )

            quant1 = self.env["stock.quant"].search(
                [
                    ("location_id", "in", self.locations_ids.ids),
                    
                ]
            )

            orders1=[]
            for line in product:
                for record in line.location_ids1:
                    orders1.append([record.name,line.default_code,line.name,line.qty_available])

            quant=[]
            for line in quant1:
                if not quant:
                    quant.append([line.location_id.name,line.product_id.default_code,line.product_id.name,line.qty])
                else:
                    for record in quant:
                        if line.product_id.default_code== record[1] and line.location_id.name==record[0]:
                            record[2]=record[2]+line.qty
            
            orders=orders1+quant

        return orders
    
    def get_orders1(self):
        orders = {}
        if self.tipo_stock == "z" and self.tipo_cate=="p":
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                ("id", "in", self.product_id.ids),
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,]

        elif self.tipo_stock == "z" and self.tipo_cate=="c":
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                ("categ_id", "in", self.categ_id.ids),
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,
                            ]

        elif self.tipo_stock == "z" and not self.tipo_cate:
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,
                            ]

        elif self.tipo_stock == "p" and self.tipo_cate=="p":
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
                ("product_id.id","in",self.product_id.ids)
            ])
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty
        elif self.tipo_stock == "p" and self.tipo_cate=="c":
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
                ("product_id.categ_id","in",self.categ_id.ids)
            ])
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty

        elif self.tipo_stock == "p" and not self.tipo_cate:
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
                
            ])
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty

        elif self.tipo_stock == "t" and not self.tipo_cate:
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                #("qty_available", "<=", 0),
            ])
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,
                            ]
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty

        elif self.tipo_stock == "t" and self.tipo_cate=="p":
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                ("id", "in", self.product_id.ids),
            ])
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
                ("product_id","in",self.product_id.ids)
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,
                            ]
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty
        
        elif self.tipo_stock == "t" and self.tipo_cate=="c":
            products = self.env["product.product"].search([
                ("location_ids1", "in", self.locations_ids.ids),
                ("categ_id", "in", self.categ_id.ids),
            ])
            quants = self.env["stock.quant"].search([
                ("product_id.location_ids1", "in", self.locations_ids.ids),
                ("product_id.categ_id","in",self.categ_id.ids)
            ])
            for product in products:
                for location in product.warehouses:
                    if location.lot_stock_id in self.locations_ids and location.product_qty_available<=0:
                        key = (location.lot_stock_id.id, product.id)
                        if key not in orders:
                            orders[key] = [
                                location.lot_stock_id.name,
                                product.default_code,
                                product.name,
                                location.product_qty_available,
                            ]
            for quant in quants:
                key = (quant.location_id.id, quant.product_id.id)
                if key not in orders:
                    orders[key] = [
                        quant.location_id.name,
                        quant.product_id.default_code,
                        quant.product_id.name,
                        quant.qty,
                    ]
                else:
                    orders[key][3] += quant.qty

        return orders.values()
    
    @api.multi
    def export_stock_ledger(self):
        workbook = xlwt.Workbook()
        filename = 'stock_zero.xls'
        # Style
        main_header_style = easyxf('font:height 400;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 150; align: horiz left;' "borders: top thin,bottom thin")
        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
        text_right_bold1 = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin", num_format_str='0.00')
        text_center = easyxf('font:height 150; align: horiz center;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 150; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')

        worksheet = []
        
        worksheet.append(1)
        work=0
        worksheet[work] = workbook.add_sheet("stock")
        
        worksheet[work].write_merge(0, 1, 0, 6, 'STOCK ', main_header_style)
        for i in range(0, 12):
            worksheet[work].col(i).width = 140 * 30




        tags = ['Ubicacion','Codigo','Producto','Cantidad']

        r= 3
        
        c = 1
        for tag in tags:
            worksheet[work].write(r, c, tag, header_style)
            c+=1

        lines=self.get_orders1()
        
        r=4
        
        for line in lines:
            
            c=1
            worksheet[work].write(r, c, line[0], text_left)
            c+=1
            worksheet[work].write(r,c,line[1], text_left)
            c += 1
            worksheet[work].write(r, c, line[2], text_right)
            c+=1
            worksheet[work].write(r, c, line[3], text_right)
           
            
            r+=1
          



         

        fp = StringIO()
        workbook.save(fp)
        export_id = self.env['stockzero2'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'stockzero2',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


 

class StockExcel(models.TransientModel):
    _name = "stockzero2"

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File')


